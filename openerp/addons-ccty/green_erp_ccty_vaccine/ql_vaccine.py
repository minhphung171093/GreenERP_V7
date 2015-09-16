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


class nhap_vaccine(osv.osv):
    _name = "nhap.vaccine"
    
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
        'name': fields.many2one('loai.vacxin','Loại vaccine', required = True),
        'can_bo_id': fields.many2one('res.users','Cán bộ nhập máy'),
        'ngay_nhap': fields.date('Ngày nhập'),
        'soluong': fields.integer('Số lượng'),
        'so_lo_id':fields.many2one('so.lo','Số lô', required = True),
        'han_su_dung':fields.related('so_lo_id','han_su_dung',type='date',string='HSD đến'),
        'state':fields.selection([('draft', 'Nháp'),('done', 'Duyệt')],'Status', readonly=True),
        'trang_thai_id': fields.many2one('trang.thai','Trạng thái', readonly=True),
        'hien_an': fields.function(_get_hien_an, type='boolean', string='Hien/An'),
        'chinh_sua_rel': fields.related('trang_thai_id', 'chinh_sua', type="selection",
                selection=[('nhap', 'Nháp'),('in', 'Đang xử lý'), ('ch_duyet', 'Cấp Huyện Duyệt'), ('cc_duyet', 'Chi Cục Duyệt'), ('huy', 'Hủy bỏ')], 
                string="Chinh Sua", readonly=True, select=True),
                }
    _defaults = {
        'can_bo_id': _get_user,
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
                self.pool.get('ton.vaccine').create(cr,uid, {
                                                          'vaccine_id': line.name.id,
                                                          'so_lo_id': line.so_lo_id.id,
                                                          'so_luong': line.soluong,
                                                          'loai': 'nhap',
                                                          'nhap_vaccine_id': line.id,
                                                          'ngay': line.ngay_nhap,
                                                             })
                
            elif line.trang_thai_id.stt == 2 and user.company_id.cap == 'chi_cuc':
                sql = '''
                    select id from trang_thai where stt = 3
                '''
                cr.execute(sql)
                self.write(cr,uid,ids,{
                                       'trang_thai_id': cr.dictfetchone()['id'] or False
                                       })
                self.pool.get('ton.vaccine').create(cr,uid, {
                                                          'vaccine_id': line.name.id,
                                                          'so_lo_id': line.so_lo_id.id,
                                                          'so_luong': line.soluong,
                                                          'loai': 'nhap',
                                                          'nhap_vaccine_id': line.id,
                                                          'ngay': line.ngay_nhap,
                                                             })
        return True
    
nhap_vaccine()

class so_lo(osv.osv):
    _name = "so.lo"
    _columns = {
        'name': fields.char('Số lô',size = 50),
        'han_su_dung':fields.date('HSD đến ngày'),
        'vacxin_id': fields.many2one('loai.vacxin','Loại vaccine', required = True),
                }
    
    def _check_so_lo(self, cr, uid, ids, context=None):
        for so_lo in self.browse(cr, uid, ids, context=context):
            so_lo_ids = self.search(cr,uid,[('id', '!=', so_lo.id), ('name', '=', so_lo.name), ('vacxin_id', '=', so_lo.vacxin_id.id)])
            if so_lo_ids:
                raise osv.except_osv(_('Warning!'),_('Số lô không được trùng nhau'))
                return False
        return True
         
    _constraints = [
        (_check_so_lo, 'Identical Data', []),
    ]   
so_lo()   

class ton_vaccine(osv.osv):
    _name = "ton.vaccine"
    _columns = {
        'vaccine_id': fields.many2one('loai.vacxin','Loại vaccine'),
        'so_lo_id': fields.many2one('so.lo','Số lô'),
        'ngay': fields.date('Ngày'),
        'so_luong':fields.integer('Số lượng'),
        'loai': fields.selection([('nhap', 'Nhập'),('xuat', 'Xuất')],'Loại', readonly=True),
        'nhap_vaccine_id': fields.many2one('nhap.vaccine','Nhap vaccine'),
                }
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ton_vaccine_view')
        cr.execute("""
            create or replace view ton_vaccine_view as (
                select
                   min(t_vc.id) as id,
                    t_vc.vaccine_id as vaccine_id,
                    t_vc.so_lo_id as so_lo_id,
                    t_vc.so_luong as so_luong,
                    t_vc.ngay as ngay
  
                from
                    ton_vaccine t_vc
                      
                  
              
                group by
                    t_vc.vaccine_id,
                    t_vc.so_lo_id,
                    t_vc.so_luong,
                    t_vc.ngay
            )
        """)
ton_vaccine() 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
