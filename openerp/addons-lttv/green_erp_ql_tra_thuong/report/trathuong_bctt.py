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
        self.localcontext.update({
            'get_lines': self.get_lines,
            'get_ten_khachhang': self.get_ten_khachhang,
            'get_soluong_giatri': self.get_soluong_giatri,
            'get_tong': self.get_tong,
            'get_tong_cong_soluong_giatri': self.get_tong_cong_soluong_giatri,
            'get_tong_cong': self.get_tong_cong,
            'get_date_from': self.get_date_from,
            'get_date_to': self.get_date_to,
            'get_date_now': self.get_date_now,
        })
    
    def get_date_now(self):
        return time.strftime('%Y-%m-%d')
    
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        return date_from[8:10]+'/'+date_from[5:7]+'/'+date_from[:4]
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date_to = wizard_data['date_to']
        return date_to[8:10]+'/'+date_to[5:7]+'/'+date_to[:4]
    
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select nguoi_nhan_thuong from tra_thuong_thucte where state='done' and ngay_tra_thuong between '%s' and '%s' group by nguoi_nhan_thuong
        '''%(date_from,date_to)
        self.cr.execute(sql)
        return self.cr.fetchall()
    
    def get_ten_khachhang(self,line):
#         return self.pool.get('res.partner').browse(self.cr, self.uid, line[0]).name
        return line[0]
    
    def get_soluong_giatri(self,line,menhgia):
        soluong = 0
        giatri = 0
        menhgia_obj = self.pool.get('product.product')
        tt_tt_obj = self.pool.get('tra.thuong.thucte.line')
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        menhgia_ids=False
        if menhgia=='1':
            sql = '''
                select id from product_product where default_code='MG-10.000d'
            '''
            self.cr.execute(sql)
            menhgia_ids = [r[0] for r in self.cr.fetchall()]
        if menhgia=='2':
            sql = '''
                select id from product_product where default_code='MG-20.000d'
            '''
            self.cr.execute(sql)
            menhgia_ids = [r[0] for r in self.cr.fetchall()]
        if menhgia=='5':
            sql = '''
                select id from product_product where default_code='MG-50.000d'
            '''
            self.cr.execute(sql)
            menhgia_ids = [r[0] for r in self.cr.fetchall()]
        if menhgia_ids:
            sql = '''
                select id from tra_thuong_thucte_line
                    where product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where state='done' and nguoi_nhan_thuong='%s' and ngay_tra_thuong between '%s' and '%s')
            '''%(menhgia_ids[0],line[0],date_from,date_to)
#             sql = '''
#                 select id from tra_thuong_thucte_line
#                     where product_id=%s
#                         and trathuong_id in (select id from tra_thuong_thucte where state='done' and ngay_tra_thuong between '%s' and '%s')
#             '''%(menhgia_ids[0],date_from,date_to)
            self.cr.execute(sql)
            tt_tt_ids = [r[0] for r in self.cr.fetchall()]
            for tt in tt_tt_obj.browse(self.cr, self.uid, tt_tt_ids):
                soluong += tt.sl_trung
                giatri += tt.tong
        return {
            'soluong': soluong,
            'giatri': giatri,
        }
        
    def get_tong(self,line):
        soluong = 0
        giatri = 0
        tt_tt_obj = self.pool.get('tra.thuong.thucte.line')
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select id from tra_thuong_thucte_line
                where trathuong_id in (select id from tra_thuong_thucte where state='done' and nguoi_nhan_thuong='%s' and ngay_tra_thuong between '%s' and '%s')
        '''%(line[0],date_from,date_to)
#         sql = '''
#             select id from tra_thuong_thucte_line
#                 where trathuong_id in (select id from tra_thuong_thucte where state='done' and ngay_tra_thuong between '%s' and '%s')
#         '''%(date_from,date_to)
        self.cr.execute(sql)
        tt_tt_ids = [r[0] for r in self.cr.fetchall()]
        for tt in tt_tt_obj.browse(self.cr, self.uid, tt_tt_ids):
            soluong += tt.sl_trung
            giatri += tt.tong
        return {
            'soluong': soluong,
            'giatri': giatri,
        }
        
    def get_tong_cong_soluong_giatri(self,menhgia):
        soluong = 0
        giatri = 0
        menhgia_obj = self.pool.get('product.product')
        tt_tt_obj = self.pool.get('tra.thuong.thucte.line')
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        menhgia_ids=False
        if menhgia=='1':
            sql = '''
                select id from product_product where default_code='MG-10.000d'
            '''
            self.cr.execute(sql)
            menhgia_ids = [r[0] for r in self.cr.fetchall()]
        if menhgia=='2':
            sql = '''
                select id from product_product where default_code='MG-20.000d'
            '''
            self.cr.execute(sql)
            menhgia_ids = [r[0] for r in self.cr.fetchall()]
        if menhgia=='5':
            sql = '''
                select id from product_product where default_code='MG-50.000d'
            '''
            self.cr.execute(sql)
            menhgia_ids = [r[0] for r in self.cr.fetchall()]
        if menhgia_ids:
            sql = '''
                select id from tra_thuong_thucte_line
                    where product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where state='done' and ngay_tra_thuong between '%s' and '%s')
            '''%(menhgia_ids[0],date_from,date_to)
            self.cr.execute(sql)
            tt_tt_ids = [r[0] for r in self.cr.fetchall()]
            for tt in tt_tt_obj.browse(self.cr, self.uid, tt_tt_ids):
                soluong += tt.sl_trung
                giatri += tt.tong
        return {
            'soluong': soluong,
            'giatri': giatri,
        }
        
    def get_tong_cong(self):
        soluong = 0
        giatri = 0
        tt_tt_obj = self.pool.get('tra.thuong.thucte.line')
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select id from tra_thuong_thucte_line
                where trathuong_id in (select id from tra_thuong_thucte where state='done' and ngay_tra_thuong between '%s' and '%s')
        '''%(date_from,date_to)
        self.cr.execute(sql)
        tt_tt_ids = [r[0] for r in self.cr.fetchall()]
        for tt in tt_tt_obj.browse(self.cr, self.uid, tt_tt_ids):
            soluong += tt.sl_trung
            giatri += tt.tong
        return {
            'soluong': soluong,
            'giatri': giatri,
        }
    