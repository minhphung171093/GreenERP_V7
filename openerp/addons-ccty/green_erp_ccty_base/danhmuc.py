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
import os
# from xlrd import open_workbook,xldate_as_tuple
from openerp import modules
base_path = os.path.dirname(modules.get_module_path('green_erp_ccty_base'))

class can_bo(osv.osv):
    _name = "can.bo"
    _columns = {
        'name': fields.char('Họ tên', size=30,required = True),
        'don_vi_id': fields.many2one( 'don.vi','Đơn vị'),
        'email': fields.char( 'Email',size = 50),
        'dien_thoai': fields.char( 'Điện thoại',size = 50),
                }
can_bo()
class don_vi(osv.osv):
    _name = "don.vi"
    _columns = {
        'name': fields.char('Đơn vị', size=30,required = True),
        
                }
don_vi()
class tram_thu_y(osv.osv):
    _name = "tram.thu.y"
    _columns = {
        'name': fields.char('Tên trạm', size=30,required = True),
        'thanh_pho_id': fields.many2one( 'tinh.tp','Tỉnh'),
        'dia_chi': fields.char('Địa chỉ', size=200),
        'email': fields.char( 'Email',size = 50),
        'dien_thoai': fields.char( 'Điện thoại',size = 50),
        'tram_truong_id': fields.many2one( 'can.bo','Trạm trưởng'),
        'toa_do_x': fields.char( 'Tọa độ X',size = 10),
        'toa_do_y': fields.char( 'Tọa độ Y',size = 10),
                }
tram_thu_y()
class tinh_tp(osv.osv):
    _name = "tinh.tp"
    _columns = {
        'name': fields.char('Thành Phố',size = 50),
                }
tinh_tp()
class loai_vat(osv.osv):
    _name = "loai.vat"
    _columns = {
        'ma_loai': fields.char('Mã loài',size = 50),
        'name': fields.char('Tên loài',size = 50),
        'thuoc_loai': fields.selection((('a','Động vật thường'), ('b','Động vật hoang dã')),'Thuộc',required = True),
        'thoi_gian': fields.integer('thời gian nuôi (tháng)'),
                }
loai_vat()
class chan_nuoi(osv.osv):
    _name = "chan.nuoi"
    _columns = {
        'name': fields.char('Tên cơ sở',size = 50),
        'ho_ten': fields.char('Họ tên chủ cơ sở',size = 50),
        'ma_so': fields.char('Mã số',size = 50),
        'dia_chi': fields.char('Địa chỉ',size = 50),
        'ngay_lap': fields.date('Ngày lập sổ'),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)',domain="[('quan_huyen_id','=',quan_huyen_id)]"),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)',domain="[('phuong_xa_id','=',phuong_xa_id)]"),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)'),
                }
chan_nuoi()
class phuong_xa(osv.osv):
    _name = "phuong.xa"
    _columns = {
        'name': fields.char('Phường (xã)',size = 50),
         'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)'),
                }
phuong_xa()
class quan_huyen(osv.osv):
    _name = "quan.huyen"
    _columns = {
        'name': fields.char('Quận (huyện)',size = 50),
                }
quan_huyen()
class khu_pho(osv.osv):
    _name = "khu.pho"
    _columns = {
        'name': fields.char('Khu phố (ấp)',size = 50),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)'),
                }
khu_pho()
class loai_hang(osv.osv):
    _name = "loai.hang"
    _columns = {
        'name': fields.char('Loại hàng',size = 50),
        'don_vi': fields.char('Đơn vị tính',size = 50),
                }
loai_hang()
class loai_vacxin(osv.osv):
    _name = "loai.vacxin"
    _columns = {
        'ma_loai': fields.char('Mã loại vacxin',size = 50),
        'name': fields.char('Tên loại vacxin',size = 50),
                }
loai_hang()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
