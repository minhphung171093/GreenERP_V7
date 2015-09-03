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



class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'thoigian_giaohang':fields.datetime('Thời gian giao hàng'),
        'nguoi_gioithieu_id':fields.many2one('res.partner','Người giới thiệu',readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'dieukien_giaohang_id':fields.many2one('dieukien.giaohang','Điều kiện giao hàng'),
        'hop_dong_id':fields.many2one('hop.dong','Hợp đồng',readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'hinhthuc_giaohang_id':fields.many2one('hinhthuc.giaohang','Hình thức giao hàng'),
        'so_chuyenphatnhanh':fields.char('Số chuyển phát nhanh',size=1024),
        'thanhtoan':fields.boolean('Thanh toán'),
        'ngay_thanhtoan':fields.date('Ngày thanh toán'),
        'dagui_nganhang':fields.boolean('Đã gửi ngân hàng'),
        'ngaygui_nganhang':fields.date('Ngày gửi ngân hàng'),
        'dagui_hopdong':fields.boolean('Đã gửi hợp đồng'),
        'ngaygui_hopdong':fields.date('Ngày gửi hợp đồng'),
        'dagui_hoadon':fields.boolean('Đã gửi hóa đơn'),
        'ngaygui_hoadon':fields.date('Ngày gửi hóa đơn'),
        'dagui_chungtugoc':fields.boolean('Đã gửi chứng từ gốc'),
        'ngaygui_chungtugoc':fields.date('Ngày gửi chứng từ gốc'),
        'plhd_id':fields.many2one('phuluc.hop.dong','Phụ lục hợp đồng'),
    }
#     
#     def action_button_confirm(self, cr, uid, ids, context=None):
#         assert len(ids) == 1, 'This option should only be used for a single id at a time.'
#         sale_line_obj = self.pool.get('sale.order.line')
#         hop_dong_obj = self.pool.get('hop.dong')
#         hop_dong_line_obj = self.pool.get('hopdong.line')
#         for sale in self.browse(cr, uid, ids):
#             if sale.hop_dong_id:
#                 for order_line in sale.order_line:
#                     hop_dong_line = hop_dong_line_obj.search(cr,uid,[('hopdong_id','=',sale.hop_dong_id.id),('product_id','=',order_line.product_id.id)])
#                     if not hop_dong_line:
#                         raise osv.except_osv(_('Warning!'),_('Sản phẩm %s không có trong hợp đồng!')%(order_line.product_id.name))
#                     sql = '''
#                         select product_id, sum(product_uom_qty) as total_qty
#                         from sale_order_line l
#                         inner join sale_order s on l.order_id = s.id
#                         where s.hop_dong_id = %s and s.partner_id = %s and l.product_id = %s and s.state in ('done','manual','progress')
#                         group by product_id
#                     '''%(sale.hop_dong_id.id,sale.partner_id.id,order_line.product_id.id)
#                     cr.execute(sql)
#                     lines_qty = cr.dictfetchall()
#                     product_uom_qty = order_line.product_uom_qty
#                     if hop_dong_line_obj.browse(cr,uid,hop_dong_line[0]).tax_id != order_line.tax_id:
#                         raise osv.except_osv(_('Warning!'),_('Không thể duyệt sản phẩm có thuế khác thuế trong hợp đồng!'))
#                     if hop_dong_line_obj.browse(cr,uid,hop_dong_line[0]).price_unit != order_line.price_unit:
#                         raise osv.except_osv(_('Warning!'),_('Không thể duyệt sản phẩm với đơn giá khác đơn giá trong hợp đồng: %s!')%(hop_dong_line_obj.browse(cr,uid,hop_dong_line[0]).price_unit))
#                     if lines_qty:
#                         for line_qty in lines_qty:
#                             product_uom_qty += line_qty['total_qty']
#                     if product_uom_qty > hop_dong_line_obj.browse(cr,uid,hop_dong_line[0]).product_qty:
#                         raise osv.except_osv(_('Warning!'),_('Không thể duyệt sản phẩm với số lượng lớn hơn số lượng trong hợp đồng: %s!')%(hop_dong_line_obj.browse(cr,uid,hop_dong_line[0]).product_qty))
#         wf_service = netsvc.LocalService('workflow')
#         wf_service.trg_validate(uid, 'sale.order', ids[0], 'order_confirm', cr)
#         return True
#     
    def _prepare_order_picking(self, cr, uid, order, context=None):
        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        return {
            'name': pick_name,
            'origin': order.name,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'type': 'out',
            'state': 'auto',
            'move_type': order.picking_policy,
            'sale_id': order.id,
            'partner_id': order.partner_shipping_id.id,
            'note': order.note,
            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
            'company_id': order.company_id.id,
            'nguoi_denghi_id': order.user_id and order.user_id.id or False,
        }
#Them hop dong tren stock move khj confirm sale    
    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):
        location_id = order.shop_id.warehouse_id.lot_stock_id.id
        output_id = order.shop_id.warehouse_id.lot_output_id.id
        return {
            'name': line.name,
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id)\
                    or line.product_uom.id,
            'product_packaging': line.product_packaging.id,
            'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
            'location_id': location_id,
            'location_dest_id': output_id,
            'sale_line_id': line.id,
            'tracking_id': False,
            'state': 'draft',
            #'state': 'waiting',
            'company_id': order.company_id.id,
            'price_unit': line.product_id.standard_price or 0.0,
            'hop_dong_ban_id': order.hop_dong_id and order.hop_dong_id.id or False,
            'chatluong_id': line.product_id.chatluong_id and line.product_id.chatluong_id.id or False,
            'quycach_donggoi_id': line.product_id.quycach_donggoi_id and line.product_id.quycach_donggoi_id.id or False,
            'quycach_baobi_id': line.product_id.quycach_baobi_id and line.product_id.quycach_baobi_id.id or False,
        }
    
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sales order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        if context is None:
            context = {}
        journal_ids = self.pool.get('account.journal').search(cr, uid,
            [('type', '=', 'sale'), ('company_id', '=', order.company_id.id)],
            limit=1)
        if not journal_ids:
            raise osv.except_osv(_('Error!'),
                _('Please define sales journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))
        invoice_vals = {
            'name': order.client_order_ref or '',
            'origin': order.name,
            'type': 'out_invoice',
            'reference': order.client_order_ref or order.name,
            'account_id': order.partner_id.property_account_receivable.id,
            'partner_id': order.partner_invoice_id.id,
            'journal_id': journal_ids[0],
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'comment': order.note,
            'payment_term': order.payment_term and order.payment_term.id or False,
            'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            'date_invoice': context.get('date_invoice', False),
            'company_id': order.company_id.id,
            'user_id': order.user_id and order.user_id.id or False,
            'hop_dong_id': order.hop_dong_id and order.hop_dong_id.id or False,
        }

        # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
        invoice_vals.update(self._inv_get(cr, uid, order, context=context))
        return invoice_vals
    
    def onchange_hop_dong_id(self, cr, uid, ids, hop_dong_id=False, context=None):
        if ids:
            cr.execute(''' delete from sale_order_line where order_id in %s ''',(tuple(ids),))
        vals = {'order_line':[]}
        order_line = []
        if hop_dong_id:
            hd_obj = self.pool.get('hop.dong')
            hd = hd_obj.browse(cr, uid, hop_dong_id)
            for hd_line in hd.hopdong_line:
                sql = '''
                    select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end quantity
                        from sale_order_line where hd_line_id=%s
                '''%(hd_line.id)
                cr.execute(sql)
                quantity = cr.fetchone()[0]
                if quantity<hd_line.product_qty:
                    val_line={
                        'product_id': hd_line.product_id and hd_line.product_id.id or False,
                        'name':hd_line.name,
                        'chatluong_id':hd_line.chatluong_id and hd_line.chatluong_id.id or False,
                        'quycach_donggoi_id':hd_line.quycach_donggoi_id and hd_line.quycach_donggoi_id.id or False,
                        'product_uom': hd_line.product_uom and hd_line.product_uom.id or False,
                        'product_uom_qty': hd_line.product_qty-quantity,
                        'price_unit': hd_line.price_unit,
                        'tax_id': [(6,0,[t.id for t in hd_line.tax_id])],
                        'hd_line_id': hd_line.id,
                        'state': 'draft',
                        'type': 'make_to_stock',
                    }
                    order_line.append((0,0,val_line))
            vals.update({
                'order_line': order_line,
                'nguoi_gioithieu_id': hd.donbanhang_id.nguoi_gioithieu_id and hd.donbanhang_id.nguoi_gioithieu_id.id or False,
                'dieukien_giaohang_id': hd.donbanhang_id.dieukien_giaohang_id and hd.donbanhang_id.dieukien_giaohang_id.id or False,
                'hinhthuc_giaohang_id': hd.donbanhang_id.hinhthuc_giaohang_id and hd.donbanhang_id.hinhthuc_giaohang_id.id or False,
                'so_chuyenphatnhanh': hd.donbanhang_id.so_chuyenphatnhanh,
            })
        return {'value': vals}
    
sale_order()
class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns = {
                'chatluong_id':fields.many2one('chatluong.sanpham','Chất lượng'),
                'quycach_donggoi_id':fields.many2one('quycach.donggoi','Quy cách đóng gói'),
                'hd_line_id':fields.many2one('hopdong.line','Thông tin mặt hàng'),
                'plhd_line_id':fields.many2one('phuluc.hopdong.line','Phụ lục hợp đồng line'),
                }
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        lang = lang or context.get('lang',False)
        if not  partner_id:
            raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
        warning = {}
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        context = {'lang': lang, 'partner_id': partner_id}
        if partner_id:
            lang = partner_obj.browse(cr, uid, partner_id).lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)

        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False
        fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
        if update_tax: #The quantity only have changed
            result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)

        if not flag:
            result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
            if product_obj.description_sale:
                result['name'] += '\n'+product_obj.description_sale
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}
        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
        # get unit price

        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                    'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        })[pricelist]
            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                result.update({'price_unit': price})
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        result.update({'chatluong_id': product_obj.chatluong_id.id,'quycach_donggoi_id': product_obj.quycach_donggoi_id.id})
        return {'value': result, 'domain': domain, 'warning': warning}
sale_order_line()  

class hop_dong(osv.osv):
    _inherit = "hop.dong"
    
    def thuchien_hd_noi(self, cr, uid, ids, context=None):
        sale_obj = self.pool.get('sale.order')
        order_line = []
        vals = {}
        for hd in self.browse(cr, uid, ids):
            vals={'partner_id':hd.partner_id.id,'hop_dong_id':hd.id,'order_policy':'picking','state':'draft'}
            vals.update(sale_obj.onchange_partner_id(cr, uid, [], hd.partner_id.id)['value'])
            vals.update(sale_obj.onchange_hop_dong_id(cr, uid, [], hd.id)['value'])
            vals.update({'pricelist_id':hd.pricelist_id.id,})
            sale_id = sale_obj.create(cr, uid, vals)
            sale_obj.action_button_confirm(cr, uid, [sale_id])
        return self.write(cr, uid, ids, {'state': 'thuc_hien'})
    
    def huy_hd_noi(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService('workflow')
        for huy in self.browse(cr,uid,ids):
            sql = '''
                select id from account_invoice where hop_dong_id = %s
            '''%(huy.id)
            cr.execute(sql)
            invoice_ids = cr.dictfetchall()
            if invoice_ids:
                for invoice in invoice_ids:
                    wf_service.trg_validate(uid, 'account.invoice', invoice['id'], 'invoice_cancel', cr)
                    self.pool.get('account.invoice').action_cancel_draft(cr,uid,[invoice['id']])
                    sql = '''
                        delete from account_invoice_line where invoice_id = %s
                    '''%(invoice['id'])
                    cr.execute(sql)
                    sql = '''
                        delete from account_invoice where id = %s
                    '''%(invoice['id'])
                    cr.execute(sql)
            sql = '''
                 select id from stock_move where hop_dong_ban_id = %s and state = 'done'
            '''%(huy.id)
            cr.execute(sql)
            move_ids = cr.dictfetchall()
            if move_ids:
                for move in move_ids:
                    sql = '''
                        delete from account_move_line where move_id in (select id from account_move where stock_move_id = %s)
                    '''%(move['id'])
                    cr.execute(sql)
                    sql = '''
                        delete from account_move where stock_move_id = %s
                    '''%(move['id'])
                    cr.execute(sql)
                    sql = '''
                        delete from stock_picking where id in (select picking_id from stock_move where id = %s)
                    '''%(move['id'])
                    cr.execute(sql)
                    sql = '''
                        delete from stock_move where id = %s
                    '''%(move['id'])
                    cr.execute(sql)
            sql = '''
                 select id,picking_id from stock_move where hop_dong_ban_id = %s and state != 'done'
            '''%(huy.id)
            cr.execute(sql)
            move_state_ids = cr.dictfetchall()
            if move_state_ids:
                for move_state in move_state_ids:
                    wf_service.trg_validate(uid, 'stock.picking', move_state['picking_id'], 'button_cancel', cr)
                    sql = '''
                        delete from stock_picking where id in (select picking_id from stock_move where id = %s)
                    '''%(move_state['id'])
                    cr.execute(sql)
                    sql = '''
                        delete from stock_move where id = %s
                    '''%(move_state['id']) 
                    cr.execute(sql)
                    
            sql = '''
                 select id from sale_order where hop_dong_id = %s and state in ('manual', 'process')
            '''%(huy.id)
            cr.execute(sql)
            sale_ids = cr.dictfetchall()   
            if sale_ids:
                for sale in sale_ids:
                    self.pool.get('sale.order').action_cancel(cr,uid,[sale['id']]) 
                    sql = '''
                        delete from sale_order_line where order_id in (select id from sale_order where id = %s)
                    '''%(sale['id'])
                    cr.execute(sql)
                    sql = '''
                        delete from sale_order where id = %s
                    '''%(sale['id']) 
                    
            sql = '''
                 select id from sale_order where hop_dong_id = %s and state not in ('manual', 'process')
            '''%(huy.id)
            cr.execute(sql)
            sale_2_ids = cr.dictfetchall()   
            if sale_2_ids:
                for sale_2 in sale_2_ids:
                    sql = '''
                        delete from sale_order_line where order_id in (select id from sale_order where id = %s)
                    '''%(sale_2['id'])
                    cr.execute(sql)
                    sql = '''
                        delete from sale_order where id = %s
                    '''%(sale_2['id']) 
                    cr.execute(sql)
        return self.write(cr, uid, ids, {'state': 'huy_bo'})

    def huy_hd_ngoai(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService('workflow')
        for huy in self.browse(cr,uid,ids):
            sql = '''
                select id from account_invoice where hop_dong_id = %s
            '''%(huy.id)
            cr.execute(sql)
            invoice_ids = cr.dictfetchall()
            if invoice_ids:
                for invoice in invoice_ids:
                    wf_service.trg_validate(uid, 'account.invoice', invoice['id'], 'invoice_cancel', cr)
                    self.pool.get('account.invoice').action_cancel_draft(cr,uid,[invoice['id']])
                    sql = '''
                        delete from account_invoice_line where invoice_id = %s
                    '''%(invoice['id'])
                    cr.execute(sql)
                    sql = '''
                        delete from account_invoice where id = %s
                    '''%(invoice['id'])
                    cr.execute(sql)
            sql = '''
                 select id from stock_move where hop_dong_ban_id = %s and state = 'done'
            '''%(huy.id)
            cr.execute(sql)
            move_ids = cr.dictfetchall()
            if move_ids:
                for move in move_ids:
                    sql = '''
                        delete from account_move_line where move_id in (select id from account_move where stock_move_id = %s)
                    '''%(move['id'])
                    cr.execute(sql)
                    sql = '''
                        delete from account_move where stock_move_id = %s
                    '''%(move['id'])
                    cr.execute(sql)
                    sql = '''
                        delete from stock_picking where id in (select picking_id from stock_move where id = %s)
                    '''%(move['id'])
                    cr.execute(sql)
                    sql = '''
                        delete from stock_move where id = %s
                    '''%(move['id'])
                    cr.execute(sql)
            sql = '''
                 select id,picking_id from stock_move where hop_dong_ban_id = %s and state != 'done'
            '''%(huy.id)
            cr.execute(sql)
            move_state_ids = cr.dictfetchall()
            if move_state_ids:
                for move_state in move_state_ids:
                    wf_service.trg_validate(uid, 'stock.picking', move_state['picking_id'], 'button_cancel', cr)
                    sql = '''
                        delete from stock_picking where id in (select picking_id from stock_move where id = %s)
                    '''%(move_state['id'])
                    cr.execute(sql)
                    sql = '''
                        delete from stock_move where id = %s
                    '''%(move_state['id']) 
                    cr.execute(sql)
                    
            sql = '''
                 select id from sale_order where hop_dong_id = %s and state in ('manual', 'process')
            '''%(huy.id)
            cr.execute(sql)
            sale_ids = cr.dictfetchall()   
            if sale_ids:
                for sale in sale_ids:
                    self.pool.get('sale.order').action_cancel(cr,uid,[sale['id']]) 
                    sql = '''
                        delete from sale_order_line where order_id in (select id from sale_order where id = %s)
                    '''%(sale['id'])
                    cr.execute(sql)
                    sql = '''
                        delete from sale_order where id = %s
                    '''%(sale['id']) 
                    
            sql = '''
                 select id from sale_order where hop_dong_id = %s and state not in ('manual', 'process')
            '''%(huy.id)
            cr.execute(sql)
            sale_2_ids = cr.dictfetchall()   
            if sale_2_ids:
                for sale_2 in sale_2_ids:
                    sql = '''
                        delete from sale_order_line where order_id in (select id from sale_order where id = %s)
                    '''%(sale_2['id'])
                    cr.execute(sql)
                    sql = '''
                        delete from sale_order where id = %s
                    '''%(sale_2['id']) 
                    cr.execute(sql)
        return self.write(cr, uid, ids, {'state': 'huy_bo'})
        
    def thuchien_hd_ngoai(self, cr, uid, ids, context=None):
        sale_obj = self.pool.get('sale.order')
        order_line = []
        vals = {}
        for hd in self.browse(cr, uid, ids):
            vals={'partner_id':hd.partner_id.id,'hop_dong_id':hd.id,'order_policy':'picking','state':'draft'}
            vals.update(sale_obj.onchange_partner_id(cr, uid, [], hd.partner_id.id)['value'])
            vals.update(sale_obj.onchange_hop_dong_id(cr, uid, [], hd.id)['value'])
            vals.update({'pricelist_id':hd.pricelist_id.id,})
            sale_id = sale_obj.create(cr, uid, vals)
            sale_obj.action_button_confirm(cr, uid, [sale_id])
        return self.write(cr, uid, ids, {'state': 'thuc_hien'})
    
hop_dong()

class phuluc_hop_dong(osv.osv):
    _inherit = "phuluc.hop.dong"
    
    def duyet_phuluc_hd_noi(self, cr, uid, ids, context=None):
        hd_line_obj = self.pool.get('hopdong.line')
        sale_obj = self.pool.get('sale.order')
        stock_move_obj = self.pool.get('stock.move')
        account_move_obj = self.pool.get('account.move')
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoice_obj = self.pool.get('account.invoice')
        sale_line_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product.product')
        for plhd in self.browse(cr, uid, ids):
            order_line = []
            for plhp_line in plhd.phuluc_hopdong_line:
                hd_line_ids = hd_line_obj.search(cr, uid, [('hopdong_id','=',plhp_line.phuluc_hopdong_id.hop_dong_id.id),('product_id','=',plhp_line.product_id.id)])
                #sua san pham da co trong hop dong
                if hd_line_ids:
                    for hd_line in hd_line_obj.browse(cr, uid, hd_line_ids):
                        # thay doi don gia
                        if plhp_line.price_unit!=hd_line.price_unit:
                            sale_line_ids = sale_line_obj.search(cr, uid, [('hd_line_id','=',hd_line.id)])
                            sale_line_obj.write(cr, uid, sale_line_ids, {'price_unit': plhp_line.price_unit})
                            stock_move_ids = stock_move_obj.search(cr, uid, [('sale_line_id','in',sale_line_ids)])
                            cr.execute('''
                                select invoice_id from account_invoice_line where stock_move_id in %s and invoice_id in (select id from account_invoice where hop_dong_id=%s)
                            ''',(tuple(stock_move_ids),hd_line.hopdong_id.id,))
                            invoices = cr.fetchall()
                            for invoice in invoices:
                                if invoice and invoice_obj  .browse(cr, uid, invoice[0]).state not in ['draft','cancel']:
                                    raise osv.except_osv(_('Cảnh báo!'),_("Vui lòng hủy hóa đơn để chỉnh sửa!")) 
                            invoice_line_ids = invoice_line_obj.search(cr, uid, [('stock_move_id','in',stock_move_ids)])
                            invoice_line_obj.write(cr, uid, invoice_line_ids, {'price_unit': plhp_line.price_unit})
                            
                        # thay doi so luong tang
                        if plhp_line.product_qty>hd_line.product_qty:
                            val_line={
                                'product_id': plhp_line.product_id and plhp_line.product_id.id or False,
                                'name':plhp_line.name,
                                'chatluong_id':plhp_line.product_id and plhp_line.product_id.chatluong_id and plhp_line.product_id.chatluong_id.id or False,
                                'quycach_donggoi_id':plhp_line.product_id and plhp_line.product_id.quycach_donggoi_id and plhp_line.product_id.quycach_donggoi_id.id or False,
                                'product_uom': plhp_line.product_uom and plhp_line.product_uom.id or False,
                                'product_uom_qty': plhp_line.product_qty-hd_line.product_qty,
                                'price_unit': plhp_line.price_unit,
                                'tax_id': [(6,0,[t.id for t in plhp_line.tax_id])],
                                'plhd_line_id': plhp_line.id,
                                'state': 'draft',
                                'type': 'make_to_stock',
                            }
                            order_line.append((0,0,val_line))
                            
                        # thay doi so luong giam
                        if plhp_line.product_qty<hd_line.product_qty:
                            sale_line_ids = sale_line_obj.search(cr, uid, [('hd_line_id','=',hd_line.id)])
                            sale_line_obj.write(cr, uid, sale_line_ids, {'product_uom_qty': plhp_line.product_qty})
                            stock_move_ids = stock_move_obj.search(cr, uid, [('sale_line_id','in',sale_line_ids)],order='product_qty desc')
                            qty = hd_line.product_qty-plhp_line.product_qty
                            for stock_move in stock_move_obj.browse(cr, uid, stock_move_ids):
                                if qty <= 0:
                                    break
                                move_qty = stock_move.product_qty
                                if move_qty<=qty:
                                    cr.execute(''' delete from account_move_line where move_id in (select id from account_move where stock_move_id = %s ) ''',(stock_move.id,))
                                    cr.execute(''' delete from account_move where stock_move_id = %s ''',(stock_move.id,))
                                    sql = '''
                                        select invoice_id from account_invoice_line where stock_move_id = %s and invoice_id in (select id from account_invoice where hop_dong_id=%s) limit 1
                                    '''%(stock_move.id,hd_line.hopdong_id.id)
                                    cr.execute(sql)
                                    invoice = cr.fetchone()
                                    if invoice and invoice_obj.browse(cr, uid, invoice[0]).state not in ['draft','cancel']:
                                        raise osv.except_osv(_('Cảnh báo!'),_("Vui lòng hủy hóa đơn để chỉnh sửa!")) 
                                    cr.execute(''' delete from account_invoice_line where stock_move_id = %s and invoice_id in (select id from account_invoice where hop_dong_id=%s) ''',(stock_move.id,hd_line.hopdong_id.id,))
                                    cr.execute(''' delete from stock_move where id = %s ''',(stock_move.id,))
                                else:
                                    move_in_ids = stock_move_obj.search(cr, uid, [('picking_id','=',stock_move.picking_in_id.id),('product_id','=',stock_move.product_id.id)])
                                    if move_in_ids:
                                        move_in = stock_move_obj.browse(cr, uid, move_in_ids[0])
                                        product_obj.write(cr, uid, [stock_move.product_id.id], {'standard_price':move_in.purchase_line_id.price_unit})
                                    stock_move_obj.write(cr, uid, [stock_move.id], {'product_qty': stock_move.product_qty-qty})
                                    cr.execute(''' delete from account_move where stock_move_id = %s ''',(stock_move.id,))
                                    stock_move_obj._create_product_valuation_moves(cr, uid, stock_move)
                                    sql = '''
                                        select invoice_id from account_invoice_line where stock_move_id = %s and invoice_id in (select id from account_invoice where hop_dong_id=%s) limit 1
                                    '''%(stock_move.id,hd_line.hopdong_id.id)
                                    cr.execute(sql)
                                    invoice = cr.fetchone()
                                    if invoice and invoice_obj.browse(cr, uid, invoice[0]).state not in ['draft','cancel']:
                                        raise osv.except_osv(_('Cảnh báo!'),_("Vui lòng hủy hóa đơn để chỉnh sửa!")) 
                                    invoice_line_ids = invoice_line_obj.search(cr, uid, [('stock_move_id','=',stock_move.id)])
                                    invoice_line_obj.write(cr, uid, invoice_line_ids, {'quantity': stock_move.product_qty-qty})
                                qty -= move_qty
                #them moi san pham chua co trong hop dong        
                else:
                    val_line={
                        'product_id': plhp_line.product_id and plhp_line.product_id.id or False,
                        'name':plhp_line.name,
                        'chatluong_id':plhp_line.product_id and plhp_line.product_id.chatluong_id and plhp_line.product_id.chatluong_id.id or False,
                        'quycach_donggoi_id':plhp_line.product_id and plhp_line.product_id.quycach_donggoi_id and plhp_line.product_id.quycach_donggoi_id.id or False,
                        'product_uom': plhp_line.product_uom and plhp_line.product_uom.id or False,
                        'product_uom_qty': plhp_line.product_qty,
                        'price_unit': plhp_line.price_unit,
                        'tax_id': [(6,0,[t.id for t in plhp_line.tax_id])],
                        'plhd_line_id': plhp_line.id,
                        'state': 'draft',
                        'type': 'make_to_stock',
                    }
                    order_line.append((0,0,val_line))
            if order_line:
                create_sale_vals={'partner_id':plhd.hop_dong_id.partner_id.id,
                                  'hop_dong_id':plhd.hop_dong_id.id,
                                  'plhd_id': plhd.id,
                                  'order_policy':'picking',
                                  'state':'draft'}
                create_sale_vals.update(sale_obj.onchange_partner_id(cr, uid, [], plhd.hop_dong_id.partner_id.id)['value'])
                create_sale_vals.update({'pricelist_id':plhd.hop_dong_id.pricelist_id.id,
                                         'order_line': order_line})
                sale_id = sale_obj.create(cr, uid, create_sale_vals)
                sale_obj.action_button_confirm(cr, uid, [sale_id])
        return self.write(cr, uid, ids, {'state': 'da_duyet'})
    
    def duyet_phuluc_hd_ngoai(self, cr, uid, ids, context=None):
        hd_line_obj = self.pool.get('hopdong.line')
        sale_obj = self.pool.get('sale.order')
        stock_move_obj = self.pool.get('stock.move')
        account_move_obj = self.pool.get('account.move')
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoice_obj = self.pool.get('account.invoice')
        sale_line_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product.product')
        for plhd in self.browse(cr, uid, ids):
            order_line = []
            for plhp_line in plhd.phuluc_hopdong_line:
                hd_line_ids = hd_line_obj.search(cr, uid, [('hopdong_id','=',plhp_line.phuluc_hopdong_id.hop_dong_id.id),('product_id','=',plhp_line.product_id.id)])
                #sua san pham da co trong hop dong
                if hd_line_ids:
                    for hd_line in hd_line_obj.browse(cr, uid, hd_line_ids):
                        # thay doi don gia
                        if plhp_line.price_unit!=hd_line.price_unit:
                            sale_line_ids = sale_line_obj.search(cr, uid, [('hd_line_id','=',hd_line.id)])
                            sale_line_obj.write(cr, uid, sale_line_ids, {'price_unit': plhp_line.price_unit})
                            stock_move_ids = stock_move_obj.search(cr, uid, [('sale_line_id','in',sale_line_ids)])
                            cr.execute('''
                                select invoice_id from account_invoice_line where stock_move_id in %s and invoice_id in (select id from account_invoice where hop_dong_id=%s)
                            ''',(tuple(stock_move_ids),hd_line.hopdong_id.id,))
                            invoices = cr.fetchall()
                            for invoice in invoices:
                                if invoice and invoice_obj  .browse(cr, uid, invoice[0]).state not in ['draft','cancel']:
                                    raise osv.except_osv(_('Cảnh báo!'),_("Vui lòng hủy hóa đơn để chỉnh sửa!")) 
                            invoice_line_ids = invoice_line_obj.search(cr, uid, [('stock_move_id','in',stock_move_ids)])
                            invoice_line_obj.write(cr, uid, invoice_line_ids, {'price_unit': plhp_line.price_unit})
                            
                        # thay doi so luong tang
                        if plhp_line.product_qty>hd_line.product_qty:
                            val_line={
                                'product_id': plhp_line.product_id and plhp_line.product_id.id or False,
                                'name':plhp_line.name,
                                'chatluong_id':plhp_line.product_id and plhp_line.product_id.chatluong_id and plhp_line.product_id.chatluong_id.id or False,
                                'quycach_donggoi_id':plhp_line.product_id and plhp_line.product_id.quycach_donggoi_id and plhp_line.product_id.quycach_donggoi_id.id or False,
                                'product_uom': plhp_line.product_uom and plhp_line.product_uom.id or False,
                                'product_uom_qty': plhp_line.product_qty-hd_line.product_qty,
                                'price_unit': plhp_line.price_unit,
                                'tax_id': [(6,0,[t.id for t in plhp_line.tax_id])],
                                'plhd_line_id': plhp_line.id,
                                'state': 'draft',
                                'type': 'make_to_stock',
                            }
                            order_line.append((0,0,val_line))
                            
                        # thay doi so luong giam
                        if plhp_line.product_qty<hd_line.product_qty:
                            sale_line_ids = sale_line_obj.search(cr, uid, [('hd_line_id','=',hd_line.id)])
                            sale_line_obj.write(cr, uid, sale_line_ids, {'product_uom_qty': plhp_line.product_qty})
                            stock_move_ids = stock_move_obj.search(cr, uid, [('sale_line_id','in',sale_line_ids)],order='product_qty desc')
                            qty = hd_line.product_qty-plhp_line.product_qty
                            for stock_move in stock_move_obj.browse(cr, uid, stock_move_ids):
                                if qty <= 0:
                                    break
                                move_qty = stock_move.product_qty
                                if move_qty<=qty:
                                    cr.execute(''' delete from account_move_line where move_id in (select id from account_move where stock_move_id = %s ) ''',(stock_move.id,))
                                    cr.execute(''' delete from account_move where stock_move_id = %s ''',(stock_move.id,))
                                    sql = '''
                                        select invoice_id from account_invoice_line where stock_move_id = %s and invoice_id in (select id from account_invoice where hop_dong_id=%s) limit 1
                                    '''%(stock_move.id,hd_line.hopdong_id.id)
                                    cr.execute(sql)
                                    invoice = cr.fetchone()
                                    if invoice and invoice_obj.browse(cr, uid, invoice[0]).state not in ['draft','cancel']:
                                        raise osv.except_osv(_('Cảnh báo!'),_("Vui lòng hủy hóa đơn để chỉnh sửa!")) 
                                    cr.execute(''' delete from account_invoice_line where stock_move_id = %s and invoice_id in (select id from account_invoice where hop_dong_id=%s) ''',(stock_move.id,hd_line.hopdong_id.id,))
                                    cr.execute(''' delete from stock_move where id = %s ''',(stock_move.id,))
                                else:
                                    move_in_ids = stock_move_obj.search(cr, uid, [('picking_id','=',stock_move.picking_in_id.id),('product_id','=',stock_move.product_id.id)])
                                    if move_in_ids:
                                        move_in = stock_move_obj.browse(cr, uid, move_in_ids[0])
                                        product_obj.write(cr, uid, [stock_move.product_id.id], {'standard_price':move_in.purchase_line_id.price_unit})
                                    stock_move_obj.write(cr, uid, [stock_move.id], {'product_qty': stock_move.product_qty-qty})
                                    cr.execute(''' delete from account_move where stock_move_id = %s ''',(stock_move.id,))
                                    stock_move_obj._create_product_valuation_moves(cr, uid, stock_move)
                                    sql = '''
                                        select invoice_id from account_invoice_line where stock_move_id = %s and invoice_id in (select id from account_invoice where hop_dong_id=%s) limit 1
                                    '''%(stock_move.id,hd_line.hopdong_id.id)
                                    cr.execute(sql)
                                    invoice = cr.fetchone()
                                    if invoice and invoice_obj.browse(cr, uid, invoice[0]).state not in ['draft','cancel']:
                                        raise osv.except_osv(_('Cảnh báo!'),_("Vui lòng hủy hóa đơn để chỉnh sửa!")) 
                                    invoice_line_ids = invoice_line_obj.search(cr, uid, [('stock_move_id','=',stock_move.id)])
                                    invoice_line_obj.write(cr, uid, invoice_line_ids, {'quantity': stock_move.product_qty-qty})
                                qty -= move_qty
                #them moi san pham chua co trong hop dong        
                else:
                    val_line={
                        'product_id': plhp_line.product_id and plhp_line.product_id.id or False,
                        'name':plhp_line.name,
                        'chatluong_id':plhp_line.product_id and plhp_line.product_id.chatluong_id and plhp_line.product_id.chatluong_id.id or False,
                        'quycach_donggoi_id':plhp_line.product_id and plhp_line.product_id.quycach_donggoi_id and plhp_line.product_id.quycach_donggoi_id.id or False,
                        'product_uom': plhp_line.product_uom and plhp_line.product_uom.id or False,
                        'product_uom_qty': plhp_line.product_qty,
                        'price_unit': plhp_line.price_unit,
                        'tax_id': [(6,0,[t.id for t in plhp_line.tax_id])],
                        'plhd_line_id': plhp_line.id,
                        'state': 'draft',
                        'type': 'make_to_stock',
                    }
                    order_line.append((0,0,val_line))
            if order_line:
                create_sale_vals={'partner_id':plhd.hop_dong_id.partner_id.id,
                                  'hop_dong_id':plhd.hop_dong_id.id,
                                  'plhd_id': plhd.id,
                                  'order_policy':'picking',
                                  'state':'draft'}
                create_sale_vals.update(sale_obj.onchange_partner_id(cr, uid, [], plhd.hop_dong_id.partner_id.id)['value'])
                create_sale_vals.update({'pricelist_id':plhd.hop_dong_id.pricelist_id.id,
                                         'order_line': order_line})
                sale_id = sale_obj.create(cr, uid, create_sale_vals)
                sale_obj.action_button_confirm(cr, uid, [sale_id])
        return self.write(cr, uid, ids, {'state': 'da_duyet'})
    
phuluc_hop_dong()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
