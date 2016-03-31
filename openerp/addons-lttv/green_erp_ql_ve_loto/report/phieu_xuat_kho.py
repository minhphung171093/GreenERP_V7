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
            rs10 = ''
            rs20 = ''
            rs50 = ''
            sql='''
                select ma_daily, name, (select case when sum(product_qty)>0 then sum(product_qty) else 0 end product_qty from stock_move where picking_id = %(picking_id)s and 
                            product_id = (select id from product_product where default_code like '%(mg10)s') and daily_id = %(daily_id)s) qty_10,
                            (select case when sum(product_qty)>0 then sum(product_qty) else 0 end product_qty from stock_move where picking_id = %(picking_id)s and 
                            product_id = (select id from product_product where default_code like '%(mg20)s') and daily_id = %(daily_id)s) qty_20,
                            (select case when sum(product_qty)>0 then sum(product_qty) else 0 end product_qty from stock_move where picking_id = %(picking_id)s and 
                            product_id = (select id from product_product where default_code like '%(mg50)s') and daily_id = %(daily_id)s) qty_50
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
            sql='''
                select lot.name as series_10 from stock_production_lot lot, stock_move sm where sm.prodlot_id = lot.id and sm.product_id = (select id from product_product where default_code like '%(mg10)s')
                and daily_id = %(daily_id)s and picking_id = %(picking_id)s
            '''%{
                 'picking_id': picking_id,
                 'daily_id': line,
                 'mg10':'%10.000%',
                 }
            self.cr.execute(sql)
            for ve10 in self.cr.fetchall():
                rs10 += ve10 and ve10[0] + '; ' or ''
                
            sql='''
                select lot.name as series_20 from stock_production_lot lot, stock_move sm where sm.prodlot_id = lot.id and sm.product_id = (select id from product_product where default_code like '%(mg20)s')
                and daily_id = %(daily_id)s and picking_id = %(picking_id)s
            '''%{
                 'picking_id': picking_id,
                 'daily_id': line,
                 'mg20':'%20.000%',
                 }
            self.cr.execute(sql)
            for ve20 in self.cr.fetchall():
                rs20 += ve20 and ve20[0] + '; ' or ''
                
            sql='''
                select lot.name as series_50 from stock_production_lot lot, stock_move sm where sm.prodlot_id = lot.id and sm.product_id = (select id from product_product where default_code like '%(mg50)s')
                and daily_id = %(daily_id)s and picking_id = %(picking_id)s
            '''%{
                 'picking_id': picking_id,
                 'daily_id': line,
                 'mg50':'%50.000%',
                 }
            self.cr.execute(sql)
            for ve50 in self.cr.fetchall():
                rs50 += ve50 and ve50[0] + '; ' or ''
            
            if rs:
                self.total_10 += rs['qty_10']
                self.total_20 += rs['qty_20']
                self.total_50 += rs['qty_50']
                res.append({
                            'ma_daily':rs['ma_daily'],
                            'name':rs['name'],
                            'qty_10':format(rs['qty_10'], ',').split('.')[0],
                            'qty_20':format(rs['qty_20'], ',').split('.')[0],
                            'qty_50':format(rs['qty_50'], ',').split('.')[0],
                            'rs10': rs10 and rs10[:-2] or '',
                            'rs20': rs20 and rs20[:-2] or '',
                            'rs50': rs50 and rs50[:-2] or '',
                            })
        return res
    
    def get_total(self):
        res = {
                'total_10':format(self.total_10, ',').split('.')[0],
                'total_20':format(self.total_20, ',').split('.')[0],
                'total_50':format(self.total_50, ',').split('.')[0],
               }
        return res
    
    def get_date(self):
        date = time.strftime('%Y-%m-%d')
        return date
    
