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
import locale
from green_erp_viruco_sale.report import amount_to_text_en
from green_erp_viruco_sale.report import amount_to_text_vn
# from green_erp_arulmani_sale.report import amount_to_text_indian
# from amount_to_text_indian import Number2Words
#locale.setlocale(locale.LC_NUMERIC, "en_IN")
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from green_erp_viruco_sale.report import amount_to_text_en

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'convert':self.convert,
            'convert_f_amount':self.convert_f_amount,
            'convert_date': self.convert_date,
            'get_tong': self.get_tong,
        })
        
    def convert_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d-%b-%y')
        
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
    
    def get_tong(self, o):
        qty = 0
        dongia = 0
        thanhtien = 0
        for line in o.hopdong_line:
            qty+=line.product_qty
            dongia += line.price_unit
            thanhtien += line.price_subtotal
        return {
            'qty': qty,
            'dongia': dongia,
            'thanhtien': thanhtien,    
        }
        
        