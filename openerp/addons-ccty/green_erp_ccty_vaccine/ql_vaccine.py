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
    _columns = {
        'name': fields.many2one('loai.vacxin','Loại vaccine', required = True, states={ 'done':[('readonly', True)]}),
        'can_bo_id': fields.many2one('can.bo','Cán bộ nhập máy', required = True, states={ 'done':[('readonly', True)]}),
        'ngay_nhap': fields.date('Ngày nhập xuất', states={ 'done':[('readonly', True)]}),
        'soluong': fields.char('Số lượng',size = 50, states={ 'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Nháp'),('done', 'Duyệt')],'Status', readonly=True),
                }
    _defaults = {
        'state': 'draft',
                 }
    def bt_duyet(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'done'})
nhap_vaccine()

    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
