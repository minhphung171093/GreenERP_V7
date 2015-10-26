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
            'get_line_out':self.get_line_out, 
            'get_info_out':self.get_info_out,
            'get_line_in':self.get_line_in,
            'get_date_from': self.get_date_from,
            'get_date_to': self.get_date_to,
        })
    
    
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['tu_ngay'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['den_ngay'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_line_in(self,line_id):
        wizard_data = self.localcontext['data']['form']
        tu_ngay = wizard_data['tu_ngay']
        den_ngay = wizard_data['den_ngay']
        sql = '''
                select * from account_invoice_line where invoice_id in (select id from account_invoice
                    where type='in_invoice' and state in ('open', 'paid') and id in (select invoice_id from account_invoice_line where stock_move_id in (
                    select id from stock_move where picking_id in(select picking_in_id from stock_move where id in (select stock_move_id from account_invoice_line where id =%s)))))
            '''%(line_id)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_line_out(self):
        wizard_data = self.localcontext['data']['form']
        tu_ngay = wizard_data['tu_ngay']
        den_ngay = wizard_data['den_ngay']
        sql = '''
            select * from account_invoice_line where invoice_id in (select id from account_invoice 
            where type = 'out_invoice' and state in ('open', 'paid') and date_invoice between '%s' and '%s')
        '''%(tu_ngay, den_ngay)
        self.cr.execute(sql)
        out_ids = self.cr.dictfetchall()
        return out_ids
    
    def get_info_out(self,inv_id):
        res = []
        inv = self.pool.get('account.invoice').browse(self.cr,self.uid,inv_id)
        return {
                'ki_hieu': inv.ki_hieu_hd or '',
                'number': inv.so_hd or '',
                'ngay_hd':inv.date_invoice or '',
                'khach_hang':inv.partner_id.name or '',
                'hop_dong':inv.hop_dong_id.name or '',
                'doanh_thu':inv.amount_total or ''
                }
        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
