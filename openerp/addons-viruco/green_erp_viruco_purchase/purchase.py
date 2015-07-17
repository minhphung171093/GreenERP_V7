# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import time
from datetime import date
from datetime import timedelta
from datetime import datetime
import calendar
import openerp.addons.decimal_precision as dp
import codecs
from openerp import netsvc


class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _columns = {
        'hop_dong_id':fields.many2one('hop.dong','Hợp đồng',required = True,readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'user_id':fields.many2one('res.users','Người đề nghị',readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
    }
    
    _defaults = {
        'user_id': lambda self, cr, uid, context=None: uid,
    }
    
    def onchange_hop_dong_id(self, cr, uid, ids, hop_dong_id=False, context=None):
        if ids:
            cr.execute(''' delete from purchase_order_line where order_id in %s ''',(tuple(ids),))
        vals = {'order_line':[]}
        order_line = []
        if hop_dong_id:
            hd_obj = self.pool.get('hop.dong')
            for hd_line in hd_obj.browse(cr, uid, hop_dong_id).hopdong_line:
                sql = '''
                    select case when sum(product_qty)!=0 then sum(product_qty) else 0 end quantity
                        from purchase_order_line where hd_line_id=%s
                '''%(hd_line.id)
                cr.execute(sql)
                quantity = cr.fetchone()[0]
                if quantity<hd_line.product_qty:
                    val_line={
                        'product_id': hd_line.product_id and hd_line.product_id.id or False,
                        'name':hd_line.name,
                        'chatluong_id':hd_line.product_id and hd_line.product_id.chatluong_id and hd_line.product_id.chatluong_id.id or False,
                        'quycach_donggoi_id':hd_line.product_id and hd_line.product_id.quycach_donggoi_id and hd_line.product_id.quycach_donggoi_id.id or False,
                        'product_uom': hd_line.product_uom and hd_line.product_uom.id or False,
                        'product_qty': hd_line.product_qty-quantity,
                        'price_unit': hd_line.price_unit,
                        'taxes_id': [(6,0,[t.id for t in hd_line.tax_id])],
                        'hd_line_id': hd_line.id,
                        'state': 'draft',
                        'date_planned': time.strftime('%Y-%m-%d'),
                    }
                    order_line.append((0,0,val_line))
            vals['order_line'] = order_line
        return {'value': vals}
    
    #Rang buoc khi mua hang
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        todo = []
        hop_dong_obj = self.pool.get('hop.dong')
        hop_dong_line_obj = self.pool.get('hopdong.line')
        for po in self.browse(cr, uid, ids, context=context):
            if not po.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a purchase order without any purchase order line.'))
            if po.invoice_method == 'picking' and not any([l.product_id and l.product_id.type in ('product', 'consu') for l in po.order_line]):
                raise osv.except_osv(
                    _('Error!'),
                    _("You cannot confirm a purchase order with Invoice Control Method 'Based on incoming shipments' that doesn't contain any stockable item."))
            if po.hop_dong_id:
                for order_line in po.order_line:
                    hop_dong_line = hop_dong_line_obj.search(cr,uid,[('hopdong_id','=',po.hop_dong_id.id),('product_id','=',order_line.product_id.id)])
                    if not hop_dong_line:
                        raise osv.except_osv(_('Warning!'),_('Sản phẩm %s không có trong hợp đồng mua!')%(order_line.product_id.name))
                    sql = '''
                        select product_id, sum(product_qty) as total_qty
                        from purchase_order_line l
                        inner join purchase_order p on l.order_id = p.id
                        where p.hop_dong_id = %s and p.partner_id = %s and l.product_id = %s and p.state in ('confirmed','done','approved','except_picking','except_invoice')
                        group by product_id
                    '''%(po.hop_dong_id.id,po.partner_id.id,order_line.product_id.id)
                    cr.execute(sql)
                    lines_qty = cr.dictfetchall()
                    product_qty = order_line.product_qty
                    if hop_dong_line_obj.browse(cr,uid,hop_dong_line[0]).tax_id != order_line.taxes_id:
                        raise osv.except_osv(_('Warning!'),_('Không thể duyệt sản phẩm có thuế khác thuế trong hợp đồng mua!'))
                    if hop_dong_line_obj.browse(cr,uid,hop_dong_line[0]).price_unit != order_line.price_unit:
                        raise osv.except_osv(_('Warning!'),_('Không thể duyệt sản phẩm với đơn giá khác đơn giá trong hợp đồng mua: %s!')%(hop_dong_line_obj.browse(cr,uid,hop_dong_line[0]).price_unit))
                    if lines_qty:
                        for line_qty in lines_qty:
                            product_qty += line_qty['total_qty']
                    if product_qty > hop_dong_line_obj.browse(cr,uid,hop_dong_line[0]).product_qty:
                        raise osv.except_osv(_('Warning!'),_('Không thể duyệt sản phẩm với số lượng lớn hơn số lượng trong hợp đồng mua: %s!')%(hop_dong_line_obj.browse(cr,uid,hop_dong_line[0]).product_qty))
            for line in po.order_line:
                if line.state=='draft':
                    todo.append(line.id)

        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid})
        return True
    
    def _prepare_order_picking(self, cr, uid, order, context=None):
        return {
            'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
            'origin': order.name + ((order.origin and (':' + order.origin)) or ''),
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'partner_id': order.partner_id.id,
            'invoice_state': '2binvoiced' if order.invoice_method == 'picking' else 'none',
            'type': 'in',
            'purchase_id': order.id,
            'nguoi_denghi_id': order.user_id and order.user_id.id or False,
            'company_id': order.company_id.id,
            'move_lines' : [],
        }
    
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        price_unit = order_line.price_unit
        if order.currency_id.id != order.company_id.currency_id.id:
            #we don't round the price_unit, as we may want to store the standard price with more digits than allowed by the currency
            price_unit = self.pool.get('res.currency').compute(cr, uid, order.currency_id.id, order.company_id.currency_id.id, price_unit, round=False, context=context)
        return {
            'name': order_line.name or '',
            'product_id': order_line.product_id.id,
            'product_qty': order_line.product_qty,
            'product_uos_qty': order_line.product_qty,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_uom.id,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'date_expected': self.date_to_datetime(cr, uid, order_line.date_planned, context),
            'location_id': order.partner_id.property_stock_supplier.id,
            'location_dest_id': order.location_id.id,
            'picking_id': picking_id,
            'partner_id': order.dest_address_id.id or order.partner_id.id,
            'move_dest_id': order_line.move_dest_id.id,
            'state': 'draft',
            'type':'in',
            'purchase_line_id': order_line.id,
            'company_id': order.company_id.id,
            'price_unit': price_unit,
            'hop_dong_mua_id': order.hop_dong_id and order.hop_dong_id.id or False,
            'chatluong_id': order_line.product_id.chatluong_id and order_line.product_id.chatluong_id.id or False,
            'quycach_donggoi_id': order_line.product_id.quycach_donggoi_id and order_line.product_id.quycach_donggoi_id.id or False,
            'quycach_baobi_id': order_line.product_id.quycach_baobi_id and order_line.product_id.quycach_baobi_id.id or False,
        }
        
    def action_invoice_create(self, cr, uid, ids, context=None):
        """Generates invoice for given ids of purchase orders and links that invoice ID to purchase order.
        :param ids: list of ids of purchase orders.
        :return: ID of created invoice.
        :rtype: int
        """
        if context is None:
            context = {}
        journal_obj = self.pool.get('account.journal')
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')

        res = False
        uid_company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        for order in self.browse(cr, uid, ids, context=context):
            context.pop('force_company', None)
            if order.company_id.id != uid_company_id:
                #if the company of the document is different than the current user company, force the company in the context
                #then re-do a browse to read the property fields for the good company.
                context['force_company'] = order.company_id.id
                order = self.browse(cr, uid, order.id, context=context)
            pay_acc_id = order.partner_id.property_account_payable.id
            journal_ids = journal_obj.search(cr, uid, [('type', '=', 'purchase'), ('company_id', '=', order.company_id.id)], limit=1)
            if not journal_ids:
                raise osv.except_osv(_('Error!'),
                    _('Define purchase journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))

            # generate invoice line correspond to PO line and link that to created invoice (inv_id) and PO line
            inv_lines = []
            for po_line in order.order_line:
                acc_id = self._choose_account_from_po_line(cr, uid, po_line, context=context)
                inv_line_data = self._prepare_inv_line(cr, uid, acc_id, po_line, context=context)
                inv_line_id = inv_line_obj.create(cr, uid, inv_line_data, context=context)
                inv_lines.append(inv_line_id)

                po_line.write({'invoice_lines': [(4, inv_line_id)]}, context=context)

            # get invoice data and create invoice
            inv_data = {
                'name': order.partner_ref or order.name,
                'reference': order.partner_ref or order.name,
                'account_id': pay_acc_id,
                'type': 'in_invoice',
                'partner_id': order.partner_id.id,
                'currency_id': order.pricelist_id.currency_id.id,
                'journal_id': len(journal_ids) and journal_ids[0] or False,
                'invoice_line': [(6, 0, inv_lines)],
                'origin': order.name,
                'fiscal_position': order.fiscal_position.id or False,
                'payment_term': order.payment_term_id.id or False,
                'company_id': order.company_id.id,
                'hop_dong_id': order.hop_dong_id and order.hop_dong_id.id or False,
            }
            inv_id = inv_obj.create(cr, uid, inv_data, context=context)

            # compute the invoice
            inv_obj.button_compute(cr, uid, [inv_id], context=context, set_total=True)

            # Link this new invoice to related purchase order
            order.write({'invoice_ids': [(4, inv_id)]}, context=context)
            res = inv_id
        return res
    
purchase_order()

class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"
    _columns = {
                'chatluong_id':fields.many2one('chatluong.sanpham','Chất lượng'),
                'quycach_donggoi_id':fields.many2one('quycach.donggoi','Quy cách đóng gói'),
                'hd_line_id':fields.many2one('hopdong.line','Thông tin mặt hàng'),
                }
    
    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, context=None):
        """
        onchange handler of product_id.
        """
        if context is None:
            context = {}

        res = {'value': {'price_unit': price_unit or 0.0, 'name': name or '', 'product_uom' : uom_id or False}}
        if not product_id:
            return res

        product_product = self.pool.get('product.product')
        product_uom = self.pool.get('product.uom')
        res_partner = self.pool.get('res.partner')
        product_supplierinfo = self.pool.get('product.supplierinfo')
        product_pricelist = self.pool.get('product.pricelist')
        account_fiscal_position = self.pool.get('account.fiscal.position')
        account_tax = self.pool.get('account.tax')

        # - check for the presence of partner_id and pricelist_id
        #if not partner_id:
        #    raise osv.except_osv(_('No Partner!'), _('Select a partner in purchase order to choose a product.'))
        #if not pricelist_id:
        #    raise osv.except_osv(_('No Pricelist !'), _('Select a price list in the purchase order form before choosing a product.'))

        # - determine name and notes based on product in partner lang.
        context_partner = context.copy()
        if partner_id:
            lang = res_partner.browse(cr, uid, partner_id).lang
            context_partner.update( {'lang': lang, 'partner_id': partner_id} )
        product = product_product.browse(cr, uid, product_id, context=context_partner)
        #call name_get() with partner in the context to eventually match name and description in the seller_ids field
        if not name or not uom_id:
            # The 'or not uom_id' part of the above condition can be removed in master. See commit message of the rev. introducing this line.
            dummy, name = product_product.name_get(cr, uid, product_id, context=context_partner)[0]
            if product.description_purchase:
                name += '\n' + product.description_purchase
            res['value'].update({'name': name})

        # - set a domain on product_uom
        res['domain'] = {'product_uom': [('category_id','=',product.uom_id.category_id.id)]}

        # - check that uom and product uom belong to the same category
        product_uom_po_id = product.uom_po_id.id
        if not uom_id:
            uom_id = product_uom_po_id

        if product.uom_id.category_id.id != product_uom.browse(cr, uid, uom_id, context=context).category_id.id:
            if context.get('purchase_uom_check') and self._check_product_uom_group(cr, uid, context=context):
                res['warning'] = {'title': _('Warning!'), 'message': _('Selected Unit of Measure does not belong to the same category as the product Unit of Measure.')}
            uom_id = product_uom_po_id

        res['value'].update({'product_uom': uom_id})

        # - determine product_qty and date_planned based on seller info
        if not date_order:
            date_order = fields.date.context_today(self,cr,uid,context=context)


        supplierinfo = False
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Unit of Measure')
        for supplier in product.seller_ids:
            if partner_id and (supplier.name.id == partner_id):
                supplierinfo = supplier
                if supplierinfo.product_uom.id != uom_id:
                    res['warning'] = {'title': _('Warning!'), 'message': _('The selected supplier only sells this product by %s') % supplierinfo.product_uom.name }
                min_qty = product_uom._compute_qty(cr, uid, supplierinfo.product_uom.id, supplierinfo.min_qty, to_uom_id=uom_id)
                if float_compare(min_qty , qty, precision_digits=precision) == 1: # If the supplier quantity is greater than entered from user, set minimal.
                    if qty:
                        res['warning'] = {'title': _('Warning!'), 'message': _('The selected supplier has a minimal quantity set to %s %s, you should not purchase less.') % (supplierinfo.min_qty, supplierinfo.product_uom.name)}
                    qty = min_qty
        dt = self._get_date_planned(cr, uid, supplierinfo, date_order, context=context).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        qty = qty or 1.0
        res['value'].update({'date_planned': date_planned or dt})
        if qty:
            res['value'].update({'product_qty': qty})

        # - determine price_unit and taxes_id
        if pricelist_id:
            price = product_pricelist.price_get(cr, uid, [pricelist_id],
                    product.id, qty or 1.0, partner_id or False, {'uom': uom_id, 'date': date_order})[pricelist_id]
        else:
            price = product.standard_price

        taxes = account_tax.browse(cr, uid, map(lambda x: x.id, product.supplier_taxes_id))
        fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
        taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
        res['value'].update({'price_unit': price, 'taxes_id': taxes_ids})
        
        res['value'].update({'chatluong_id': product.chatluong_id.id,'quycach_donggoi_id': product.quycach_donggoi_id.id})
        return res

purchase_order_line()

class hop_dong(osv.osv):
    _inherit = "hop.dong"
    
    def duyet_hd_mua(self, cr, uid, ids, context=None):
        purchase_obj = self.pool.get('purchase.order')
        order_line = []
        vals = {}
        wf_service = netsvc.LocalService('workflow')
        for hd in self.browse(cr, uid, ids):
            warehouse_obj = self.pool.get('stock.warehouse')
            warehouse_ids = warehouse_obj.search(cr, uid, [('company_id','=',hd.company_id.id)])
            vals={'pricelist_id':hd.pricelist_id.id,'warehouse_id': warehouse_ids and warehouse_ids[0] or False,'partner_id':hd.partner_id.id,'hop_dong_id':hd.id,'invoice_method':'picking','state':'draft'}
            vals.update(purchase_obj.onchange_partner_id(cr, uid, [], hd.partner_id.id)['value'])
            vals.update(purchase_obj.onchange_hop_dong_id(cr, uid, [], hd.id)['value'])
            vals.update(purchase_obj.onchange_warehouse_id(cr, uid, [], warehouse_ids and warehouse_ids[0] or False)['value'])
            purchase_id = purchase_obj.create(cr, uid, vals)
            wf_service.trg_validate(uid, 'purchase.order', purchase_id, 'purchase_confirm', cr)
        return self.write(cr, uid, ids, {'state': 'da_duyet'})
    
hop_dong()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
