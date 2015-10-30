# -*- coding: utf-8 -*-
##############################################################################
#
#    HLVSolution, Open Source Management Solution
#
##############################################################################

import time
from report import report_sxw
from tools.translate import _
from datetime import datetime
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.account_id =False
        self.times = False
        self.start_date = False
        self.end_date = False
        self.company_name = False
        self.company_address = False
        self.vat = False
        self.localcontext.update({
            'get_vietname_date':self.get_vietname_date, 
            'get_line':self.get_line,
            'get_header':self.get_header,
            'get_account':self.get_account,
            'get_start_date':self.get_start_date,
            'get_end_date':self.get_end_date,
            'get_company_name':self.get_company_name,
            'get_company_address':self.get_company_address,
            'get_company_vat':self.get_company_vat,
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
    
    def get_header(self):
        wizard_data = self.localcontext['data']['form']
        self.times = wizard_data['times']
        #Get company info
        self.company_id = wizard_data['company_id'] and wizard_data['company_id'][0] or False
        self.get_company(self.company_id)
        
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
            
    def get_start_date(self):
        wizard_data = self.localcontext['data']['form']
        fyear = wizard_data['fiscalyear'][0] and wizard_data['fiscalyear'][0] or False
        if fyear:
            return self.get_vietname_date(self.pool.get('account.fiscalyear').browse(self.cr,self.uid,fyear).date_start) 
    
    def get_end_date(self):
        wizard_data = self.localcontext['data']['form']
        fyear = wizard_data['fiscalyear'][0] and wizard_data['fiscalyear'][0] or False
        if fyear:
            return self.get_vietname_date(self.pool.get('account.fiscalyear').browse(self.cr,self.uid,fyear).date_stop) 
    
    def get_account(self):
        values ={}
        wizard_data = self.localcontext['data']['form']
        self.account_id = wizard_data['account_id'][0]
        if self.account_id:
            account_obj = self.pool.get('account.account').browse(self.cr,self.uid,self.account_id)
            values ={
                     'account_code': account_obj.code,
                     'account_name':account_obj.name,
                     }
            return values
    
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
        
#     def get_line(self):
#         if not self.start_date:
#             self.get_header()
#         return self.pool.get('sql.profit.loss').get_line(self.cr, self.start_date,self.end_date,self.times,self.company_id)
    
    def get_line(self,stt):
        times = 'periods'
        period = ''
        period_obj = self.pool.get('account.period')
        wizard_data = self.localcontext['data']['form']
        fyear = wizard_data['fiscalyear'][0] and wizard_data['fiscalyear'][0] or False
        if not self.start_date:
            self.get_header()
        if stt and fyear:
            period = stt + '/' + self.pool.get('account.fiscalyear').browse(self.cr,self.uid,fyear).code
            period_ids = period_obj.search(self.cr, self.uid, [('code','=',period),('special','=',False)])
            if period_ids:
                period_id = period_obj.browse(self.cr, self.uid,period_ids[0])
             
                return self.pool.get('sql.profit.loss').get_line(self.cr, period_id.date_start,period_id.date_stop,times,self.company_id)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: