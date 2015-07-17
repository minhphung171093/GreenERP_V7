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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
