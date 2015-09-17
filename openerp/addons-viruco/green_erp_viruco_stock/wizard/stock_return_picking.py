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

class stock_return_picking(osv.osv):
    _inherit = 'stock.return.picking'

    _columns = {
        'return_type': fields.selection([('none', 'Normal'), ('internal','Return Internal'), ('customer', 'Return from Customer'), ('supplier', 'Return to Supplier')], 'Type', required=True, readonly=True, help="Type specifies whether the Picking has been returned or not."),
        'note':        fields.text('Notes'),
        'location_id': fields.many2one('stock.location', 'Location', help='If a location is chosen the destination location for customer return (or origin for supplier return) is forced for all moves.'),
        'journal_id':fields.many2one('stock.journal', 'Stock Journal',required=True,),
        'option':fields.boolean('Tranfer Product'),
    }
    _defaults = {
#         'return_type': lambda self, cr, uid, context: self._get_return_type(cr, uid, context=context),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(stock_return_picking, self).default_get(cr, uid, fields, context)
        record_id = context and context.get('active_id', False) or False
        pick_obj = self.pool.get('stock.picking')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        if pick and pick.sale_id and pick.sale_id:
            warehouse = pick.sale_id.shop_id and pick.sale_id.shop_id.warehouse_id
            res.update({'location_id': warehouse and warehouse.lot_return_id and warehouse.lot_return_id.id or False})
        
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
        else:
            new_type = 'internal'
            journal_id =  [pick.stock_journal_id.id] or False
            location_id = pick.location_id and pick.location_id.id or False
            location_dest_id = pick.location_dest_id and pick.location_dest_id.id or False
        
        seq_obj_name = 'stock.picking.' + new_type
        # SHOULD USE ir_sequence.next_by_code() or ir_sequence.next_by_id()
        new_pick_name = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
        new_picking_vals = {'name': _('%s-%s-return') % (new_pick_name, pick.name),
                            'move_lines': [],
                            'state':'draft',
                            'type': new_type,
                            'return': data['return_type'],
                            'note': data['note'],
                            'origin':pick.name or '',
                            'date':date_cur,
                            'invoice_state': data['invoice_state'], 
                            'stock_journal_id':journal_id and journal_id[0] or False,
                            'location_id':location_dest_id,
                            'location_dest_id':location_id,}
        new_picking = pick_obj.copy(cr, uid, pick.id, new_picking_vals)
        #Hung them chuc nang doi san pham.
        if pick.type =='out' and pick.sale_id and return_picking_obj.option:
            new_id = pick_obj.copy(cr, uid, pick.id, {
                                        'name': pick.name + '-ship',
                                        'move_lines': [], 
                                        'state':'draft', 
                                        'type': 'out',
                                        'date':date_cur,
                                        'date_done':False, 
                                        'invoice_state': data['invoice_state'], })
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
                                    'note': data['note']}
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
