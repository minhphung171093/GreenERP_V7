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
            'get_line_product':self.get_line_product, 
            'get_detail_product': self.get_detail_product,
            'get_line': self.get_line,
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
    
    def get_line_product(self):
        wizard_data = self.localcontext['data']['form']
        tu_ngay = wizard_data['tu_ngay']
        den_ngay = wizard_data['den_ngay']
        sql = '''
                select product_id from account_invoice_line where invoice_id in (select id from account_invoice
                    where state in ('open', 'paid') and date_invoice between '%s' and '%s') group by product_id
            '''%(tu_ngay, den_ngay)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_line(self, product_id):
        wizard_data = self.localcontext['data']['form']
        tu_ngay = wizard_data['tu_ngay']
        den_ngay = wizard_data['den_ngay']
        mang = []
        sql = '''
            select id, quantity, price_unit from account_invoice_line where product_id = %s and invoice_id in (select id from account_invoice 
            where type = 'out_invoice' and state in ('open', 'paid') and date_invoice between '%s' and '%s')
        '''%(product_id, tu_ngay, den_ngay)
        self.cr.execute(sql)
        line_out_ids = self.cr.dictfetchall()
        if line_out_ids:
            lai = 0
            gia_von = 0
            sl_out = 0
            doanh_thu_out = 0
            thue_out = 0
            for line_out in line_out_ids:
                sql = '''
                    select tax_id from account_invoice_line_tax where invoice_line_id = %s
                '''%(line_out['id'])
                self.cr.execute(sql)
                tax_ids = self.cr.dictfetchall()
                amount = 0
                if tax_ids:
                    tax_id = tax_ids[0]
                    amount = self.pool.get('account.tax').browse(self.cr,self.uid,tax_id['tax_id']).amount
                sl_out += line_out['quantity'] or 0
                doanh_thu_out += line_out['quantity']*line_out['price_unit']
                thue_out += line_out['quantity']*line_out['price_unit']*amount
                sql = '''
                        select price_unit from account_invoice_line where product_id = %s and invoice_id in (select id from account_invoice
                            where type='in_invoice' and state in ('open', 'paid') and id in (select invoice_id from account_invoice_line where stock_move_id in (
                            select id from stock_move where picking_id in(select picking_in_id from stock_move where id in (select stock_move_id from account_invoice_line where id =%s)))))
                    '''%(product_id,line_out['id'])
                self.cr.execute(sql)
                price_unit = self.cr.dictfetchone()
                price_unit_in = price_unit and price_unit['price_unit'] or 0
                gia_von += line_out['quantity']*price_unit_in
                lai = doanh_thu_out - gia_von
            mang.append(({
                          'sl_out': sl_out,
                          'doanh_thu_out': doanh_thu_out,
                          'thue_out': thue_out,
                          'gia_von': gia_von,
                          'lai': lai,
                          }))
        return mang
    
    def get_detail_product(self,product_id):
        res = []
        product = self.pool.get('product.product').browse(self.cr,self.uid,product_id)
        return {
                'default_code': product.default_code or '',
                'name': product.name or '',
                'dvt':product.uom_id and product.uom_id.name or '',
                }
        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
