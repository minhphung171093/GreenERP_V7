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
    
    def _get_user(self, cr, uid, ids, context=None):
        return uid
    
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
        'can_bo_ghi_so': fields.char('Cán bộ ghi sổ'),
        'can_bo_id': fields.many2one('res.users','Cán bộ nhập máy'),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)'),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)'),
        'quan_huyen_id': fields.many2one('quan.huyen','Quận (huyện)'),
        'chitiet_loai_xuly':fields.one2many('chitiet.loai.xuly','xuly_giasuc_id','Chi tiet'),
        'chi_tiet_vaccine_line':fields.one2many('ct.xuly.giasuc.vaccine.line','xuly_giasuc_id','Chi tiết Vaccine'),
        'company_id': fields.many2one('res.company','Trạm'),
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
    
    def _check_sl_ton_vaccine(self, cr, uid, ids, context=None):
        for xl_gs in self.browse(cr, uid, ids, context=context):
            for vaccine in xl_gs.chi_tiet_vaccine_line:
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong from ton_vaccine
                    where vaccine_id = %s and so_lo_id = %s
                '''%(vaccine.loai_vaccine_id.id, vaccine.so_lo_id.id)
                cr.execute(sql)
                ton_vaccine = cr.dictfetchone()['so_luong']
                if vaccine.so_luong_vc > ton_vaccine:
                    raise osv.except_osv(_('Warning!'),_('Bạn nhập %s vaccine nhưng chỉ  còn %s vaccine trong lô %s của loại %s')%(vaccine.so_luong_vc, ton_vaccine, vaccine.so_lo_id.name, vaccine.loai_vaccine_id.name))
                    return False
        return True
         
    _constraints = [
        (_check_sl_ton_vaccine, 'Identical Data', []),
    ]   
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
                for vaccine in line.chi_tiet_vaccine_line:
                    self.pool.get('ton.vaccine').create(cr,uid, {
                                                              'vaccine_id': vaccine.loai_vaccine_id.id,
                                                              'so_lo_id': vaccine.so_lo_id.id,
                                                              'so_luong': -(vaccine.so_luong_vc),
                                                              'loai': 'xuat',
                                                              'xuly_giasuc_id': vaccine.xuly_giasuc_id.id,
                                                              'ngay': vaccine.xuly_giasuc_id.ngay,
                                                                 })
            elif line.trang_thai_id.stt == 2 and user.company_id.cap == 'chi_cuc':
                sql = '''
                    select id from trang_thai where stt = 3
                '''
                cr.execute(sql)
                self.write(cr,uid,ids,{
                                       'trang_thai_id': cr.dictfetchone()['id'] or False
                                       })
                for vaccine in line.chi_tiet_vaccine_line:
                    self.pool.get('ton.vaccine').create(cr,uid, {
                                                              'vaccine_id': vaccine.loai_vaccine_id.id,
                                                              'so_lo_id': vaccine.so_lo_id.id,
                                                              'so_luong': -(vaccine.so_luong_vc),
                                                              'loai': 'xuat',
                                                              'xuly_giasuc_id': vaccine.xuly_giasuc_id.id,
                                                              'ngay': vaccine.xuly_giasuc_id.ngay,
                                                                 })
        return True
    
    def onchange_chon_loai(self, cr, uid, ids, ten_ho_id = False, loai_id = False, context=None):
        chi_tiet= []
        for lmlm in self.browse(cr,uid,ids):
            sql = '''
                delete from ct_tiem_phong_lmlm_line where tp_lmlm_id = %s
            '''%(lmlm.id)
            cr.execute(sql)
        if ten_ho_id and loai_id:
            sql = '''
                select * from chi_tiet_loai_line where co_cau_id in (select id from co_cau 
                where ten_ho_id = %s and chon_loai = %s and trang_thai = 'new')
            '''%(ten_ho_id, loai_id)
            cr.execute(sql)
            for line in cr.dictfetchall():
                chi_tiet.append((0,0,{
                                      'name': line['name'],
                                      'tong_dan': line['tong_sl']
                                      }))
        return {'value': {'chitiet_loai_xuly': chi_tiet}}
xuly_giasuc()

class chitiet_loai_xuly(osv.osv):
    _name = "chitiet.loai.xuly"
    _columns = {
        'xuly_giasuc_id': fields.many2one('xuly.giasuc','Xu ly gia suc', ondelete = 'cascade'),
        'name': fields.char('Thông tin', readonly = True),
        'tong_dan': fields.float('Tổng đàn', readonly = True),
        'so_luong': fields.float('Số lượng xử lý'),
        'ly_do': fields.char('Lý do bệnh',size = 200),
        'ket_qua_xn': fields.char('Kết quả xét nghiệm',size = 200),
        'bien_phap': fields.char('Biện pháp xử lý',size = 200),
#         'vacxin_id': fields.many2one('loai.vacxin','Thuốc sử dụng'),
#         'lieu_luong': fields.float('Liều lượng'),
#         'lieu_trinh': fields.char('Liệu trình',size = 200),
#         'ket_qua_dieu_tri': fields.char('Kết quả điều trị',size = 200),
                }
chitiet_loai_xuly()

class ct_xuly_giasuc_vaccine_line(osv.osv):
    _name = "ct.xuly.giasuc.vaccine.line"
    _columns = {
        'xuly_giasuc_id': fields.many2one( 'xuly.giasuc','Xu ly gia suc', ondelete = 'cascade'),
        'loai_vaccine_id': fields.many2one('loai.vacxin','Loại vaccine'),
        'so_lo_id':fields.many2one('so.lo','Số lô'),
        'han_su_dung_rel':fields.related('so_lo_id','han_su_dung',type='date',string='HSD đến'),
        'so_luong_vc': fields.float('Số lượng Vaccine'),
        'lieu_trinh': fields.char('Liệu trình',size = 200),
                }
ct_xuly_giasuc_vaccine_line()

class ton_vaccine(osv.osv):
    _inherit = "ton.vaccine"
    
    _columns = {
        'xuly_giasuc_id': fields.many2one('xuly.giasuc','XLGS'),
                }
    
ton_vaccine()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
