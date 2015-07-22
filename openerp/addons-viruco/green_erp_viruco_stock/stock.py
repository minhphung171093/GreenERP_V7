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
    
    _columns = {
        'nguoi_denghi_id':fields.many2one('res.users','Người đề nghị'),
        'donvi_vanchuyen':fields.many2one('res.partner','Đơn vị vận chuyển'),
        'lotrinh_id':fields.many2one('lo.trinh','Lộ trình'),
        'dongia_vanchuyen':fields.float('Đơn giá vận chuyển'),
        'picking_location_dest_id': fields.many2one('stock.location', 'Destination Location',states={'done': [('readonly', True)]}, select=True,),
        'cang_donghang_id': fields.many2one('cang.donghang', 'Cảng đóng hàng',states={'done': [('readonly', True)]}, select=True,),
    }
    
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

        return {
            'name': name,
            'origin': origin,
            'invoice_id': invoice_id,
            'uos_id': uos_id,
            'product_id': move_line.product_id.id,
            'account_id': account_id,
            'price_unit': self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type']),
            'discount': self._get_discount_invoice(cr, uid, move_line),
            'quantity': move_line.product_uos_qty or move_line.product_qty,
            'invoice_line_tax_id': [(6, 0, self._get_taxes_invoice(cr, uid, move_line, invoice_vals['type']))],
            'account_analytic_id': self._get_account_analytic_invoice(cr, uid, picking, move_line),
            'stock_move_id': move_line.id,
        }
    
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
    
stock_picking()

class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    
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
    }
    
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
    
stock_picking_in()
class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    
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
    }
    
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
    
stock_picking_out()

class stock_move(osv.osv):
    _inherit = "stock.move"
    _columns = {
        'chatluong_id':fields.many2one('chatluong.sanpham','Chất lượng'),
        'quycach_baobi_id':fields.many2one('quycach.baobi','Quy cách bao bì'),
        'quycach_donggoi_id':fields.many2one('quycach.donggoi','Quy cách đóng gói'),
        'hop_dong_mua_id':fields.many2one('hop.dong','Hợp đồng mua'),
        'hop_dong_ban_id':fields.many2one('hop.dong','Hợp đồng bán'),
#         'picking_ids': fields.many2many('stock.picking.in', 'move_picking_ref', 'move_id', 'picking_id', 'Phiếu nhập kho'),
        'picking_in_id': fields.many2one('stock.picking.in', 'Phiếu nhập kho'),
        'ghichu':fields.char('Ghi chú'),
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
                         'ref': move.picking_id and move.picking_id.name}, context=company_ctx)
    
stock_move()

class stock_location(osv.osv):
    _inherit = "stock.location"
    
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

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    _columns = {
        'stock_move_id': fields.many2one('stock.move', 'Stock Move'),
    }
    
account_invoice_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
