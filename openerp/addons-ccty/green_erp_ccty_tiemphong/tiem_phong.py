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
        'tram_id': fields.many2one( 'tram.thu.y','Trạm thú y', required = True),
        'can_bo_id': fields.many2one( 'res.users','Cán bộ thú y thực hiện tiêm'),
        'loai_vaccine_id': fields.many2one('loai.vacxin','Loại vaccine'),
        'loai_vat_id': fields.many2one('loai.vat','Loài vật được tiêm'),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)'),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)'),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)'),
        'ho_chan_nuoi_id': fields.many2one( 'chan.nuoi','Hộ chăn nuôi'),
                }


tiem_phong()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
