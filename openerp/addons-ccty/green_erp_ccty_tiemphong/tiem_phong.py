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
        'name': fields.datetime('Ngày tiêm', required = True),
        'loai_id': fields.many2one('loai.vat','Loài vật', required = True ),
        'tram_id': fields.many2one( 'res.company','Trạm'),
        'can_bo_id': fields.many2one( 'res.users','Cán bộ thú y nhập'),
        'can_bo_tiem': fields.char('Cán bộ thú y thực hiện tiêm', size = 100),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)'),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)'),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)'),
        'ho_chan_nuoi_id': fields.many2one( 'chan.nuoi','Hộ chăn nuôi'),
        'chi_tiet_tp_line':fields.one2many('ct.tiem.phong.lmlm.line','tp_lmlm_id','Chi tiết tiêm phòng'),
        'chi_tiet_vaccine_line':fields.one2many('ct.tiem.phong.vaccine.line','tp_lmlm_id','Chi tiết Vaccine'),
        'state':fields.selection([('draft', 'Nháp'),('done', 'Duyệt')],'Status', readonly=True),
        'trang_thai_id': fields.many2one('trang.thai','Trạng thái'),
        'hien_an': fields.function(_get_hien_an, type='boolean', string='Hien/An'),
        'chinh_sua_rel': fields.related('trang_thai_id', 'chinh_sua', type="selection",
                selection=[('nhap', 'Nháp'),('in', 'Đang xử lý'), ('ch_duyet', 'Cấp Huyện Duyệt'), ('cc_duyet', 'Chi Cục Duyệt'), ('huy', 'Hủy bỏ')], 
                string="Chinh Sua", readonly=True, select=True),
                }
    _defaults = {
        'can_bo_id': _get_user,
        'tram_id': _get_company,
        'trang_thai_id': get_trangthai_nhap,
                 }
    
    def _check_sl_ton_vaccine(self, cr, uid, ids, context=None):
        for tiem_phong in self.browse(cr, uid, ids, context=context):
            for vaccine in tiem_phong.chi_tiet_vaccine_line:
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
                                                              'lmlm_id': vaccine.tp_lmlm_id.id,
                                                              'ngay': vaccine.tp_lmlm_id.name,
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
                                                              'lmlm_id': vaccine.tp_lmlm_id.id,
                                                              'ngay': vaccine.tp_lmlm_id.name,
                                                                 })
        return True
    
    def onchange_ho_chan_nuoi_id(self, cr, uid, ids, ho_chan_nuoi_id = False, loai_id = False, context=None):
        chi_tiet= []
        for lmlm in self.browse(cr,uid,ids):
            sql = '''
                delete from ct_tiem_phong_lmlm_line where tp_lmlm_id = %s
            '''%(lmlm.id)
            cr.execute(sql)
        if ho_chan_nuoi_id and loai_id:
            sql = '''
                select * from chi_tiet_loai_line where co_cau_id in (select id from co_cau 
                where ten_ho_id = %s and chon_loai = %s and trang_thai = 'new')
            '''%(ho_chan_nuoi_id, loai_id)
            cr.execute(sql)
            for line in cr.dictfetchall():
                chi_tiet.append((0,0,{
                                      'name': line['name'],
                                      'so_luong': line['tong_sl']
                                      }))
        return {'value': {'chi_tiet_tp_line': chi_tiet}}

tiem_phong_lmlm()

class ct_tiem_phong_lmlm_line(osv.osv):
    _name = "ct.tiem.phong.lmlm.line"
    
    _columns = {
        'tp_lmlm_id': fields.many2one( 'tiem.phong.lmlm','tiem phong lmlm', ondelete = 'cascade'),
        'name': fields.char('Thông tin', readonly = True),
        'so_luong': fields.float('Tổng đàn', readonly = True),
        'sl_ngoai_dien': fields.float('Ngoại diện'),
        'sl_mien_dich': fields.float('Tiêm phòng còn Miễn dịch'),
        'sl_thuc_tiem': fields.float('Số lượng thực tiêm'),
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
        'so_luong_vc': fields.float('Số lượng Vaccine'),
                }
    
ct_tiem_phong_vaccine_line()

class ton_vaccine(osv.osv):
    _inherit = "ton.vaccine"
    
    _columns = {
        'lmlm_id': fields.many2one('tiem.phong.lmlm','LMLM'),
                }
    
ton_vaccine()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
