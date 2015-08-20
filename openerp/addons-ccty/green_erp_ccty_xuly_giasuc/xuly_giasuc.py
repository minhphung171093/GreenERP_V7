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


class xuly_giasuc(osv.osv):
    _name = "xuly.giasuc"
    
    def _get_company(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr,uid,uid)
        return user.company_id.id or False
    
    def get_trangthai_nhap(self, cr, uid, ids, context=None):
        sql = '''
            select id from trang_thai where stt = 1
        '''
        cr.execute(sql)
        trang = cr.dictfetchone()['id'] or False
        return trang
    
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
        'name': fields.char('Mã số gia súc nhiễm bệnh',size = 50, required = True),
        'loai_id': fields.many2one('loai.vat','Loài vật', required = True),
        'ngay': fields.date('Ngày', required = True),
        'ten_ho_id': fields.many2one('chan.nuoi','Hộ', required = True),
        'can_bo_id': fields.many2one('res.users','Cán bộ'),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)'),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)'),
        'quan_huyen_id': fields.many2one('quan.huyen','Quận (huyện)'),
        'chitiet_loai_xuly':fields.one2many('chitiet.loai.xuly','xuly_giasuc_id','Chi tiet'),
        'company_id': fields.many2one('res.company','Trạm'),
        'trang_thai_id': fields.many2one('trang.thai','Trạng thái', readonly=True),
        'hien_an': fields.function(_get_hien_an, type='boolean', string='Hien/An'),
                }
    _defaults = {
        'company_id': _get_company,
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
    
    def onchange_chon_loai(self, cr, uid, ids, loai_id = False, context=None):
        chi_tiet= []
        for xu_ly in self.browse(cr,uid,ids):
            sql = '''
                delete from chitiet_loai_xuly where xuly_giasuc_id = %s
            '''%(xu_ly.id)
            cr.execute(sql)
        if loai_id:
            loai = self.pool.get('loai.vat').browse(cr,uid,loai_id)    
            for line_loaivat in loai.chitiet_loaivat:
                chi_tiet.append((0,0,{
                                      'name': line_loaivat.name
                                      }))
        return {'value': {'chitiet_loai_xuly': chi_tiet,
                          }}
xuly_giasuc()

class chitiet_loai_xuly(osv.osv):
    _name = "chitiet.loai.xuly"
    _columns = {
        'xuly_giasuc_id': fields.many2one('xuly.giasuc','Xu ly gia suc', ondelete = 'cascade'),
        'name': fields.char('Thông tin', readonly = True),
        'so_luong': fields.float('Số lượng'),
        'ly_do': fields.char('Lý do bệnh',size = 200),
        'ket_qua_xn': fields.char('Kết quả xét nghiệm',size = 200),
        'bien_phap': fields.char('Biện pháp xử lý',size = 200),
        'vacxin_id': fields.many2one('loai.vacxin','Thuốc sử dụng'),
        'lieu_luong': fields.float('Liều lượng'),
        'lieu_trinh': fields.char('Liệu trình',size = 200),
        'ket_qua_dieu_tri': fields.char('Kết quả điều trị',size = 200),
                }
chitiet_loai_xuly()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
