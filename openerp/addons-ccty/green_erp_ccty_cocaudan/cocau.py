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
        'chitiet_giay_tiemphong':fields.one2many('chi.tiet.tiem.phong','co_cau_id','Tiem Phong'),
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
        'loai_hinh_so_huu_id':fields.many2one('loai.hinh.so.huu','Loại hình sở hữu', required = True),
        'quy_cach': fields.selection([('ho', 'Trại hở'),('lanh', 'Trại lạnh')],'Quy cách chuồng trại'),
        'xu_ly_moi_truong': fields.selection([('bioga', 'Biogas'),('sinh_hoc', 'Đệm lót sinh học'),
                                              ('khac', 'Phương thức xử lý khác,...'),('khong', 'Không xử lý')],'Xử lý môi trường(chỉ chọn 1)',required=True),
        'bao_ve_moi_truong':fields.selection([('co', 'Có'),('khong', 'Không')],'Cam kết bảo vệ MT'),
        'danh_gia_moi_truong':fields.selection([('co', 'Có'),('khong', 'Không')],'Đánh giá tác động MT'),
        'san_xuat_giong':fields.selection([('thuong_pham', 'Giống thương phẩm'),('bo_me', 'Giống bố mẹ, ông bà, cụ kỵ')],'Cơ sở sản xuất giống'),
        'tieu_chuan_viet':fields.boolean('VietGAHP'),
        'tieu_chuan_global':fields.boolean('Tiêu chuẩn Global GAP'),
        'an_toan_dich':fields.boolean('Cơ sở An toàn dịch'),
        'tieu_chuan_khac':fields.boolean('Tiêu chuẩn khác'),
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
                                      'ct_loai_id': line.id,
                                      'name': line.name,
                                      'tong_sl': tong_sl-tong_sl_giam,
                                      }))
        return {'value': {'chitiet_loai': chi_tiet,
                          'loai_ho_id': ho.loai_ho_id.id}}
    
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
            res[line.id] = tong_sl - tong_sl_giam
        return res
    
    _columns = {
        'co_cau_id': fields.many2one( 'co.cau','Co cau', ondelete = 'cascade'),
        'name': fields.char('Thông tin', readonly = True),
        'ct_loai_id': fields.many2one('chi.tiet.loai.vat','Thông tin'),
        'tiem_phong':fields.boolean('Có được tiêm phòng?'),
        'tong_sl':fields.function(sum_so_luong,type='integer',string='Tổng số lượng(hiện có)', store = True),
        'so_luong': fields.integer('Số lượng'),
        'ct_tiem_phong_line':fields.one2many('chi.tiet.tiem.phong.line','ct_cocau_loai_id','Chi tiet'),     
                }
chi_tiet_loai_line()

class chi_tiet_tiem_phong_line(osv.osv):
    _name = "chi.tiet.tiem.phong.line"
     
     
    def sum_sl_da_tiem(self, cr, uid, ids, name, args, context=None):
        res = {}
        tong_sl_tiem = 0
        so_luong_xuat = 0
        so_luong_chet = 0
        for line in self.browse(cr, uid, ids, context=context):
            sql = '''
                select case when sum(sl_thuc_tiem)!=0 then sum(sl_thuc_tiem) else 0 end sl_thuc_tiem
                from ct_tiem_phong_lmlm_line
                where tp_lmlm_id in (select id from tiem_phong_lmlm where loai_id = %s and ho_chan_nuoi_id = %s and vacxin_id = %s
                and trang_thai_id in (select id from trang_thai where stt = 3)) and ct_loai_id = %s
            '''%(line.ct_cocau_loai_id.co_cau_id.chon_loai.id, line.ct_cocau_loai_id.co_cau_id.ten_ho_id.id, line.vacxin_id.id, line.ct_cocau_loai_id.ct_loai_id.id)
            cr.execute(sql)
            tong_sl_tiem = cr.dictfetchone()['sl_thuc_tiem']
             
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong 
                from chi_tiet_da_tiem_phong where nhap_xuat_tiemphong_id in (select id from nhap_xuat_canh_giasuc 
                where trang_thai_id in (select id from trang_thai where stt = 3) and loai_id = %s and ten_ho_id = %s and loai = 'xuat')
                and vacxin_id = %s and ct_loai_id = %s
            '''%(line.ct_cocau_loai_id.co_cau_id.chon_loai.id, line.ct_cocau_loai_id.co_cau_id.ten_ho_id.id, line.vacxin_id.id, line.ct_cocau_loai_id.ct_loai_id.id)
            cr.execute(sql)
            so_luong_xuat = cr.dictfetchone()['so_luong']
             
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong 
                from ct_xuly_giasuc_tp_line where xuly_giasuc_id in (select id from xuly_giasuc 
                where trang_thai_id in (select id from trang_thai where stt = 3) and loai_id = %s and ten_ho_id = %s)
                and vacxin_id = %s and ct_loai_id = %s
            '''%(line.ct_cocau_loai_id.co_cau_id.chon_loai.id, line.ct_cocau_loai_id.co_cau_id.ten_ho_id.id, line.vacxin_id.id, line.ct_cocau_loai_id.ct_loai_id.id)
            cr.execute(sql)
            so_luong_chet = cr.dictfetchone()['so_luong']
             
            res[line.id] = tong_sl_tiem - so_luong_xuat - so_luong_chet
        return res
      
    def _get_thuc_tiem(self, cr, uid, ids, context=None):
        result = {}
        co_cau_ids =[]
        for line in self.pool.get('tiem.phong.lmlm').browse(cr, uid, ids, context=context):
            sql = '''
                select id from chi_tiet_tiem_phong_line where vacxin_id = %s and ct_cocau_loai_id in (select id from chi_tiet_loai_line 
                where co_cau_id in (select id from co_cau
                where chon_loai = %s and ten_ho_id = %s and trang_thai = 'new'))
            '''%(line.vacxin_id.id, line.loai_id.id, line.ho_chan_nuoi_id.id)
            cr.execute(sql)
            co_cau_ids = [row[0] for row in cr.fetchall()]
        return co_cau_ids
      
    def ti_le_tp(self, cr, uid, ids, name, args, context=None):
        res = {}
        tong_sl_tiem = 0
        so_luong_xuat = 0
        so_luong_chet = 0
        
        for line in self.browse(cr, uid, ids, context=context):
            sql = '''
                select case when sum(sl_thuc_tiem)!=0 then sum(sl_thuc_tiem) else 0 end sl_thuc_tiem
                from ct_tiem_phong_lmlm_line
                where tp_lmlm_id in (select id from tiem_phong_lmlm where loai_id = %s and ho_chan_nuoi_id = %s and vacxin_id = %s
                and trang_thai_id in (select id from trang_thai where stt = 3)) and ct_loai_id = %s
            '''%(line.ct_cocau_loai_id.co_cau_id.chon_loai.id, line.ct_cocau_loai_id.co_cau_id.ten_ho_id.id, line.vacxin_id.id, line.ct_cocau_loai_id.ct_loai_id.id)
            cr.execute(sql)
            tong_sl_tiem = cr.dictfetchone()['sl_thuc_tiem']
             
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong 
                from chi_tiet_da_tiem_phong where nhap_xuat_tiemphong_id in (select id from nhap_xuat_canh_giasuc 
                where trang_thai_id in (select id from trang_thai where stt = 3) and loai_id = %s and ten_ho_id = %s and loai = 'xuat')
                and vacxin_id = %s and ct_loai_id = %s
            '''%(line.ct_cocau_loai_id.co_cau_id.chon_loai.id, line.ct_cocau_loai_id.co_cau_id.ten_ho_id.id, line.vacxin_id.id, line.ct_cocau_loai_id.ct_loai_id.id)
            cr.execute(sql)
            so_luong_xuat = cr.dictfetchone()['so_luong']
             
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong 
                from ct_xuly_giasuc_tp_line where xuly_giasuc_id in (select id from xuly_giasuc 
                where trang_thai_id in (select id from trang_thai where stt = 3) and loai_id = %s and ten_ho_id = %s)
                and vacxin_id = %s and ct_loai_id = %s
            '''%(line.ct_cocau_loai_id.co_cau_id.chon_loai.id, line.ct_cocau_loai_id.co_cau_id.ten_ho_id.id, line.vacxin_id.id, line.ct_cocau_loai_id.ct_loai_id.id)
            cr.execute(sql)
            so_luong_chet = cr.dictfetchone()['so_luong']
            
            sl_da_tiem = tong_sl_tiem - so_luong_xuat - so_luong_chet
            if line.ct_cocau_loai_id.tong_sl != 0:
                res[line.id] = float(sl_da_tiem)/float(line.ct_cocau_loai_id.tong_sl)*100
        return res
    
    def _get_cc(self, cr, uid, ids, context=None):
        result = {}
        co_cau_ids =[]
        for line in self.pool.get('co.cau').browse(cr, uid, ids, context=context):
            sql = '''
                select id from chi_tiet_tiem_phong_line where ct_cocau_loai_id in (select id from chi_tiet_loai_line where co_cau_id = %s)
            '''%(line.id)
            cr.execute(sql)
        for r in cr.fetchall():
            result[r[0]] = True
        return result.keys()
    
    def _get_ctll(self, cr, uid, ids, context=None):
        result = {}
        co_cau_ids =[]
        for line in self.pool.get('chi.tiet.loai.line').browse(cr, uid, ids, context=context):
            sql = '''
                select id from chi_tiet_tiem_phong_line where ct_cocau_loai_id = %s
            '''%(line.id)
            cr.execute(sql)
            for r in cr.fetchall():
                result[r[0]] = True
        return result.keys()
        
    _columns = {
        'ct_cocau_loai_id': fields.many2one('chi.tiet.loai.line','CT Co cau', ondelete = 'cascade'),
        'vacxin_id': fields.many2one('loai.vacxin','Loại Vaccine', readonly = True),
        'sl_da_tiem':fields.function(sum_sl_da_tiem,type='integer',string='Số lượng đã tiêm phòng', store = {
                    'co.cau': (_get_cc,['trang_thai_id','chitiet_loai'],10),
                    'chi.tiet.loai.line': (_get_ctll,['ct_tiem_phong_line'],10),
                    'chi.tiet.tiem.phong.line': (lambda self, cr, uid, ids, c={}: ids, ['ct_cocau_loai_id','vacxin_id'], 10),
                    'tiem.phong.lmlm':(_get_thuc_tiem,['chi_tiet_tp_line', 'trang_thai_id'],10), 
                                                                                                             }),
        'ti_le': fields.function(ti_le_tp,type='float',string='Tỉ lệ tiêm phòng (%)', store = {
                    'co.cau': (_get_cc,['trang_thai_id','chitiet_loai'],10),
                    'chi.tiet.loai.line': (_get_ctll,['ct_tiem_phong_line'],10),
                    'chi.tiet.tiem.phong.line': (lambda self, cr, uid, ids, c={}: ids, ['ct_cocau_loai_id','vacxin_id'], 10),
                    'tiem.phong.lmlm':(_get_thuc_tiem,['chi_tiet_tp_line', 'trang_thai_id'],10), 
                                                                                                            }),
                }
chi_tiet_tiem_phong_line()

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
