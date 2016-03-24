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
        'nha_moigioi':fields.boolean('Nhà môi giới'),
        'donvi_vanchuyen':fields.boolean('Đơn vị vận chuyển'),
        'is_giaodichtructiep':fields.boolean('Giao dịch trực tiếp'),
        'nha_moigioi_id':fields.many2one('res.partner','Nhà môi giới'),
        'nguoi_daidien':fields.char('Người đại diện', size=1024),
        'chuc_vu':fields.char('Chức vụ', size=1024),
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
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_buyer_form_e'):
            buyer_ids = []
            sql = '''
                select id from res_partner
                    where ma_kh LIKE '%DAL'
            '''
            cr.execute(sql)
            buyer_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',buyer_ids)]        
        return super(res_partner, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
        
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if args is None:
            args = []
        args+=['|',('name','ilike',name),('ma_kh','ilike',name)]
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
    
res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
