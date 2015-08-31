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
    
    def _get_company(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr,uid,uid)
        return user.company_id.id or False
    
    def _get_user(self, cr, uid, ids, context=None):
        return uid
    
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
        'name': fields.char('Số Giấy kiểm dịch',size = 50, required = True),
        'loai_id': fields.many2one('loai.vat','Loài vật', required = True),
        'ngay_cap': fields.date('Ngày cấp', required = True),
        'ngay_kiem_tra': fields.date('Ngày', required = True),
        'ten_ho_id': fields.many2one('chan.nuoi','Hộ', required = True),
        'can_bo_id': fields.many2one('res.users','Cán bộ nhập máy'),
        'can_bo_ghi_so': fields.char('Cán bộ ghi sổ'),
        'tram_id': fields.many2one('tram.thu.y','Trạm'),
        'nguon_tinh_thanh_id': fields.many2one( 'tinh.tp','Tỉnh/Thành Phố', required = True),
        'nguon_phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)', required = True),
        'nguon_khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)', required = True),
        'nguon_quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)', required = True),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)', required = True),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)', required = True),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)', required = True),
        'loai':fields.selection([('nhap', 'Nhập'),('xuat', 'Xuất')],'Loại', readonly=True),
        'chitiet_loai_nx':fields.one2many('chi.tiet.loai.nhap.xuat','nhap_xuat_loai_id','Chi tiet'),
        'chitiet_da_tiem_phong':fields.one2many('chi.tiet.da.tiem.phong','nhap_xuat_tiemphong_id','Chi tiet'),
        'company_id': fields.many2one('res.company','Company'),
        'state':fields.selection([('draft', 'Nháp'),('done', 'Duyệt')],'Status', readonly=True),
        'trang_thai_id': fields.many2one('trang.thai','Trạng thái', readonly=True),
        'hien_an': fields.function(_get_hien_an, type='boolean', string='Hien/An'),
        'chinh_sua_rel': fields.related('trang_thai_id', 'chinh_sua', type="selection",
                selection=[('nhap', 'Nháp'),('in', 'Đang xử lý'), ('ch_duyet', 'Cấp Huyện Duyệt'), ('cc_duyet', 'Chi Cục Duyệt'), ('huy', 'Hủy bỏ')], 
                string="Chinh Sua", readonly=True, select=True),
                }
    _defaults = {
        'can_bo_id': _get_user,
        'company_id': _get_company,
        'trang_thai_id': get_trangthai_nhap,
                 }
    def onchange_tinh_thanh(self, cr, uid, ids, context=None):
        vals = {}
        vals = {'quan_huyen_id':False}
        return {'value': vals}            
    def onchange_quan_huyen(self, cr, uid, ids, context=None):
        vals = {}
        vals = {'phuong_xa_id':False}
        return {'value': vals}
    def onchange_phuong_xa(self, cr, uid, ids, context=None):
        vals = {}
        vals = {'khu_pho_id':False}
        return {'value': vals}
    def onchange_khu_pho(self, cr, uid, ids, context=None):
        vals = {}
        vals = {'ten_ho_id':False}
        return {'value': vals} 
    
    def onchange_nguon_tinh_thanh(self, cr, uid, ids, context=None):
        vals = {}
        vals = {'nguon_quan_huyen_id':False}
        return {'value': vals}            
    def onchange_nguon_quan_huyen(self, cr, uid, ids, context=None):
        vals = {}
        vals = {'nguon_phuong_xa_id':False}
        return {'value': vals}
    def onchange_nguon_phuong_xa(self, cr, uid, ids, context=None):
        vals = {}
        vals = {'nguon_khu_pho_id':False}
        return {'value': vals}
    
    def _check_so_luong(self, cr, uid, ids, context=None):
        for nhap_xuat in self.browse(cr, uid, ids, context=context):
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_loai from chi_tiet_loai_nhap_xuat
                where nhap_xuat_loai_id = %s
            '''%(nhap_xuat.id)
            cr.execute(sql)
            sl_loai = cr.dictfetchone()['sl_loai']
            for tiem in nhap_xuat.chitiet_da_tiem_phong:
                if tiem.so_luong>sl_loai:
                    if nhap_xuat.loai == 'nhap':
                        raise osv.except_osv(_('Warning!'),_('Số lượng loài %s đã tiêm phòng với loại bệnh %s không được nhiều hơn số lượng loài %s nhập vào')%(nhap_xuat.loai_id.name, tiem.name, nhap_xuat.loai_id.name))
                        return False
                    if nhap_xuat.loai == 'xuat':
                        raise osv.except_osv(_('Warning!'),_('Số lượng loài %s đã tiêm phòng với loại bệnh %s không được nhiều hơn số lượng loài %s xuất ra')%(nhap_xuat.loai_id.name, tiem.name, nhap_xuat.loai_id.name))
                        return False
        return True
        
    def _check_so_luong_xuat(self, cr, uid, ids, context=None):
        for nhap_xuat in self.browse(cr, uid, ids, context=context):
            if nhap_xuat.loai == 'xuat':
                for line in nhap_xuat.chitiet_loai_nx:
                    sql = '''
                        select tong_sl from chi_tiet_loai_line where co_cau_id in (select id from co_cau where chon_loai = %s and ten_ho_id = %s 
                        and trang_thai = 'new') and name = '%s'
                    '''%(nhap_xuat.loai_id.id, nhap_xuat.ten_ho_id.id, line.name)
                    cr.execute(sql)
                    sl = cr.dictfetchone()
                    tong_sl = sl and sl['tong_sl'] or 0
                    if line.so_luong > tong_sl:
                        raise osv.except_osv(_('Warning!'),_('Số lượng đàn %s trong hộ %s không đủ để xuất')%(line.name, nhap_xuat.ten_ho_id.name))
                        return False
        return True
    
    def _check_giay_kiem_dich(self, cr, uid, ids, context=None):
        for nhap_xuat in self.browse(cr, uid, ids, context=context):
            nhap_xuat_ids = self.search(cr,uid,[('id', '!=', nhap_xuat.id), ('name', '=', nhap_xuat.name)])
            if nhap_xuat_ids:
                raise osv.except_osv(_('Warning!'),_('Số giấy kiểm dịch không được trùng nhau'))
                return False
        return True
         
    _constraints = [
        (_check_so_luong, 'Identical Data', []),
        (_check_so_luong_xuat, 'Identical Data', []),
        (_check_giay_kiem_dich, 'Identical Data', []),
    ]   
    
    def bt_duyet(self, cr, uid, ids, context=None):
        chi_tiet_loai =[]
        co_cau_obj = self.pool.get('co.cau')
        user = self.pool.get('res.users').browse(cr,uid,uid)
        
        for line in self.browse(cr, uid, ids, context=context):
            if line.loai == 'nhap':
                for loai in line.chitiet_loai_nx:
                    chi_tiet_loai.append((0,0,{
                    'name':loai.name,
                    'so_luong':loai.so_luong,                           
                                               }))
                if line.trang_thai_id.stt == 1 and user.company_id.cap == 'huyen':
                    sql = '''
                        select id from trang_thai where stt = 2
                    '''
                    cr.execute(sql)
                    trang = cr.dictfetchone()
                    self.write(cr,uid,ids,{
                                           'trang_thai_id': trang and trang['id'] or False,
                                           })
                elif line.trang_thai_id.stt == 1 and user.company_id.cap == 'chi_cuc':
                    sql = '''
                        select id from trang_thai where stt = 3
                    '''
                    cr.execute(sql)
                    trang = cr.dictfetchone()
                    self.write(cr,uid,ids,{
                                           'trang_thai_id': trang and trang['id'] or False,
                                           })
                    value ={
                    'chon_loai':line.loai_id.id,
                    'can_bo_ghi_so_id':line.can_bo_id and line.can_bo_id.id or False,
                    'ngay_ghi_so':line.ngay_cap or False,
                    'tang_giam':'a',
                    'ly_do':u'Nhập từ số giấy kiểm dịch'+' '+ line.name,
                    'quan_huyen_id':line.quan_huyen_id and line.quan_huyen_id.id or False,
                    'phuong_xa_id':line.phuong_xa_id and line.phuong_xa_id.id or False,
                    'khu_pho_id':line.khu_pho_id and line.khu_pho_id.id or False,
                    'ten_ho_id':line.ten_ho_id and line.ten_ho_id.id or False,
                    'chitiet_loai':chi_tiet_loai,
                    'trang_thai':'new',
                    'company_id':line.company_id.id,
                    'nhap_xuat_id': line.id,
                    'trang_thai_id': trang and trang['id'] or False,
                            }
                    co_cau_id = co_cau_obj.create(cr,uid,value)
                    co_cau_obj.bt_duyet(cr,uid,[co_cau_id])
                elif line.trang_thai_id.stt == 2 and user.company_id.cap == 'chi_cuc':
                    sql = '''
                        select id from trang_thai where stt = 3
                    '''
                    cr.execute(sql)
                    trang = cr.dictfetchone()
                    self.write(cr,uid,ids,{
                                           'trang_thai_id': trang and trang['id'] or False,
                                           })
                    value ={
                    'chon_loai':line.loai_id.id,
                    'can_bo_ghi_so_id':line.can_bo_id and line.can_bo_id.id or False,
                    'ngay_ghi_so':line.ngay_cap or False,
                    'tang_giam':'a',
                    'ly_do':u'Nhập từ số giấy kiểm dịch'+' '+ line.name,
                    'quan_huyen_id':line.quan_huyen_id and line.quan_huyen_id.id or False,
                    'phuong_xa_id':line.phuong_xa_id and line.phuong_xa_id.id or False,
                    'khu_pho_id':line.khu_pho_id and line.khu_pho_id.id or False,
                    'ten_ho_id':line.ten_ho_id and line.ten_ho_id.id or False,
                    'chitiet_loai':chi_tiet_loai,
                    'trang_thai':'new',
                    'company_id':line.company_id.id,
                    'nhap_xuat_id': line.id,
                    'trang_thai_id': trang and trang['id'] or False,
                            }
                    co_cau_id = co_cau_obj.create(cr,uid,value)
                    co_cau_obj.bt_duyet(cr,uid,[co_cau_id])
            elif line.loai == 'xuat':
                for loai in line.chitiet_loai_nx:
                    chi_tiet_loai.append((0,0,{
                    'name':loai.name,
                    'so_luong':loai.so_luong,                           
                                               }))
                
                if line.trang_thai_id.stt == 1 and user.company_id.cap == 'huyen':
                    sql = '''
                        select id from trang_thai where stt = 2
                    '''
                    cr.execute(sql)
                    trang = cr.dictfetchone()
                    self.write(cr,uid,ids,{
                                           'trang_thai_id': trang and trang['id'] or False,
                                           })
                elif line.trang_thai_id.stt == 1 and user.company_id.cap == 'chi_cuc':
                    sql = '''
                        select id from trang_thai where stt = 3
                    '''
                    cr.execute(sql)
                    trang = cr.dictfetchone()
                    self.write(cr,uid,ids,{
                                           'trang_thai_id': trang and trang['id'] or False,
                                           })
                    value ={
                    'chon_loai':line.loai_id.id,
                    'can_bo_ghi_so_id':line.can_bo_id and line.can_bo_id.id or False,
                    'ngay_ghi_so':line.ngay_cap or False,
                    'tang_giam':'b',
                    'ly_do':u'Xuất từ số giấy kiểm dịch'+' '+ line.name,
                    'quan_huyen_id':line.quan_huyen_id and line.quan_huyen_id.id or False,
                    'phuong_xa_id':line.phuong_xa_id and line.phuong_xa_id.id or False,
                    'khu_pho_id':line.khu_pho_id and line.khu_pho_id.id or False,
                    'ten_ho_id':line.ten_ho_id and line.ten_ho_id.id or False,
                    'chitiet_loai':chi_tiet_loai,
                    'trang_thai':'new',
                    'company_id':line.company_id.id,
                    'nhap_xuat_id': line.id,
                    'trang_thai_id': trang and trang['id'] or False,
                        }
                    co_cau_id = co_cau_obj.create(cr,uid,value)
                    co_cau_obj.bt_duyet(cr,uid,[co_cau_id])
                elif line.trang_thai_id.stt == 2 and user.company_id.cap == 'chi_cuc':
                    sql = '''
                        select id from trang_thai where stt = 3
                    '''
                    cr.execute(sql)
                    trang = cr.dictfetchone()
                    self.write(cr,uid,ids,{
                                           'trang_thai_id': trang and trang['id'] or False,
                                           })
                    value ={
                    'chon_loai':line.loai_id.id,
                    'can_bo_ghi_so_id':line.can_bo_id and line.can_bo_id.id or False,
                    'ngay_ghi_so':line.ngay_cap or False,
                    'tang_giam':'b',
                    'ly_do':u'Xuất từ số giấy kiểm dịch'+' '+ line.name,
                    'quan_huyen_id':line.quan_huyen_id and line.quan_huyen_id.id or False,
                    'phuong_xa_id':line.phuong_xa_id and line.phuong_xa_id.id or False,
                    'khu_pho_id':line.khu_pho_id and line.khu_pho_id.id or False,
                    'ten_ho_id':line.ten_ho_id and line.ten_ho_id.id or False,
                    'chitiet_loai':chi_tiet_loai,
                    'trang_thai':'new',
                    'company_id':line.company_id.id,
                    'nhap_xuat_id': line.id,
                    'trang_thai_id': trang and trang['id'] or False,
                        }
                    co_cau_id = co_cau_obj.create(cr,uid,value)
                    co_cau_obj.bt_duyet(cr,uid,[co_cau_id])
        return True
    def onchange_chon_loai(self, cr, uid, ids, loai_id = False, context=None):
        chi_tiet= []
        tiem_phong = []
        for nhap_xuat in self.browse(cr,uid,ids):
            sql = '''
                delete from chi_tiet_loai_nhap_xuat where nhap_xuat_loai_id = %s
            '''%(nhap_xuat.id)
            cr.execute(sql)
            sql = '''
                delete from chi_tiet_da_tiem_phong where nhap_xuat_tiemphong_id = %s
            '''%(nhap_xuat.id)
            cr.execute(sql)
        if loai_id:
            loai = self.pool.get('loai.vat').browse(cr,uid,loai_id)    
            for line_loaivat in loai.chitiet_loaivat:
                chi_tiet.append((0,0,{
                                      'name': line_loaivat.name
                                      }))
            for line_loaibenh in loai.chitiet_loaibenh:
                tiem_phong.append((0,0,{
                                      'name': line_loaibenh.name
                                      }))
        return {'value': {'chitiet_loai_nx': chi_tiet,
                          'chitiet_da_tiem_phong': tiem_phong,
                          }}
    
nhap_xuat_canh_giasuc()

class chi_tiet_loai_nhap_xuat(osv.osv):
    _name = "chi.tiet.loai.nhap.xuat"
    _columns = {
        'nhap_xuat_loai_id': fields.many2one('nhap.xuat.canh.giasuc','Nhap Xuat', ondelete = 'cascade'),
        'name': fields.char('Thông tin', readonly = True),
        'so_luong': fields.integer('Số lượng'),
                }
chi_tiet_loai_nhap_xuat()

class chi_tiet_da_tiem_phong(osv.osv):
    _name = "chi.tiet.da.tiem.phong"
    _columns = {
        'nhap_xuat_tiemphong_id': fields.many2one('nhap.xuat.canh.giasuc','Nhap Xuat', ondelete = 'cascade'),
        'name': fields.char('Loại bệnh', readonly = True),
        'so_luong': fields.integer('Số lượng'),
                }
chi_tiet_da_tiem_phong()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
