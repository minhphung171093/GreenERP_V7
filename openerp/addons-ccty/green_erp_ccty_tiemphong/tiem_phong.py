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


class tiem_phong(osv.osv):
    _name = "tiem.phong"
    def onchange_quan_huyen(self, cr, uid, ids, context=None):
        vals = {}
        vals = {'phuong_xa_id':False}
        return {'value': vals}
    def onchange_phuong_xa(self, cr, uid, ids, context=None):
        vals = {}
        vals = {'khu_pho_id':False}
        return {'value': vals}


    _columns = {
        'tu_tiem': fields.boolean('Tự tiêm'),
        'can_bo_tiem': fields.boolean('Cán bộ thú y tiêm'),
        'so_luong_tiem': fields.integer('số lượng con được tiêm'),
        'hinh_thuc_tiem':fields.selection([('tu_tiem','Tự tiêm'),('can_bo','Cán bộ thú y tiêm')]),
        'name': fields.date('Ngày tiêm', required = True),
        'tram_id': fields.many2one( 'res.company','Trạm', required = True),
        'can_bo_id': fields.many2one( 'res.users','Cán bộ thú y thực hiện tiêm'),
        'loai_vaccine_id': fields.many2one('loai.vacxin','Loại vaccine'),
        'loai_vat_id': fields.many2one('loai.vat','Loài vật được tiêm'),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)'),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)'),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)'),
        'ho_chan_nuoi_id': fields.many2one( 'chan.nuoi','Hộ chăn nuôi'),
                }


tiem_phong()

class tiem_phong_lmlm(osv.osv):
    _name = "tiem.phong.lmlm"
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
        vals = {'ho_chan_nuoi_id':False}
        return {'value': vals}
    
    def _get_company(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr,uid,uid)
        return user.company_id.id or False
    
    def _get_loaibenh(self, cr, uid, ids, context=None):
        sql = '''
            select id from chi_tiet_loai_benh where name = 'LMLM'
        '''
        cr.execute(sql)
        lmlm_id = cr.dictfetchone()
        return lmlm_id and lmlm_id['id'] or False
    
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
    
    def _get_sl_tiem(self, cr, uid, ids, name, arg, context=None):        
        result = {}
        for tiem in self.browse(cr,uid,ids):
            sum = 0
            for line in tiem.chi_tiet_tp_line:
                sum += line.sl_thuc_tiem
            result[tiem.id] = sum    
        return result

    _columns = {
        'ngay_tiem': fields.datetime('Ngày tiêm', required = True),
        'loai_id': fields.many2one('loai.vat','Loài vật', required = True ),
        'tram_id': fields.many2one( 'res.company','Trạm'),
        'can_bo_id': fields.many2one( 'res.users','Cán bộ thú y nhập'),
        'can_bo_tiem': fields.char('Cán bộ thú y thực hiện tiêm', size = 100),
        'loai_giay_tp_id': fields.many2one('loai.giay.tiem.phong','Hình thức tiêm phòng'),
        'name': fields.char('Số giấy tiêm phòng', size = 100,required = True),
        'so_quyen': fields.char('Số quyển tiêm phòng', size = 100),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)', required = True),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)', required = True),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)', required = True),
        'ho_chan_nuoi_id': fields.many2one( 'chan.nuoi','Hộ chăn nuôi', required = True),
        'chi_tiet_tp_line':fields.one2many('ct.tiem.phong.lmlm.line','tp_lmlm_id','Chi tiết tiêm phòng'),
        'chi_tiet_vaccine_line':fields.one2many('ct.tiem.phong.vaccine.line','tp_lmlm_id','Chi tiết Vaccine'),
        'state':fields.selection([('draft', 'Nháp'),('done', 'Duyệt')],'Status', readonly=True),
        'trang_thai_id': fields.many2one('trang.thai','Trạng thái'),
        'hien_an': fields.function(_get_hien_an, type='boolean', string='Hien/An'),
        'chinh_sua_rel': fields.related('trang_thai_id', 'chinh_sua', type="selection",
                selection=[('nhap', 'Nháp'),('in', 'Đang xử lý'), ('ch_duyet', 'Cấp Huyện Duyệt'), ('cc_duyet', 'Chi Cục Duyệt'), ('huy', 'Hủy bỏ')], 
                string="Chinh Sua", readonly=True, select=True),
#        'loai_vaccine_id': fields.many2one('loai.vacxin','Loại vaccine'),
        'so_lo_id':fields.many2one('so.lo','Số lô'),
        'han_su_dung_rel':fields.related('so_lo_id','han_su_dung',type='date',string='HSD đến'),
        'so_luong_vc': fields.integer('Số lượng Vaccine'),
#         'nhap_xuat_id': fields.many2one('nhap.xuat.canh.giasuc','Phiếu nhập/xuất'),
        'tong_sl_tiem': fields.function(_get_sl_tiem, type='integer', string='SL đã tiêm phòng', store = True),
        'loai_benh_id': fields.many2one('chi.tiet.loai.benh','Loại bệnh'),
        'vacxin_id': fields.many2one('loai.vacxin','Loại Vaccine', required = True),
                }
        
    _defaults = {
        'can_bo_id': _get_user,
#         'loai_benh_id': _get_loaibenh,
        'trang_thai_id': get_trangthai_nhap,
                 }

    def create(self, cr, uid, vals, context=None):
        if 'name' in vals:
            name = vals['name'].replace(" ","")
            vals['name'] = name
        return super(tiem_phong_lmlm, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'name' in vals:
            name = vals['name'].replace(" ","")
            vals['name'] = name
        return super(tiem_phong_lmlm, self).write(cr, uid,ids, vals, context)    

    def _check_giay_tp(self, cr, uid, ids, context=None):
        for tp in self.browse(cr, uid, ids, context=context):
            tp_ids = self.search(cr,uid,[('id', '!=', tp.id), ('name', '=', tp.name)])
            sql = '''
                select id from tiem_phong_lmlm where id != %s and lower(name) = lower('%s')
            '''%(tp.id,tp.name)
            cr.execute(sql)
            lower_ids = [row[0] for row in cr.fetchall()]
            if tp_ids or lower_ids:
                raise osv.except_osv(_('Warning!'),_('Số giấy tiêm phòng không được trùng nhau'))
                return False
        return True
    
#     def _check_sl_ton_vaccine(self, cr, uid, ids, context=None):
#         for tiem_phong in self.browse(cr, uid, ids, context=context):
#             for vaccine in tiem_phong.chi_tiet_vaccine_line:
#                 sql = '''
#                     select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong from ton_vaccine
#                     where vaccine_id = %s and so_lo_id = %s
#                 '''%(vaccine.loai_vaccine_id.id, vaccine.so_lo_id.id)
#                 cr.execute(sql)
#                 ton_vaccine = cr.dictfetchone()['so_luong']
#                 if vaccine.so_luong_vc > ton_vaccine:
#                     raise osv.except_osv(_('Warning!'),_('Bạn nhập %s vaccine nhưng chỉ  còn %s vaccine trong lô %s của loại %s')%(vaccine.so_luong_vc, ton_vaccine, vaccine.so_lo_id.name, vaccine.loai_vaccine_id.name))
#                     return False
#         return True
         
    _constraints = [
        (_check_giay_tp, 'Identical Data', []),
    ]   
    
    def bt_duyet(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr,uid,uid)
        for line in self.browse(cr, uid, ids, context=context):
            sql = '''
                 select id from co_cau where trang_thai = 'new' and chon_loai = %s and ten_ho_id = %s
                 and trang_thai_id in (select id from trang_thai where stt = 3) 
            '''%(line.loai_id.id, line.ho_chan_nuoi_id.id)
            cr.execute(sql)
            co_cau_id = cr.dictfetchone()['id']
            sql = '''
                 update tiem_phong_lmlm set co_cau_id = %s where id = %s 
            '''%(co_cau_id, line.id)
            cr.execute(sql)
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
                                                              'vaccine_id': vaccine.tp_lmlm_id.vacxin_id.id,
                                                              'so_lo_id': vaccine.so_lo_id.id,
                                                              'so_luong': -(vaccine.so_luong_vc),
                                                              'loai': 'xuat',
                                                              'lmlm_id': vaccine.tp_lmlm_id.id,
                                                              'ngay': vaccine.tp_lmlm_id.ngay_tiem,
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
                                                              'vaccine_id': vaccine.tp_lmlm_id.vacxin_id.id,
                                                              'so_lo_id': vaccine.so_lo_id.id,
                                                              'so_luong': -(vaccine.so_luong_vc),
                                                              'loai': 'xuat',
                                                              'lmlm_id': vaccine.tp_lmlm_id.id,
                                                              'ngay': vaccine.tp_lmlm_id.ngay_tiem,
                                                                 })
        return True
    
    def onchange_ho_chan_nuoi_id(self, cr, uid, ids, ho_chan_nuoi_id = False, loai_id = False, vacxin_id = False, context=None):
        chi_tiet = []
        chi_tiet_vacxin = []
        sl_thuc_tiem_before = 0
        sl_xuat_tp = 0
        so_luong_chet = 0
        tram_id = False
        for lmlm in self.browse(cr,uid,ids):
            sql = '''
                delete from ct_tiem_phong_lmlm_line where tp_lmlm_id = %s
            '''%(lmlm.id)
            cr.execute(sql)
            sql = '''
                delete from ct_tiem_phong_vaccine_line where tp_lmlm_id = %s
            '''%(lmlm.id)
            cr.execute(sql)
        if vacxin_id:
            sql = '''
                select * from so_lo where vacxin_id = %s 
            '''%(vacxin_id)
            cr.execute(sql)
            for vacxin in cr.dictfetchall():
                sql = '''
                    select case when sum(soluong)!=0 then sum(soluong) else 0 end soluong from nhap_vaccine
                    where so_lo_id = %s and name = %s and trang_thai_id in (select id from trang_thai where stt = 3)
                '''%(vacxin['id'], vacxin_id)
                cr.execute(sql)
                nhap = cr.dictfetchone()['soluong']
                
                sql = '''
                    select case when sum(so_luong_vc)!=0 then sum(so_luong_vc) else 0 end so_luong_vc from ct_tiem_phong_vaccine_line
                    where so_lo_id = %s and tp_lmlm_id in (select id from tiem_phong_lmlm where vacxin_id = %s and trang_thai_id in (select id from trang_thai where stt = 3))
                '''%(vacxin['id'], vacxin_id)
                cr.execute(sql)
                xuat = cr.dictfetchone()['so_luong_vc']
                if nhap-xuat>0:
                    chi_tiet_vacxin.append((0,0,{
                                          'so_lo_id': vacxin['id'],
                                          'han_su_dung_rel': vacxin['han_su_dung'],
                                          'so_luong_ton': nhap-xuat,
                                          }))
        if ho_chan_nuoi_id:
            ho = self.pool.get('chan.nuoi').browse(cr,uid,ho_chan_nuoi_id)
            tram_id = ho.company_id.id
            if loai_id and vacxin_id:
                sql = '''
                    select * from chi_tiet_loai_line where tiem_phong='true' and co_cau_id in (select id from co_cau 
                    where ten_ho_id = %s and chon_loai = %s and trang_thai = 'new')
                '''%(ho_chan_nuoi_id, loai_id)
                cr.execute(sql)
                for line in cr.dictfetchall():
                    sql = '''
                        select case when sum(sl_thuc_tiem)!=0 then sum(sl_thuc_tiem) else 0 end sl_thuc_tiem 
                        from ct_tiem_phong_lmlm_line where tp_lmlm_id in (select id from tiem_phong_lmlm 
                        where ho_chan_nuoi_id = %s and loai_id = %s and vacxin_id = %s and trang_thai_id in (select id from trang_thai where stt = 3))
                        and ct_loai_id = %s
                    '''%(ho_chan_nuoi_id, loai_id, vacxin_id, line['ct_loai_id'])
                    cr.execute(sql)
                    sl_thuc_tiem_before = cr.dictfetchone()['sl_thuc_tiem']
                    
                    sql = '''
                        select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong 
                        from chi_tiet_da_tiem_phong where nhap_xuat_tiemphong_id in (select id from nhap_xuat_canh_giasuc 
                        where ten_ho_id = %s and loai_id = %s and loai = 'nhap' and trang_thai_id in (select id from trang_thai where stt = 3))
                        and ct_loai_id = %s and vacxin_id = %s
                    '''%(ho_chan_nuoi_id, loai_id, line['ct_loai_id'], vacxin_id)
                    cr.execute(sql)
                    sl_nhap_tp = cr.dictfetchone()['so_luong']
                    
                    sql = '''
                        select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong 
                        from chi_tiet_da_tiem_phong where nhap_xuat_tiemphong_id in (select id from nhap_xuat_canh_giasuc 
                        where ten_ho_id = %s and loai_id = %s and loai = 'xuat' and trang_thai_id in (select id from trang_thai where stt = 3))
                        and ct_loai_id = %s and vacxin_id = %s
                    '''%(ho_chan_nuoi_id, loai_id, line['ct_loai_id'], vacxin_id)
                    cr.execute(sql)
                    sl_xuat_tp = cr.dictfetchone()['so_luong']
                    
                    sql = '''
                        select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong 
                        from ct_xuly_giasuc_tp_line where xuly_giasuc_id in (select id from xuly_giasuc 
                        where ten_ho_id = %s and loai_id = %s and trang_thai_id in (select id from trang_thai where stt = 3))
                        and ct_loai_id = %s and vacxin_id = %s
                    '''%(ho_chan_nuoi_id, loai_id, line['ct_loai_id'], vacxin_id)
                    cr.execute(sql)
                    so_luong_chet = cr.dictfetchone()['so_luong']
                    chi_tiet.append((0,0,{
                                          'name': line['name'],
                                          'ct_loai_id': line['ct_loai_id'],
                                          'so_luong': line['tong_sl'],
                                          'tiem_phong':line['tiem_phong'],
                                          'sl_mien_dich': sl_thuc_tiem_before + sl_nhap_tp - sl_xuat_tp - so_luong_chet
                                          }))
        return {'value': {'chi_tiet_tp_line': chi_tiet, 'chi_tiet_vaccine_line': chi_tiet_vacxin, 'tram_id': tram_id}}
    
tiem_phong_lmlm()

class ct_tiem_phong_lmlm_line(osv.osv):
    _name = "ct.tiem.phong.lmlm.line"
    
    _columns = {
        'tp_lmlm_id': fields.many2one( 'tiem.phong.lmlm','tiem phong lmlm', ondelete = 'cascade'),
#         'tp_co_cau_id':fields.many2one('co.cau','Co Cau dan'),
        'name': fields.char('Thông tin', readonly = True),
        'ct_loai_id': fields.many2one('chi.tiet.loai.vat','Thông tin'),
        'tiem_phong':fields.boolean('Có được phép tiêm ?'),
        'loai_benh_id': fields.many2one('chi.tiet.loai.benh','Loại bệnh'),
        'so_luong': fields.integer('Tổng đàn', readonly = True),
        'sl_ngoai_dien': fields.integer('Ngoại diện'),
        'sl_mien_dich': fields.integer('Tiêm phòng còn Miễn dịch'),
        'sl_thuc_tiem': fields.integer('Số lượng thực tiêm'),
#         'trang_thai_id_relate': fields.related('tp_lmlm_id','trang_thai_id',type='many2one', relation='trang.thai',string='Trang Thai', store = False),
                }
    _defaults = {
        'tiem_phong':False,
        
                 }    
    def _check_so_luong(self, cr, uid, ids, context=None):
        tong_sl = 0
        for line in self.browse(cr, uid, ids, context=context):
            tong_sl = line.sl_ngoai_dien + line.sl_mien_dich + line.sl_thuc_tiem
            if tong_sl > line.so_luong:
                raise osv.except_osv(_('Warning!'),_('Tổng số lượng của ngoại diện, tiêm phòng còn miễn dịch, số lượng thực tiêm không được lớn hơn số lượng tổng đàn'))
                return False
        return True
    _constraints = [
        (_check_so_luong, 'Identical Data', []),
    ]
ct_tiem_phong_lmlm_line()

class ct_tiem_phong_vaccine_line(osv.osv):
    _name = "ct.tiem.phong.vaccine.line"
    
    _columns = {
        'tp_lmlm_id': fields.many2one( 'tiem.phong.lmlm','tiem phong lmlm', ondelete = 'cascade'),
        'loai_vaccine_id': fields.many2one('loai.vacxin','Loại vaccine'),
        'so_lo_id':fields.many2one('so.lo','Số lô'),
        'han_su_dung_rel':fields.related('so_lo_id','han_su_dung',type='date',string='HSD đến'),
        'so_luong_ton': fields.integer('Số lượng tồn'),
        'so_luong_vc': fields.integer('Số lượng Vaccine'),
#         'trang_thai_id_relate': fields.related('tp_lmlm_id','trang_thai_id',type='many2one', relation='trang.thai',string='Trang Thai'),
                }
    
    def _check_so_luong_ton_vaccine(self, cr, uid, ids, context=None):
        tong_sl = 0
        for line in self.browse(cr, uid, ids, context=context):
            if line.so_luong_vc > line.so_luong_ton:
                raise osv.except_osv(_('Warning!'),_('Số lượng tiêm vaccine lớn hơn số lượng tồn vaccine'))
                return False
        return True
    _constraints = [
        (_check_so_luong_ton_vaccine, 'Identical Data', []),
    ]
    
ct_tiem_phong_vaccine_line()

class ton_vaccine(osv.osv):
    _inherit = "ton.vaccine"
    
    _columns = {
        'lmlm_id': fields.many2one('tiem.phong.lmlm','LMLM'),
                }
    
ton_vaccine()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: