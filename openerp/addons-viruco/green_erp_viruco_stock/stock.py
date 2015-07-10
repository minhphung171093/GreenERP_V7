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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
