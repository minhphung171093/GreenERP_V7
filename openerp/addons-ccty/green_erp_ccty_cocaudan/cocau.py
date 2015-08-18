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
    _columns = {
        'chon_loai': fields.many2one('loai.vat','Chọn loài', required = True),
        'can_bo_ghi_so_id': fields.many2one('res.users','Cán bộ ghi sổ'),
        'ngay_ghi_so': fields.date('Ngày ghi sổ', required = True),
        'tang_giam': fields.selection((('a','Tăng'), ('b','Giảm')),'Tăng/Giảm'),
        'ly_do': fields.char('Lý do tăng giảm',size = 50),
        'ten_ho_id': fields.many2one('chan.nuoi','Hộ'),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)'),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)'),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)'),
        'chitiet_loai':fields.one2many('chi.tiet.loai.line','co_cau_id','Co Cau'),
        'company_id': fields.many2one( 'res.company','Company'),
        'trang_thai': fields.selection((('old','Old'), ('new','New')),'Trang thai'),
                }
    _defaults = {
        'company_id': _get_company,
        'trang_thai': 'new',
                 }
    
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
    
    def onchange_chon_loai(self, cr, uid, ids, chon_loai = False, context=None):
        chi_tiet= []
        for co_cau in self.browse(cr,uid,ids):
            sql = '''
                delete from chi_tiet_loai_line where co_cau_id = %s
            '''%(co_cau.id)
            cr.execute(sql)
        if chon_loai:
            loai = self.pool.get('loai.vat').browse(cr,uid,chon_loai)    
            for line in loai.chitiet_loaivat:
                chi_tiet.append((0,0,{
                                      'name': line.name
                                      }))
        return {'value': {'chitiet_loai': chi_tiet}}
co_cau()

class chi_tiet_loai_line(osv.osv):
    _name = "chi.tiet.loai.line"
    
    def sum_so_luong(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            amount = 0
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end tong_sl from chi_tiet_loai_line
                where co_cau_id in (select id from co_cau where chon_loai = %s and ten_ho_id = %s and ngay_ghi_so <= '%s')
                and name = '%s'
            '''%(line.co_cau_id.chon_loai.id, line.co_cau_id.ten_ho_id.id, line.co_cau_id.ngay_ghi_so, line.name)
            cr.execute(sql)
            tong_sl = cr.dictfetchone()['tong_sl']
            res[line.id] = tong_sl
        return res
    
    _columns = {
        'co_cau_id': fields.many2one( 'co.cau','Co cau', ondelete = 'cascade'),
        'name': fields.char('Thông tin', readonly = True),
        'tong_sl':fields.function(sum_so_luong,type='float',string='Tổng số lượng(hiện có)', store = True),
        'so_luong': fields.float('Số lượng'),
                }
chi_tiet_loai_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
