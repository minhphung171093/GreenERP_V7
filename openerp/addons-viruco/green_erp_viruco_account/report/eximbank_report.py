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
from green_erp_viruco_account.report import amount_to_text_vn
import amount_to_text_en

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.account_id =False
        self.times = False
        self.start_date = False
        self.end_date = False
        self.company_name = False
        self.company_address = False
        self.showdetail = False
        self.vat = False
        self.shop_ids = []
        self.localcontext.update({
            'get_vietname_date':self.get_vietname_date, 
            'get_sum': self.get_sum,
            'amount_to_text': self.amount_to_text,
            'get_so_tk': self.get_so_tk,
            'get_ten_nh': self.get_ten_nh,
        })
    
    
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_sum(self, exim_id):
        total = 0
        exim = self.pool.get('account.voucher.batch').browse(self.cr,self.uid,exim_id)
        for line in exim.voucher_lines:
            total += line.amount
        return total
    
    def amount_to_text(self, nbr, lang='vn'):
        if lang == 'vn':
            return  amount_to_text_vn.amount_to_text(nbr, lang)
        
    def get_so_tk(self, partner_id):
        if partner_id:
            partner = self.pool.get('res.partner').browse(self.cr,self.uid,partner_id)
            if partner.bank_ids:
                line = partner.bank_ids[0]
                return line.acc_number
            else:
                return ''
        else:
            return ''
    
    def get_ten_nh(self, partner_id):
        if partner_id:
            partner = self.pool.get('res.partner').browse(self.cr,self.uid,partner_id)
            if partner.bank_ids:
                line = partner.bank_ids[0]
                return line.bank_name
            else:
                return ''
        else:
            return ''
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
