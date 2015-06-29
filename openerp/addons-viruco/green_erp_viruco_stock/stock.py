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
        'lotrinh_tu_id':fields.many2one('lo.trinh','Lộ trình từ'),
        'lotrinh_den_id':fields.many2one('lo.trinh','Lộ trình đến'),
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
        'lotrinh_tu_id':fields.many2one('lo.trinh','Lộ trình từ'),
        'lotrinh_den_id':fields.many2one('lo.trinh','Lộ trình đến'),
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
        'lotrinh_tu_id':fields.many2one('lo.trinh','Lộ trình từ'),
        'lotrinh_den_id':fields.many2one('lo.trinh','Lộ trình đến'),
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
        'picking_ids': fields.many2many('stock.picking.in', 'move_picking_ref', 'move_id', 'picking_id', 'Phiếu nhập kho'),
        'ghichu':fields.char('Ghi chú'),
    }
stock_move()    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
