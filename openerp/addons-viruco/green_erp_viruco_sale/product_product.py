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


class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
        'chatluong_id':fields.many2one('chatluong.sanpham','Chất lượng',size=1024),
        'quycach_donggoi_id':fields.many2one('quycach.donggoi','Quy cách đóng gói'),
        'quycach_baobi_id':fields.many2one('quycach.donggoi','Quy cách bao bì'),
        'nha_sanxuat_id':fields.many2one('nha.sanxuat','Nhà sản xuất'),
        'nuoc_sanxuat_id':fields.many2one('res.country','Nước sản xuất'),
    }
    
product_product()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
