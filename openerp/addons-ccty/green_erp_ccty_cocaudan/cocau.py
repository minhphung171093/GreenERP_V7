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
        'chon_loai': fields.many2one('loai.vat','Chọn loài'),
        'can_bo_ghi_so_id': fields.many2one( 'can.bo','Cán bộ ghi sổ'),
        'ngay_ghi_so': fields.date('Ngày ghi sổ'),
        'tang_giam': fields.selection((('a','Tăng'), ('b','Giảm')),'Tăng/Giảm'),
        'ly_do': fields.char('Lý do tăng giảm',size = 50),
        'ten_ho_id': fields.many2one( 'chan.nuoi','Chọn hộ'),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)',domain="[('quan_huyen_id','=',quan_huyen_id)]"),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)',domain="[('phuong_xa_id','=',phuong_xa_id)]"),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)'),
                }
co_cau()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
