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
    _columns = {
        'nguoi_denghi_id':fields.many2one('res.users','Người đề nghị'),
        'donvi_vanchuyen':fields.many2one('res.partner','Đơn vị vận chuyển'),
        'lotrinh_tu_id':fields.many2one('lo.trinh','Lộ trình từ'),
        'lotrinh_den_id':fields.many2one('lo.trinh','Lộ trình đến'),
        'dongia_vanchuyen':fields.float('Đơn giá vận chuyển'),
    }
     
stock_picking()
class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    _columns = {
        'nguoi_denghi_id':fields.many2one('res.users','Người đề nghị'),
        'donvi_vanchuyen':fields.many2one('res.partner','Đơn vị vận chuyển'),
        'lotrinh_tu_id':fields.many2one('lo.trinh','Lộ trình từ'),
        'lotrinh_den_id':fields.many2one('lo.trinh','Lộ trình đến'),
        'dongia_vanchuyen':fields.float('Đơn giá vận chuyển'),
    }
     
stock_picking_in()
class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    _columns = {
        'nguoi_denghi_id':fields.many2one('res.users','Người đề nghị'),
        'donvi_vanchuyen':fields.many2one('res.partner','Đơn vị vận chuyển'),
        'lotrinh_tu_id':fields.many2one('lo.trinh','Lộ trình từ'),
        'lotrinh_den_id':fields.many2one('lo.trinh','Lộ trình đến'),
        'dongia_vanchuyen':fields.float('Đơn giá vận chuyển'),
    }
     
stock_picking_out()
class stock_move(osv.osv):
    _inherit = "stock.move"
    _columns = {
        'chatluong_id':fields.many2one('chatluong.sanpham','Chất lượng'),
        'quycach_donggoi_id':fields.many2one('quycach.donggoi','Quy cách đóng gói'),
#         'hop_dong_mua_id':fields.many2one('hop.dong','Hợp đồng mua'),
        'hop_dong_ban_id':fields.many2one('hop.dong','Hợp đồng bán'),
    }
stock_move()    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
