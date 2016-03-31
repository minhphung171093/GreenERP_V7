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
            'get_ddt_name': self.get_ddt_name,
            'get_2_dc': self.get_2_dc,
            'get_2_18': self.get_2_18,
        })
        
    def get_ddt_name(self, dai_duthuong_id):
        dai_duthuong = self.pool.get('dai.duthuong').browse(self.cr, self.uid, dai_duthuong_id)
        return dai_duthuong.name
        
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        product = wizard_data['product_id']
        sql = '''
            select date_to
                from quyet_toan_ve_ngay
                where product_id=%s and id in (select quyettoan_id from quyet_toan_ve_ngay_line where ngay_mo_thuong='%s')
                group by date_to order by date_to
        '''%(product[0],date)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_2_dc(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        product = wizard_data['product_id']
        res = []
        seq = -1
        sl_tong = 0
        st_tong = 0
        for col in self.get_lines():
            seq += 1
            seq_n = seq
            if seq==0:
                res.append({
                    'name': 'Đ/C',
                    col['date_to']:0,
                    'sl_tong': 0,
                    'slan_tong': 0,
                    'st_tong': 0,     
                })
            else:
                res.append({
                    'name': '',
                    col['date_to']:0,
                    'sl_tong': 0,
                    'slan_tong': 0,
                    'st_tong': 0,     
                })
            sql = '''
                select slan_2_dc,
                        case when sum(sl_2_dc)!=0 then sum(sl_2_dc) else 0 end sl_2_dc,
                        case when sum(st_2_dc)!=0 then sum(st_2_dc) else 0 end st_2_dc
                
                    from quyet_toan_ve_ngay_line
                    
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s)
                    
                    group by slan_2_dc
            '''%(col['date_to'],product[0])
            self.cr.execute(sql)
            for seq_2_dc, line_2_dc in enumerate(self.cr.dictfetchall()):
                if seq_n+seq_2_dc < seq:
                    seq += 1
                    res.append({
                        'name': '',
                        col['date_to']:0,
                        'sl_tong': 0,
                        'slan_tong': 0,
                        'st_tong': 0,     
                    })
                res[seq_n+seq_2_dc][col['date_to']] = line_2_dc['sl_2_dc']
                res[seq_n+seq_2_dc]['sl_tong'] += line_2_dc['sl_2_dc']
                res[seq_n+seq_2_dc]['slan_tong'] = line_2_dc['slan_2_dc']
                res[seq_n+seq_2_dc]['st_tong'] += line_2_dc['st_2_dc']
        return res
    
    def get_2_18(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        product = wizard_data['product_id']
        res = []
        seq = -1
        sl_tong = 0
        st_tong = 0
        for col in self.get_lines():
            seq += 1
            seq_n = seq
            if seq==0:
                res.append({
                    'name': '18 Lô',
                    col['date_to']:0,
                    'sl_tong': 0,
                    'slan_tong': 0,
                    'st_tong': 0,     
                })
            else:
                res.append({
                    'name': '',
                    col['date_to']:0,
                    'sl_tong': 0,
                    'slan_tong': 0,
                    'st_tong': 0,     
                })
            sql = '''
                select slan_2_18,
                        case when sum(sl_2_18)!=0 then sum(sl_2_18) else 0 end sl_2_18,
                        case when sum(st_2_18)!=0 then sum(st_2_18) else 0 end st_2_18
                
                    from quyet_toan_ve_ngay_line
                    
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s)
                    
                    group by slan_2_18
            '''%(date,product[0])
            self.cr.execute(sql)
            for seq_2_18, line_2_18 in enumerate(self.cr.dictfetchall()):
                if seq_n+seq_2_18 > seq:
                    seq += 1
                    res.append({
                        'name': '',
                        col['date_to']:0,
                        'sl_tong': 0,
                        'slan_tong': 0,
                        'st_tong': 0,     
                    })
                res[seq_n+seq_2_18][col['date_to']] = line_2_18['sl_2_18']
                res[seq_n+seq_2_18]['sl_tong'] += line_2_18['sl_2_18']
                res[seq_n+seq_2_18]['slan_tong'] = line_2_18['slan_2_18']
                res[seq_n+seq_2_18]['st_tong'] += line_2_18['st_2_18']
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
    