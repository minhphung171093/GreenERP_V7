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
        return res

    _columns = {
        'qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_id': fields.many2one('product.product', 'Product', required=True, select=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure'),
        'line_ids': fields.one2many('split.hop.dong.line', 'wizard_id', 'Phân bổ hợp đồng'),
        'location_id': fields.many2one('stock.location', 'Source Location')
     }

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
                lines = [l for l in data.line_ids if l]
                total_move_qty = 0.0
                for line in lines:
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

                    move_obj.write(cr, uid, [current_move], {'hop_dong_mua_id': line.hd_mua_id.id,
                                                             'hop_dong_ban_id': line.hd_ban_id.id,
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
    _description = "Stock move Split lines"
    _columns = {
        'quantity': fields.float('Quantity',required=True),
        'wizard_id': fields.many2one('split.hop.dong', 'Parent Wizard',ondelete='cascade',required=True),
        'hd_mua_id': fields.many2one('hop.dong', 'Hợp đồng mua',required=True),
        'hd_ban_id': fields.many2one('hop.dong', 'Hợp đồng bán',required=True),
    }
    _defaults = {
        'quantity': 1.0,
    }

split_hop_dong_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
