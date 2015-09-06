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
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)', required = True),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)', required = True),
        'quan_huyen_id': fields.many2one('quan.huyen','Quận (huyện)', required = True),
        'chitiet_loai_xuly':fields.one2many('chitiet.loai.xuly','xuly_giasuc_id','Chi tiet'),
        'chi_tiet_vaccine_line':fields.one2many('ct.xuly.giasuc.vaccine.line','xuly_giasuc_id','Chi tiết Vaccine'),
        'chi_tiet_tp_line':fields.one2many('ct.xuly.giasuc.tp.line','xuly_giasuc_id','Chi tiết tiêm phòng'),
        'company_id': fields.many2one('res.company','Trạm'),
        'trang_thai_id': fields.many2one('trang.thai','Trạng thái', readonly=True),
        'hien_an': fields.function(_get_hien_an, type='boolean', string='Hien/An'),
        'co_khong_tp': fields.selection((('co','Có'), ('khong','Không')),'Có tiêm phòng LMLM: ', required = True),
        'chinh_sua_rel': fields.related('trang_thai_id', 'chinh_sua', type="selection",
                selection=[('nhap', 'Nháp'),('in', 'Đang xử lý'), ('ch_duyet', 'Cấp Huyện Duyệt'), ('cc_duyet', 'Chi Cục Duyệt'), ('huy', 'Hủy bỏ')], 
                string="Chinh Sua", readonly=True, select=True),
                }
    _defaults = {
        'can_bo_id': _get_user,
        'company_id': _get_company,
        'trang_thai_id': get_trangthai_nhap,
        'co_khong_tp': 'co',
                 }
    def _check_sl_gia_suc(self, cr, uid, ids, context=None):
        for sl_gs in self.browse(cr, uid, ids, context=context):
            for gs in sl_gs.chitiet_loai_xuly:
                if gs.dvt == 'kg':
                    if gs.sl_tuong_duong > gs.tong_dan:
                        raise osv.except_osv(_('Cảnh báo!'),_('Bạn nhập %s con nhưng tổng đàn chỉ có %s con của loại %s')%(gs.sl_tuong_duong, gs.tong_dan, gs.name))
                        return False
                if gs.dvt == 'con':
                    if gs.so_luong > gs.tong_dan:
                        raise osv.except_osv(_('Cảnh báo!'),_('Bạn nhập %s con nhưng tổng đàn chỉ có %s con của loại %s')%(gs.so_luong, gs.tong_dan, gs.name))
                        return False
        return True    
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
    
    def _check_xuly_giasuc(self, cr, uid, ids, context=None):
        for giasuc in self.browse(cr, uid, ids, context=context):
            giasuc_ids = self.search(cr,uid,[('id', '!=', giasuc.id), ('name', '=', giasuc.name)])
            if giasuc_ids:
                raise osv.except_osv(_('Warning!'),_('Mã số gia súc nhiễm bệnh không được trùng nhau'))
                return False
        return True
    
    def _check_chet_da_tp(self, cr, uid, ids, context=None):
        for xuly in self.browse(cr, uid, ids, context=context):
            for line in xuly.chi_tiet_tp_line:
                if line.so_luong > line.sl_tiem:
                    raise osv.except_osv(_('Warning!'),_('Số lượng loài %s xử lý không được lớn hơn số lượng đã tiêm của phiếu tiêm phòng %s ')%(line.name, line.tiem_phong_id.name))
                    return False
        return True
         
    def _check_so_luong_theo_ct_loai(self, cr, uid, ids, context=None):
        for xuly in self.browse(cr, uid, ids, context=context):
            for line in xuly.chitiet_loai_xuly:
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_tp from ct_xuly_giasuc_tp_line
                    where xuly_giasuc_id = %s and name = '%s'
                '''%(xuly.id, line.name)
                cr.execute(sql)
                sl_tp = cr.dictfetchone()['sl_tp']
            
                if sl_tp>line.sl_tuong_duong:
                    raise osv.except_osv(_('Warning!'),_('Số lượng loài %s xử lý đã tiêm phòng không được lớn hơn số lượng muốn xử lý')%(line.name))
                    return False
        return True
    
    _constraints = [
        (_check_sl_ton_vaccine, 'Identical Data', []),
        (_check_xuly_giasuc, 'Identical Data', []),
        (_check_sl_gia_suc, 'Identical Data', []),
        (_check_chet_da_tp, 'Identical Data', []),
        (_check_so_luong_theo_ct_loai, 'Identical Data', []),
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
        chi_tiet_loai =[]
        co_cau_obj = self.pool.get('co.cau')
        user = self.pool.get('res.users').browse(cr,uid,uid)
        for line in self.browse(cr, uid, ids, context=context):
            for gs in line.chitiet_loai_xuly:
                sql = '''
                    select tiem_phong from chi_tiet_loai_vat where loai_id = %s and name = '%s'
                '''%(line.loai_id.id, gs.name)
                cr.execute(sql)
                tiem_phong = cr.dictfetchone()['tiem_phong']
                if gs.dvt == 'con':
                    chi_tiet_loai.append((0,0,{
                        'name':gs.name,
                        'so_luong':gs.so_luong,   
                        'tiem_phong':tiem_phong,
                    }))
                else:
                    chi_tiet_loai.append((0,0,{
                        'name':gs.name,
                        'so_luong':gs.sl_tuong_duong,     
                        'tiem_phong':tiem_phong,    
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
                'can_bo__id':line.can_bo_id and line.can_bo_id.id or False,
                'ngay_ghi_so':line.ngay or False,
                'tang_giam':'b',
                'ly_do':u'Xuất từ mã số gia súc nhiễm bệnh'+' '+ line.name,
                'quan_huyen_id':line.quan_huyen_id and line.quan_huyen_id.id or False,
                'phuong_xa_id':line.phuong_xa_id and line.phuong_xa_id.id or False,
                'khu_pho_id':line.khu_pho_id and line.khu_pho_id.id or False,
                'ten_ho_id':line.ten_ho_id and line.ten_ho_id.id or False,
                'chitiet_loai':chi_tiet_loai,
                'trang_thai':'new',
                'company_id':line.company_id.id,
                'xu_ly_id': line.id,
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
                'can_bo__id':line.can_bo_id and line.can_bo_id.id or False,
                'ngay_ghi_so':line.ngay or False,
                'tang_giam':'b',
                'ly_do':u'Xuất từ mã số gia súc nhiễm bệnh'+' '+ line.name,
                'quan_huyen_id':line.quan_huyen_id and line.quan_huyen_id.id or False,
                'phuong_xa_id':line.phuong_xa_id and line.phuong_xa_id.id or False,
                'khu_pho_id':line.khu_pho_id and line.khu_pho_id.id or False,
                'ten_ho_id':line.ten_ho_id and line.ten_ho_id.id or False,
                'chitiet_loai':chi_tiet_loai,
                'trang_thai':'new',
                'company_id':line.company_id.id,
                'xu_ly_id': line.id,
                'trang_thai_id': trang and trang['id'] or False,
                    }
                co_cau_id = co_cau_obj.create(cr,uid,value)
                co_cau_obj.bt_duyet(cr,uid,[co_cau_id])
        return True
    
    def onchange_chon_loai(self, cr, uid, ids, ten_ho_id = False, loai_id = False, context=None):
        chi_tiet= []
        tiem_phong = []
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
                        from ct_xuly_giasuc_tp_line where xuly_giasuc_id in (select id from xuly_giasuc 
                        where trang_thai_id in (select id from trang_thai where stt = 3) )
                        and tiem_phong_id = %s and name = '%s'
                    '''%(lmlm_line.tp_lmlm_id.id, lmlm_line.name)
                    cr.execute(sql)
                    so_luong_chet = cr.dictfetchone()['so_luong']
                    
                    sql = '''
                        select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong 
                        from chi_tiet_da_tiem_phong where nhap_xuat_tiemphong_id in (select id from nhap_xuat_canh_giasuc 
                        where trang_thai_id in (select id from trang_thai where stt = 3) )
                        and tiem_phong_id = %s and name = '%s'
                    '''%(lmlm_line.tp_lmlm_id.id, lmlm_line.name)
                    cr.execute(sql)
                    so_luong_xuat = cr.dictfetchone()['so_luong']
                            
                    if lmlm_line.sl_thuc_tiem - so_luong_chet- so_luong_xuat > 0:
                        tiem_phong.append((0,0,{
                                      'tiem_phong_id': lmlm_line.tp_lmlm_id.id,
                                      'name': lmlm_line.name,
                                      'loai_benh_id':lmlm_line.tp_lmlm_id.loai_benh_id.id,
                                      'sl_tiem':lmlm_line.sl_thuc_tiem - so_luong_chet - so_luong_xuat,
                                      }))
        return {'value': {'chitiet_loai_xuly': chi_tiet, 'chi_tiet_tp_line':tiem_phong }
                }
xuly_giasuc()

class chitiet_loai_xuly(osv.osv):
    _name = "chitiet.loai.xuly"
    _columns = {
        'xuly_giasuc_id': fields.many2one('xuly.giasuc','Xu ly gia suc', ondelete = 'cascade'),
        'name': fields.char('Thông tin', readonly = True),
        'tong_dan': fields.integer('Tổng đàn', readonly = True),
        'so_luong': fields.float('Số lượng xử lý'),
#         'dvt':fields.many2one('don.vi.tinh','ĐVT',required=True),
        'dvt':fields.selection([('kg', 'Kg'),('con', 'Con')],'ĐVT'),
        'sl_tuong_duong':fields.integer('Tương đương (con)', required = True),
        'ly_do': fields.char('Lý do bệnh',size = 200),
        'ket_qua_xn': fields.char('Kết quả xét nghiệm',size = 200),
        'bien_phap': fields.char('Biện pháp xử lý',size = 200),
                }
    
    def onchange_dvt(self, cr, uid, ids, dvt = False, so_luong = False, context=None):
        if dvt == 'con' and so_luong:
            return {'value': {'sl_tuong_duong': so_luong}}
        else:
            return {'value': {'sl_tuong_duong': False}}
    
chitiet_loai_xuly()

class ct_xuly_giasuc_vaccine_line(osv.osv):
    _name = "ct.xuly.giasuc.vaccine.line"
    _columns = {
        'xuly_giasuc_id': fields.many2one( 'xuly.giasuc','Xu ly gia suc', ondelete = 'cascade'),
        'loai_hoa_chat_id':fields.many2one('loai.hoa.chat','Loại hoá chất',required=True),
        'so_luong':fields.float('Số lượng'),
                }
ct_xuly_giasuc_vaccine_line()

class ct_xuly_giasuc_tp_line(osv.osv):
    _name = "ct.xuly.giasuc.tp.line"
    _columns = {
        'xuly_giasuc_id': fields.many2one('xuly.giasuc','Xu ly gia suc', ondelete = 'cascade'),
        'name': fields.char('Thông tin', readonly = True),
        'tiem_phong_id': fields.many2one('tiem.phong.lmlm','Số giấy tiêm phòng'),
        'loai_benh_id': fields.many2one('chi.tiet.loai.benh','Loại bệnh', readonly = True),
        'sl_tiem': fields.integer('Số lượng đã tiêm', readonly = True),
        'so_luong': fields.integer('Số lượng chết'),
                }
ct_xuly_giasuc_tp_line()

class ton_vaccine(osv.osv):
    _inherit = "ton.vaccine"
    
    _columns = {
        'xuly_giasuc_id': fields.many2one('xuly.giasuc','XLGS'),
                }
    
ton_vaccine()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
