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


class sale_arbitration(osv.osv):
    _name = 'sale.arbitration'
    _columns = {
        'name':fields.char('Name',size=1024,required=True),
        'description': fields.text('Description'),
    }
    
sale_arbitration()
class chatluong_sanpham(osv.osv):
    _name = 'chatluong.sanpham'
    _columns = {
        'name':fields.char('Tên',size=1024,required=True),
        'description': fields.text('Ghi chú'),
    }
    
chatluong_sanpham()
class quycach_donggoi(osv.osv):
    _name = 'quycach.donggoi'
    _columns = {
        'name':fields.char('Tên',size=1024,required=True),
        'description': fields.text('Ghi chú'),
    }
    
quycach_donggoi()
class quycach_baobi(osv.osv):
    _name = 'quycach.baobi'
    _columns = {
        'name':fields.char('Tên',size=1024,required=True),
        'description': fields.text('Ghi chú'),
    }
    
quycach_baobi()
class nha_sanxuat(osv.osv):
    _name = 'nha.sanxuat'
    _columns = {
        'name':fields.char('Tên nhà sản xuất',size=1024,required=True),
        'description': fields.text('Ghi chú'),
    }
    
nha_sanxuat()

class dieukien_giaohang(osv.osv):
    _name = 'dieukien.giaohang'
    _columns = {
        'name':fields.char('Điều kiện',size=1024,required=True),
        'description': fields.text('Ghi chú'),
    }
    
dieukien_giaohang()

class hinhthuc_giaohang(osv.osv):
    _name = 'hinhthuc.giaohang'
    _columns = {
        'name':fields.char('Tên',size=1024,required=True),
        'description': fields.text('Ghi chú'),
    }
    
hinhthuc_giaohang()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
