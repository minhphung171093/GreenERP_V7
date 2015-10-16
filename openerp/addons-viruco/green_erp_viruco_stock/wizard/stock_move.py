# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class split_hop_dong(osv.osv_memory):
    _name = "split.hop.dong"

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(split_hop_dong, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            move = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context=context)
            if 'product_id' in fields:
                res.update({'product_id': move.product_id.id})
            if 'product_uom' in fields:
                res.update({'product_uom': move.product_uom.id})
            if 'qty' in fields:
                res.update({'qty': move.product_qty})
            if 'location_id' in fields:
                res.update({'location_id': move.location_id.id})
            chitiet_tonkho_line = []
            sql = '''
                select id from stock_location where usage='internal' and chained_location_type!='customer'
            '''
            cr.execute(sql)
            location_ids = [r[0] for r in cr.fetchall()]
            for location_id in location_ids:
                sql = '''
                    select hop_dong_mua_id,picking_id,sum(product_qty) as product_qty,price_unit
                        from stock_move where state='done' and product_id=%s and location_id!=location_dest_id and location_dest_id=%s and hop_dong_mua_id is not null
                        and picking_id in (select id from stock_picking where return != 'customer')
                        group by hop_dong_mua_id,picking_id,price_unit
                '''%(move.product_id.id,location_id)
                cr.execute(sql)
                lines = cr.dictfetchall()
                for line in lines:
                    picking = self.pool.get('stock.picking').browse(cr,uid,line['picking_id'])
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty_out
                            from stock_move
                            where state!='cancel' and product_id=%s and location_id!=location_dest_id and location_id=%s and picking_in_id=%s and hop_dong_mua_id=%s and id!=%s
                    '''%(move.product_id.id,location_id,line['picking_id'],line['hop_dong_mua_id'],move.id)
                    cr.execute(sql)
                    product_qty_out = cr.fetchone()[0]
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty_return
                            from stock_move
                            where state!='cancel' and product_id=%s and location_id!=location_dest_id and location_id=%s and hop_dong_mua_id=%s
                            and picking_id in (select id from stock_picking where return = 'supplier' and type = 'out' and origin = '%s')
                    '''%(move.product_id.id,location_id,line['hop_dong_mua_id'], picking.name)
                    cr.execute(sql)
                    product_qty_return_to_sup = cr.fetchone()[0]
                    
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty_return
                            from stock_move
                            where state ='done' and product_id=%s and location_id!=location_dest_id and location_dest_id=%s and hop_dong_mua_id=%s
                            and picking_id in (select id from stock_picking where return = 'customer' and type = 'in' and origin in (
                            select name from stock_picking where id in (select picking_id from stock_move where hop_dong_mua_id=%s
                            and picking_in_id = %s and product_id = %s and location_id = %s)))
                    '''%(move.product_id.id,location_id,line['hop_dong_mua_id'], line['hop_dong_mua_id'],line['picking_id'],move.product_id.id,location_id)
                    cr.execute(sql)
                    product_qty_return_from_cus = cr.fetchone()[0]
                    if line['product_qty']-product_qty_out-product_qty_return_to_sup+product_qty_return_from_cus>0:
                        picking = self.pool.get('stock.picking').browse(cr, uid, line['picking_id'])
                        chitiet_tonkho_line.append((0,0,{
                            'location_id': location_id,
                            'hd_mua_id': line['hop_dong_mua_id'],
                            'picking_in_id': line['picking_id'],
                            'partner_id': picking.partner_id and picking.partner_id.id or False,
                            'ngay_nhaphang': picking.date_done,
                            'don_gia': line['price_unit'],
                            'quantity_ton': line['product_qty']-product_qty_out-product_qty_return_to_sup+product_qty_return_from_cus,
                        }))
            res.update({'line_ids': chitiet_tonkho_line,'move_id': context['active_id']})
        return res

    _columns = {
        'qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_id': fields.many2one('product.product', 'Product', required=True, select=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure'),
        'line_ids': fields.one2many('split.hop.dong.line', 'wizard_id', 'Phân bổ hợp đồng'),
        'location_id': fields.many2one('stock.location', 'Source Location'),
        'location_choose_id': fields.many2one('stock.location', 'Kho'),
        'move_id': fields.many2one('stock.move', 'Move'),
     }
    
    def onchange_location_choose_id(self, cr, uid, ids, location_id=False, move_id=False, context=None):
        vals = {}
        chitiet_tonkho_line = []
        #Hung giu lai nhung dong da chon
#         for data in self.browse(cr, uid, ids, context=context):
#             for wizard_line in data.line_ids:
#                 if wizard_line.is_choose:
#                     chitiet_tonkho_line.append((0,0,{
#                             'location_id': location_id,
#                             'hd_mua_id': wizard_line.hd_mua_id.id,
#                             'picking_in_id': wizard_line.picking_in_id.id,
#                             'quantity_ton': wizard_line.quantity,
#                         }))
        if location_id and move_id:
            move = self.pool.get('stock.move').browse(cr, uid, move_id, context=context)
            sql = '''
                select hop_dong_mua_id,picking_id,sum(product_qty) as product_qty,price_unit
                    from stock_move where state='done' and product_id=%s and location_id!=location_dest_id and location_dest_id=%s and hop_dong_mua_id is not null
                    group by hop_dong_mua_id,picking_id,price_unit
            '''%(move.product_id.id,location_id)
            cr.execute(sql)
            lines = cr.dictfetchall()
            for line in lines:
                sql = '''
                    select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty_out
                        from stock_move
                        where state!='cancel' and product_id=%s and location_id!=location_dest_id and location_id=%s and picking_in_id=%s and hop_dong_mua_id=%s and id!=%s
                '''%(move.product_id.id,location_id,line['picking_id'],line['hop_dong_mua_id'],move.id)
                cr.execute(sql)
                product_qty_out = cr.fetchone()[0]
                if product_qty_out<line['product_qty']:
                    picking = self.pool.get('stock.picking').browse(cr, uid, line['picking_id'])
                    chitiet_tonkho_line.append((0,0,{
                        'location_id': location_id,
                        'hd_mua_id': line['hop_dong_mua_id'],
                        'picking_in_id': line['picking_id'],
                        'partner_id': picking.partner_id and picking.partner_id.id or False,
                        'ngay_nhaphang': picking.date_done,
                        'don_gia': line['price_unit'],
                        'quantity_ton': line['product_qty']-product_qty_out,
                    }))
        if not location_id and move_id:
            move = self.pool.get('stock.move').browse(cr, uid, move_id, context=context)
            sql = '''
                select id from stock_location where usage='internal' and chained_location_type!='customer'
            '''
            cr.execute(sql)
            location_ids = [r[0] for r in cr.fetchall()]
            for location_id in location_ids:
                sql = '''
                    select hop_dong_mua_id,picking_id,sum(product_qty) as product_qty,price_unit
                        from stock_move where state='done' and product_id=%s and location_id!=location_dest_id and location_dest_id=%s and hop_dong_mua_id is not null
                        group by hop_dong_mua_id,picking_id,price_unit
                '''%(move.product_id.id,location_id)
                cr.execute(sql)
                lines = cr.dictfetchall()
                for line in lines:
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty_out
                            from stock_move
                            where state!='cancel' and product_id=%s and location_id!=location_dest_id and location_id=%s and picking_in_id=%s and hop_dong_mua_id=%s and id!=%s
                    '''%(move.product_id.id,location_id,line['picking_id'],line['hop_dong_mua_id'],move.id)
                    cr.execute(sql)
                    product_qty_out = cr.fetchone()[0]
                    if product_qty_out<line['product_qty']:
                        picking = self.pool.get('stock.picking').browse(cr, uid, line['picking_id'])
                        chitiet_tonkho_line.append((0,0,{
                            'location_id': location_id,
                            'hd_mua_id': line['hop_dong_mua_id'],
                            'picking_in_id': line['picking_id'],
                            'partner_id': picking.partner_id and picking.partner_id.id or False,
                            'ngay_nhaphang': picking.date_done,
                            'don_gia': line['price_unit'],
                            'quantity_ton': line['product_qty']-product_qty_out,
                        }))
        return {'value': {'line_ids': chitiet_tonkho_line}}

    def split_lot(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = self.split(cr, uid, ids, context.get('active_ids'), context=context)
        return {'type': 'ir.actions.act_window_close'}

    def split(self, cr, uid, ids, move_ids, context=None):
        if context is None:
            context = {}
        assert context.get('active_model') == 'stock.move',\
             'Incorrect use of the stock move split wizard'
        move_obj = self.pool.get('stock.move')
        new_move = []
        for data in self.browse(cr, uid, ids, context=context):
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                move_qty = move.product_qty
                quantity_rest = move.product_qty
                uos_qty_rest = move.product_uos_qty
                new_move = []
                lines = [l for l in data.line_ids if l and l.is_choose]
                total_move_qty = 0.0
                for line in lines:
#                     if not line.picking_ids:
#                         raise osv.except_osv(_('Cảnh báo!'), _('Vui lòng nhập phiếu nhập kho!'))
                    quantity = line.quantity
                    total_move_qty += quantity
                    if total_move_qty > move_qty:
                        raise osv.except_osv(_('Cảnh báo!'), _('Số lượng đang chuyển %d của %s lớn hơn số lượng hiện có (%d)!') \
                                % (total_move_qty, move.product_id.name, move_qty))
                    if quantity <= 0 or move_qty == 0:
                        continue
                    quantity_rest -= quantity
                    uos_qty = quantity / move_qty * move.product_uos_qty
                    uos_qty_rest = quantity_rest / move_qty * move.product_uos_qty
                    if quantity_rest < 0:
                        quantity_rest = quantity
                        self.pool.get('stock.move').log(cr, uid, move.id, _('Unable to assign all lots to this move!'))
                        return False
                    default_val = {
                        'product_qty': quantity,
                        'product_uos_qty': uos_qty,
                        'state': move.state
                    }
                    if quantity_rest > 0:
                        current_move = move_obj.copy(cr, uid, move.id, default_val, context=context)
                        new_move.append(current_move)

                    if quantity_rest == 0:
                        current_move = move.id
                    
#                     picking_ids = [p.id for p in line.picking_ids]
                    move_obj.write(cr, uid, [current_move], {'hop_dong_mua_id': line.hd_mua_id.id,
                                                             'picking_in_id': line.picking_in_id.id,
                                                             'location_id': line.location_id.id,
                                                             'state':move.state})

                    update_val = {}
                    if quantity_rest > 0:
                        update_val['product_qty'] = quantity_rest
                        update_val['product_uos_qty'] = uos_qty_rest
                        update_val['state'] = move.state
                        move_obj.write(cr, uid, [move.id], update_val)
        return new_move

split_hop_dong()

class split_hop_dong_line(osv.osv_memory):
    _name = "split.hop.dong.line"
    _columns = {
        'quantity_ton': fields.float('Số lượng tồn',required=True),
        'quantity': fields.float('Số lượng',required=True),
        'wizard_id': fields.many2one('split.hop.dong', 'Parent Wizard',ondelete='cascade'),
        'hd_mua_id': fields.many2one('hop.dong', 'Hợp đồng mua',required=False),
        'location_id': fields.many2one('stock.location', 'Kho',required=True),
#         'picking_ids': fields.many2many('stock.picking.in', 'split_hd_picking_ref', 'split_hd_id', 'picking_id', 'Phiếu nhập kho',required=False),
        'picking_in_id': fields.many2one('stock.picking.in', 'Phiếu nhập kho',required=True),
        'is_choose': fields.boolean('Chọn',required=False),
        'ngay_nhaphang': fields.datetime('Ngày nhập hàng'),
        'don_gia': fields.float('Đơn giá'),
        'partner_id': fields.many2one('res.partner','Nhà cung cấp'),
    }
    _defaults = {
        'quantity': 1.0,
    }
    
    def onchange_quantity(self, cr, uid, ids, quantity_ton=False, quantity=False, context=None):
        vals = {}
        warning = {}
        if quantity_ton<quantity:
            warning = {
                'title': _('Cảnh báo!'),
                'message' : _('Số lượng phân bổ vượt quá số lượng tồn kho hiện tại')
            }
            vals={'quantity':quantity_ton}
        return {'value': vals,'warning': warning}

split_hop_dong_line()




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
