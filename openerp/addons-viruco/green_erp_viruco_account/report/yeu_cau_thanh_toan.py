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
from green_erp_viruco_purchase.report import amount_to_text_vn
class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_thue':self.get_thue,
            'get_tong':self.get_tong,
            'convert':self.convert,
            'convert_f_amount':self.convert_f_amount,
            'convert_tt':self.convert_tt,
            'get_vietname_date':self.get_vietname_date,
            'get_thanhtoan':self.get_thanhtoan,
        })
    
    def convert_f_amount(self, amount):
        a = format(amount,',')
        b = a.split('.')
        if len(b)==2 and len(b[1])==1:
            a+='0'
        return a.replace(',',' ')
    
    def convert(self, amount):
        amount_text = amount_to_text_vn.amount_to_text(amount, 'vn')
        if amount_text and len(amount_text)>1:
            amount = amount_text[1:]
            head = amount_text[:1]
            amount_text = head.upper()+amount
        return amount_text

    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def convert_tt(self, amount):
        tt=False
        if amount and amount.type=='bank':
            tt='Chuyển khoản'
        else:
            tt='Tiền mặt'
        return tt
    def get_thanhtoan(self,hopdong):
        res=[]
        if hopdong:
            sql = '''
                select amount from account_voucher where type='payment' and hop_dong_id=%s and state='posted'
            '''%(hopdong)
            self.cr.execute(sql)
            thanhtoan = self.cr.fetchall()
            for line in thanhtoan:
                res.append(str(line[0])[:-2])
            return res
    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit, line.product_qty, line.product_id, line.donmuahang_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val
    
    def get_thue(self,order,line):
        cur_obj = self.pool.get('res.currency')
        cur = order.pricelist_id.currency_id
        val = self._amount_line_tax(self.cr, self.uid, line)
        return val
#         return cur_obj.round(self.cr, self.uid, cur, val)
    
    def get_tong(self,order):
        cur_obj = self.pool.get('res.currency')
        cur = order.pricelist_id.currency_id
        val = 0
        val1 = 0
        for line in order.don_mua_hang_line:
            val += self._amount_line_tax(self.cr, self.uid, line)
            val1 += line.price_subtotal
#         tax = cur_obj.round(self.cr, self.uid, cur, val)
#         total = cur_obj.round(self.cr, self.uid, cur, val1)
        return {
                'tax': val,
                'total': val+val1,
                }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
