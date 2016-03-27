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

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.total_10= 0.0
        self.total_20 = 0.0
        self.total_50= 0.0
        self.localcontext.update({
            'get_line': self.get_line,
            'get_total':self.get_total,
            'get_date':self.get_date,
        })
    
    def get_line(self,picking_id):
        res = []
        sql='''
            select distinct daily_id from stock_move where picking_id = %s 
        '''%(picking_id)
        self.cr.execute(sql)
        daily_ids = [r[0] for r in self.cr.fetchall()]
        for line in daily_ids:
            sql='''
                select ma_daily, name, (select case when sum(product_qty)>0 then sum(product_qty) else 0 end product_qty from stock_move where picking_id = %(picking_id)s and 
                            product_id = (select id from product_product where name_template like '%(mg10)s') and daily_id = %(daily_id)s) qty_10,
                            (select case when sum(product_qty)>0 then sum(product_qty) else 0 end product_qty from stock_move where picking_id = %(picking_id)s and 
                            product_id = (select id from product_product where name_template like '%(mg20)s') and daily_id = %(daily_id)s) qty_20,
                            (select case when sum(product_qty)>0 then sum(product_qty) else 0 end product_qty from stock_move where picking_id = %(picking_id)s and 
                            product_id = (select id from product_product where name_template like '%(mg50)s') and daily_id = %(daily_id)s) qty_50
                from res_partner where id = %(daily_id)s
            '''%{
                 'mg10':'%10.000%',
                 'mg20':'%20.000%',
                 'mg50':'%50.000%',
                 'picking_id': picking_id,
                 'daily_id': line,
                 }
            self.cr.execute(sql)
            rs = self.cr.dictfetchone()
            if rs:
                self.total_10 += rs['qty_10']
                self.total_20 += rs['qty_20']
                self.total_50 += rs['qty_50']
                res.append({
                            'ma_daily':rs['ma_daily'],
                            'name':rs['name'],
                            'qty_10':rs['qty_10'],
                            'qty_20':rs['qty_20'],
                            'qty_50':rs['qty_50'],
                            })
        return res
    
    def get_total(self):
        res = {
                'total_10':self.total_10,
                'total_20':self.total_20,
                'total_50':self.total_50,
               }
        return res
    
    def get_date(self):
        date = time.strftime('%Y-%m-%d'),
        rs =str(date)[2:12]
        return rs
    
