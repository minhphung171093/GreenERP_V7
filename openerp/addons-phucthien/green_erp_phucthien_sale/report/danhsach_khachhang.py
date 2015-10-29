# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
from datetime import date
from dateutil.rrule import rrule, DAILY

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'convert_date': self.convert_date,
            'get_lines': self.get_lines,
            'display_address': self.display_address,
        })
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        categ_ids = wizard_data['categ_ids']
        sql = '''
            select rp.internal_code as ma_kh, rp.name as ten_kh, rp.id as partner_id, rp.vat as mst,
                rpu.name as tdv
                from res_partner rp
                left join res_users ru on rp.user_id=ru.id 
                left join res_partner rpu on ru.partner_id = rpu.id 
                where rp.customer='t' and rp.is_company='t' 
        '''
        if categ_ids:
            categ_obj = self.pool.get('product.category')
            categ_ids = categ_obj.search(self.cr, self.uid, [('parent_id','child_of',categ_ids)])
            categ_ids = str(categ_ids).replace('[', '(')
            categ_ids = str(categ_ids).replace(']', ')')
            sql+='''
                and rp.id in (select partner_id from sale_order
                    where id in (select order_id from sale_order_line
                        where product_id in (select id from product_product
                            where product_tmpl_id in (select id from product_template
                                where categ_id in %s))))
            '''%(categ_ids)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def display_address(self, partner_id):
        partner = self.pool.get('res.partner').browse(self.cr, self.uid, partner_id)
        address = partner.street and partner.street + ' , ' or ''
        address += partner.street2 and partner.street2 + ' , ' or ''
        address += partner.city and partner.city.name + ' , ' or ''
        if address:
            address = address[:-3]
        return address
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

