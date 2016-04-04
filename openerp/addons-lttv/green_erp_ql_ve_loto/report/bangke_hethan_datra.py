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
from green_erp_ql_ve_loto.report import amount_to_text_vn
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.addons.green_erp_ql_ve_loto.report import amount_to_text_vn

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_vietname_date': self.get_vietname_date,
            'convert': self.convert,
            'get_gt_menhgia': self.get_gt_menhgia,
            'get_lines': self.get_lines,
            'get_name_menhgia': self.get_name_menhgia,
            'get_ngaymothuong': self.get_ngaymothuong,
            'get_daiduthuong': self.get_daiduthuong,
            'get_date_now': self.get_date_now,
            'get_2_18': self.get_2_18,
        })
        
    def get_date_now(self):
        return time.strftime(DATE_FORMAT)
        
    def get_ngaymothuong(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        if not date:
            return ''
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_daiduthuong(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        sql = '''
            select ddt.name
                from ketqua_xoso kqxs
                left join dai_duthuong ddt on ddt.id = kqxs.dai_duthuong_id 
                where name='%s'
        '''(date)
        self.cr.execute(sql)
        ddt = self.cr.fetchall()
        if dtt:
            return dtt[0]
        else:
            return ''
        
    def get_2_18(self):
        res = []
        for sl in 'so lan trung  ngay mo thuong order by tang dan':
            'sql sum so tien, so luong phai tra'
            'sql sum so tien, so luong da tra'
            res.append({
                        'so_lan':sl,
                        'sl_phai_tra': 0,
                        'stien_phai_tra': 0,
                        'sl_da_tra': 0,
                        'stien_da_tra': 0,
                        'sl_con_lai': 0,
                        'stien_con_lai': 0,
                        })
            'dung bien toan cuc de tim tong cong'
        return res
    
    def get_vietname_date(self, date):
        if not date:
            return ''
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_name_menhgia(self):
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        menhgia = self.pool.get('product.product').browse(self.cr, self.uid, product[0])
        return menhgia.name
    
    def convert(self, amount):
        amount_text = amount_to_text_vn.amount_to_text(amount, 'vn')
        if amount_text and len(amount_text)>1:
            amount = amount_text[1:]
            head = amount_text[:1]
            amount_text = head.upper()+amount
        return amount_text
    
    def get_gt_menhgia(self):
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        menhgia = self.pool.get('product.product').browse(self.cr, self.uid, product[0])
        return int(menhgia.list_price)/10000
    