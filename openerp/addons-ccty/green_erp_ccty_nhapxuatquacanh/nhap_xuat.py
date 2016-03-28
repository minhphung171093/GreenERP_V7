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
        'loai_id': fields.many2one('loai.vat','Loài vật', required = True, ondelete = 'restrict'),
        'ngay_cap': fields.date('Ngày cấp', required = True),
        'ngay_kiem_tra': fields.date('Ngày', required = True),
        'ten_ho_id': fields.many2one('chan.nuoi','Hộ', required = True),
        'can_bo_id': fields.many2one('res.users','Cán bộ nhập máy'),
        'can_bo_ghi_so': fields.char('Cán bộ ghi sổ'),
        'loai_ho_id': fields.many2one('loai.ho','Loại hộ'),
        'tram_id': fields.many2one('tram.thu.y','Trạm'),
        'nguon_tinh_thanh_id': fields.many2one( 'tinh.tp','Tỉnh/Thành Phố'),
        'nguon_phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)', required = False),
        'nguon_khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)', required = False),
        'nguon_quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)', required = False),
        'bien_so_xe': fields.char('Biển số xe',size = 50),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)', required = True),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)', required = True),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)', required = True),
        'loai':fields.selection([('nhap', 'Nhập'),('xuat', 'Xuất')],'Loại'),
        'chitiet_loai_nx':fields.one2many('chi.tiet.loai.nhap.xuat','nhap_xuat_loai_id','Chi tiet'),
        'chitiet_da_tiem_phong':fields.one2many('chi.tiet.da.tiem.phong','nhap_xuat_tiemphong_id','Chi tiet'),
        'company_id': fields.many2one('res.company','Company'),
        'state':fields.selection([('draft', 'Nháp'),('done', 'Duyệt')],'Status', readonly=True),
        'trang_thai_id': fields.many2one('trang.thai','Trạng thái', readonly=True),
        'hien_an': fields.function(_get_hien_an, type='boolean', string='Hien/An'),
        'chinh_sua_rel': fields.related('trang_thai_id', 'chinh_sua', type="selection",
                selection=[('nhap', 'Nháp'),('in', 'Đang xử lý'), ('ch_duyet', 'Cấp Huyện Duyệt'), ('cc_duyet', 'Chi Cục Duyệt'), ('huy', 'Hủy bỏ')], 
                string="Chinh Sua", readonly=True, select=True),
        'chan_nuoi_id': fields.many2one('chan.nuoi','Hộ ban đầu', ondelete='cascade'),
                }
    _defaults = {
        'can_bo_id': _get_user,
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
    
    def onchange_ten_ho_id(self, cr, uid, ids, ten_ho_id = False, context=None):
        res = {'value':{
                        'loai_ho_id':False,
                      }
               }
        if ten_ho_id:
            ho = self.pool.get('chan.nuoi').browse(cr,uid,ten_ho_id)
            res['value'].update({
                        'loai_ho_id':ho.loai_ho_id and ho.loai_ho_id.id or False,
                        'company_id':ho.company_id and ho.company_id.id or False,
            })
        return res
    
    def create(self, cr, uid, vals, context=None):
        if 'ten_ho_id' in vals:
            ho = self.pool.get('chan.nuoi').browse(cr,uid,vals['ten_ho_id'])
            vals.update({
                'loai_ho_id':ho.loai_ho_id and ho.loai_ho_id.id or False,
                'company_id':ho.company_id and ho.company_id.id or False,
                })
        if vals.get('chan_nuoi_id',False):
            vals.update({'ten_ho_id':vals['chan_nuoi_id']})
            vals.update({'name':self.pool.get('ir.sequence').get(cr, SUPERUSER_ID,'ton.dong.vat')})
        new_id = super(nhap_xuat_canh_giasuc, self).create(cr, uid, vals, context=context)
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'ten_ho_id' in vals:
            ho = self.pool.get('chan.nuoi').browse(cr,uid,vals['ten_ho_id'])
            vals.update({
                'loai_ho_id':ho.loai_ho_id and ho.loai_ho_id.id or False,
                'company_id':ho.company_id and ho.company_id.id or False,
                })
        new_write = super(nhap_xuat_canh_giasuc, self).write(cr, uid,ids, vals, context)
        return new_write
    
    def _check_so_luong(self, cr, uid, ids, context=None):
        for nhap_xuat in self.browse(cr, uid, ids, context=context):
            for line in nhap_xuat.chitiet_loai_nx:
                sql = '''
                     select id from loai_vacxin 
                '''
                cr.execute(sql)
                vacxin_ids = [r[0] for r in cr.fetchall()]
                for vacxin in self.pool.get('loai.vacxin').browse(cr,uid,vacxin_ids):
                    sql = '''
                        select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_tp from chi_tiet_da_tiem_phong
                        where nhap_xuat_tiemphong_id = %s and ct_loai_id = %s and vacxin_id = %s
                    '''%(nhap_xuat.id, line.ct_loai_id.id, vacxin.id)
                    cr.execute(sql)
                    sl_tp = cr.dictfetchone()['sl_tp']
            
                    if sl_tp>line.so_luong:
                        if nhap_xuat.loai == 'nhap':
                            raise osv.except_osv(_('Warning!'),_('Số lượng nhập đã tiêm phòng không được lớn hơn số lượng muốn nhập'))
                            return False
                        if nhap_xuat.loai == 'xuat':
                            raise osv.except_osv(_('Warning!'),_('Số lượng xuất đã tiêm phòng không được lớn hơn số lượng muốn xuất'))
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

    def _check_xuat_da_tp(self, cr, uid, ids, context=None):
        for nhap_xuat in self.browse(cr, uid, ids, context=context):
            if nhap_xuat.loai == 'xuat':
                for line in nhap_xuat.chitiet_da_tiem_phong:
                    if line.so_luong > line.sl_tiem:
                        raise osv.except_osv(_('Warning!'),_('Số lượng xuất không được lớn hơn số lượng đã tiêm của phiếu tiêm phòng %s ')%(line.tiem_phong_id.name))
                        return False
        return True
         
    _constraints = [
        (_check_so_luong, 'Identical Data', []),
        (_check_so_luong_xuat, 'Identical Data', []),
        (_check_giay_kiem_dich, 'Identical Data', []),
        (_check_xuat_da_tp, 'Identical Data', []),
    ]   
    
    def bt_duyet(self, cr, uid, ids, context=None):
        chi_tiet_loai =[]
        ct_tiem_phong = []
        co_cau_obj = self.pool.get('co.cau')
        user = self.pool.get('res.users').browse(cr,uid,uid)
        
        for line in self.browse(cr, uid, ids, context=context):
            for vaccine_line in line.loai_id.chitiet_loai_vaccine:
                if vaccine_line.yes_no == True:
                    ct_tiem_phong.append((0,0,{
                        'vacxin_id': vaccine_line.vacxin_id.id,
                                                   }))
            if line.loai == 'nhap':
                for loai in line.chitiet_loai_nx:
                    chi_tiet_loai.append((0,0,{
                    'ct_loai_id': loai.ct_loai_id.id,
                    'name':loai.name and loai.name or '',
                    'so_luong':loai.so_luong,     
                    'tiem_phong':loai.tiem_phong,        
                    'ct_tiem_phong_line': ct_tiem_phong,   
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
                    if line.chan_nuoi_id:
                        value ={
                        'chon_loai':line.loai_id.id,
                        'can_bo_ghi_so_id':line.can_bo_id and line.can_bo_id.id or False,
                        'ngay_ghi_so':line.ngay_cap or False,
                        'tang_giam':'a',
                        'ly_do':u'Dữ liệu ban đầu của hộ'+' '+ line.chan_nuoi_id.name,
                        'quan_huyen_id':line.quan_huyen_id and line.quan_huyen_id.id or False,
                        'phuong_xa_id':line.phuong_xa_id and line.phuong_xa_id.id or False,
                        'khu_pho_id':line.khu_pho_id and line.khu_pho_id.id or False,
                        'ten_ho_id':line.ten_ho_id and line.ten_ho_id.id or False,
                        'loai_ho_id':line.loai_ho_id and line.loai_ho_id.id or False,
                        'chitiet_loai':chi_tiet_loai,
                        'trang_thai':'new',
                        'company_id':line.company_id.id,
                        'nhap_xuat_id': line.id,
                        'trang_thai_id': trang and trang['id'] or False,
                        'loai_hinh_so_huu_id':line.ten_ho_id and line.ten_ho_id.loai_hinh_so_huu_id.id or False,
                        'cty_gia_cong_ids': line.ten_ho_id and [(6,0,[r.id for r in line.ten_ho_id.cty_gia_cong_ids])] or False,
                        'quy_cach': line.ten_ho_id and line.ten_ho_id.quy_cach or False,
                        'xu_ly_moi_truong_ids': line.ten_ho_id and [(6,0,[r.id for r in line.ten_ho_id.xu_ly_moi_truong_ids])] or False,
                        'bao_ve_moi_truong':line.ten_ho_id and line.ten_ho_id.bao_ve_moi_truong or False,
                        'danh_gia_moi_truong':line.ten_ho_id and line.ten_ho_id.danh_gia_moi_truong or False,
                        'san_xuat_giong_id':line.ten_ho_id and line.ten_ho_id.san_xuat_giong_id.id or False,
                        'tieu_chuan_viet':line.ten_ho_id and line.ten_ho_id.tieu_chuan_viet or False,
                        'tieu_chuan_global':line.ten_ho_id and line.ten_ho_id.tieu_chuan_global or False,
                        'an_toan_dich':line.ten_ho_id and line.ten_ho_id.an_toan_dich or False,
                        'du_dk_thu_y':line.ten_ho_id and line.ten_ho_id.du_dk_thu_y or False,
                        'tieu_chuan_khac':line.ten_ho_id and line.ten_ho_id.tieu_chuan_khac or False,
                                }
                        co_cau_id = co_cau_obj.create(cr,uid,value)
                        co_cau_obj.bt_duyet(cr,uid,[co_cau_id])
                    else:
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
                        'loai_ho_id':line.loai_ho_id and line.loai_ho_id.id or False,
                        'chitiet_loai':chi_tiet_loai,
                        'trang_thai':'new',
                        'company_id':line.company_id.id,
                        'nhap_xuat_id': line.id,
                        'trang_thai_id': trang and trang['id'] or False,
                        'loai_hinh_so_huu_id':line.ten_ho_id and line.ten_ho_id.loai_hinh_so_huu_id.id or False,
                        'cty_gia_cong_ids': line.ten_ho_id and [(6,0,[r.id for r in line.ten_ho_id.cty_gia_cong_ids])] or False,
                        'quy_cach': line.ten_ho_id and line.ten_ho_id.quy_cach or False,
                        'xu_ly_moi_truong_ids': line.ten_ho_id and [(6,0,[r.id for r in line.ten_ho_id.xu_ly_moi_truong_ids])] or False,
                        'bao_ve_moi_truong':line.ten_ho_id and line.ten_ho_id.bao_ve_moi_truong or False,
                        'danh_gia_moi_truong':line.ten_ho_id and line.ten_ho_id.danh_gia_moi_truong or False,
                        'san_xuat_giong_id':line.ten_ho_id and line.ten_ho_id.san_xuat_giong_id.id or False,
                        'tieu_chuan_viet':line.ten_ho_id and line.ten_ho_id.tieu_chuan_viet or False,
                        'tieu_chuan_global':line.ten_ho_id and line.ten_ho_id.tieu_chuan_global or False,
                        'an_toan_dich':line.ten_ho_id and line.ten_ho_id.an_toan_dich or False,
                        'du_dk_thu_y':line.ten_ho_id and line.ten_ho_id.du_dk_thu_y or False,
                        'tieu_chuan_khac':line.ten_ho_id and line.ten_ho_id.tieu_chuan_khac or False,
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
                    if line.chan_nuoi_id:
                        value ={
                        'chon_loai':line.loai_id.id,
                        'can_bo_ghi_so_id':line.can_bo_id and line.can_bo_id.id or False,
                        'ngay_ghi_so':line.ngay_cap or False,
                        'tang_giam':'a',
                        'ly_do':u'Dữ liệu ban đầu của hộ'+' '+ line.chan_nuoi_id.name,
                        'quan_huyen_id':line.quan_huyen_id and line.quan_huyen_id.id or False,
                        'phuong_xa_id':line.phuong_xa_id and line.phuong_xa_id.id or False,
                        'khu_pho_id':line.khu_pho_id and line.khu_pho_id.id or False,
                        'ten_ho_id':line.ten_ho_id and line.ten_ho_id.id or False,
                        'loai_ho_id':line.loai_ho_id and line.loai_ho_id.id or False,
                        'chitiet_loai':chi_tiet_loai,
                        'trang_thai':'new',
                        'company_id':line.company_id and line.company_id.id or False ,
                        'nhap_xuat_id': line.id,
                        'trang_thai_id': trang and trang['id'] or False,
                        'loai_hinh_so_huu_id':line.ten_ho_id and line.ten_ho_id.loai_hinh_so_huu_id.id or False,
                        'cty_gia_cong_ids': line.ten_ho_id and [(6,0,[r.id for r in line.ten_ho_id.cty_gia_cong_ids])] or False,
                        'quy_cach': line.ten_ho_id and line.ten_ho_id.quy_cach or False,
                        'xu_ly_moi_truong_ids': line.ten_ho_id and [(6,0,[r.id for r in line.ten_ho_id.xu_ly_moi_truong_ids])] or False,
                        'bao_ve_moi_truong':line.ten_ho_id and line.ten_ho_id.bao_ve_moi_truong or False,
                        'danh_gia_moi_truong':line.ten_ho_id and line.ten_ho_id.danh_gia_moi_truong or False,
                        'san_xuat_giong_id':line.ten_ho_id and line.ten_ho_id.san_xuat_giong_id.id or False,
                        'tieu_chuan_viet':line.ten_ho_id and line.ten_ho_id.tieu_chuan_viet or False,
                        'tieu_chuan_global':line.ten_ho_id and line.ten_ho_id.tieu_chuan_global or False,
                        'an_toan_dich':line.ten_ho_id and line.ten_ho_id.an_toan_dich or False,
                        'du_dk_thu_y':line.ten_ho_id and line.ten_ho_id.du_dk_thu_y or False,
                        'tieu_chuan_khac':line.ten_ho_id and line.ten_ho_id.tieu_chuan_khac or False,
#                         'dien_tich_chuong':line.ten_ho_id and line.ten_ho_id.dien_tich_chuong or False,
#                         'mo_ta':line.ten_ho_id and line.ten_ho_id.mo_ta or False,
                                }
                        co_cau_id = co_cau_obj.create(cr,uid,value)
                        co_cau_obj.bt_duyet(cr,uid,[co_cau_id])
                    else:
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
                        'loai_ho_id':line.loai_ho_id and line.loai_ho_id.id or False,
                        'chitiet_loai':chi_tiet_loai,
                        'trang_thai':'new',
                        'company_id':line.company_id.id,
                        'nhap_xuat_id': line.id,
                        'trang_thai_id': trang and trang['id'] or False,
                        'loai_hinh_so_huu_id':line.ten_ho_id and line.ten_ho_id.loai_hinh_so_huu_id.id or False,
                        'cty_gia_cong_ids': line.ten_ho_id and [(6,0,[r.id for r in line.ten_ho_id.cty_gia_cong_ids])] or False,
                        'quy_cach': line.ten_ho_id and line.ten_ho_id.quy_cach or False,
                        'xu_ly_moi_truong_ids': line.ten_ho_id and [(6,0,[r.id for r in line.ten_ho_id.xu_ly_moi_truong_ids])] or False,
                        'bao_ve_moi_truong':line.ten_ho_id and line.ten_ho_id.bao_ve_moi_truong or False,
                        'danh_gia_moi_truong':line.ten_ho_id and line.ten_ho_id.danh_gia_moi_truong or False,
                        'san_xuat_giong_id':line.ten_ho_id and line.ten_ho_id.san_xuat_giong_id.id or False,
                        'tieu_chuan_viet':line.ten_ho_id and line.ten_ho_id.tieu_chuan_viet or False,
                        'tieu_chuan_global':line.ten_ho_id and line.ten_ho_id.tieu_chuan_global or False,
                        'an_toan_dich':line.ten_ho_id and line.ten_ho_id.an_toan_dich or False,
                        'du_dk_thu_y':line.ten_ho_id and line.ten_ho_id.du_dk_thu_y or False,
                        'tieu_chuan_khac':line.ten_ho_id and line.ten_ho_id.tieu_chuan_khac or False,
#                         'dien_tich_chuong':line.ten_ho_id and line.ten_ho_id.dien_tich_chuong or False,
#                         'mo_ta':line.ten_ho_id and line.ten_ho_id.mo_ta or False,
                                }
                        co_cau_id = co_cau_obj.create(cr,uid,value)
                        co_cau_obj.bt_duyet(cr,uid,[co_cau_id])
            elif line.loai == 'xuat':
                for loai in line.chitiet_loai_nx:
                    chi_tiet_loai.append((0,0,{
                    'ct_loai_id': loai.ct_loai_id.id,
                    'name':loai.name,
                    'so_luong':loai.so_luong,    
                    'tiem_phong':loai.tiem_phong,              
                    'ct_tiem_phong_line': ct_tiem_phong,                        
                                               }))
                
                for tp in line.chitiet_da_tiem_phong:
                    sl_con_lai = tp.sl_tiem - tp.so_luong
                    sql = '''
                        update tiem_phong_lmlm set tong_sl_tiem = %s where id = %s
                    '''%(sl_con_lai, tp.tiem_phong_id.id)
                    cr.execute(sql)
                
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
                    'loai_ho_id':line.loai_ho_id and line.loai_ho_id.id or False,
                    'chitiet_loai':chi_tiet_loai,
                    'trang_thai':'new',
                    'company_id':line.company_id.id,
                    'nhap_xuat_id': line.id,
                    'trang_thai_id': trang and trang['id'] or False,
                    'loai_hinh_so_huu_id':line.ten_ho_id and line.ten_ho_id.loai_hinh_so_huu_id.id or False,
                    'cty_gia_cong_ids': line.ten_ho_id and [(6,0,[r.id for r in line.ten_ho_id.cty_gia_cong_ids])] or False,
                    'quy_cach': line.ten_ho_id and line.ten_ho_id.quy_cach or False,
                    'xu_ly_moi_truong_ids': line.ten_ho_id and [(6,0,[r.id for r in line.ten_ho_id.xu_ly_moi_truong_ids])] or False,
                    'bao_ve_moi_truong':line.ten_ho_id and line.ten_ho_id.bao_ve_moi_truong or False,
                    'danh_gia_moi_truong':line.ten_ho_id and line.ten_ho_id.danh_gia_moi_truong or False,
                    'san_xuat_giong_id':line.ten_ho_id and line.ten_ho_id.san_xuat_giong_id.id or False,
                    'tieu_chuan_viet':line.ten_ho_id and line.ten_ho_id.tieu_chuan_viet or False,
                    'tieu_chuan_global':line.ten_ho_id and line.ten_ho_id.tieu_chuan_global or False,
                    'an_toan_dich':line.ten_ho_id and line.ten_ho_id.an_toan_dich or False,
                    'du_dk_thu_y':line.ten_ho_id and line.ten_ho_id.du_dk_thu_y or False,
                    'tieu_chuan_khac':line.ten_ho_id and line.ten_ho_id.tieu_chuan_khac or False,
#                     'dien_tich_chuong':line.ten_ho_id and line.ten_ho_id.dien_tich_chuong or False,
#                     'mo_ta':line.ten_ho_id and line.ten_ho_id.mo_ta or False,
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
                    'loai_ho_id':line.loai_ho_id and line.loai_ho_id.id or False,
                    'chitiet_loai':chi_tiet_loai,
                    'trang_thai':'new',
                    'company_id':line.company_id.id,
                    'nhap_xuat_id': line.id,
                    'trang_thai_id': trang and trang['id'] or False,
                    'loai_hinh_so_huu_id':line.ten_ho_id and line.ten_ho_id.loai_hinh_so_huu_id.id or False,
                    'cty_gia_cong_ids': line.ten_ho_id and [(6,0,[r.id for r in line.ten_ho_id.cty_gia_cong_ids])] or False,
                    'quy_cach': line.ten_ho_id and line.ten_ho_id.quy_cach or False,
                    'xu_ly_moi_truong_ids': line.ten_ho_id and [(6,0,[r.id for r in line.ten_ho_id.xu_ly_moi_truong_ids])] or False,
                    'bao_ve_moi_truong':line.ten_ho_id and line.ten_ho_id.bao_ve_moi_truong or False,
                    'danh_gia_moi_truong':line.ten_ho_id and line.ten_ho_id.danh_gia_moi_truong or False,
                    'san_xuat_giong_id':line.ten_ho_id and line.ten_ho_id.san_xuat_giong_id.id or False,
                    'tieu_chuan_viet':line.ten_ho_id and line.ten_ho_id.tieu_chuan_viet or False,
                    'tieu_chuan_global':line.ten_ho_id and line.ten_ho_id.tieu_chuan_global or False,
                    'an_toan_dich':line.ten_ho_id and line.ten_ho_id.an_toan_dich or False,
                    'du_dk_thu_y':line.ten_ho_id and line.ten_ho_id.du_dk_thu_y or False,
                    'tieu_chuan_khac':line.ten_ho_id and line.ten_ho_id.tieu_chuan_khac or False,
#                     'dien_tich_chuong':line.ten_ho_id and line.ten_ho_id.dien_tich_chuong or False,
#                     'mo_ta':line.ten_ho_id and line.ten_ho_id.mo_ta or False,
                        }
                    co_cau_id = co_cau_obj.create(cr,uid,value)
                    co_cau_obj.bt_duyet(cr,uid,[co_cau_id])
        return True
    
    def onchange_chon_loai(self, cr, uid, ids, loai_id = False, ten_ho_id = False, loai_select = False, context=None):
        chi_tiet= []
        tiem_phong = []
        loai_ho_id = False
        company_id = False
        so_luong_xuat = 0
        so_luong_chet = 0
        for nhap_xuat in self.browse(cr,uid,ids):
            sql = '''
                delete from chi_tiet_loai_nhap_xuat where nhap_xuat_loai_id = %s
            '''%(nhap_xuat.id)
            cr.execute(sql)
            sql = '''
                delete from chi_tiet_da_tiem_phong where nhap_xuat_tiemphong_id = %s
            '''%(nhap_xuat.id)
            cr.execute(sql)
        if ten_ho_id:
            ho = self.pool.get('chan.nuoi').browse(cr,uid,ten_ho_id)
            loai_ho_id = ho.loai_ho_id.id
            company_id = ho.company_id.id
        if loai_id and ten_ho_id:
            loai = self.pool.get('loai.vat').browse(cr,uid,loai_id)    
            for line_loaivat in loai.chitiet_loaivat:
                chi_tiet.append((0,0,{
                                      'ct_loai_id': line_loaivat.id,
                                      'name': line_loaivat.name,
                                      'tiem_phong':line_loaivat.tiem_phong,
                                      }))
                if loai_select == 'nhap':
                    for line_loaibenh in loai.chitiet_loai_vaccine:
                        if line_loaibenh.yes_no == True:
                            tiem_phong.append((0,0,{
                                                  'vacxin_id': line_loaibenh.vacxin_id.id,
                                                  'name': line_loaivat.name,
                                                  'ct_loai_id': line_loaivat.id,
                                                  }))
            if loai_select == 'xuat':
                sql = '''
                    select id from ct_tiem_phong_lmlm_line where tp_lmlm_id in (select id from tiem_phong_lmlm where loai_id = %s and ho_chan_nuoi_id = %s 
                    and trang_thai_id in (select id from trang_thai where stt = 3) )
                '''%(loai_id, ten_ho_id)
                cr.execute(sql)
                lmlm_ids = [r[0] for r in cr.fetchall()]
                if lmlm_ids:
                    for lmlm_line in self.pool.get('ct.tiem.phong.lmlm.line').browse(cr,uid,lmlm_ids):
                        sql = '''
                            select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong 
                            from chi_tiet_da_tiem_phong where nhap_xuat_tiemphong_id in (select id from nhap_xuat_canh_giasuc 
                            where trang_thai_id in (select id from trang_thai where stt = 3) and loai = 'xuat')
                            and tiem_phong_id = %s and ct_loai_id = %s and vacxin_id = %s
                        '''%(lmlm_line.tp_lmlm_id.id,lmlm_line.ct_loai_id.id,lmlm_line.tp_lmlm_id.vacxin_id.id)
                        cr.execute(sql)
                        so_luong_xuat = cr.dictfetchone()['so_luong']
#                              
                        sql = '''
                            select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong 
                            from ct_xuly_giasuc_tp_line where xuly_giasuc_id in (select id from xuly_giasuc 
                            where trang_thai_id in (select id from trang_thai where stt = 3) )
                            and tiem_phong_id = %s and ct_loai_id = %s and vacxin_id = %s
                        '''%(lmlm_line.tp_lmlm_id.id,lmlm_line.ct_loai_id.id,lmlm_line.tp_lmlm_id.vacxin_id.id)
                        cr.execute(sql)
                        so_luong_chet = cr.dictfetchone()['so_luong']
                 
                        if lmlm_line.sl_thuc_tiem + lmlm_line.sl_mien_dich - so_luong_xuat - so_luong_chet> 0:
                            tiem_phong.append((0,0,{
                                          'tiem_phong_id': lmlm_line.tp_lmlm_id.id,
                                          'ct_loai_id': lmlm_line.ct_loai_id.id,
                                          'name': lmlm_line.name,
                                          'vacxin_id':lmlm_line.tp_lmlm_id.vacxin_id.id,
                                          'sl_tiem':lmlm_line.sl_thuc_tiem + lmlm_line.sl_mien_dich - so_luong_xuat - so_luong_chet,
                                          }))
                
        return {'value': {'chitiet_loai_nx': chi_tiet,
                          'chitiet_da_tiem_phong': tiem_phong,
                          'loai_ho_id': loai_ho_id,
                          'company_id': company_id,
                          }}
    
nhap_xuat_canh_giasuc()

class chan_nuoi(osv.osv):
    _inherit = "chan.nuoi"
    _columns = {
         'nhap_dongvat_line': fields.one2many('nhap.xuat.canh.giasuc','chan_nuoi_id','Chi tiet'),
         'loai_id_rel': fields.related('nhap_dongvat_line', 'loai_id', type="many2one", relation="loai.vat",
                string="Loài"),
                }
                
chan_nuoi()

class chi_tiet_loai_nhap_xuat(osv.osv):
    _name = "chi.tiet.loai.nhap.xuat"
    _columns = {
        'nhap_xuat_loai_id': fields.many2one('nhap.xuat.canh.giasuc','Nhap Xuat', ondelete = 'cascade'),
        'ct_loai_id': fields.many2one('chi.tiet.loai.vat','Thông tin'),
        'name': fields.char('Thông tin'),
        'tiem_phong':fields.boolean('Có được tiêm phòng'),
        'so_luong': fields.integer('Số lượng'),
                }
    def onchange_ct_loai_id(self, cr, uid, ids, ct_loai_id = False, context=None):
        ct = self.pool.get('chi.tiet.loai.vat').browse(cr,uid,ct_loai_id)
        return {'value': {'tiem_phong': ct.tiem_phong,
                          }}
    
chi_tiet_loai_nhap_xuat()

class chi_tiet_da_tiem_phong(osv.osv):
    _name = "chi.tiet.da.tiem.phong"
    _columns = {
        'nhap_xuat_tiemphong_id': fields.many2one('nhap.xuat.canh.giasuc','Nhap Xuat', ondelete = 'cascade'),
        'name': fields.char('Thông tin', readonly = True),
        'ct_loai_id': fields.many2one('chi.tiet.loai.vat','Thông tin'),
        'tiem_phong_id': fields.many2one('tiem.phong.lmlm','Số giấy tiêm phòng'),
        'vacxin_id': fields.many2one('loai.vacxin','Loại Vaccine'),
        'sl_tiem': fields.integer('Số lượng đã tiêm', readonly = True),
        'ngay_tiem':fields.date('Ngày tiêm'),
        'so_luong': fields.integer('Số lượng xuất'),
                }
     
chi_tiet_da_tiem_phong()
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
