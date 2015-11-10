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
            'get_so_phuluc': self.get_so_phuluc,
            'get_price_hh': self.get_price_hh,
            'get_tax_hh': self.get_tax_hh,
            'get_ngaynhan_lc': self.get_ngaynhan_lc,
        })
        
    def get_ngaynhan_lc(self, hopdong_id):
        hop_dong = self.pool.get('hop.dong').browse(self.cr,self.uid,hopdong_id)
        if hop_dong.dk_thanhtoan_id.loai == 'lc':
            sql = '''
                select id from account_voucher where type = 'receipt' and hop_dong_id = %s and state = 'posted'
                order by id
            '''%(hopdong_id)
            self.cr.execute(sql)
            account_voucher_ids = [r[0] for r in self.cr.fetchall()]
            if account_voucher_ids:
                account = self.pool.get('account.voucher').browse(self.cr,self.uid,account_voucher_ids[0])
                return account.date
            else:
                return ''
        else:
            return ''
             
    def get_so_phuluc(self, hop_dong_id):
        so_phuluc = ''
        tu_ngay = ''
        sql = '''
            select name, tu_ngay from phuluc_hop_dong where type = 'hd_ngoai' and hop_dong_id = %s
        '''%(hop_dong_id)
        self.cr.execute(sql)
        phuluc_ids = self.cr.dictfetchall()
        if phuluc_ids:
            for phuluc in phuluc_ids:
                so_phuluc += phuluc['name'] + ' '
                tu_ngay += phuluc['tu_ngay'] + ' '
        return {
                'so_phuluc': so_phuluc,
                'tu_ngay': tu_ngay,
                }
    
    def get_price_hh(self,product_id,hop_dong_id): 
        price_unit = 0.0
        sql = '''
            select price_unit from hopdong_hoahong_line where hopdong_hh_id = %s and product_id = %s
        '''%(hop_dong_id,product_id)
        self.cr.execute(sql)
        price_unit = self.cr.dictfetchone()['price_unit']
        return price_unit
    
    def get_tax_hh(self,o):
        line = o.hopdong_hoahong_line[0]
        return line.tax_hh
        
        
    def convert_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d-%m-%y')
        
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
        
        