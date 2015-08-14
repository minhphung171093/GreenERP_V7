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
    _columns = {
        'chon_loai': fields.many2one('loai.vat','Chọn loài', required = True),
        'can_bo_ghi_so_id': fields.many2one( 'can.bo','Cán bộ ghi sổ'),
        'ngay_ghi_so': fields.date('Ngày ghi sổ'),
        'tang_giam': fields.selection((('a','Tăng'), ('b','Giảm')),'Tăng/Giảm'),
        'ly_do': fields.char('Lý do tăng giảm',size = 50),
        'ten_ho_id': fields.many2one('chan.nuoi','Hộ'),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)'),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)'),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)'),
        'chitiet_loai':fields.one2many('chi.tiet.loai.line','co_cau_id','Co Cau'),
                }
    
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
    def amount_all_line(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                'tong_so': 0.0,
            }
            sum=0.0
            sum += line.sinh_san + line.thit + line.nghe + line.bo_sua + line.be + line.nai + line.noc + line.theo_me
            res[line.id]['tong_so'] = sum
        return res
    _columns = {
        'co_cau_id': fields.many2one( 'co.cau','Co cau', ondelete = 'cascade'),
        'name': fields.char('Thông tin', readonly = True),
        'so_luong': fields.float('Số lượng'),
#         'tong_so': fields.function(amount_all_line, multi='sums',string='Tổng số')
                }
chi_tiet_loai_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
