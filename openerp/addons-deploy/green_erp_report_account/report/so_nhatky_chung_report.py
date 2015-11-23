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
    
    def get_year(self):
        return self.year
    
    def get_header(self):
        wizard_data = self.localcontext['data']['form']
        #Get company info
        self.company_id = wizard_data['company_id'] and wizard_data['company_id'][0] or False
        self.get_company(self.company_id)
        #Get shops
        
        self.year = self.pool.get('account.fiscalyear').browse(self.cr,self.uid,self.get_id('fiscalyear')).name
        self.start_date = self.pool.get('account.fiscalyear').browse(self.cr,self.uid,self.get_id('fiscalyear')).date_start
        self.end_date = self.pool.get('account.fiscalyear').browse(self.cr,self.uid,self.get_id('fiscalyear')).date_stop
            
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_line(self):
        sql = '''
            select am.name as so,am.date as ngay,aa.code as tkdu,aml.debit as debit,aml.credit as credit,
                coalesce(aih.product_showin_report, coalesce(avh.dien_giai,concat(am.ref, am.ref_number))) description
                from account_move_line aml
                left join account_account aa on aa.id=aml.account_id
                left join account_move am on am.id=aml.move_id
                left join account_invoice aih on aml.move_id = aih.move_id -- lien ket voi invoice
                left join account_voucher avh on aml.move_id = avh.move_id -- lien ket thu/chi
                        
                where am.state='posted' and am.date between '%s' and '%s' and am.company_id=%s
            order by aml.date,aml.move_id,aml.debit desc
        '''%(self.start_date,self.end_date,self.company_id)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
