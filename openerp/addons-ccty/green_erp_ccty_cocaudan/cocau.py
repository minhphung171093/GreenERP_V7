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
        'chon_loai': fields.many2one('loai.vat','Chọn loài', required = True),
        'can_bo_id': fields.many2one( 'res.users','Cán bộ thú y nhập', readonly = True),
        'can_bo_ghi_so': fields.char('Cán bộ ghi sổ'),
        'ngay_ghi_so': fields.date('Ngày ghi sổ', required = True),
        'tang_giam': fields.selection((('a','Tăng'), ('b','Giảm')),'Tăng/Giảm', required = True),
        'ly_do': fields.char('Lý do tăng giảm',size = 50),
        'ten_ho_id': fields.many2one('chan.nuoi','Hộ', required = True),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)'),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)'),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)'),
        'chitiet_loai':fields.one2many('chi.tiet.loai.line','co_cau_id','Co Cau'),
        'company_id': fields.many2one( 'res.company','Company', readonly = True),
        'trang_thai': fields.selection((('old','Old'), ('new','New')),'Trang thai'),
        'trang_thai_id': fields.many2one('trang.thai','Trạng thái', readonly=True),
        'hien_an': fields.function(_get_hien_an, type='boolean', string='Hien/An'),
                }
    _defaults = {
        'can_bo_id': _get_user,
        'company_id': _get_company,
        'trang_thai': 'new',
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
    
    def create(self, cr, uid, vals, context=None):
        sql = '''
            select id from co_cau where chon_loai = %s and ten_ho_id = %s
        '''%(vals['chon_loai'], vals['ten_ho_id'])
        cr.execute(sql)
        co_cau_ids = cr.fetchall()
        if co_cau_ids:
            cr.execute("update co_cau set trang_thai = 'old' where id in %s",(tuple(co_cau_ids),))
        new_id = super(co_cau, self).create(cr, uid, vals, context)
        return new_id  
    
    def onchange_chon_loai(self, cr, uid, ids, chon_loai = False, ten_ho_id = False, context=None):
        chi_tiet= []
        for co_cau in self.browse(cr,uid,ids):
            sql = '''
                delete from chi_tiet_loai_line where co_cau_id = %s
            '''%(co_cau.id)
            cr.execute(sql)
        if chon_loai and ten_ho_id:
            loai = self.pool.get('loai.vat').browse(cr,uid,chon_loai)    
            for line in loai.chitiet_loaivat:
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end tong_sl from chi_tiet_loai_line
                    where co_cau_id in (select id from co_cau where chon_loai = %s and ten_ho_id = %s and tang_giam = 'a')
                    and name = '%s'
                '''%(chon_loai, ten_ho_id, line.name)
                cr.execute(sql)
                tong_sl = cr.dictfetchone()['tong_sl']
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end tong_sl_giam from chi_tiet_loai_line
                    where co_cau_id in (select id from co_cau where chon_loai = %s and ten_ho_id = %s and tang_giam = 'b')
                    and name = '%s'
                '''%(chon_loai, ten_ho_id, line.name)
                cr.execute(sql)
                tong_sl_giam = cr.dictfetchone()['tong_sl_giam']
                chi_tiet.append((0,0,{
                                      'name': line.name,
                                      'tong_sl': tong_sl-tong_sl_giam,
                                      }))
        return {'value': {'chitiet_loai': chi_tiet}}
co_cau()

class chi_tiet_loai_line(osv.osv):
    _name = "chi.tiet.loai.line"
    
    def sum_so_luong(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end tong_sl from chi_tiet_loai_line
                where co_cau_id in (select id from co_cau where chon_loai = %s and ten_ho_id = %s and tang_giam = 'a')
                and name = '%s'
            '''%(line.co_cau_id.chon_loai.id, line.co_cau_id.ten_ho_id.id, line.name)
            cr.execute(sql)
            tong_sl = cr.dictfetchone()['tong_sl']
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end tong_sl_giam from chi_tiet_loai_line
                where co_cau_id in (select id from co_cau where chon_loai = %s and ten_ho_id = %s and tang_giam = 'b')
                and name = '%s'
            '''%(line.co_cau_id.chon_loai.id, line.co_cau_id.ten_ho_id.id, line.name)
            cr.execute(sql)
            tong_sl_giam = cr.dictfetchone()['tong_sl_giam']
            res[line.id] = tong_sl - tong_sl_giam
        return res
    
    _columns = {
        'co_cau_id': fields.many2one( 'co.cau','Co cau', ondelete = 'cascade'),
        'name': fields.char('Thông tin', readonly = True),
        'tong_sl':fields.function(sum_so_luong,type='float',string='Tổng số lượng(hiện có)', store = True),
        'so_luong': fields.float('Số lượng'),
                }
chi_tiet_loai_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
