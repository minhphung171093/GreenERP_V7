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
# import os
# from xlrd import open_workbook,xldate_as_tuple
# from openerp import modules
# base_path = os.path.dirname(modules.get_module_path('green_erp_viruco_base'))


# class res_country_state(osv.osv):
#     _inherit = "res.country.state"
#     _columns = {
#     }
#     def init(self, cr):
#         country_obj = self.pool.get('res.country')
#         wb = open_workbook(base_path + '/green_erp_viruco_base/data/TinhTP.xls')
#         for s in wb.sheets():
#             if (s.name =='Sheet1'):
#                 for row in range(1,s.nrows):
#                     val0 = s.cell(row,0).value
#                     val1 = s.cell(row,1).value
#                     val2 = s.cell(row,2).value
#                     country_ids = country_obj.search(cr, 1, [('code','=',val2)])
#                     if country_ids:
#                         state_ids = self.search(cr, 1, [('name','=',val1),('code','=',val0),('country_id','in',country_ids)])
#                         if not state_ids:
#                             self.create(cr, 1, {'name': val1,'code':val0,'country_id':country_ids[0]})
#          
# res_country_state()

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

class lo_trinh(osv.osv):
    _name = 'lo.trinh'
    _columns = {
        'name':fields.char('Name',size=1024,required=True),
        'diadiem_tu':fields.char('Từ',size=1024,required=True),
        'diadiem_den':fields.char('Đến',size=1024,required=True),
        'description': fields.text('Description'),
    }
    
lo_trinh()
class cang_donghang(osv.osv):
    _name = 'cang.donghang'
    _columns = {
        'name':fields.char('Name',size=1024,required=True),
        'description': fields.text('Description'),
    }
    
cang_donghang()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
