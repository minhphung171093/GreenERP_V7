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

class stock_journal(osv.osv):
    _inherit = "stock.journal"
    _columns = {
        'name': fields.char('Stock Journal', size=32, required=True),
        'user_id': fields.many2one('res.users', 'Responsible'),
        'source_type': fields.selection([
                                        ('in', 'Getting Goods'), 
                                        ('out', 'Sending Goods'),
                                        ('return_customer', 'Return from customer'), 
                                        ('return_supplier', 'Return to supplier'), 
                                        ('internal', 'Internal'),
                                        ('production', 'Production'),
                                        ('phys_adj', 'Physical Adjustment'),], 'Source Type', size=16, required=True),
        'sequence_id': fields.many2one('ir.sequence', 'Sequence'),
        
        'from_location_id':fields.many2many('stock.location','stock_journal_from_location_ref', 
                                                 'journal_id','location_id','From Location',required = True), 
        'to_location_id':fields.many2many('stock.location','stock_journal_to_location_ref', 
                                                 'journal_id','location_id','From Location',required = True), 
    }
    _defaults = {
        'user_id': lambda s, c, u, ctx: u
    }
    
stock_journal()

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    def onchange_picking_location_dest_id(self, cr, uid, ids,picking_location_dest_id=False, context=None):
        if picking_location_dest_id:
            for picking_id in self.pool.get('stock.picking').browse(cr, uid, ids):
                for stock_move_id in picking_id.move_lines:
                    self.pool.get('stock.move').write(cr,uid,stock_move_id.id,{'location_dest_id':picking_location_dest_id})
        return True
    
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, partner_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        wf_service = netsvc.LocalService("workflow")
        date_done = partial_datas.get('delivery_date',False)
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty, prodlot_ids, product_avail, partial_qty, uos_qty,location_id,location_dest_id, product_uoms = {}, {},{}, {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s'%(move.id), {})
                product_qty = partial_data.get('product_qty',0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom', move.product_uom.id)
                product_price = partial_data.get('product_price',0.0)
                product_currency = partial_data.get('product_currency',False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
                uos_qty[move.id] = move.product_id._compute_uos_qty(product_uom, product_qty, move.product_uos) if product_qty else 0.0
                location_id[move.id] = partial_data.get('location_id',False)
                location_dest_id[move.id] = partial_data.get('location_dest_id',False)
                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)

                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    # Record the values that were chosen in the wizard, so they can be
                    # used for average price computation and inventory valuation
                    move_obj.write(cr, uid, [move.id],
                            {'price_unit': product_price,
                             'price_currency_id': product_currency})

            # every line of the picking is empty, do not generate anything
            empty_picking = not any(q for q in move_product_qty.values() if q > 0)

            for move in too_few:
                product_qty = move_product_qty[move.id]
                if not new_picking and not empty_picking:
                    new_picking_name = pick.name
                    self.write(cr, uid, [pick.id], 
                               {'name': sequence_obj.get(cr, uid,
                                            'stock.picking.%s'%(pick.type)),
                               })
                    pick.refresh()
                    new_picking = self.copy(cr, uid, pick.id,
                            {
                                'name': new_picking_name,
                                'move_lines' : [],
                                'state':'draft',
                            })
                if product_qty != 0:
                    defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': uos_qty[move.id],
                            'picking_id' : new_picking,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            'product_uom': product_uoms[move.id],
                            'location_id':location_id[move.id],
                            'location_dest_id':location_dest_id[move.id]
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)
                move_obj.write(cr, uid, [move.id],
                        {
                            'product_qty': move.product_qty - partial_qty[move.id],
                            'product_uos_qty': move.product_uos_qty - uos_qty[move.id],
                            'prodlot_id': False,
                            'tracking_id': False,
                        })

            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id],
                            'product_qty': move_product_qty[move.id],
                            'location_id':location_id[move.id],
                            'location_dest_id':location_dest_id[move.id],}
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id]})
                move_obj.write(cr, uid, [move.id], defaults)
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty' : product_qty,
                    'product_uos_qty': uos_qty[move.id],
                    'product_uom': product_uoms[move.id],
                    'location_id':location_id[move.id],
                    'location_dest_id':location_dest_id[move.id],
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking], context={'date_done':date_done})
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = new_picking
                self.message_post(cr, uid, new_picking, body=_("Back order <em>%s</em> has been <b>created</b>.") % (pick.name), context=context)
            elif empty_picking:
                delivered_pack_id = pick.id
            else:
                self.action_move(cr, uid, [pick.id], context={'date_done':date_done})
                self.write(cr, uid, [pick.id], {'date_done':date_done})
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id

            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}

        return res
    
    def _get_location_info(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        shop_id = False
        warehouse_id = False
        for pick in self.browse(cr, uid, ids, context=context):
            
            res[pick.id] = {
                            'shop_id': False,
                            'warehouse_id': False,
                            }
            
            if pick.location_id.usage =='internal':
                warehouse_id = pick.location_id and pick.location_id.warehouse_id.id or False
            if not warehouse_id:
                if pick.location_dest_id.usage =='internal':
                    warehouse_id = pick.location_dest_id and pick.location_dest_id.warehouse_id.id or False
                
            
            if warehouse_id:
                res[pick.id]['warehouse_id'] = warehouse_id
                sql='''
                    SELECT id FROM sale_shop WHERE warehouse_id = %s
                '''%(warehouse_id)
                cr.execute(sql)
                shop_res = cr.fetchone()
                shop_id = shop_res and shop_res[0] or False
            if shop_id:
                res[pick.id]['shop_id'] = shop_id
        return res
    
    _columns = {
        'nguoi_denghi_id':fields.many2one('res.users','Người đề nghị'),
        'donvi_vanchuyen':fields.many2one('res.partner','Đơn vị vận chuyển'),
        'lotrinh_id':fields.many2one('lo.trinh','Lộ trình'),
        'dongia_vanchuyen':fields.float('Đơn giá vận chuyển'),
        'picking_location_dest_id': fields.many2one('stock.location', 'Destination Location',states={'done': [('readonly', True)]}, select=True,),
        'cang_donghang_id': fields.many2one('cang.donghang', 'Cảng đóng hàng',states={'done': [('readonly', True)]}, select=True,),
        'shop_id': fields.function(_get_location_info, type='many2one', relation='sale.shop', string='Shop',
            store={
                'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['location_id','location_dest_id'], 10),
            }, readonly=True, multi='lo_info'),
        'warehouse_id': fields.function(_get_location_info, type='many2one', relation='stock.warehouse', string='Warehouse',
            store={
                'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['location_id','location_dest_id'], 10),
            }, readonly=True, multi='lo_info'),
                
        'stock_journal_id': fields.many2one('stock.journal','Stock Journal', required=True, select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
         'return': fields.selection([('none', 'Normal'), ('customer', 'Return from Customer'),('internal','Return Internal'), ('supplier', 'Return to Supplier')], 'Type', required=True, select=True, help="Type specifies whether the Picking has been returned or not."),
    }
    
    def _get_journal(self, cr, uid, context=None):
        journal_domain = []
        if context.get('default_type',False) and context.get('default_return',False):
            default_type = context['default_type']
            default_return = context['default_return']
            if default_type == 'in':
                journal_domain = [('source_type', '=', 'in')]
                if default_return == 'customer':
                    journal_domain = [('source_type', '=', 'return_customer')]
            if default_type == 'out':
                journal_domain = [('source_type', '=', 'out')]
                if default_return == 'supplier':
                    journal_domain = [('source_type', '=', 'return_supplier')]
        else:
            journal_domain = [('source_type', '=', 'internal')]
        journal_ids = self.pool.get('stock.journal').search(cr, uid, journal_domain)
        return journal_ids and journal_ids[0] or False
    
    _defaults = {    
        'return': 'none',
        'type':   'internal',
        'stock_journal_id': _get_journal,
    }
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        journal_obj = self.pool.get('stock.journal')
        if context is None:
            context = {}
        res = super(stock_picking,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        
        if view_type == 'form':
            journal_ids = []
            if context.get('default_type',False):
                journal_domain = []
                if context.get('default_return',False):
                    default_type = context['default_type']
                    default_return = context['default_return']
                    if default_type == 'in':
                        journal_domain = [('source_type', '=', 'in')]
                        if default_return == 'customer':
                            journal_domain = [('source_type', '=', 'return_customer')]
                    if default_type == 'out':
                        journal_domain = [('source_type', '=', 'out')]
                        if default_return == 'supplier':
                            journal_domain = [('source_type', '=', 'return_supplier')]
                
                if context['default_type'] == 'internal':
                    journal_domain = [('source_type', '=', 'internal')]
                if context.get('search_source_type',False) and context['search_source_type'] == 'production':
                    journal_domain = [('source_type', '=', 'production')]
                if context.get('search_source_type',False) and context['search_source_type'] == 'phys_adj':
                    journal_domain = [('source_type', '=', 'phys_adj')]
                    
                journal_ids = journal_obj._name_search(cr, uid, '', journal_domain, context=context, limit=None, name_get_uid=1)
            if journal_ids != []:
                for field in res['fields']:
                    if field == 'stock_journal_id':
                        res['fields'][field]['selection'] = journal_ids
        return res
    
    def create(self, cr, user, vals, context=None):
        context = context or {}
        context.update({'sequence_obj_ids':[]})
        if ('name' not in vals) or (vals.get('name')=='/'):
            if vals.get('stock_journal_id',False):
                journal = self.pool.get('stock.journal').browse(cr, user, vals['stock_journal_id'])
                if not journal.sequence_id:
                    raise osv.except_osv(_('Warning!'), _('Please define Sequence for Stock Journal.'))
                vals['name'] = self.pool.get('ir.sequence').get_id(cr, user, journal.sequence_id.id, code_or_id='id', context=context)
                
        new_id = super(osv.osv, self).create(cr, user, vals, context)
        return new_id
    
    
    def action_invoice_create(self, cr, uid, ids, journal_id=False,group=False, type='out_invoice', context=None):
        """ Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        if context is None:
            context = {}

        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        partner_obj = self.pool.get('res.partner')
        invoices_group = {}
        res = {}
        inv_type = type
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.invoice_state != '2binvoiced':
                continue
            partner = self._get_partner_to_invoice(cr, uid, picking, context=context)
            if isinstance(partner, int):
                partner = partner_obj.browse(cr, uid, [partner], context=context)[0]
            if not partner:
                raise osv.except_osv(_('Error, no partner!'),
                    _('Please put a partner on the picking list if you want to generate invoice.'))

            if not inv_type:
                inv_type = self._get_invoice_type(picking)

            if group and partner.id in invoices_group:
                invoice_id = invoices_group[partner.id]
                invoice = invoice_obj.browse(cr, uid, invoice_id)
                invoice_vals_group = self._prepare_invoice_group(cr, uid, picking, partner, invoice, context=context)
                invoice_obj.write(cr, uid, [invoice_id], invoice_vals_group, context=context)
            else:
                invoice_vals = self._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context=context)
                invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)
                invoices_group[partner.id] = invoice_id
            res[picking.id] = invoice_id
            for move_line in picking.move_lines:
                if move_line.state == 'cancel':
                    continue
                if move_line.scrapped:
                    # do no invoice scrapped products
                    continue
                vals = self._prepare_invoice_line(cr, uid, group, picking, move_line,
                                invoice_id, invoice_vals, context=context)
                if vals:
                    invoice_line_id = invoice_line_obj.create(cr, uid, vals, context=context)
                    self._invoice_line_hook(cr, uid, move_line, invoice_line_id)
                    
            invoice_obj.button_compute(cr, uid, [invoice_id], context=context,
                    set_total=(inv_type in ('in_invoice', 'in_refund')))
            
            
        for picking in self.browse(cr, uid, res.keys(), context=context):
            invoiced=True
            for line in picking.move_lines:
                return_qty = self.pool.get('stock.invoice.onshipping').get_returned_qty(cr,uid,line)
                invoicing_qty = line.product_qty - return_qty 
                if invoicing_qty != line.invoiced_qty:
                    invoiced = False
                    break
            if invoiced:
                self.write(cr, uid, [picking.id], {
                'invoice_state': 'invoiced',
                }, context=context)    
            
        return res
    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id,
        invoice_vals, context=None):
        """ Builds the dict containing the values for the invoice line
            @param group: True or False
            @param picking: picking object
            @param: move_line: move_line object
            @param: invoice_id: ID of the related invoice
            @param: invoice_vals: dict used to created the invoice
            @return: dict that will be used to create the invoice line
        """
        if group:
            name = (picking.name or '') + '-' + move_line.name
        else:
            name = move_line.name
        origin = move_line.picking_id.name or ''
        if move_line.picking_id.origin:
            origin += ':' + move_line.picking_id.origin

        if invoice_vals['type'] in ('out_invoice', 'out_refund'):
            account_id = move_line.product_id.property_account_income.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_income_categ.id
            if invoice_vals['type'] == 'out_refund':
                account_id = move_line.product_id.account_deducted_id.id
                if not account_id:
                    account_id = move_line.product_id.categ_id.account_deducted_id.id
        else:
            account_id = move_line.product_id.property_account_expense.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_expense_categ.id
        if invoice_vals['fiscal_position']:
            fp_obj = self.pool.get('account.fiscal.position')
            fiscal_position = fp_obj.browse(cr, uid, invoice_vals['fiscal_position'], context=context)
            account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)
        # set UoS if it's a sale and the picking doesn't have one
        uos_id = move_line.product_uos and move_line.product_uos.id or False
        if not uos_id and invoice_vals['type'] in ('out_invoice', 'out_refund'):
            uos_id = move_line.product_uom.id
            
        quantity =  move_line.product_uos_qty or move_line.product_qty
        if context.get('invoicing_list',False):
            quantity = 0
            for line in context['invoicing_list']:
                if move_line.id == line.move_id.id and line.check_invoice:
                    quantity = line.quantity
                    self.pool.get('stock.move').write(cr,uid,move_line.id,{'invoiced_qty':move_line.invoiced_qty + quantity})
                    break
        if quantity:
            return {
                'name': name,
                'origin': origin,
                'invoice_id': invoice_id,
                'uos_id': uos_id,
                'product_id': move_line.product_id.id,
                'account_id': account_id,
                'price_unit': self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type']),
                'discount': self._get_discount_invoice(cr, uid, move_line),
                'quantity': quantity,
                'invoice_line_tax_id': [(6, 0, self._get_taxes_invoice(cr, uid, move_line, invoice_vals['type']))],
                'account_analytic_id': self._get_account_analytic_invoice(cr, uid, picking, move_line),
                'source_obj':'stock.move',
                'source_id':move_line.id,
                #Hung moi them so lo vao invoice line
                'prodlot_id':move_line.prodlot_id.id,
                'stock_move_id': move_line.id,
            }

        else:
            return {}
        
    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        """ Builds the dict containing the values for the invoice
            @param picking: picking object
            @param partner: object of the partner to invoice
            @param inv_type: type of the invoice ('out_invoice', 'in_invoice', ...)
            @param journal_id: ID of the accounting journal
            @return: dict that will be used to create the invoice object
        """
        if isinstance(partner, int):
            partner = self.pool.get('res.partner').browse(cr, uid, partner, context=context)
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = partner.property_account_receivable.id
            payment_term = partner.property_payment_term.id or False
        else:
            account_id = partner.property_account_payable.id
            payment_term = partner.property_supplier_payment_term.id or False
        comment = self._get_comment_invoice(cr, uid, picking)
        if picking.type=='in':
            hop_dong_id = picking.purchase_id and picking.purchase_id.hop_dong_id.id or False
        if picking.type=='out':
            hop_dong_id = picking.sale_id and picking.sale_id.hop_dong_id.id or False
        #Hung them shop
        warehouse_id = picking.location_id.warehouse_id and picking.location_id.warehouse_id.id or False
        if not warehouse_id:
            warehouse_id = picking.location_dest_id.warehouse_id.id or False
        shop_ids = self.pool.get('sale.shop').search(cr, uid, [('warehouse_id','=',warehouse_id)])
        invoice_vals = {
            'name': picking.name,
            'origin': (picking.name or '') + (picking.origin and (':' + picking.origin) or ''),
            'type': inv_type,
            'account_id': account_id,
            'partner_id': partner.id,
            'comment': comment,
            'payment_term': payment_term,
            'fiscal_position': partner.property_account_position.id,
            'date_invoice': context.get('date_inv', False),
            'company_id': picking.company_id.id,
            'user_id': uid,
            'hop_dong_id': hop_dong_id,
            'shop_id': shop_ids and shop_ids[0] or False,
        }
        cur_id = self.get_currency_id(cr, uid, picking)
        if cur_id:
            invoice_vals['currency_id'] = cur_id
        if journal_id:
            invoice_vals['journal_id'] = journal_id
        return invoice_vals
    
    def has_valuation_moves(self, cr, uid, move):
        return self.pool.get('account.move').search(cr, uid, [
            ('stock_move_id', '=', move.id),
            ])
    
    def action_revert_done(self, cr, uid, ids, context=None):
        move_ids = []
        invoice_ids = []
        if not len(ids):
            return False
        
        sql ='''
            Select id 
            FROM
                stock_move where picking_id = %s
        '''%(ids[0])
        cr.execute(sql)
        for line in cr.dictfetchall():
            move_ids.append(line['id'])
        if move_ids:
            sql='''
                SELECT state ,id
                FROM account_invoice 
                WHERE id IN (
                     SELECT distinct invoice_id 
                     FROM account_invoice_line 
                     WHERE stock_move_id in(%s))
            '''%(','.join(map(str,move_ids)))
            cr.execute(sql)
            for line in cr.dictfetchall():
                if line['state'] not in ('draft','cancel'):
                    raise osv.except_osv(
                        _('Cảnh báo'),
                        _('You must first cancel all Invoice order(s) attached to this sales order.'))
                else:
                    invoice_ids.append(line['id'])
            if invoice_ids:
                cr.execute('delete from account_invoice where id in %s',(tuple(invoice_ids),))
#                 self.pool.get('account.invoice').unlink(cr,uid,invoice_ids)
                
        for picking in self.browse(cr, uid, ids, context):
            for line in picking.move_lines:
                if self.has_valuation_moves(cr, uid, line):
                    raise osv.except_osv(
                        _('Cảnh báo'),
                        _('Sản phẩm "%s" đã sinh bút toán "%s". \
                            Vui lòng xóa bút toán trước') % (line.name,
                                                   line.picking_id.name))
                line.write({'state': 'draft','invoiced_qty':0})
            self.write(cr, uid, [picking.id], {'state': 'draft'})
            if picking.invoice_state == 'invoiced':# and not picking.invoice_id:
                self.write(cr, uid, [picking.id],
                           {'invoice_state': '2binvoiced'})
            wf_service = netsvc.LocalService("workflow")
            # Deleting the existing instance of workflow
            wf_service.trg_delete(uid, 'stock.picking', picking.id, cr)
            wf_service.trg_create(uid, 'stock.picking', picking.id, cr)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _(
                "The stock picking '%s' has been set in draft state."
                ) % (name,)
            self.log(cr, uid, id, message)
        return True
    
    def onchange_journal(self, cr, uid, ids, stock_journal_id):
        value ={}
        domain = {}
        if not stock_journal_id:
            value.update({'location_id':False,
                           'location_dest_id':False})
            domain.update({'location_id':[('id','=',False)],
                           'location_dest_id':[('id','=',False)]})
        else:
            journal = self.pool.get('stock.journal').browse(cr, uid, stock_journal_id)
            from_location_ids = [x.id for x in journal.from_location_id]
            to_location_ids = [x.id for x in journal.to_location_id]
            domain.update({'location_id':[('id','=',from_location_ids)],
                           'location_dest_id':[('id','=',to_location_ids)]})
            location_id = from_location_ids and from_location_ids[0] or False
            location_dest_id = False
            if to_location_ids and to_location_ids[0] != location_id:
                location_dest_id = to_location_ids[0]
            value.update({'location_id':location_id,
                          'location_dest_id': location_dest_id})
        return {'value': value,'domain':domain}
    
    def onchange_location(self,cr,uid,ids,location_id,location_dest_id,move_lines):
        if location_id and location_dest_id and location_id == location_dest_id:
            value ={}
            value.update({'location_dest_id':False})
            warning = {
            'title': _('Location Warning!'),
            'message' : _('Location = Location Dest')
            }
            return {'value': value, 'warning': warning} 
        if location_id:
            i = 0
            for line in move_lines:
                if not line[2]:
                    move_lines[i][0] = 1
                    move_lines[i][2] = {'location_id':location_id}
                else:
                    move_lines[i][2]['location_id'] = location_id
                i+= 1
        if location_dest_id:
            i = 0
            for line in move_lines:
                if not line[2]:
                    move_lines[i][0] = 1
                    move_lines[i][2] = {'location_dest_id':location_dest_id}
                else:
                    move_lines[i][2]['location_dest_id'] = location_dest_id
                i+= 1
        
        result ={
                 'move_lines': move_lines,
                 'location_id': location_id,
                 }
        
        return  {'value': result}
    
    def print_denghi_nhapkho(self, cr, uid, ids, context=None):
        hopdong = self.browse(cr, uid, ids[0])
        datas = {
             'ids': ids,
             'model': 'stock.picking',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'denghi_nhapkho_report',
            }
    def print_denghi_xuatkho(self, cr, uid, ids, context=None):
        hopdong = self.browse(cr, uid, ids[0])
        datas = {
             'ids': ids,
             'model': 'stock.picking',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'denghi_xuatkho_report',
            }

    def print_denghi_xuathang(self, cr, uid, ids, context=None):
        hopdong = self.browse(cr, uid, ids[0])
        datas = {
             'ids': ids,
             'model': 'stock.picking',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'denghi_xuathang_report',
            }
    
stock_picking()

class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    
    def _get_location_info(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        shop_id = False
        warehouse_id = False
        for pick in self.browse(cr, uid, ids, context=context):
            
            res[pick.id] = {
                            'shop_id': False,
                            'warehouse_id': False,
                            }
            
            if pick.location_id.usage =='internal':
                warehouse_id = pick.location_id and pick.location_id.warehouse_id and pick.location_id.warehouse_id.id or False
            if not warehouse_id:
                if pick.location_dest_id.usage =='internal':
                    warehouse_id = pick.location_dest_id and pick.location_dest_id.warehouse_id and pick.location_dest_id.warehouse_id.id or False
                
            
            if warehouse_id:
                res[pick.id]['warehouse_id'] = warehouse_id
                sql='''
                    SELECT id FROM sale_shop WHERE warehouse_id = %s
                '''%(warehouse_id)
                cr.execute(sql)
                shop_res = cr.fetchone()
                shop_id = shop_res and shop_res[0] or False
            if shop_id:
                res[pick.id]['shop_id'] = shop_id
        return res
    
    def onchange_picking_location_dest_id(self, cr, uid, ids,picking_location_dest_id=False, context=None):
        if picking_location_dest_id:
            for picking_id in self.pool.get('stock.picking').browse(cr, uid, ids):
                for stock_move_id in picking_id.move_lines:
                    self.pool.get('stock.move').write(cr,uid,stock_move_id.id,{'location_dest_id':picking_location_dest_id})
        return True
    
    _columns = {
        'nguoi_denghi_id':fields.many2one('res.users','Người đề nghị'),
        'donvi_vanchuyen':fields.many2one('res.partner','Đơn vị vận chuyển'),
        'lotrinh_id':fields.many2one('lo.trinh','Lộ trình'),
        'dongia_vanchuyen':fields.float('Đơn giá vận chuyển'),
        'picking_location_dest_id': fields.many2one('stock.location', 'Destination Location',states={'done': [('readonly', True)]}, select=True,),
        'shop_id': fields.function(_get_location_info, type='many2one', relation='sale.shop', string='Shop',
            store={
                'stock.picking.in': (lambda self, cr, uid, ids, c={}: ids, ['location_id','location_dest_id'], 10),
            }, readonly=True, multi='pro_info'),
        'warehouse_id': fields.function(_get_location_info, type='many2one', relation='stock.warehouse', string='Warehouse',
            store={
                'stock.picking.in': (lambda self, cr, uid, ids, c={}: ids, ['location_id','location_dest_id'], 10),
            }, readonly=True, multi='pro_info'),
        'stock_journal_id': fields.many2one('stock.journal','Stock Journal', required=True, select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'return': fields.selection([('none', 'Normal'), ('customer', 'Return from Customer'),('internal','Return Internal'), ('supplier', 'Return to Supplier')], 'Type', required=True, select=True, help="Type specifies whether the Picking has been returned or not."),
    }
    
    _defaults = {  
        'return': 'none',
        'type':   'in',  
    }
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        return self.pool.get('stock.picking').fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
    
    def has_valuation_moves(self, cr, uid, move):
        return self.pool.get('account.move').search(cr, uid, [
            ('stock_move_id', '=', move.id),
            ])
    
    def action_revert_done(self, cr, uid, ids, context=None):
        move_ids = []
        invoice_ids = []
        if not len(ids):
            return False
        
        sql ='''
            Select id 
            FROM
                stock_move where picking_id = %s
        '''%(ids[0])
        cr.execute(sql)
        for line in cr.dictfetchall():
            move_ids.append(line['id'])
        if move_ids:
            sql='''
                SELECT state ,id
                FROM account_invoice 
                WHERE id IN (
                     SELECT distinct invoice_id 
                     FROM account_invoice_line 
                     WHERE stock_move_id in(%s))
            '''%(','.join(map(str,move_ids)))
            cr.execute(sql)
            for line in cr.dictfetchall():
                if line['state'] not in ('draft','cancel'):
                    raise osv.except_osv(
                        _('Cảnh báo'),
                        _('Vui lòng hủy bỏ tất cả các hóa đơn của phiếu nhập này trước!'))
                else:
                    invoice_ids.append(line['id'])
            if invoice_ids:
                cr.execute('delete from account_invoice where id in %s',(tuple(invoice_ids),))
#                 self.pool.get('account.invoice').unlink(cr,uid,invoice_ids)
                
        for picking in self.browse(cr, uid, ids, context):
            for line in picking.move_lines:
                if self.has_valuation_moves(cr, uid, line):
                    raise osv.except_osv(
                        _('Cảnh báo'),
                        _('Sản phẩm "%s" đã sinh bút toán "%s". \
                            Vui lòng xóa bút toán trước') % (line.name,
                                                   line.picking_id.name))
                line.write({'state': 'draft','invoiced_qty':0})
            self.write(cr, uid, [picking.id], {'state': 'draft'})
            if picking.invoice_state == 'invoiced':# and not picking.invoice_id:
                self.write(cr, uid, [picking.id],
                           {'invoice_state': '2binvoiced'})
            wf_service = netsvc.LocalService("workflow")
            # Deleting the existing instance of workflow
            wf_service.trg_delete(uid, 'stock.picking', picking.id, cr)
            wf_service.trg_create(uid, 'stock.picking', picking.id, cr)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _(
                "The stock picking '%s' has been set in draft state."
                ) % (name,)
            self.log(cr, uid, id, message)
        return True

    def print_denghi_nhapkho(self, cr, uid, ids, context=None):
        hopdong = self.browse(cr, uid, ids[0])
        datas = {
             'ids': ids,
             'model': 'stock.picking',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'denghi_nhapkho_report',
            }
        

    
    def onchange_journal(self, cr, uid, ids, stock_journal_id):
        value ={}
        domain = {}
        if not stock_journal_id:
            value.update({'location_id':False,
                           'location_dest_id':False})
            domain.update({'location_id':[('id','=',False)],
                           'location_dest_id':[('id','=',False)]})
        else:
            journal = self.pool.get('stock.journal').browse(cr, uid, stock_journal_id)
            from_location_ids = [x.id for x in journal.from_location_id]
            to_location_ids = [x.id for x in journal.to_location_id]
            domain.update({'location_id':[('id','=',from_location_ids)],
                           'location_dest_id':[('id','=',to_location_ids)]})
            location_id = from_location_ids and from_location_ids[0] or False
            location_dest_id = False
            if to_location_ids and to_location_ids[0] != location_id:
                location_dest_id = to_location_ids[0]
            value.update({'location_id':location_id,
                          'location_dest_id': location_dest_id})
        return {'value': value,'domain':domain}
    
    def create(self, cr, user, vals, context=None):
        context = context or {}
        context.update({'sequence_obj_ids':[]})
        if ('name' not in vals) or (vals.get('name')=='/'):
            if vals.get('stock_journal_id',False):
                journal = self.pool.get('stock.journal').browse(cr, user, vals['stock_journal_id'])
                if not journal.sequence_id:
                    raise osv.except_osv(_('Warning!'), _('Please define Sequence for Stock Journal.'))
                vals['name'] = self.pool.get('ir.sequence').get_id(cr, user, journal.sequence_id.id, code_or_id='id', context=context)
                
        new_id = super(osv.osv, self).create(cr, user, vals, context)
        return new_id
    
    
stock_picking_in()
class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    
    def _get_location_info(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        shop_id = False
        warehouse_id = False
        for pick in self.browse(cr, uid, ids, context=context):
            
            res[pick.id] = {
                            'shop_id': False,
                            'warehouse_id': False,
                            }
            
            if pick.location_id.usage =='internal':
                warehouse_id = pick.location_id and pick.location_id.warehouse_id and pick.location_id.warehouse_id.id or False
            if not warehouse_id:
                if pick.location_dest_id.usage =='internal':
                    warehouse_id = pick.location_dest_id and pick.location_dest_id.warehouse_id and pick.location_dest_id.warehouse_id.id or False
                
            
            if warehouse_id:
                res[pick.id]['warehouse_id'] = warehouse_id
                sql='''
                    SELECT id FROM sale_shop WHERE warehouse_id = %s
                '''%(warehouse_id)
                cr.execute(sql)
                shop_res = cr.fetchone()
                shop_id = shop_res and shop_res[0] or False
            if shop_id:
                res[pick.id]['shop_id'] = shop_id
        return res
    
    def onchange_picking_location_dest_id(self, cr, uid, ids,picking_location_dest_id=False, context=None):
        if picking_location_dest_id:
            for picking_id in self.pool.get('stock.picking').browse(cr, uid, ids):
                for stock_move_id in picking_id.move_lines:
                    self.pool.get('stock.move').write(cr,uid,stock_move_id.id,{'location_dest_id':picking_location_dest_id})
        return True
    _columns = {
        'nguoi_denghi_id':fields.many2one('res.users','Người đề nghị'),
        'donvi_vanchuyen':fields.many2one('res.partner','Đơn vị vận chuyển'),
        'lotrinh_id':fields.many2one('lo.trinh','Lộ trình'),
        'dongia_vanchuyen':fields.float('Đơn giá vận chuyển'),
        'picking_location_dest_id': fields.many2one('stock.location', 'Destination Location',states={'done': [('readonly', True)]}, select=True,),
        'cang_donghang_id': fields.many2one('cang.donghang', 'Cảng đóng hàng',states={'done': [('readonly', True)]}, select=True,),
        'shop_id': fields.function(_get_location_info, type='many2one', relation='sale.shop', string='Shop',
            store={
                'stock.picking.out': (lambda self, cr, uid, ids, c={}: ids, ['location_id','location_dest_id'], 10),
            }, readonly=True, multi='pro_info'),
        'warehouse_id': fields.function(_get_location_info, type='many2one', relation='stock.warehouse', string='Warehouse',
            store={
                'stock.picking.out': (lambda self, cr, uid, ids, c={}: ids, ['location_id','location_dest_id'], 10),
            }, readonly=True, multi='pro_info'),
        'stock_journal_id': fields.many2one('stock.journal','Stock Journal', required=True, select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'return': fields.selection([('none', 'Normal'), ('customer', 'Return from Customer'),('internal','Return Internal'), ('supplier', 'Return to Supplier')], 'Type', required=True, select=True, help="Type specifies whether the Picking has been returned or not."),
    }
    
    _defaults = {    
        'return': 'none',
        'type':   'out',
    }
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        return self.pool.get('stock.picking').fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
    
    def has_valuation_moves(self, cr, uid, move):
        return self.pool.get('account.move').search(cr, uid, [
            ('stock_move_id', '=', move.id),
            ])
    
    def action_revert_done(self, cr, uid, ids, context=None):
        move_ids = []
        invoice_ids = []
        if not len(ids):
            return False
        
        sql ='''
            Select id 
            FROM
                stock_move where picking_id = %s
        '''%(ids[0])
        cr.execute(sql)
        for line in cr.dictfetchall():
            move_ids.append(line['id'])
        if move_ids:
            sql='''
                SELECT state ,id
                FROM account_invoice 
                WHERE id IN (
                     SELECT distinct invoice_id 
                     FROM account_invoice_line 
                     WHERE stock_move_id in(%s))
            '''%(','.join(map(str,move_ids)))
            cr.execute(sql)
            for line in cr.dictfetchall():
                if line['state'] not in ('draft','cancel'):
                    raise osv.except_osv(
                        _('Cảnh báo'),
                        _('Vui lòng hủy bỏ tất cả các hóa đơn của phiếu xuất này trước!'))
                else:
                    invoice_ids.append(line['id'])
            if invoice_ids:
                cr.execute('delete from account_invoice where id in %s',(tuple(invoice_ids),))
#                 self.pool.get('account.invoice').unlink(cr,uid,invoice_ids)
                
        for picking in self.browse(cr, uid, ids, context):
            for line in picking.move_lines:
                if self.has_valuation_moves(cr, uid, line):
                    raise osv.except_osv(
                        _('Cảnh báo'),
                        _('Sản phẩm "%s" đã sinh bút toán "%s". \
                            Vui lòng xóa bút toán trước') % (line.name,
                                                   line.picking_id.name))
                line.write({'state': 'draft','invoiced_qty':0})
            self.write(cr, uid, [picking.id], {'state': 'draft'})
            if picking.invoice_state == 'invoiced':# and not picking.invoice_id:
                self.write(cr, uid, [picking.id],
                           {'invoice_state': '2binvoiced'})
            wf_service = netsvc.LocalService("workflow")
            # Deleting the existing instance of workflow
            wf_service.trg_delete(uid, 'stock.picking', picking.id, cr)
            wf_service.trg_create(uid, 'stock.picking', picking.id, cr)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _(
                "The stock picking '%s' has been set in draft state."
                ) % (name,)
            self.log(cr, uid, id, message)
        return True
    
    def onchange_journal(self, cr, uid, ids, stock_journal_id):
        value ={}
        domain = {}
        if not stock_journal_id:
            value.update({'location_id':False,
                           'location_dest_id':False})
            domain.update({'location_id':[('id','=',False)],
                           'location_dest_id':[('id','=',False)]})
        else:
            journal = self.pool.get('stock.journal').browse(cr, uid, stock_journal_id)
            from_location_ids = [x.id for x in journal.from_location_id]
            to_location_ids = [x.id for x in journal.to_location_id]
            domain.update({'location_id':[('id','=',from_location_ids)],
                           'location_dest_id':[('id','=',to_location_ids)]})
            location_id = from_location_ids and from_location_ids[0] or False
            location_dest_id = False
            if to_location_ids and to_location_ids[0] != location_id:
                location_dest_id = to_location_ids[0]
            value.update({'location_id':location_id,
                          'location_dest_id': location_dest_id})
        return {'value': value,'domain':domain}
    
    def create(self, cr, user, vals, context=None):
        context = context or {}
        context.update({'sequence_obj_ids':[]})
        if ('name' not in vals) or (vals.get('name')=='/'):
            if vals.get('stock_journal_id',False):
                journal = self.pool.get('stock.journal').browse(cr, user, vals['stock_journal_id'])
                if not journal.sequence_id:
                    raise osv.except_osv(_('Warning!'), _('Please define Sequence for Stock Journal.'))
                vals['name'] = self.pool.get('ir.sequence').get_id(cr, user, journal.sequence_id.id, code_or_id='id', context=context)
                
        new_id = super(osv.osv, self).create(cr, user, vals, context)
        return new_id
    
    def print_denghi_xuatkho(self, cr, uid, ids, context=None):
        hopdong = self.browse(cr, uid, ids[0])
        datas = {
             'ids': ids,
             'model': 'stock.picking',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'denghi_xuatkho_report',
            }

    def print_denghi_xuathang(self, cr, uid, ids, context=None):
        hopdong = self.browse(cr, uid, ids[0])
        datas = {
             'ids': ids,
             'model': 'stock.picking',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'denghi_xuathang_report',
            }
    
stock_picking_out()

class stock_move(osv.osv):
    _inherit = "stock.move"
    
    def product_id_change(self, cr, uid, ids, product, location_id, location_dest_id, context=None):
        context = context or {}
        result = {}
        
        product_obj = self.pool.get('product.product').browse(cr, uid, product, context=context)
        if product_obj and product_obj.uom_id:
            result['product_uom'] = product_obj.uom_id.id
        result['name'] = product_obj.name
        result['location_id'] = location_id
        result['location_dest_id'] = location_dest_id
        return {'value': result}
    
    def _get_product_info(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        uom_obj = self.pool.get('product.uom')
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                            'primary_qty': 0.0,
                            }
            if line.product_id and line.product_uom:
                if line.product_uom.id != line.product_id.uom_id.id:
                    if line.product_id.__hasattr__('uom_ids'):
                        res[line.id]['primary_qty'] = uom_obj._compute_qty(cr, uid, line.product_uom.id, line.product_qty, line.product_id.uom_id.id, product_id=line.product_id.id)
                    else:
                        res[line.id]['primary_qty'] = uom_obj._compute_qty(cr, uid, line.product_uom.id, line.product_qty, line.product_id.uom_id.id)
                else:
                    res[line.id]['primary_qty'] = line.product_qty
        return res
    _columns = {
        'chatluong_id':fields.many2one('chatluong.sanpham','Chất lượng'),
        'quycach_baobi_id':fields.many2one('quycach.baobi','Quy cách bao bì'),
        'quycach_donggoi_id':fields.many2one('quycach.donggoi','Quy cách đóng gói'),
        'hop_dong_mua_id':fields.many2one('hop.dong','Hợp đồng mua'),
        'hop_dong_ban_id':fields.many2one('hop.dong','Hợp đồng bán'),
#         'picking_ids': fields.many2many('stock.picking.in', 'move_picking_ref', 'move_id', 'picking_id', 'Phiếu nhập kho'),
        'picking_in_id': fields.many2one('stock.picking.in', 'Phiếu nhập kho'),
        'ghichu':fields.char('Ghi chú'),
        'stock_journal_id':  fields.related('picking_id', 'stock_journal_id', type='many2one', relation='stock.journal', string='Stock Journal', store=True, readonly=1),
        #Hung them 'invoiced_qty' de tru so luong da len hoa don
        'invoiced_qty':fields.float('Invoiced Qty'),
        'primary_qty': fields.function(_get_product_info, string='Primary Qty', digits_compute= dp.get_precision('Product Unit of Measure'), type='float',
            store={
                'stock.move': (lambda self, cr, uid, ids, c={}: ids, ['product_id','product_uom','product_qty'], 10),
            }, readonly=True, multi='pro_info'),
    }
    
    def action_done(self, cr, uid, ids, context=None):
        """ Makes the move done and if all moves are done, it will finish the picking.
        @return:
        """
        picking_ids = []
        move_ids = []
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}

        todo = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.state=="draft":
                todo.append(move.id)
        if todo:
            self.action_confirm(cr, uid, todo, context=context)
            todo = []

        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ['done','cancel']:
                continue
            move_ids.append(move.id)

            if move.picking_id:
                picking_ids.append(move.picking_id.id)
            if move.move_dest_id.id and (move.state != 'done'):
                # Downstream move should only be triggered if this move is the last pending upstream move
                other_upstream_move_ids = self.search(cr, uid, [('id','not in',move_ids),('state','not in',['done','cancel']),
                                            ('move_dest_id','=',move.move_dest_id.id)], context=context)
                if not other_upstream_move_ids:
                    self.write(cr, uid, [move.id], {'move_history_ids': [(4, move.move_dest_id.id)]})
                    if move.move_dest_id.state in ('waiting', 'confirmed'):
                        self.force_assign(cr, uid, [move.move_dest_id.id], context=context)
                        if move.move_dest_id.picking_id:
                            wf_service.trg_write(uid, 'stock.picking', move.move_dest_id.picking_id.id, cr)
                        if move.move_dest_id.auto_validate:
                            self.action_done(cr, uid, [move.move_dest_id.id], context=context)

            self._update_average_price(cr, uid, move, context=context)
            
            if move.stock_journal_id  and move.stock_journal_id.source_type not in ['in','return_supplier']:
                product_obj = self.pool.get('product.product')
                if move.picking_id and move.picking_id.type == 'in' and move.product_id:
                    product_obj.write(cr, uid, [move.product_id.id], {'standard_price':move.purchase_line_id.price_unit})
                if move.picking_id and move.picking_id.type == 'out' and move.product_id and move.picking_in_id:
                    move_in_ids = self.search(cr, uid, [('picking_id','=',move.picking_in_id.id),('product_id','=',move.product_id.id)])
                    if move_in_ids:
                        move_in = self.browse(cr, uid, move_in_ids[0])
                        product_obj.write(cr, uid, [move.product_id.id], {'standard_price':move_in.purchase_line_id.price_unit})    
                self._create_product_valuation_moves(cr, uid, move, context=context)
                
            if move.state not in ('confirmed','done','assigned'):
                todo.append(move.id)

        if todo:
            self.action_confirm(cr, uid, todo, context=context)

        self.write(cr, uid, move_ids, {'state': 'done', 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
        for id in move_ids:
            wf_service.trg_trigger(uid, 'stock.move', id, cr)

        for pick_id in picking_ids:
            wf_service.trg_write(uid, 'stock.picking', pick_id, cr)

        return True
    
    def _create_product_valuation_moves(self, cr, uid, move, context=None):
        """
        Generate the appropriate accounting moves if the product being moves is subject
        to real_time valuation tracking, and the source or destination location is
        a transit location or is outside of the company.
        """
        if move.product_id.valuation == 'real_time': # FIXME: product valuation should perhaps be a property?
            if context is None:
                context = {}
            src_company_ctx = dict(context,force_company=move.location_id.company_id.id)
            dest_company_ctx = dict(context,force_company=move.location_dest_id.company_id.id)
            # do not take the company of the one of the user
            # used to select the correct period
            company_ctx = dict(context, company_id=move.company_id.id)
            account_moves = []
            # Outgoing moves (or cross-company output part)
            if move.location_id.company_id \
                and (move.location_id.usage == 'internal' and move.location_dest_id.usage != 'internal'\
                     or move.location_id.company_id != move.location_dest_id.company_id):
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, src_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
                #returning goods to supplier
                if move.location_dest_id.usage == 'supplier':
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_valuation, acc_src, reference_amount, reference_currency_id, context))]
                else:
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_valuation, acc_dest, reference_amount, reference_currency_id, context))]

            # Incoming moves (or cross-company input part)
            if move.location_dest_id.company_id \
                and (move.location_id.usage != 'internal' and move.location_dest_id.usage == 'internal'\
                     or move.location_id.company_id != move.location_dest_id.company_id):
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, dest_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
                #goods return from customer
                if move.location_id.usage == 'customer':
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_dest, acc_valuation, reference_amount, reference_currency_id, context))]
                else:
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_src, acc_valuation, reference_amount, reference_currency_id, context))]

            move_obj = self.pool.get('account.move')
            for j_id, move_lines in account_moves:
                move_obj.create(cr, uid,
                        {
                         'journal_id': j_id,
                         'line_id': move_lines,
                         'company_id': move.company_id.id,
                         'stock_move_id': move.id,
                         'shop_id':move.picking_id and move.picking_id.shop_id and move.picking_id.shop_id.id or False,
                         'ref': move.picking_id and move.picking_id.name}, context=company_ctx)
    
stock_move()

class stock_location(osv.osv):
    _inherit = "stock.location"
    
    _columns = {
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse'),
    }
    
    def name_get(self, cr, uid, ids, context=None):
        # always return the full hierarchical name
        res = self._complete_name(cr, uid, ids, 'complete_name', None, context=context)
        return res.items()

    def _complete_name(self, cr, uid, ids, name, args, context=None):
        """ Forms complete name of location from parent location to child location.
        @return: Dictionary of values
        """
        res = {}
        for m in self.browse(cr, uid, ids, context=context):
#             names = [m.name]
#             parent = m.location_id
#             while parent:
#                 names.append(parent.name)
#                 parent = parent.location_id
            res[m.id] = m.name
        return res

stock_location()

class account_move(osv.osv):
    _inherit = "account.move"
    
    _columns = {
        'stock_move_id': fields.many2one('stock.move', 'Stock Move'),
    }
    
account_move()

class stock_return_picking(osv.osv):
    _inherit = 'stock.return.picking'

    _columns = {
        'return_type': fields.selection([('none', 'Normal'), ('internal','Return Internal'), ('customer', 'Return from Customer'), ('supplier', 'Return to Supplier')], 'Type', required=True, readonly=True, help="Type specifies whether the Picking has been returned or not."),
        'note':        fields.text('Notes'),
        'location_id': fields.many2one('stock.location', 'Location', help='If a location is chosen the destination location for customer return (or origin for supplier return) is forced for all moves.'),
        'journal_id':fields.many2one('stock.journal', 'Stock Journal',required=True,),
        'option':fields.boolean('Tranfer Product'),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(stock_return_picking, self).default_get(cr, uid, fields, context)
        record_id = context and context.get('active_id', False) or False
        pick_obj = self.pool.get('stock.picking')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
#         if pick and pick.sale_id and pick.sale_id:
#             warehouse = pick.sale_id.shop_id and pick.sale_id.shop_id.warehouse_id
#             res.update({'location_id': warehouse and warehouse.lot_return_id and warehouse.lot_return_id.id or False})
        
        if pick:
            if pick.type == 'in':
                journal_ids =  self.pool.get('stock.journal').search(cr,uid,[('source_type','=','return_supplier')])
                if pick['return'] == 'none':
                    res.update({'return_type': 'supplier','journal_id':journal_ids and journal_ids[0] or False})
            elif pick.type == 'out':
                journal_ids =  self.pool.get('stock.journal').search(cr,uid,[('source_type','=','return_customer')])
                if pick['return'] == 'none':
                    res.update({'return_type': 'customer','journal_id':journal_ids and journal_ids[0] or False})
            else:
                if pick['return'] == 'none':
                    res.update({'return_type': 'internal','journal_id':pick.stock_journal_id.id})
                    
            result1 = []
            return_history = self.get_return_history(cr, uid, record_id, context)       
            for line in pick.move_lines:
                if line.state in ('cancel') or line.scrapped:
                    continue
                qty = line.product_qty - return_history.get(line.id, 0)
                if qty > 0:
                    result1.append({'product_id': line.product_id.id, 'quantity': qty,'move_id':line.id, 'prodlot_id': line.prodlot_id and line.prodlot_id.id or False})
            if 'product_return_moves' in fields:
                res.update({'product_return_moves': result1})
        return res
    
    def create_returns(self, cr, uid, ids, context=None):
        """ 
         Creates return picking.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: List of ids selected
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {} 
        record_id = context and context.get('active_id', False) or False
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        data_obj = self.pool.get('stock.return.picking.memory')
        act_obj = self.pool.get('ir.actions.act_window')
        model_obj = self.pool.get('ir.model.data')
        wf_service = netsvc.LocalService("workflow")
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        data = self.read(cr, uid, ids[0], context=context)
        date_cur = time.strftime('%Y-%m-%d %H:%M:%S')
        set_invoice_state_to_none = False#True LY by default 
        returned_lines = 0
        location_id = False
        location_dest_id = False
        return_picking_obj = self.browse(cr,uid,ids[0])
        # Create new picking for returned products

        if pick.type == 'out':
            new_type = 'in'
            location_id = pick.location_id and pick.location_id.id or False
            location_dest_id = pick.location_dest_id and pick.location_dest_id.id or False
            # lay mat dinh stoc
            journal_id =  self.pool.get('stock.journal').search(cr,uid,[('source_type','=','return_customer')])
        elif pick.type == 'in':
            new_type = 'out'
            location_id = pick.location_id and pick.location_id.id or False
            location_dest_id = pick.location_dest_id and pick.location_dest_id.id or False
            journal_id =  self.pool.get('stock.journal').search(cr,uid,[('source_type','=','return_supplier')])
            return_history = self.get_return_history(cr, uid, record_id, context)
            for line in pick.move_lines:
                sl_da_xuat = 0
                phieu_xuat = ''
                if line.state in ('cancel') or line.scrapped:
                    continue
                qty = line.product_qty - return_history.get(line.id, 0)
                sql = '''
                    select product_qty, picking_id
                    from stock_move where hop_dong_mua_id is not null and picking_in_id is not null 
                    and hop_dong_mua_id = %s and picking_in_id = %s and product_id = %s
                    and picking_id in (select id from stock_picking where type = 'out' and state != 'cancel')
                '''%(line.hop_dong_mua_id.id, line.picking_id.id, line.product_id.id)
                cr.execute(sql)
                for move in cr.dictfetchall():
                    sl_da_xuat += move['product_qty']
                    picking = self.pool.get('stock.picking').browse(cr,uid,move['picking_id'])
                    phieu_xuat+=picking.name+' '
                qty = qty - sl_da_xuat
                for return_picking in return_picking_obj.product_return_moves:
                    if line.product_id.id == return_picking.product_id.id:
                        if return_picking.quantity > qty:
                            raise osv.except_osv(_('Cảnh báo!'), _("Đã xuất %s %s sản phẩm %s (%s). Bạn chỉ có thể trả lại %s %s")%(sl_da_xuat, line.product_id.uom_id.name, line.product_id.name, phieu_xuat, qty,line.product_id.uom_id.name))
        else:
            new_type = 'internal'
            journal_id =  [pick.stock_journal_id.id] or False
            location_id = pick.location_id and pick.location_id.id or False
            location_dest_id = pick.location_dest_id and pick.location_dest_id.id or False
        
        new_picking_vals = {'name': self.pool.get('ir.sequence').get_id(cr, uid, return_picking_obj.journal_id.sequence_id.id, code_or_id='id', context=context),
                            'move_lines': [],
                            'state':'draft',
                            'type': new_type,
                            'return': data['return_type'],
                            'note': data['note'],
                            'origin':pick.name or '',
                            'date':date_cur,
                            'invoice_state': data['invoice_state'], 
                            'stock_journal_id':return_picking_obj.journal_id and return_picking_obj.journal_id.id or False,
                            'location_id':location_dest_id,
                            'location_dest_id':location_id,}
        new_picking = pick_obj.copy(cr, uid, pick.id, new_picking_vals)
        #Hung them chuc nang doi san pham.lay journal tren picking goc va tren wizard
        if return_picking_obj.option:
            new_id = pick_obj.copy(cr, uid, pick.id, {
                                        'name': self.pool.get('ir.sequence').get_id(cr, uid, pick.stock_journal_id.sequence_id.id, code_or_id='id', context=context),
                                        'move_lines': [], 
                                        'state':'draft', 
                                        'type': pick.type,
                                        'date':date_cur,
                                        'date_done':False, 
                                        'invoice_state': data['invoice_state'],
                                        'stock_journal_id':pick.stock_journal_id and pick.stock_journal_id.id or False,
                                         })
            val_id = data['product_return_moves']
            for v in val_id:
                data_get = data_obj.browse(cr, uid, v, context=context)
                mov_id = data_get.move_id.id
                new_qty = data_get.quantity
                move = move_obj.browse(cr, uid, mov_id, context=context)
                if new_qty >move.product_qty:
                    error = 'Không vượt quá số lượng đơn hàng'
                    raise osv.except_osv(unicode('Lỗi', 'utf8'), unicode(error, 'utf8'))
                if move.state in ('cancel') or move.scrapped:
                    continue
                new_location = move.location_dest_id.id
                returned_qty = move.product_qty
                for rec in move.move_history_ids2:
                    returned_qty -= rec.product_qty
                if new_qty:
                    returned_lines += 1
                    new_move_vals = {'prodlot_id':move.prodlot_id and move.prodlot_id.id or False,
                                    'product_qty': new_qty,
                                    'product_uos_qty': uom_obj._compute_qty(cr, uid, move.product_uom.id, new_qty, move.product_uos.id),
                                    'picking_id': new_id,
                                    'state': 'draft',
                                    'location_id': new_location,
                                    'location_dest_id': move.location_id.id,
                                    'date': date_cur,
                                    'note': data['note'],
                                    }
                    if data['location_id']:
                        if data['return_type'] == 'customer':
                            new_move_vals.update({'location_dest_id': data['location_id'][0], })
                        else:
                            new_move_vals.update({'location_id': data['location_id'][0], })
                    
                    new_move = move_obj.copy(cr, uid, move.id, new_move_vals)
                    move_obj.write(cr, uid, [move.id], {'move_history_ids2':[(4, new_move)]}, context=context)
            if not returned_lines:
                raise osv.except_osv(_('Warning!'), _("Please specify at least one non-zero quantity."))

        val_id = data['product_return_moves']
        for v in val_id:
            data_get = data_obj.browse(cr, uid, v, context=context)
            mov_id = data_get.move_id.id
            new_qty = data_get.quantity
            move = move_obj.browse(cr, uid, mov_id, context=context)
            new_location = move.location_dest_id.id
            returned_qty = move.product_qty
            for rec in move.move_history_ids2:
                returned_qty -= rec.product_qty
    
            if returned_qty != new_qty:
                set_invoice_state_to_none = False
            if new_qty:
                returned_lines += 1
                new_move=move_obj.copy(cr, uid, move.id, {
                                            'prodlot_id':move.prodlot_id and move.prodlot_id.id or False,
                                            'product_qty': new_qty,
                                            'product_uos_qty': uom_obj._compute_qty(cr, uid, move.product_uom.id, new_qty, move.product_uos.id),
                                            'picking_id': new_picking, 
                                            'state': 'draft',
                                            'location_id': new_location, 
                                            'location_dest_id': move.location_id.id,
                                            'date': date_cur,
                })
                move_obj.write(cr, uid, [move.id], {'move_history_ids2':[(4,new_move)]}, context=context)
        if not returned_lines:
            raise osv.except_osv(_('Warning!'), _("Please specify at least one non-zero quantity."))
        #LY make it can be invoiced
        if data['invoice_state'] == 'none':#returned_qty == new_qty #!= new_qty:
            set_invoice_state_to_none = True#LY False
        if set_invoice_state_to_none:
            pick_obj.write(cr, uid, [pick.id], {'invoice_state':'none'}, context=context)
        wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
        pick_obj.force_assign(cr, uid, [new_picking], context)
        # Update view id in context, lp:702939
        model_list = {
                'out': 'stock.picking.out',
                'in': 'stock.picking.in',
                'internal': 'stock.picking',
        }
        return {
            'domain': "[('id', 'in', [" + str(new_picking) + "])]",
            'name': _('Returned Picking'),
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model': model_list.get(new_type, 'stock.picking'),
            'type':'ir.actions.act_window',
            'context':context,
        }

stock_return_picking()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    _columns = {
        'stock_move_id': fields.many2one('stock.move', 'Stock Move'),
    }
    
account_invoice_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
