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
        pool = pooler.get_pool(self.cr.dbname)
        self.account_id =False
        self.account_code = False
        self.account_name = False
        self.start_date = False
        self.end_date = False
        self.partner_id = False
        self.partner_name = False
        
        self.company_name = False
        self.company_address = False
        self.vat = False
        self.total_residual = 0
        self.type = False
        self.depreciation_value = False
        self.acc_depreciation =False
        self.remaining_value = False
        
        self.localcontext.update({
            'get_vietname_date':self.get_vietname_date, 
            'get_header':self.get_header,
            'get_start_date':self.get_start_date,
            'get_end_date':self.get_end_date,
            'get_company_name':self.get_company_name,
            'get_company': self.get_company,
            'get_line':self.get_line,
            'get_master': self.get_master,
            'get_total': self.get_total,
            'get_sum_2_gt': self.get_sum_2_gt,
        })
    
    def get_company(self, company_id):
        if company_id:
            company_obj = self.pool.get('res.company').browse(self.cr, self.uid, company_id)
            self.company_name = company_obj.name or ''
            self.company_address = company_obj.street or ''
            self.vat = company_obj.vat or ''
        return True
    
    def get_company_name(self):
        self.get_header()
        return self.company_name
    
    def get_header(self):
        wizard_data = self.localcontext['data']['form']
        user_obj = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        self.get_company(user_obj.company_id.id or False)
        self.start_date = wizard_data['tu_ngay']
        self.end_date   = wizard_data['den_ngay']
            
    
    def get_start_date(self):
        return self.get_vietname_date(self.start_date) 
    
    def get_end_date(self):
        return self.get_vietname_date(self.end_date) 
    
    
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    
    def get_master(self):
        sql = '''
            select id, name, purchase_value, method_number from account_asset_asset where state = 'open' 
            and id in (select asset_id from account_asset_depreciation_line where move_check = 't' and depreciation_date between '%s' and '%s')
        '''%(self.start_date, self.end_date)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_line(self, master_id):
        start_date = self.get_vietname_date(self.start_date)
        end_date = self.get_vietname_date(self.end_date)
        sql = '''
            select id, depreciation_date, depreciated_value, amount, remaining_value 
            from account_asset_depreciation_line
            where depreciation_date between '%s' and '%s' and asset_id = %s and move_check = 't'
            order by depreciation_date desc
        '''%(self.start_date, self.end_date, master_id)
        self.cr.execute(sql)
        if self.cr.rowcount:
            return self.cr.dictfetchall()[0]
#         else:
#             raise osv.except_osv(_('Cảnh báo!'),_('Không có tài sản nào phù hợp từ %s đến %s!')%(start_date, end_date))
    
    def get_total(self):
        total = []
        sum_purchase_value = 0
        sum_depreciated_value = 0
        sum_gt_conlai = 0
        sum_method_number = 0
        sum_amount = 0
        sum_haomonluyke_ck = 0
        sum_gt_conlai_ck = 0
        start_date = self.get_vietname_date(self.start_date)
        end_date = self.get_vietname_date(self.end_date)
        for master in self.get_master():
            sql = '''
                select id, depreciation_date, depreciated_value, amount, remaining_value 
                from account_asset_depreciation_line
                where depreciation_date between '%s' and '%s' and asset_id = %s and move_check = 't'
                order by depreciation_date desc
            '''%(self.start_date, self.end_date, master['id'])
            self.cr.execute(sql)
            if self.cr.rowcount:
                line = self.cr.dictfetchall()[0]
                sum_purchase_value += master['purchase_value']
                sum_depreciated_value += line['depreciated_value']
                sum_gt_conlai += line['amount'] + line['remaining_value']
                sum_method_number += master['method_number']
                sum_amount += line['amount']
                sum_haomonluyke_ck += line['depreciated_value'] + line['amount']
                sum_gt_conlai_ck += line['remaining_value']
        total.append(({
                  'nguyen_gia': sum_purchase_value and sum_purchase_value or '',
                  'haomonluyke_dk': sum_depreciated_value and sum_depreciated_value or '',
                  'gt_conlai_dk': sum_gt_conlai and sum_gt_conlai or '',
                  'so_thang_kh': sum_method_number and sum_method_number or '',
                  'khau_hao': sum_amount and sum_amount or '',
                  'nguyen_gia_cl': sum_purchase_value and sum_purchase_value or '',
                  'haomonluyke_ck': sum_haomonluyke_ck and sum_haomonluyke_ck or '',
                  'gt_conlai_ck': sum_gt_conlai_ck and sum_gt_conlai_ck or '',
                  }))
        return total
    
    def get_sum_2_gt(self, a, b):
        return a+b
    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
