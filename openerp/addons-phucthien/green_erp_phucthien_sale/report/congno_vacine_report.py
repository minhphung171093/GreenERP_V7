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
            'get_date_from':self.get_date_from,
            'get_month_year': self.get_month_year,
            'get_lines': self.get_lines,
        })
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_month_year(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%m/%Y')
    
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']    
        user_ids = wizard_data['user_id']
        invoice_obj = self.pool.get('account.invoice')
        cus_ids = []
        res = []
        if not user_ids:
            sql ='''
             select partner_id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                            from product_product,product_template 
                            where product_template.categ_id in (select id from product_category where code ='VC') 
                            and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                (select id from account_invoice where date_invoice <= '%s' and type ='out_invoice' and state ='open'))
            '''%(date_from)
            self.cr.execute(sql)   
            cus_ids = [r[0] for r in self.cr.fetchall()]
        else:
            user_ids = str(user_ids).replace("[","(")
            user_ids = str(user_ids).replace("]",")")
            sql = '''
                select id from res_partner where user_id in %s and customer is True
            '''%(user_ids)
            self.cr.execute(sql)
            cus_ids = [r[0] for r in self.cr.fetchall()]  
        if cus_ids:
            for cus in cus_ids:
                sql = ''' 
                    select case when sum(residual)!=0 then sum(residual) else 0 end sum30 from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                                from product_product,product_template 
                                where product_template.categ_id in (select id from product_category where code ='VC') 
                                and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                    (select id from account_invoice where date_invoice <= '%s' and type ='out_invoice' and state ='open'))
                                    and ('%s'::date - date_invoice) <= 30 and partner_id = %s
                '''%(date_from,date_from,cus)
                self.cr.execute(sql) 
                sum30 = self.cr.fetchone()[0]
                
                sql = ''' 
                    select case when sum(residual)!=0 then sum(residual) else 0 end sum30 from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                                from product_product,product_template 
                                where product_template.categ_id in (select id from product_category where code ='VC') 
                                and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                    (select id from account_invoice where date_invoice <= '%s' and type ='out_invoice' and state ='open'))
                                    and ('%s'::date - date_invoice)>=31 and ('%s'::date - date_invoice)<=45 and partner_id = %s
                '''%(date_from,date_from,date_from,cus)
                self.cr.execute(sql) 
                sum31 = self.cr.fetchone()[0]
                
                sql = ''' 
                    select case when sum(residual)!=0 then sum(residual) else 0 end sum30 from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                                from product_product,product_template 
                                where product_template.categ_id in (select id from product_category where code ='VC') 
                                and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                    (select id from account_invoice where date_invoice <= '%s' and type ='out_invoice' and state ='open'))
                                    and ('%s'::date - date_invoice)>=46 and ('%s'::date - date_invoice)<=60 and partner_id = %s
                '''%(date_from,date_from,date_from,cus)
                self.cr.execute(sql) 
                sum46 = self.cr.fetchone()[0]
                
                sql = ''' 
                    select case when sum(residual)!=0 then sum(residual) else 0 end sum30 from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                                from product_product,product_template 
                                where product_template.categ_id in (select id from product_category where code ='VC') 
                                and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                    (select id from account_invoice where date_invoice <= '%s' and type ='out_invoice' and state ='open'))
                                    and ('%s'::date - date_invoice)>=61 and ('%s'::date - date_invoice)<=90 and partner_id = %s
                '''%(date_from,date_from,date_from,cus)
                self.cr.execute(sql) 
                sum61 = self.cr.fetchone()[0]
                
                sql = ''' 
                    select case when sum(residual)!=0 then sum(residual) else 0 end sum30 from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                                from product_product,product_template 
                                where product_template.categ_id in (select id from product_category where code ='VC') 
                                and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                    (select id from account_invoice where date_invoice <= '%s' and type ='out_invoice' and state ='open'))
                                    and ('%s'::date - date_invoice)>=91 and partner_id = %s
                '''%(date_from,date_from,cus)
                self.cr.execute(sql) 
                sum91 = self.cr.fetchone()[0]
#                 sql = '''
#                     select res_partner.name as cus, res_users.name as nv from res_partner,res_users where id = %s
#                 '''%(cus)
#                 self.cr.execute(sql) 
#                 cus_name = self.cr.fetchone()[0] or ''
                
                cus_name = self.pool.get('res.partner').browse(self.cr,self.uid,cus).name 
                tdv_name = self.pool.get('res.partner').browse(self.cr,self.uid,cus).user_id and self.pool.get('res.partner').browse(self.cr,self.uid,cus).user_id.name or ''
                kv = self.pool.get('res.partner').browse(self.cr,self.uid,cus).kv_benh_vien and self.pool.get('res.partner').browse(self.cr,self.uid,cus).kv_benh_vien.name or ''
                res.append({'cus_name': cus_name,
                            'sum30':sum30,
                            'sum31':sum31,
                            'sum46':sum46,
                            'sum61':sum61,
                            'sum91':sum91,
                            'no_qh': sum31 + sum46 + sum61 + sum91,
                            'kv': kv,
                            'tong_no': sum30 + sum31 + sum46 + sum61 + sum91,
                            'tdv': tdv_name,})
        return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

