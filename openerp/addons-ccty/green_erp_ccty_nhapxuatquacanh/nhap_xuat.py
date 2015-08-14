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


class nhap_xuat(osv.osv):
    _name = "nhap.xuat"
    _columns = {
        'name': fields.char('Giấy kiểm dịch',size = 50, required = True),
        'chu_hang': fields.char('Họ tên chủ cơ sở',size = 50, required = True),
        'loai_hinh': fields.selection((('a','Nhập'), ('b','Xuất'), ('c','quá cảnh')),'Loại hình'),
        'loai_hang': fields.many2one('loai.hang','Loại hàng'),
        'ngay_nhap_xuat': fields.date('Ngày nhập xuất'),
        'soluong': fields.char('Số lượng',size = 50),
        'noi_xuat_phat': fields.char('Nơi xuất phát',size = 50),
        'noi_nhan': fields.char('Nơi nhận hàng',size = 50),
        'so_xe': fields.char('Số xe',size = 50),
                }
nhap_xuat()

class nhap_xuat_canh_giasuc(osv.osv):
    _name = "nhap.xuat.canh.giasuc"
    _columns = {
        'name': fields.char('Số Giấy kiểm dịch',size = 50, required = True),
        'loai_id': fields.many2one('loai.vat','Loài vật', required = True),
        'ngay_cap': fields.date('Ngày cấp'),
        'ten_ho_id': fields.many2one('chan.nuoi','Hộ'),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)'),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)'),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)'),
        'loai':fields.selection([('nhap', 'Nhập'),('xuất', 'Xuất')],'Loại', readonly=True),
        'chitiet_loai_nx':fields.one2many('chi.tiet.loai.nhap.xuat','nhap_xuat_loai_id','Chi tiet'),
        'chitiet_da_tiem_phong':fields.one2many('chi.tiet.da.tiem.phong','nhap_xuat_tiemphong_id','Chi tiet'),
                }
nhap_xuat_canh_giasuc()

class chi_tiet_loai_nhap_xuat(osv.osv):
    _name = "chi.tiet.loai.nhap.xuat"
    _columns = {
        'nhap_xuat_loai_id': fields.many2one('nhap.xuat.canh.giasuc','Nhap Xuat', ondelete = 'cascade'),
        'name': fields.char('Thông tin', readonly = True),
        'so_luong': fields.float('Số lượng'),
                }
chi_tiet_loai_nhap_xuat()

class chitiet_da_tiem_phong(osv.osv):
    _name = "chi.tiet.da.tiem.phong"
    _columns = {
        'nhap_xuat_tiemphong_id': fields.many2one('nhap.xuat.canh.giasuc','Nhap Xuat', ondelete = 'cascade'),
        'name': fields.char('Loại bệnh', readonly = True),
        'so_luong': fields.float('Số lượng'),
                }
chitiet_da_tiem_phong()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
