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
        self.tong_tien = 0
        self.tong_exim = 0
        self.tong_acb = 0
        self.tong_agr = 0
        self.localcontext.update({
            'convert_date': self.convert_date,
            'get_period_name': self.get_period_name,
            'get_lines': self.get_lines, 
            'display_address': self.display_address,
            'get_tong':self.get_tong,
            'get_date_from':self.get_date_from,
            'get_date_to': self.get_date_to,
        })
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
        
    def get_period_name(self):
        wizard_data = self.localcontext['data']['form']
        period_id = wizard_data['period_id'] 
        period_name = ''
        if period_id:
            period_name = self.pool.get('account.period').browse(self.cr,self.uid,period_id[0]).name
        return period_name
    
    def display_address(self, partner_id):
        partner = self.pool.get('res.partner').browse(self.cr, self.uid, partner_id)
        address = partner.street and partner.street + ' , ' or ''
        address += partner.street2 and partner.street2 + ' , ' or ''
        address += partner.city and partner.city.name + ' , ' or ''
        if address:
            address = address[:-3]
        return address
    
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
#         period_id = wizard_data['period_id']    
        user_ids = wizard_data['user_ids']
        date_from = wizard_data['date_from']   
        date_to = wizard_data['date_to']  
        invoice_obj = self.pool.get('account.invoice') 
        period_obj = self.pool.get('account.period')
#         period_start = period_obj.browse(self.cr,self.uid,period_id[0]).date_start
#         period_stop = period_obj.browse(self.cr,self.uid,period_id[0]).date_stop
        cus_ids = []
        res = []
        inv_ids = []
        if not user_ids:
            sql ='''
             select id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                            from product_product,product_template 
                            where product_template.categ_id in (select id from product_category where code ='MP') 
                            and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                (select id from account_invoice where date_invoice between '%s' and '%s'  and type ='out_invoice' and state in ('open','paid')))
                            order by date_invoice
            '''%(date_from,date_to)
            self.cr.execute(sql)   
            inv_ids = [r[0] for r in self.cr.fetchall()]
        else:
            user_ids = str(user_ids).replace("[","(")
            user_ids = str(user_ids).replace("]",")")
            sql = '''
                select id from res_partner where user_id in %s and customer is True
            '''%(user_ids)
            self.cr.execute(sql)
            cus_ids = [r[0] for r in self.cr.fetchall()]  
            if cus_ids:
                cus_ids = str(cus_ids).replace("[","(")
                cus_ids = str(cus_ids).replace("]",")")
                sql ='''
                 select id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                                from product_product,product_template 
                                where product_template.categ_id in (select id from product_category where code ='MP') 
                                and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                    (select id from account_invoice where date_invoice between '%s' and '%s'  and type ='out_invoice' and state in ('open','paid')))
                                and partner_id in %s
                '''%(date_from,date_to,cus_ids)
                self.cr.execute(sql)   
                inv_ids = [r[0] for r in self.cr.fetchall()] 
        if inv_ids:
            for inv in inv_ids:
                tien_mat = 0
                exim = 0
                acb = 0 
                agr = 0
                ngay_tt = ''
                so_ngay_no = 0
                sql = ''' 
                    select date_invoice, reference_number, amount_total, rp.name as cus, rp.id as cus_id, rp.internal_code as code from account_invoice ai, res_partner rp 
                        where ai.partner_id = rp.id and ai.id = %s 
                        
                '''%(inv)
                self.cr.execute(sql) 
                inv_id = self.cr.dictfetchone()
                
                sql = '''
                    select case when sum(residual)!=0 then sum(residual) else 0 end nodk from account_invoice 
                    where state='open' and date_invoice < '%s' and partner_id = %s
                '''%(date_from,inv_id['cus_id'])
                self.cr.execute(sql) 
                nodk = self.cr.fetchone()[0]
                invoice_id = invoice_obj.browse(self.cr,self.uid,inv)
                nock = nodk + (invoice_id.residual and invoice_id.residual or 0)
                tdv_name = self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).user_id and self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).user_id.name or ''
                kv = self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).kv_benh_vien and self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).kv_benh_vien.name or ''
                for pay in invoice_id.payment_ids:
                    if pay.journal_id.code == '11':
                        tien_mat += pay.credit
                        self.tong_tien += tien_mat
                    if pay.journal_id.code == '12':
                        acb += pay.credit
                        self.tong_acb += acb
                    if pay.journal_id.code == '13':
                        exim += pay.credit
                        self.tong_exim += exim
                    if pay.journal_id.code == '16':
                        agr += pay.credit 
                        self.tong_agr += agr
                    if ngay_tt < pay.date:
                        ngay_tt = pay.date
                sql='''
                    select ma.name from account_invoice_line acc, product_product pr , manufacturer_product ma
                    where invoice_id = %s and acc.product_id = pr.id and ma.id = pr.manufacturer_product_id
                '''%(inv)
                self.cr.execute(sql) 
                hang_sx = self.cr.fetchone() or False
                if invoice_id.state != 'paid':
                    sql='''
                        select case when ('%s'::date - date_invoice)!=0 then ('%s'::date - date_invoice) else 0 end ngayno from account_invoice where id = %s
                    '''%(date_to,date_to,inv)
                    self.cr.execute(sql) 
                    so_ngay_no = self.cr.fetchone()[0]
                res.append({'cus_name': inv_id['cus'],
                            'dia_chi': inv_id['cus_id'] and self.display_address(inv_id['cus_id']) or '',
                            'ngay_xuat': inv_id['date_invoice'] and self.convert_date(inv_id['date_invoice']) or '',
                            'date_invoice':inv_id['date_invoice'],
                            'reference_number':inv_id['reference_number'],
                            'internal_code':inv_id['code'],
                            'nodk': nodk,
                            'phatsinh':float(inv_id['amount_total']),
                            'tienmat': tien_mat,
                            'acb': acb,
                            'exim': exim,
                            'agr': agr,
                            'nock': nock,
                            'ngay_tt': ngay_tt and self.convert_date(ngay_tt) or '',
                            'tdv_name': tdv_name,
                            'kv': kv,
                            'hang_sx': hang_sx and hang_sx[0] or '',
                            'so_ngay_no':so_ngay_no,
                            })
                
        return res
    
    def get_tong(self):
        wizard_data = self.localcontext['data']['form']
#         period_id = wizard_data['period_id']    
        user_ids = wizard_data['user_ids']
        invoice_obj = self.pool.get('account.invoice') 
        period_obj = self.pool.get('account.period')
        date_from = wizard_data['date_from']   
        date_to = wizard_data['date_to']  
#         period_start = period_obj.browse(self.cr,self.uid,period_id[0]).date_start
#         period_stop = period_obj.browse(self.cr,self.uid,period_id[0]).date_stop
        cus_ids = []
        res = {}
        inv_ids = []
        customer_ids = []
        if not user_ids:
            sql ='''
             select id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                            from product_product,product_template 
                            where product_template.categ_id in (select id from product_category where code ='MP') 
                            and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                (select id from account_invoice where date_invoice between '%s' and '%s'  and type ='out_invoice' and state in ('open','paid')))
            '''%(date_from,date_to)
            self.cr.execute(sql)   
            inv_ids = [r[0] for r in self.cr.fetchall()]
            if inv_ids:
                inv_ids = str(inv_ids).replace("[","(")
                inv_ids = str(inv_ids).replace("]",")")
                sql='''
                    select partner_id from account_invoice where id in %s
                '''%(inv_ids)
                self.cr.execute(sql)   
                customer_ids = [r[0] for r in self.cr.fetchall()]
        else:
            user_ids = str(user_ids).replace("[","(")
            user_ids = str(user_ids).replace("]",")")
            sql = '''
                select id from res_partner where user_id in %s and customer is True
            '''%(user_ids)
            self.cr.execute(sql)
            cus_ids = [r[0] for r in self.cr.fetchall()]  
            if cus_ids:
                cus_ids = str(cus_ids).replace("[","(")
                cus_ids = str(cus_ids).replace("]",")")
                sql ='''
                 select id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                                from product_product,product_template 
                                where product_template.categ_id in (select id from product_category where code ='MP') 
                                and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                    (select id from account_invoice where date_invoice between '%s' and '%s'  and type ='out_invoice' and state in ('open','paid')))
                                and partner_id in %s
                '''%(date_from,date_to,cus_ids)
                self.cr.execute(sql)   
                inv_ids = [r[0] for r in self.cr.fetchall()] 
                if inv_ids:
                    inv_ids = str(inv_ids).replace("[","(")
                    inv_ids = str(inv_ids).replace("]",")")
                    sql='''
                        select partner_id from account_invoice where id in %s
                    '''%(inv_ids)
                    self.cr.execute(sql)   
                    customer_ids = [r[0] for r in self.cr.fetchall()]
        if customer_ids:
            customer_ids = str(customer_ids).replace("[","(")
            customer_ids = str(customer_ids).replace("]",")")
            sql = '''
                select case when sum(residual)!=0 then sum(residual) else 0 end nodk from account_invoice 
                where state='open' and date_invoice < '%s' and partner_id in %s
            '''%(date_from,customer_ids)
            self.cr.execute(sql) 
            tong_nodk = self.cr.fetchone()[0]
            if inv_ids:
                sql = '''
                    select case when sum(amount_total)!=0 then sum(amount_total) else 0 end phatsinh, case when sum(residual)!=0 then sum(residual) else 0 end notrongki from account_invoice 
                    where state in ('open','paid') and date_invoice between '%s' and '%s' and id in %s
                '''%(date_from,date_to,inv_ids)
                self.cr.execute(sql) 
                tong =self.cr.fetchone()
                tong_phatsinh = tong[0]
                tong_notrongki = tong[1]
                tong_no_ck = tong_nodk + tong_notrongki
                res.update({'tong_nodk':tong_nodk,
                            'tong_phatsinh':tong_phatsinh,
                            'tong_tien':self.tong_tien,
                            'tong_exim':self.tong_exim,
                            'tong_acb':self.tong_acb,
                            'tong_agr':self.tong_agr,
                            'tong_no_ck': tong_no_ck,
                            })
        return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

