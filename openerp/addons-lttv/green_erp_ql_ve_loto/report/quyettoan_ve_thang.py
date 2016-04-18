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
            'get_date_to': self.get_date_to,
            'get_name_menhgia': self.get_name_menhgia,
            'get_line_tong': self.get_line_tong,
            'get_ddt_name': self.get_ddt_name,
        })
        
    def get_ddt_name(self, dai_duthuong_id):
        dai_duthuong = self.pool.get('dai.duthuong').browse(self.cr, self.uid, dai_duthuong_id)
        return dai_duthuong.name
        
    def get_line_tong(self):
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select 
                    case when sum(sl_2_d_tong)!=0 then sum(sl_2_d_tong) else 0 end sl_2_d_tong,
                    case when sum(sl_2_c_tong)!=0 then sum(sl_2_c_tong) else 0 end sl_2_c_tong,
                    case when sum(sl_2_dc_tong)!=0 then sum(sl_2_dc_tong) else 0 end sl_2_dc_tong,
                    case when sum(sl_2_18_tong)!=0 then sum(sl_2_18_tong) else 0 end sl_2_18_tong,
                    
                    case when sum(sl_3_d_tong)!=0 then sum(sl_3_d_tong) else 0 end sl_3_d_tong,
                    case when sum(sl_3_c_tong)!=0 then sum(sl_3_c_tong) else 0 end sl_3_c_tong,
                    case when sum(sl_3_dc_tong)!=0 then sum(sl_3_dc_tong) else 0 end sl_3_dc_tong,
                    case when sum(sl_3_7_tong)!=0 then sum(sl_3_7_tong) else 0 end sl_3_7_tong,
                    case when sum(sl_3_17_tong)!=0 then sum(sl_3_17_tong) else 0 end sl_3_17_tong,
                    
                    case when sum(sl_4_16_tong)!=0 then sum(sl_4_16_tong) else 0 end sl_4_16_tong,
                    
                    case when sum(st_2_d_tong)!=0 then sum(st_2_d_tong) else 0 end st_2_d_tong,
                    case when sum(st_2_c_tong)!=0 then sum(st_2_c_tong) else 0 end st_2_c_tong,
                    case when sum(st_2_dc_tong)!=0 then sum(st_2_dc_tong) else 0 end st_2_dc_tong,
                    case when sum(st_2_18_tong)!=0 then sum(st_2_18_tong) else 0 end st_2_18_tong,
                    
                    case when sum(st_3_d_tong)!=0 then sum(st_3_d_tong) else 0 end st_3_d_tong,
                    case when sum(st_3_c_tong)!=0 then sum(st_3_c_tong) else 0 end st_3_c_tong,
                    case when sum(st_3_dc_tong)!=0 then sum(st_3_dc_tong) else 0 end st_3_dc_tong,
                    case when sum(st_3_7_tong)!=0 then sum(st_3_7_tong) else 0 end st_3_7_tong,
                    case when sum(st_3_17_tong)!=0 then sum(st_3_17_tong) else 0 end st_3_17_tong,
                
                    case when sum(st_4_16_tong)!=0 then sum(st_4_16_tong) else 0 end st_4_16_tong,
                    
                    case when sum(sl_tong)!=0 then sum(sl_tong) else 0 end sl_tong,
                    case when sum(st_tong)!=0 then sum(st_tong) else 0 end st_tong
            
                from quyet_toan_ve_ngay
                
                where date_to between '%s' and '%s' and product_id=%s
                
        '''%(date_from,date_to,product[0])
        self.cr.execute(sql)
        return self.cr.dictfetchall()
        
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select dai_duthuong_id,slan_2_dc, slan_2_18, slan_3_dc, slan_3_7, slan_3_17, slan_4_16,
                    case when sum(sl_2_d)!=0 then sum(sl_2_d) else 0 end sl_2_d,
                    case when sum(sl_2_c)!=0 then sum(sl_2_c) else 0 end sl_2_c,
                    case when sum(sl_2_dc)!=0 then sum(sl_2_dc) else 0 end sl_2_dc,
                    case when sum(sl_2_18)!=0 then sum(sl_2_18) else 0 end sl_2_18,
                    
                    case when sum(sl_3_d)!=0 then sum(sl_3_d) else 0 end sl_3_d,
                    case when sum(sl_3_c)!=0 then sum(sl_3_c) else 0 end sl_3_c,
                    case when sum(sl_3_dc)!=0 then sum(sl_3_dc) else 0 end sl_3_dc,
                    case when sum(sl_3_7)!=0 then sum(sl_3_7) else 0 end sl_3_7,
                    case when sum(sl_3_17)!=0 then sum(sl_3_17) else 0 end sl_3_17,
                    
                    case when sum(sl_4_16)!=0 then sum(sl_4_16) else 0 end sl_4_16,
                    
                    case when sum(st_2_d)!=0 then sum(st_2_d) else 0 end st_2_d,
                    case when sum(st_2_c)!=0 then sum(st_2_c) else 0 end st_2_c,
                    case when sum(st_2_dc)!=0 then sum(st_2_dc) else 0 end st_2_dc,
                    case when sum(st_2_18)!=0 then sum(st_2_18) else 0 end st_2_18,
                    
                    case when sum(st_3_d)!=0 then sum(st_3_d) else 0 end st_3_d,
                    case when sum(st_3_c)!=0 then sum(st_3_c) else 0 end st_3_c,
                    case when sum(st_3_dc)!=0 then sum(st_3_dc) else 0 end st_3_dc,
                    case when sum(st_3_7)!=0 then sum(st_3_7) else 0 end st_3_7,
                    case when sum(st_3_17)!=0 then sum(st_3_17) else 0 end st_3_17,
                
                    case when sum(st_4_16)!=0 then sum(st_4_16) else 0 end st_4_16,
                    
                    case when sum(sl_tong)!=0 then sum(sl_tong) else 0 end sl_tong,
                    case when sum(st_tong)!=0 then sum(st_tong) else 0 end st_tong
            
                from quyet_toan_ve_ngay_line
                
                where quyettoan_id in (select id from quyet_toan_ve_ngay where date_to between '%s' and '%s' and product_id=%s)
                
                group by dai_duthuong_id,slan_2_dc, slan_2_18, slan_3_dc, slan_3_7, slan_3_17, slan_4_16
        '''%(date_from,date_to,product[0])
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_vietname_date(self, date):
        if not date:
            return ''
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date_to = wizard_data['date_to']
        return date_to
    
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
    