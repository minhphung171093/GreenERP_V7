# -*- coding: utf-8 -*-
##############################################################################
#
#    HLVSolution, Open Source Management Solution
#
##############################################################################

import time
from report import report_sxw
import pooler
from osv import osv
from tools.translate import _
import random
from datetime import datetime
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
import amount_to_text_vn
import amount_to_text_en

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.company_name = False
        self.company_address = False
        self.vat = False
        self.year = False
        self.start_date = False
        self.end_date = False
        self.company_id = False
        self.localcontext.update({
            'get_vietname_date':self.get_vietname_date, 
            'get_line':self.get_line,
            'get_header':self.get_header,
            'get_company_name':self.get_company_name,
            'get_company_address':self.get_company_address,
            'get_company_vat':self.get_company_vat,
            'get_year': self.get_year,
            'get_quarter_date': self.get_quarter_date,
            'get_start_date':self.get_start_date,
            'get_end_date':self.get_end_date,
            'get_total': self.get_total,
        })
    
    def get_company(self, company_id):
        if company_id:
            company_obj = self.pool.get('res.company').browse(self.cr, self.uid,company_id)
            self.company_name = company_obj.name or ''
            self.company_address = company_obj.street or ''
            self.vat = company_obj.vat or ''
        return True
             
    def get_company_name(self):
        self.get_header()
        return self.company_name
    
    def get_company_address(self):
        return self.company_address     
    
    def get_company_vat(self):
        return self.vat
    
    def get_id(self,get_id):
        wizard_data = self.localcontext['data']['form']
        period_id = wizard_data[get_id][0] or wizard_data[get_id][0] or False
        if not period_id:
            return 1
        else:
            return period_id
        
    def get_quarter_date(self,year,quarter):
        self.start_date = False
        self.end_date  = False
        if quarter == '1':
            self.start_date = '''%s-01-01'''%(year)
            self.end_date = year + '-03-31'
        elif quarter == '2':
            self.start_date = year+'-04-01'
            self.end_date =year+'-06-30'
        elif quarter == '3':
            self.start_date = year+'-07-01'
            self.end_date = year+'-09-30'
        else:
            self.start_date = year+'-10-01'
            self.end_date = year+'-12-31'
    
    def get_year(self):
        return self.year
    
    def get_start_date(self):
        self.get_header()
        return self.get_vietname_date(self.start_date) 
    
    def get_end_date(self):
        return self.get_vietname_date(self.end_date)
    
    def get_header(self):
        wizard_data = self.localcontext['data']['form']
        #Get company info
        self.company_id = wizard_data['company_id'] and wizard_data['company_id'][0] or False
        self.get_company(self.company_id)
        #Get shops
        self.times = wizard_data['times']
        if self.times =='periods':
            self.start_date = self.pool.get('account.period').browse(self.cr,self.uid,self.get_id('period_id_start')).date_start
            self.end_date   = self.pool.get('account.period').browse(self.cr,self.uid,self.get_id('period_id_start')).date_stop
        elif self.times == 'years':
            self.start_date = self.pool.get('account.fiscalyear').browse(self.cr,self.uid,self.get_id('fiscalyear_start')).date_start
            self.end_date   = self.pool.get('account.fiscalyear').browse(self.cr,self.uid,self.get_id('fiscalyear_start')).date_stop
        elif self.times == 'dates':
            self.start_date = wizard_data['date_start']
            self.end_date   = wizard_data['date_end']
            
        else:
            quarter = wizard_data['quarter'] or False
            year = self.pool.get('account.fiscalyear').browse(self.cr,self.uid,self.get_id('fiscalyear_start')).name
            self.get_quarter_date(year, quarter)
            
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_line(self):
        sql = '''
            select am.name as so,am.date as ngay,aa.code as tkdu,aml.debit as debit,aml.credit as credit,
                coalesce(aih.product_showin_report, coalesce(avh.dien_giai,concat(am.ref, am.ref_number))) description,
                    rp.name as tenkh,rp.internal_code as makh
                from account_move_line aml
                left join account_account aa on aa.id=aml.account_id
                left join account_move am on am.id=aml.move_id
                left join account_invoice aih on aml.move_id = aih.move_id -- lien ket voi invoice
                left join account_voucher avh on aml.move_id = avh.move_id -- lien ket thu/chi
                left join res_partner rp on aml.partner_id = rp.id
                        
                where am.state='posted' and am.date between '%s' and '%s' and am.company_id=%s
            order by aml.date,aml.move_id,aml.debit desc
        '''%(self.start_date,self.end_date,self.company_id)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_total(self, get_line):
        total_debit = 0
        total_credit = 0
        for line in get_line:
            total_debit += line['debit']
            total_credit += line['credit']
        return {
                'total_debit': total_debit,
                'total_credit': total_credit,
                }
            
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
