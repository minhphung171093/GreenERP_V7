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
        'tram_id': fields.many2one('res.company','Trạm'),
        'email': fields.char( 'Email',size = 50),
        'dien_thoai': fields.char( 'Điện thoại',size = 50),
        'user_id': fields.many2one( 'res.users','Người dùng',required = True),
                }
can_bo()

class trang_thai(osv.osv):
    _name = "trang.thai"
    _order = "stt"
    _columns = {
        'name': fields.char('Trạng thái', size=100,required = True),
        'stt': fields.integer('STT',required = True),
        'chinh_sua': fields.selection([('nhap', 'Nháp'),('in', 'Đang xử lý'), ('duyet', 'Duyệt'), ('huy', 'Hủy bỏ')],'Chinh Sua'),
                }
trang_thai()

class res_users(osv.osv):
    _inherit = "res.users"
    _columns = {
        'dien_thoai': fields.char( 'Điện thoại',size = 50),
                }
res_users()

class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'cap': fields.selection([('xa', 'Xã'),('huyen', 'Huyện'), ('chi_cuc', 'Chi Cục')],'Cấp'),
                }
res_company()

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
        'ds_canbo_line':fields.one2many('can.bo','tram_id','Chi tiet'),
                }
tram_thu_y()

class tinh_tp(osv.osv):
    _name = "tinh.tp"
    _columns = {
        'name': fields.char('Thành Phố',size = 50, required = True),
                }
tinh_tp()
class loai_vat(osv.osv):
    _name = "loai.vat"
    _columns = {
        'ma_loai': fields.char('Mã loài',size = 50, required = True),
        'name': fields.char('Tên loài',size = 50, required = True),
        'thuoc_loai': fields.selection((('a','Động vật thường'), ('b','Động vật hoang dã')),'Thuộc'),
        'thoi_gian': fields.integer('thời gian nuôi (tháng)'),
        'chitiet_loaivat':fields.one2many('chi.tiet.loai.vat','loai_id','Chi tiet'),
        'chitiet_loaibenh':fields.one2many('chi.tiet.loai.benh','loai_id','Chi tiet'),
                }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_loai_id'):
            bosua_model, bosua_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'green_erp_ccty_base', 'loaivat_bosua')
            self.pool.get('loai.vat').check_access_rule(cr, uid, [bosua_id], 'read', context = context)
            sql = '''
                select id from loai_vat
                where id != %s
            '''%(bosua_id)
            cr.execute(sql)
            loaivat_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',loaivat_ids)]
        return super(loai_vat, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
loai_vat()

class chi_tiet_loai_vat(osv.osv):
    _name = "chi.tiet.loai.vat"
    _columns = {
        'loai_id': fields.many2one('loai.vat','Loai vat',ondelete = 'cascade'),
        'name': fields.char('Thông tin',size = 50),
                }
chi_tiet_loai_vat()

class chi_tiet_loai_benh(osv.osv):
    _name = "chi.tiet.loai.benh"
    _columns = {
        'loai_id': fields.many2one('loai.vat','Loai vat',ondelete = 'cascade'),
        'name': fields.char('Loại bệnh',size = 50),
                }
chi_tiet_loai_benh()

class chan_nuoi(osv.osv):
    _name = "chan.nuoi"
    def get_trangthai_nhap(self, cr, uid, ids, context=None):
        sql = '''
            select id from trang_thai where stt = 1
        '''
        cr.execute(sql)
        trang = cr.dictfetchone()
        return trang and trang['id'] or False
    
    def _get_hien_an(self, cr, uid, ids, name, arg, context=None):        
        result = {}
        
        user = self.pool.get('res.users').browse(cr,uid,uid)
        for nhap_xuat in self.browse(cr,uid,ids):
            result[nhap_xuat.id] = False  
            if nhap_xuat.trang_thai_id.stt == 1 and user.company_id.cap in ['huyen', 'chi_cuc']:
                result[nhap_xuat.id] = True
            elif nhap_xuat.trang_thai_id.stt == 2 and user.company_id.cap in ['chi_cuc']:
                result[nhap_xuat.id] = True    
        return result
    _columns = {
        'ma_ho': fields.char('Mã hộ',size = 50, required = True),
        'name': fields.char('Tên hộ',size = 50, required = True),
        'so_nha': fields.char('Số nhà',size = 50),
        'ngay_cap': fields.date('Thời gian cấp'),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)'),
        'khu_pho_id': fields.many2one('khu.pho','Khu phố (ấp)'),
        'quan_huyen_id': fields.many2one('quan.huyen','Quận (huyện)'),
        'dien_tich': fields.char('Diện tích đất'),
        'trang_thai_id': fields.many2one('trang.thai','Trạng thái', readonly=True),
        'hien_an': fields.function(_get_hien_an, type='boolean', string='Hien/An'),
        'chinh_sua_rel': fields.related('trang_thai_id', 'chinh_sua', type="selection",
                selection=[('nhap', 'Nháp'),('in', 'Đang xử lý'), ('duyet', 'Duyệt'), ('huy', 'Hủy bỏ')], 
                string="Chinh Sua", readonly=True, select=True),
                }
    _defaults = {
        'trang_thai_id': get_trangthai_nhap,
                 }
    def bt_duyet(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr,uid,uid)
        for line in self.browse(cr, uid, ids, context=context):
            if line.trang_thai_id.stt == 1 and user.company_id.cap == 'huyen':
                sql = '''
                    select id from trang_thai where stt = 2
                '''
                cr.execute(sql)
                self.write(cr,uid,ids,{
                                       'trang_thai_id': cr.dictfetchone()['id'] or False
                                       })
            elif line.trang_thai_id.stt == 1 and user.company_id.cap == 'chi_cuc':
                sql = '''
                    select id from trang_thai where stt = 3
                '''
                cr.execute(sql)
                self.write(cr,uid,ids,{
                                       'trang_thai_id': cr.dictfetchone()['id'] or False
                                       })
                
            elif line.trang_thai_id.stt == 2 and user.company_id.cap == 'chi_cuc':
                sql = '''
                    select id from trang_thai where stt = 3
                '''
                cr.execute(sql)
                self.write(cr,uid,ids,{
                                       'trang_thai_id': cr.dictfetchone()['id'] or False
                                       })
        return True
chan_nuoi()
class phuong_xa(osv.osv):
    _name = "phuong.xa"
    _columns = {
        'name': fields.char('Phường (xã)',size = 50, required = True),
         'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)'),
                }
phuong_xa()
class quan_huyen(osv.osv):
    _name = "quan.huyen"
    _columns = {
        'name': fields.char('Quận (huyện)',size = 50, required = True),
                }
quan_huyen()
class khu_pho(osv.osv):
    _name = "khu.pho"
    _columns = {
        'name': fields.char('Khu phố (ấp)',size = 50, required = True),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)'),
                }
khu_pho()
class loai_hang(osv.osv):
    _name = "loai.hang"
    _columns = {
        'name': fields.char('Loại hàng',size = 50, required = True),
        'don_vi': fields.char('Đơn vị tính',size = 50),
                }
loai_hang()
class loai_vacxin(osv.osv):
    _name = "loai.vacxin"
    _columns = {
        'ma_loai': fields.char('Mã loại vacxin',size = 50, required = True),
        'name': fields.char('Tên loại vacxin',size = 50),
                }
loai_vacxin()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
