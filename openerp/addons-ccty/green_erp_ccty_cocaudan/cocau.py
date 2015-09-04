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
from openerp import modules
base_path = os.path.dirname(modules.get_module_path('green_erp_ccty_base'))

class co_cau(osv.osv):
    _name = "co.cau"
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
        'chon_loai': fields.many2one('loai.vat','Chọn loài', required = True),
        'can_bo_id': fields.many2one( 'res.users','Cán bộ thú y nhập'),
        'can_bo_ghi_so': fields.char('Cán bộ ghi sổ'),
        'ngay_ghi_so': fields.date('Ngày ghi sổ', required = True),
        'tang_giam': fields.selection((('a','Tăng'), ('b','Giảm')),'Tăng/Giảm', required = True),
        'ly_do': fields.char('Lý do tăng giảm',size = 50),
        'ten_ho_id': fields.many2one('chan.nuoi','Hộ', required = True),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)', required = True),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)', required = True),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)', required = True),
        'chitiet_loai':fields.one2many('chi.tiet.loai.line','co_cau_id','Co Cau'),
        'chitiet_giay_tiemphong':fields.one2many('tiem.phong.lmlm','co_cau_id','Tiem Phong'),
        'company_id': fields.many2one( 'res.company','Company'),
        'trang_thai': fields.selection((('old','Old'), ('new','New')),'Trang thai'),
        'loai_ho_id': fields.many2one('loai.ho','Loại hộ', readonly = True),
        'trang_thai_id': fields.many2one('trang.thai','Trạng thái', readonly=True),
        'hien_an': fields.function(_get_hien_an, type='boolean', string='Hien/An'),
        'chinh_sua_rel': fields.related('trang_thai_id', 'chinh_sua', type="selection",
                selection=[('nhap', 'Nháp'),('in', 'Đang xử lý'), ('ch_duyet', 'Cấp Huyện Duyệt'), ('cc_duyet', 'Chi Cục Duyệt'), ('huy', 'Hủy bỏ')], 
                string="Chinh Sua", readonly=True, select=True),
        'nhap_xuat_id': fields.many2one('nhap.xuat.canh.giasuc','Nhap Xuat'),
        'xu_ly_id': fields.many2one('xuly.giasuc','Xu Ly'),       
                }
    _defaults = {
        'can_bo_id': _get_user,
        'company_id': _get_company,
        'trang_thai_id': get_trangthai_nhap,
                 }
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
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        for line in self.browse(cr,uid,ids):
            cate_name = line.chon_loai.name
            res.append((line.id,cate_name))
        return res  
    
    def create(self, cr, uid, vals, context=None):
        new_id = super(co_cau, self).create(cr, uid, vals, context=context)
        cocau = self.pool.get('co.cau').browse(cr,uid,new_id)
        sql = '''
             update tiem_phong_lmlm set co_cau_id = %s where loai_id = %s and ho_chan_nuoi_id = %s 
             and trang_thai_id in (select id from trang_thai where stt = 3) 
        '''%(new_id, cocau.chon_loai.id, cocau.ten_ho_id.id)
        cr.execute(sql)
        return new_id
    
    def bt_duyet(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr,uid,uid)
        for line in self.browse(cr, uid, ids, context=context):
            if line.trang_thai_id.stt == 1 and user.company_id.cap == 'huyen':
                sql = '''
                    select id from trang_thai where stt = 2
                '''
                cr.execute(sql)
                trang = cr.dictfetchone()
                self.write(cr,uid,ids,{
                                       'trang_thai_id': trang and trang['id'] or False
                                       })
            elif line.trang_thai_id.stt == 1 and user.company_id.cap == 'chi_cuc':
                sql = '''
                    select id from trang_thai where stt = 3
                '''
                cr.execute(sql)
                trang = cr.dictfetchone()
                self.write(cr,uid,ids,{
                                       'trang_thai_id': trang and trang['id'] or False,
                                       'trang_thai': 'new',
                                       })
                sql = '''
                    select id from co_cau where chon_loai = %s and ten_ho_id = %s and id != %s
                    and trang_thai_id in (select id from trang_thai where stt = 3)
                '''%(line.chon_loai.id, line.ten_ho_id.id, line.id)
                cr.execute(sql)
                co_cau_ids = cr.fetchall()
                if co_cau_ids:
                    cr.execute("update co_cau set trang_thai = 'old' where id in %s",(tuple(co_cau_ids),))
            elif line.trang_thai_id.stt == 2 and user.company_id.cap == 'chi_cuc':
                sql = '''
                    select id from trang_thai where stt = 3
                '''
                cr.execute(sql)
                trang = cr.dictfetchone()
                self.write(cr,uid,ids,{
                                       'trang_thai_id': trang and trang['id'] or False,
                                       'trang_thai': 'new',
                                       })
                sql = '''
                    select id from co_cau where chon_loai = %s and ten_ho_id = %s and id != %s
                    and trang_thai_id in (select id from trang_thai where stt = 3)
                '''%(line.chon_loai.id, line.ten_ho_id.id, line.id)
                cr.execute(sql)
                co_cau_ids = cr.fetchall()
                if co_cau_ids:
                    cr.execute("update co_cau set trang_thai = 'old' where id in %s",(tuple(co_cau_ids),))
            elif line.trang_thai_id.stt == 3 and user.company_id.cap == 'chi_cuc':
                sql = '''
                    select id from co_cau where chon_loai = %s and ten_ho_id = %s and id != %s
                    and trang_thai_id in (select id from trang_thai where stt = 3)
                '''%(line.chon_loai.id, line.ten_ho_id.id, line.id)
                cr.execute(sql)
                co_cau_ids = cr.fetchall()
                if co_cau_ids:
                    cr.execute("update co_cau set trang_thai = 'old' where id in %s",(tuple(co_cau_ids),))
        return True
    
    def onchange_chon_loai(self, cr, uid, ids, chon_loai = False, ten_ho_id = False, context=None):
        chi_tiet= []
        for co_cau in self.browse(cr,uid,ids):
            sql = '''
                delete from chi_tiet_loai_line where co_cau_id = %s
            '''%(co_cau.id)
            cr.execute(sql)
        if chon_loai and ten_ho_id:
            loai = self.pool.get('loai.vat').browse(cr,uid,chon_loai)    
            ho = self.pool.get('chan.nuoi').browse(cr,uid,ten_ho_id)    
            for line in loai.chitiet_loaivat:
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end tong_sl from chi_tiet_loai_line
                    where co_cau_id in (select id from co_cau where chon_loai = %s and ten_ho_id = %s and tang_giam = 'a' and trang_thai_id in (select id from trang_thai where stt = 3))
                    and name = '%s'
                '''%(chon_loai, ten_ho_id, line.name)
                cr.execute(sql)
                tong_sl = cr.dictfetchone()['tong_sl']
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end tong_sl_giam from chi_tiet_loai_line
                    where co_cau_id in (select id from co_cau where chon_loai = %s and ten_ho_id = %s and tang_giam = 'b' and trang_thai_id in (select id from trang_thai where stt = 3))
                    and name = '%s'
                '''%(chon_loai, ten_ho_id, line.name)
                cr.execute(sql)
                tong_sl_giam = cr.dictfetchone()['tong_sl_giam']
                chi_tiet.append((0,0,{
                                      'name': line.name,
                                      'tong_sl': tong_sl-tong_sl_giam,
                                      }))
        return {'value': {'chitiet_loai': chi_tiet,
                          'loai_ho_id': ho.loai_ho_id.id}}
    
#     def _check_so_luong_giam(self, cr, uid, ids, context=None):
#         for co_cau in self.browse(cr, uid, ids, context=context):
#             if co_cau.tang_giam == 'b':
#                 for line in co_cau.chitiet_loai:
#                     if not co_cau.nhap_xuat_id:
#                         if line.so_luong > line.tong_sl:
#                             raise osv.except_osv(_('Warning!'),_('Số lượng giảm %s trong hộ %s vượt quá tổng số đàn hiện có')%(line.name, co_cau.ten_ho_id.name))
#                             return False
#         return True
#     _constraints = [
#         (_check_so_luong_giam, 'Identical Data', []),
#     ]   
co_cau()

class chi_tiet_loai_line(osv.osv):
    _name = "chi.tiet.loai.line"
    
    def sum_so_luong(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end tong_sl from chi_tiet_loai_line
                where co_cau_id in (select id from co_cau where chon_loai = %s and ten_ho_id = %s and tang_giam = 'a' and trang_thai_id in (select id from trang_thai where stt = 3))
                and name = '%s'
            '''%(line.co_cau_id.chon_loai.id, line.co_cau_id.ten_ho_id.id, line.name)
            cr.execute(sql)
            tong_sl = cr.dictfetchone()['tong_sl']
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end tong_sl_giam from chi_tiet_loai_line
                where co_cau_id in (select id from co_cau where chon_loai = %s and ten_ho_id = %s and tang_giam = 'b' and trang_thai_id in (select id from trang_thai where stt = 3))
                and name = '%s'
            '''%(line.co_cau_id.chon_loai.id, line.co_cau_id.ten_ho_id.id, line.name)
            cr.execute(sql)
            tong_sl_giam = cr.dictfetchone()['tong_sl_giam']
            
#             sql = '''
#                 select so_luong from chi_tiet_loai_line
#                 where co_cau_id in (select id from co_cau where chon_loai = %s and ten_ho_id = %s and tang_giam = 'a'
#                 and nhap_xuat_id is null)
#                 and name = '%s' and id = %s
#             '''%(line.co_cau_id.chon_loai.id, line.co_cau_id.ten_ho_id.id, line.name, line.id)
#             cr.execute(sql)
#             sl_tang_hientai = cr.dictfetchone()
#             tong_sl += sl_tang_hientai and sl_tang_hientai['so_luong'] or 0
#             sql = '''
#                 select so_luong from chi_tiet_loai_line
#                 where co_cau_id in (select id from co_cau where chon_loai = %s and ten_ho_id = %s and tang_giam = 'b'
#                 and nhap_xuat_id is null)
#                 and name = '%s' and id = %s
#             '''%(line.co_cau_id.chon_loai.id, line.co_cau_id.ten_ho_id.id, line.name, line.id)
#             cr.execute(sql)
#             sl_giam_hientai = cr.dictfetchone()
#             tong_sl_giam += sl_giam_hientai and sl_giam_hientai['so_luong'] or 0
            
            res[line.id] = tong_sl - tong_sl_giam
        return res
    
    def sum_sl_da_tiem(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            sql = '''
                select case when sum(sl_thuc_tiem)!=0 then sum(sl_thuc_tiem) else 0 end sl_thuc_tiem
                from ct_tiem_phong_lmlm_line
                where tp_lmlm_id in (select id from tiem_phong_lmlm where loai_id = %s and ho_chan_nuoi_id = %s 
                and trang_thai_id in (select id from trang_thai where stt = 3))
                and name = '%s'
            '''%(line.co_cau_id.chon_loai.id, line.co_cau_id.ten_ho_id.id, line.name)
            cr.execute(sql)
            tong_sl_tiem = cr.dictfetchone()['sl_thuc_tiem']
            res[line.id] = tong_sl_tiem
        return res
    
#     def _get_thuc_tiem(self, cr, uid, ids, context=None):
#         result = {}
#         for line in self.pool.get('ct.tiem.phong.lmlm.line').browse(cr, uid, ids, context=context):
#             result[line.tp_co_cau_id.id] = True
#         return result.keys()   
    
    def ti_le_tp(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end tong_sl from chi_tiet_loai_line
                where co_cau_id in (select id from co_cau where chon_loai = %s and ten_ho_id = %s and tang_giam = 'a' and trang_thai_id in (select id from trang_thai where stt = 3))
                and name = '%s'
            '''%(line.co_cau_id.chon_loai.id, line.co_cau_id.ten_ho_id.id, line.name)
            cr.execute(sql)
            tong_sl = cr.dictfetchone()['tong_sl']
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end tong_sl_giam from chi_tiet_loai_line
                where co_cau_id in (select id from co_cau where chon_loai = %s and ten_ho_id = %s and tang_giam = 'b' and trang_thai_id in (select id from trang_thai where stt = 3))
                and name = '%s'
            '''%(line.co_cau_id.chon_loai.id, line.co_cau_id.ten_ho_id.id, line.name)
            cr.execute(sql)
            tong_sl_giam = cr.dictfetchone()['tong_sl_giam']
            
            sql = '''
                select so_luong from chi_tiet_loai_line
                where co_cau_id in (select id from co_cau where chon_loai = %s and ten_ho_id = %s and tang_giam = 'a'
                and nhap_xuat_id is null)
                and name = '%s' and id = %s
            '''%(line.co_cau_id.chon_loai.id, line.co_cau_id.ten_ho_id.id, line.name, line.id)
            cr.execute(sql)
            sl_tang_hientai = cr.dictfetchone()
            tong_sl += sl_tang_hientai and sl_tang_hientai['so_luong'] or 0
            sql = '''
                select so_luong from chi_tiet_loai_line
                where co_cau_id in (select id from co_cau where chon_loai = %s and ten_ho_id = %s and tang_giam = 'b'
                and nhap_xuat_id is null)
                and name = '%s' and id = %s
            '''%(line.co_cau_id.chon_loai.id, line.co_cau_id.ten_ho_id.id, line.name, line.id)
            cr.execute(sql)
            sl_giam_hientai = cr.dictfetchone()
            tong_sl_giam += sl_giam_hientai and sl_giam_hientai['so_luong'] or 0
            
            sum_so_luong = tong_sl - tong_sl_giam
            
            sql = '''
                select case when sum(sl_thuc_tiem)!=0 then sum(sl_thuc_tiem) else 0 end sl_thuc_tiem
                from ct_tiem_phong_lmlm_line
                where tp_lmlm_id in (select id from tiem_phong_lmlm where loai_id = %s and ho_chan_nuoi_id = %s 
                and trang_thai_id in (select id from trang_thai where stt = 3))
                and name = '%s'
            '''%(line.co_cau_id.chon_loai.id, line.co_cau_id.ten_ho_id.id, line.name)
            cr.execute(sql)
            tong_sl_tiem = cr.dictfetchone()['sl_thuc_tiem']
            sum_sl_da_tiem = tong_sl_tiem
            
            res[line.id] = float(sum_sl_da_tiem)/float(sum_so_luong)*100
        return res
    
    _columns = {
        'co_cau_id': fields.many2one( 'co.cau','Co cau', ondelete = 'cascade'),
        'name': fields.char('Thông tin', readonly = True),
        'tiem_phong':fields.boolean('Có được tiêm phòng?'),
        'tong_sl':fields.function(sum_so_luong,type='integer',string='Tổng số lượng(hiện có)', store = True),
        'so_luong': fields.integer('Số lượng'),
        'sl_da_tiem':fields.function(sum_sl_da_tiem,type='integer',string='Số lượng đã tiêm phòng', store = {
                     'tiem.phong.lmlm':(_get_thuc_tiem, [], 10),                                                                                        
                                                                                                             }),
        'ti_le': fields.function(ti_le_tp,type='float',string='Tỉ lệ tiêm phòng (%)', store = True),
                }
    
chi_tiet_loai_line()

# class chi_tiet_giay_tiemphong_line(osv.osv):
#     _name = "chi.tiet.giay.tiemphong.line"
#     
#     _columns = {
#         'co_cau_id': fields.many2one('co.cau','Co cau', ondelete = 'cascade'),
#         'tiemphong_id': fields.many2one('tiem.phong.lmlm','Số giấy tiêm phòng'),
#         'loai_benh_id': fields.many2one('chi.tiet.loai.benh','Loại bệnh'),
# #         'so_luong':fields.function(sum_so_luong,type='integer',string='Tổng số lượng(hiện có)', store = True),
#         'so_luong': fields.integer('Số lượng'),
#                 }
# chi_tiet_giay_tiemphong_line()

class tiem_phong_lmlm(osv.osv):
    _inherit = "tiem.phong.lmlm"
    
    _columns = {
        'co_cau_id': fields.many2one('co.cau','Co cau'),
                }
    
tiem_phong_lmlm()

class ct_tiem_phong_lmlm_line(osv.osv):
    _inherit = "ct.tiem.phong.lmlm.line"
    
    _columns = {
        'tp_co_cau_id':fields.many2one('co.cau','Co Cau dan'),
                }
    
ct_tiem_phong_lmlm_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
