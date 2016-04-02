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
            'get_menhgia': self.get_menhgia,
            'get_lines': self.get_lines,
            'get_date_from': self.get_date_from,
            'get_date_to': self.get_date_to,
            'get_line_tong': self.get_line_tong,
            'convert_amount': self.convert_amount,
            
        })
        
    def convert_amount(self, amount):
        if not amount:
            amount = 0.0
        amount = format(amount, ',').split('.')[0]
        return amount.replace(',','.')
        
    def get_line_tong(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        res = []
        dl_dict = {}
        res.append({
            'tong_cong': 0,
        })
        for mg in self.get_menhgia():
            res[0][mg.id] = 0
            
        for menhgia in self.get_menhgia():
            sql = '''
                select case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line
                    
                    where product_id=%s and trathuong_id in (select id from tra_thuong_thucte where state='done'
                            and ngay_tra_thuong between '%s' and '%s')
            '''%(menhgia.id, date_from, date_to)
            self.cr.execute(sql)
            so_tien = self.cr.fetchone()[0]
            res[0][menhgia.id] = so_tien
            res[0]['tong_cong'] += so_tien
        return res
    
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        res = []
        dl_dict = {}
        sql = '''
            select rp.id as daily_id, rp.name as ho_ten
                
                from tra_thuong_thucte tttt
                left join res_partner rp on rp.id=tttt.daily_id
                
                where tttt.daily_id is not null and tttt.state='done' and tttt.ngay_tra_thuong between '%s' and '%s'
                
                group by rp.id, rp.name
                order by rp.id
            '''%(date_from, date_to)
        self.cr.execute(sql)
        for seq,dl in enumerate(self.cr.dictfetchall()):
            res.append({
                'ho_ten': dl['ho_ten'],
                'tong_cong': 0,
            })
            for mg in self.get_menhgia():
                res[seq][mg.id] = 0
                
            for menhgia in self.get_menhgia():
                sql = '''
                    select case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                        
                        from tra_thuong_thucte_line
                        
                        where product_id=%s and trathuong_id in (select id from tra_thuong_thucte where daily_id=%s
                                and state='done' and ngay_tra_thuong between '%s' and '%s')
                '''%(menhgia.id, dl['daily_id'], date_from, date_to)
                self.cr.execute(sql)
                so_tien = self.cr.fetchone()[0]
                res[seq][menhgia.id] = so_tien
                res[seq]['tong_cong'] += so_tien
        return res
    
    def get_vietname_date(self, date):
        if not date:
            return ''
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        return date_from
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date_to = wizard_data['date_to']
        return date_to
    
    def get_menhgia(self):
        menhgia_obj = self.pool.get('product.product')
        menh_gia_ids = menhgia_obj.search(self.cr, self.uid, [('menh_gia','=',True)])
        return menhgia_obj.browse(self.cr, self.uid, menh_gia_ids)
    
    def convert(self, amount):
        amount_text = amount_to_text_vn.amount_to_text(amount, 'vn')
        if amount_text and len(amount_text)>1:
            amount = amount_text[1:]
            head = amount_text[:1]
            amount_text = head.upper()+amount
        return amount_text
    