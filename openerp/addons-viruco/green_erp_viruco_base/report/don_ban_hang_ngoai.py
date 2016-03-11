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
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
# from openerp.tools import amount_to_text_en
from green_erp_viruco_sale.report import amount_to_text_en

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
#             'get_thue':self.get_thue,
#             'get_tong':self.get_tong,
            'convert':self.convert,
            'convert_f_amount':self.convert_f_amount,
            'get_soluong':self.get_soluong,
            'convert_date': self.convert_date,
            'get_transhipment': self.get_transhipment,
            'get_dia_chi':self.get_dia_chi,
        })
    
    def get_transhipment(self, transhipment):
        tam = ''
        if transhipment == 'allowed':
            tam = 'Allowed'
        if transhipment == 'not_allowed':
            tam = 'Not Allowed'
        return tam
    
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
    def convert_f_amount(self, amount):
        a = format(amount,',')
        b = a.split('.')
        if len(b)==2 and len(b[1])==1:
            a+='0'
        return a.replace(',',' ')
    
    def convert(self, amount):
        amount_text = amount_to_text_en.amount_to_text(amount, 'en', 'Dollars')
        if amount_text and len(amount_text)>1:
            amount = amount_text[1:]
            head = amount_text[:1]
            amount_text = head.upper()+amount
        return amount_text
    
    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit, line.product_qty, line.product_id, line.donbanhang_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val
    
#     def get_thue(self,order,line):
#         cur_obj = self.pool.get('res.currency')
#         cur = order.pricelist_id.currency_id
#         val = self._amount_line_tax(self.cr, self.uid, line)
#         return val
    
    def get_soluong(self,order):
        cur_obj = self.pool.get('res.currency')
        cur = order.pricelist_id.currency_id
        val = 0
        for line in order.don_ban_hang_line:
            val += line.product_qty
#         product_qty = cur_obj.round(self.cr, self.uid, cur, val)
        return {
                'product_qty': val,
                }
     
#     def get_tong(self,order):
#         cur_obj = self.pool.get('res.currency')
#         cur = order.pricelist_id.currency_id
#         val = 0
#         val1 = 0
#         for line in order.don_ban_hang_line:
#             val += self._amount_line_tax(self.cr, self.uid, line)
#             val1 += line.price_subtotal
#         tax = cur_obj.round(self.cr, self.uid, cur, val)
#         total = cur_obj.round(self.cr, self.uid, cur, val1)
#         return {
#                 'tax': val,
#                 'total': val+val1,
#                 }
    def get_dia_chi(self, street, street2, state_id, zip, country_id):
        address = ''
        if street:
            address += street + ', '
        if street2:
            address += street2 + ', '
        if state_id:
            state = self.pool.get('res.country.state').browse(self.cr,self.uid,state_id)
            address += state.name + ', ' 
        if zip:
            address += zip + ', '
        if country_id:
            country = self.pool.get('res.country').browse(self.cr,self.uid,country_id)
            address += country.name  
        return address
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
