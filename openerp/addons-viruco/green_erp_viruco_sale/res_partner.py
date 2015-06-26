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


class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'ma_kh':fields.char('Mã khách hàng', size=1024),
        'loaihinh_kinhdoanh':fields.char('Loại hình kinh doanh', size=1024),
        'is_giaodichtructiep':fields.boolean('Giao dịch trực tiếp'),
        'nha_moigioi_id':fields.many2one('res.partner','Nhà môi giới'),
    }
    
res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
