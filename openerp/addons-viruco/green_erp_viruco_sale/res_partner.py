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
    
    def _construct_constraint_msg(self, cr, uid, ids, context=None):
#         def default_vat_check(cn, vn):
#             # by default, a VAT number is valid if:
#             #  it starts with 2 letters
#             #  has more than 3 characters
#             return cn[0] in string.ascii_lowercase and cn[1] in string.ascii_lowercase
#         vat_country, vat_number = self._split_vat(self.browse(cr, uid, ids)[0].vat)
#         vat_no = "'CC##' (CC=Country Code, ##=VAT Number)"
#         if default_vat_check(vat_country, vat_number):
#             vat_no = _ref_vat[vat_country] if vat_country in _ref_vat else vat_no
#             if self.pool['res.users'].browse(cr, uid, uid).company_id.vat_check_vies:
#                 return '\n' + _('This VAT number either failed the VIES VAT validation check or did not respect the expected format %s.') % vat_no
#         return '\n' + _('This VAT number does not seem to be valid.\nNote: the expected format is %s') % vat_no
        return True
    
    def check_vat(self, cr, uid, ids, context=None):
#         user_company = self.pool.get('res.users').browse(cr, uid, uid).company_id
#         if user_company.vat_check_vies:
#             # force full VIES online check
#             check_func = self.vies_vat_check
#         else:
#             # quick and partial off-line checksum validation
#             check_func = self.simple_vat_check
#         for partner in self.browse(cr, uid, ids, context=context):
#             if not partner.vat:
#                 continue
#             vat_country, vat_number = self._split_vat(partner.vat)
#             if not check_func(cr, uid, vat_country, vat_number, context=context):
#                 return False
        return True
    
    _constraints = [(check_vat, _construct_constraint_msg, ["vat"])]
    
res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
