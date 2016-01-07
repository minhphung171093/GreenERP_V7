# -*- coding: utf-8 -*-
##############################################################################
#
#    HLVSolution, Open Source Management Solution
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import datetime
# from green_erp_pharma_report.report import amount_to_text_vn
class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.context = context
        self.num = 0
        self.localcontext.update({
            'get_line':self.get_line,
            'get_date':self.get_date,
            'get_date_budget': self.get_date_budget,
            'get_bdf': self.get_bdf,
            'get_allocation': self.get_allocation,
            'get_cell': self.get_cell,
        })
    
    def get_date(self,date):
        if date:
            d = datetime.datetime.strptime(date, "%Y-%m-%d")
            d = d.strftime("%d-%b-%y")
            return d
        else:
            return False
    
    def get_date_budget(self,date):
        if date:
            d = datetime.datetime.strptime(date, "%Y-%m-%d")
            d = d.strftime("%b-%y")
            return d
        else:
            return False
    
    def get_line(self):
        bdf_ids = self.context.get('active_ids')
        line_obj = self.pool.get('spending.detail')
        line_ids = []
        for bdf in self.pool.get('bdf.purchase').browse(self.cr, self.uid, bdf_ids):
            line_ids += line_obj.search(self.cr, self.uid, [('purchase_id','=',bdf.id)])
        return line_obj.browse(self.cr, self.uid, line_ids)
    
    def get_bdf(self,line):
        if line.purchase_id:
            return line.purchase_id
        elif line.purchase2_id:
            return line.purchase2_id
        elif line.purchase3_id:
            return line.purchase3_id

    def get_allocation(self):
        bdf_ids = self.context.get('active_ids')
        key_account_obj = self.pool.get('master.key.accounts')
        self.cr.execute('''
            select key_account_id from bdf_allocation 
                where spending_detail_id in (select id from spending_detail where purchase_id in %s) and allocation is not null and allocation!=0 group by key_account_id order by key_account_id 
        ''',(tuple(bdf_ids),))
        key_account_ids = [r[0] for r in self.cr.fetchall()]
        return key_account_obj.browse(self.cr, self.uid, key_account_ids)
    
    def get_cell(self, line):
        key_accounts = self.get_allocation()
        if self.num>=len(key_accounts):
            self.num = 0
        index = self.num
        self.cr.execute('''
            select allocation from bdf_allocation 
                where key_account_id=%s and spending_detail_id =%s
        ''',(key_accounts[index].id,line.id,))
        allocations = [r[0] for r in self.cr.fetchall()]
        self.num += 1
        return allocations and allocations[0] or 0
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: