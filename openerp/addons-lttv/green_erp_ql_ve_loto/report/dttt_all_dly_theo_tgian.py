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

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.total_each_sl_2 = 0.0
        self.total_each_sl_3 = 0.0
        self.total_each_sl_4 = 0.0
        self.total_each_sai_kythuat = 0.0
        self.total_each_tong_ve = 0.0
        self.total_each_thanhtien = 0.0
        
        self.total_all_sl_2 = 0.0
        self.total_all_sl_3 = 0.0
        self.total_all_sl_4 = 0.0
        self.total_all_sai_kythuat = 0.0
        self.total_all_tong_ve = 0.0
        self.total_all_thanhtien = 0.0
        self.localcontext.update({
            'get_date':self.get_date,
            'get_date_from':self.get_date_from,
            'get_date_to':self.get_date_to,
            'get_dai_ly':self.get_dai_ly,
            'get_menh_gia':self.get_menh_gia,
            'get_line':self.get_line,
            'get_tong':self.get_tong,
            'get_line_tong':self.get_line_tong,
            'get_line_tong_all':self.get_line_tong_all,
        })
        
    def get_date(self):
        wizard_data = self.localcontext['data']['form']
#         date1 = time.strftime(DATE_FORMAT)
        date = datetime.strptime(time.strftime(DATE_FORMAT), DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    def get_dai_ly(self):
        res_partner_obj = self.pool.get('res.partner')
        res_partner_ids = res_partner_obj.search(self.cr ,self.uid, [('dai_ly','=',True)],order='ma_daily')
        return res_partner_obj.browse(self.cr, self.uid, res_partner_ids)
     
    def get_menh_gia(self):
        product_product_obj = self.pool.get('product.product')
        product_product_ids = product_product_obj.search(self.cr ,self.uid, [('menh_gia','=',True)])
        return product_product_obj.browse(self.cr, self.uid, product_product_ids)
     
    def get_line(self, dl):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date']
        date_to = wizard_data['date_to']
        ve_loto_obj = self.pool.get('ve.loto')
        
        self.total_each_sl_2 = 0.0
        self.total_each_sl_3 = 0.0
        self.total_each_sl_4 = 0.0
        self.total_each_sai_kythuat = 0.0
        self.total_each_tong_ve = 0.0
        self.total_each_thanhtien = 0.0
        rs = []
        product_product_obj = self.pool.get('product.product')
        product_product_ids = product_product_obj.search(self.cr ,self.uid, [('menh_gia','=',True)])
        for menhgia in product_product_ids:
            sql ='''
                select case when sum(coalesce(tong_sai_kythuat,0))!=0
                        then sum(coalesce(tong_sai_kythuat,0)) else 0 end tong_sai_kythuat  
                from ve_loto where ngay between '%s' and '%s' 
                                and product_id=%s and daily_id = %s and state = 'done'
            '''%(date_from,date_to,menhgia,dl.id) 
            self.cr.execute(sql)
            kq1 = self.cr.dictfetchone()
            
            sql ='''
                select case when sum(coalesce(sl_2_d,0)+coalesce(sl_2_c,0)+coalesce(sl_2_dc,0)+coalesce(sl_2_18,0))!=0 
                        then sum(coalesce(sl_2_d,0)+coalesce(sl_2_c,0)+coalesce(sl_2_dc,0)+coalesce(sl_2_18,0)) else 0 end sl_2,
                   case when sum(coalesce(sl_3_d,0)+coalesce(sl_3_c,0)+coalesce(sl_3_dc,0)+coalesce(sl_3_7,0)+coalesce(sl_3_17,0))!=0
                        then sum(coalesce(sl_3_d,0)+coalesce(sl_3_c,0)+coalesce(sl_3_dc,0)+coalesce(sl_3_7,0)+coalesce(sl_3_17,0)) else 0 end sl_3,
                   case when sum(coalesce(sl_4_16,0))!=0
                        then sum(coalesce(sl_4_16,0)) else 0 end sl_4 
                
                from ve_loto_line where ve_loto_id in ( select id from ve_loto where ngay between '%s' and '%s' 
                                and product_id=%s and daily_id = %s and state = 'done')
            '''%(date_from,date_to,menhgia,dl.id)
            self.cr.execute(sql)
            kq2 = self.cr.dictfetchone()
            if kq1 and kq2:
                product_id = product_product_obj.browse(self.cr, self.uid, menhgia)
                tongve = kq2['sl_2'] + kq2['sl_3'] + kq2['sl_4']
                thanhtien = tongve*int(product_id.list_price or 0)
                self.total_each_sl_2 += kq2['sl_2']
                self.total_each_sl_3 += kq2['sl_3']
                self.total_each_sl_4 += kq2['sl_4']
                self.total_each_sai_kythuat += kq1['tong_sai_kythuat']
                self.total_each_tong_ve += tongve
                self.total_each_thanhtien += thanhtien
                rs.append(( {
                        'name_template': product_id.name_template or '',
                        'sl_2': format(kq2['sl_2'],',').split('.')[0].replace(',','.'),
                        'sl_3': format(kq2['sl_3'],',').split('.')[0].replace(',','.'),
                        'sl_4': format(kq2['sl_4'],',').split('.')[0].replace(',','.'),
                        'tong_ve': format(tongve,',').split('.')[0].replace(',','.'),
                        'thanhtien': format(thanhtien,',').split('.')[0].replace(',','.'),
                        'tong_sai_kythuat': format(kq1['tong_sai_kythuat'],',').split('.')[0].replace(',','.'),
                        }))
        return rs

    def get_tong(self):
        
        rs = [{
                'sl_2': format(self.total_each_sl_2,',').split('.')[0].replace(',','.'),
                'sl_3': format(self.total_each_sl_3,',').split('.')[0].replace(',','.'),
                'sl_4': format(self.total_each_sl_4,',').split('.')[0].replace(',','.'),
                'tong_ve': format(self.total_each_tong_ve,',').split('.')[0].replace(',','.'),
                'thanhtien': format(self.total_each_thanhtien,',').split('.')[0].replace(',','.'),
                'tong_sai_kythuat': format(self.total_each_sai_kythuat,',').split('.')[0].replace(',','.'),
               }]
        return rs
    
    def get_line_tong(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date']
        date_to = wizard_data['date_to']
        ve_loto_obj = self.pool.get('ve.loto')
        
        rs = []
        product_product_obj = self.pool.get('product.product')
        product_product_ids = product_product_obj.search(self.cr ,self.uid, [('menh_gia','=',True)])
        for menhgia in product_product_ids:
            sql ='''
                select case when sum(coalesce(tong_sai_kythuat,0))!=0
                        then sum(coalesce(tong_sai_kythuat,0)) else 0 end tong_sai_kythuat  
                from ve_loto where ngay between '%s' and '%s' 
                                and product_id=%s and state = 'done'
            '''%(date_from,date_to,menhgia) 
            self.cr.execute(sql)
            kq1 = self.cr.dictfetchone()
            
            sql ='''
                select case when sum(coalesce(sl_2_d,0)+coalesce(sl_2_c,0)+coalesce(sl_2_dc,0)+coalesce(sl_2_18,0))!=0 
                        then sum(coalesce(sl_2_d,0)+coalesce(sl_2_c,0)+coalesce(sl_2_dc,0)+coalesce(sl_2_18,0)) else 0 end sl_2,
                   case when sum(coalesce(sl_3_d,0)+coalesce(sl_3_c,0)+coalesce(sl_3_dc,0)+coalesce(sl_3_7,0)+coalesce(sl_3_17,0))!=0
                        then sum(coalesce(sl_3_d,0)+coalesce(sl_3_c,0)+coalesce(sl_3_dc,0)+coalesce(sl_3_7,0)+coalesce(sl_3_17,0)) else 0 end sl_3,
                   case when sum(coalesce(sl_4_16,0))!=0
                        then sum(coalesce(sl_4_16,0)) else 0 end sl_4 
                
                from ve_loto_line where ve_loto_id in ( select id from ve_loto where ngay between '%s' and '%s' 
                                and product_id=%s and state = 'done')
            '''%(date_from,date_to,menhgia)
            self.cr.execute(sql)
            kq2 = self.cr.dictfetchone()
            if kq1 and kq2:
                product_id = product_product_obj.browse(self.cr, self.uid, menhgia)
                tongve = kq2['sl_2'] + kq2['sl_3'] + kq2['sl_4']
                thanhtien = tongve*int(product_id.list_price or 0)
                self.total_all_sl_2 += kq2['sl_2']
                self.total_all_sl_3 += kq2['sl_3']
                self.total_all_sl_4 += kq2['sl_4']
                self.total_all_sai_kythuat += kq1['tong_sai_kythuat']
                self.total_all_tong_ve += tongve
                self.total_all_thanhtien += thanhtien
                rs.append(( {
                        'name_template': product_id.name_template,
                        'sl_2': format(kq2['sl_2'],',').split('.')[0].replace(',','.'),
                        'sl_3': format(kq2['sl_3'],',').split('.')[0].replace(',','.'),
                        'sl_4': format(kq2['sl_4'],',').split('.')[0].replace(',','.'),
                        'tong_ve': format(tongve,',').split('.')[0].replace(',','.'),
                        'thanhtien': format(thanhtien,',').split('.')[0].replace(',','.'),
                        'tong_sai_kythuat': format(kq1['tong_sai_kythuat'],',').split('.')[0].replace(',','.'),
                        }))
        return rs
        
    def get_line_tong_all(self):
        rs = [{
                'sl_2': format(self.total_all_sl_2,',').split('.')[0].replace(',','.'),
                'sl_3': format(self.total_all_sl_3,',').split('.')[0].replace(',','.'),
                'sl_4': format(self.total_all_sl_4,',').split('.')[0].replace(',','.'),
                'tong_ve': format(self.total_all_tong_ve,',').split('.')[0].replace(',','.'),
                'thanhtien': format(self.total_all_thanhtien,',').split('.')[0].replace(',','.'),
                'tong_sai_kythuat': format(self.total_all_sai_kythuat,',').split('.')[0].replace(',','.'),
               }]
        return rs
        