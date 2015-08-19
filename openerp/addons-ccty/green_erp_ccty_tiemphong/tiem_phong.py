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

    _columns = {
        'name': fields.datetime('Ngày tiêm', required = True, states={ 'done':[('readonly', True)]}),
        'loai_id': fields.many2one('loai.vat','Loài vật', required = True , states={ 'done':[('readonly', True)]}),
        'tram_id': fields.many2one( 'res.company','Trạm', required = True, states={ 'done':[('readonly', True)]}),
        'can_bo_id': fields.many2one( 'res.users','Cán bộ thú y thực hiện tiêm', states={ 'done':[('readonly', True)]}),
        'loai_vaccine_id': fields.many2one('loai.vacxin','Loại vaccine', states={ 'done':[('readonly', True)]}),
        'so_lo_id':fields.many2one('so.lo','Số lô', states={ 'done':[('readonly', True)]}),
        'han_su_dung_rel':fields.related('so_lo_id','han_su_dung',type='date',string='HSD đến', states={ 'done':[('readonly', True)]}),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)', states={ 'done':[('readonly', True)]}),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)', states={ 'done':[('readonly', True)]}),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)', states={ 'done':[('readonly', True)]}),
        'ho_chan_nuoi_id': fields.many2one( 'chan.nuoi','Hộ chăn nuôi', states={ 'done':[('readonly', True)]}),
        'chi_tiet_tp_line':fields.one2many( 'ct.tiem.phong.lmlm.line','tp_lmlm_id','Chi tiết tiêm phòng', states={ 'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Nháp'),('done', 'Duyệt')],'Status', readonly=True),
                }
    _defaults = {
        'state': 'draft',
                 }
    def bt_duyet(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'done'})
    
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
