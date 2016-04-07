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
        self.sl_phai_tra_tong = 0
        self.stien_phai_tra_tong = 0
        self.sl_da_tra_tong = 0
        self.stien_da_tra_tong = 0
        self.sl_con_lai_tong = 0
        self.stien_con_lai_tong = 0
        self.localcontext.update({
            'get_vietname_date': self.get_vietname_date,
            'convert': self.convert,
            'get_gt_menhgia': self.get_gt_menhgia,
            'get_name_menhgia': self.get_name_menhgia,
            'get_ngaymothuong': self.get_ngaymothuong,
            'get_daiduthuong': self.get_daiduthuong,
            'get_date_now': self.get_date_now,
            'get_2_d': self.get_2_d,
            'get_2_c': self.get_2_c,
            'get_2_dc': self.get_2_dc,
            'get_2_18': self.get_2_18,
            'get_3_d': self.get_3_d,
            'get_3_c': self.get_3_c,
            'get_3_dc': self.get_3_dc,
            'get_3_7': self.get_3_7,
            'get_3_17': self.get_3_17,
            'get_4_16': self.get_4_16,
            'get_tong': self.get_tong,
        })
        
    def get_tong(self):
        res = [{
            'sl_phai_tra_tong': self.sl_phai_tra_tong,
            'stien_phai_tra_tong': self.stien_phai_tra_tong,
            'sl_da_tra_tong': self.sl_da_tra_tong,
            'stien_da_tra_tong': self.stien_da_tra_tong,
            'sl_con_lai_tong': self.sl_con_lai_tong,
            'stien_con_lai_tong': self.stien_con_lai_tong,
        }]
        return res
        
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
                where kqxs.name='%s'
        '''%(date)
        self.cr.execute(sql)
        ddt = self.cr.fetchall()
        if ddt:
            return ddt[0]
        else:
            return ''
    
    def get_2_d(self):
        res = []
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        date = wizard_data['date']
        sql = '''
        select slan_trung
        
        from (
            select case when slan_trung!=0 then slan_trung else 1 end slan_trung
                from tra_thuong_line
                
                where loai='2_so' and giai='dau' and product_id=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
        ) foo
                group by slan_trung
                order by slan_trung
        '''%(product[0], date)
        self.cr.execute(sql)
        
        for sl in self.cr.dictfetchall():#'so lan trung  ngay mo thuong order by tang dan':
            #'sql sum so tien, so luong phai tra'
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung*slan_trung*tong_tien)!=0 then sum(sl_trung*slan_trung*tong_tien) else 0 end st_trung
                    
                    from tra_thuong_line
                
                where loai='2_so' and giai='dau' and product_id=%s and slan_trung=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
            '''%(product[0],sl['slan_trung'], date)
            self.cr.execute(sql)
            phaitra_2_18 = self.cr.dictfetchone()
            #'sql sum so tien, so luong da tra'
#             sql = '''
#                 select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
#                     case when sum(sl_trung*slan_trung*tong_tien)!=0 then sum(sl_trung*slan_trung*tong_tien) else 0 end st_trung
#                     
#                     from tra_thuong_thucte_line
#                 
#                 where loai='2_so' and giai='dau' and product_id=%s and slan_trung=%s and trathuong_id in (select id from tra_thuong_thucte where ngay='%s')
#             '''%(product[0],sl['slan_trung'], date)
            
            sql = '''
                select case when sum(sl_2_d)!=0 then sum(sl_2_d) else 0 end sl_trung,
                    case when sum(st_2_d)!=0 then sum(st_2_d) else 0 end st_trung
                    
                    from quyet_toan_ve_ngay_line
                
                where quyettoan_id in (select id from quyet_toan_ve_ngay where ngay_mo_thuong='%s' and product_id=%s)
            '''%(date, product[0])
            self.cr.execute(sql)
            datra_2_18 = self.cr.dictfetchone()
            res.append({
                        'so_lan':sl['slan_trung'],
                        'sl_phai_tra': phaitra_2_18['sl_trung'],
                        'stien_phai_tra': phaitra_2_18['st_trung'],
                        'sl_da_tra': datra_2_18['sl_trung'],
                        'stien_da_tra': datra_2_18['st_trung'],
                        'sl_con_lai': phaitra_2_18['sl_trung'] - datra_2_18['sl_trung'],
                        'stien_con_lai': phaitra_2_18['st_trung'] - datra_2_18['st_trung'],
                        })
            #'dung bien toan cuc de tim tong cong'
            self.sl_phai_tra_tong += phaitra_2_18['sl_trung']
            self.stien_phai_tra_tong += phaitra_2_18['st_trung']
            self.sl_da_tra_tong += datra_2_18['sl_trung']
            self.stien_da_tra_tong += datra_2_18['st_trung']
            self.sl_con_lai_tong += phaitra_2_18['sl_trung'] - datra_2_18['sl_trung']
            self.stien_con_lai_tong += phaitra_2_18['st_trung'] - datra_2_18['st_trung']
        if not res:
            res.append({
                'so_lan': '',
                'sl_phai_tra': 0,
                'stien_phai_tra': 0,
                'sl_da_tra': 0,
                'stien_da_tra': 0,
                'sl_con_lai': 0,
                'stien_con_lai': 0,
            })
        return res
    
    def get_2_c(self):
        res = []
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        date = wizard_data['date']
        sql = '''
        select slan_trung
        
        from (
            select case when slan_trung!=0 then slan_trung else 1 end slan_trung
                from tra_thuong_line
                
                where loai='2_so' and giai='cuoi' and product_id=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
        ) foo
                group by slan_trung
                order by slan_trung
        '''%(product[0], date)
        self.cr.execute(sql)
        
        for sl in self.cr.dictfetchall():#'so lan trung  ngay mo thuong order by tang dan':
            #'sql sum so tien, so luong phai tra'
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung*slan_trung*tong_tien)!=0 then sum(sl_trung*slan_trung*tong_tien) else 0 end st_trung
                    
                    from tra_thuong_line
                
                where loai='2_so' and giai='cuoi' and product_id=%s and slan_trung=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
            '''%(product[0],sl['slan_trung'], date)
            self.cr.execute(sql)
            phaitra_2_18 = self.cr.dictfetchone()
            #'sql sum so tien, so luong da tra'
#             sql = '''
#                 select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
#                     case when sum(sl_trung*slan_trung*tong_tien)!=0 then sum(sl_trung*slan_trung*tong_tien) else 0 end st_trung
#                     
#                     from tra_thuong_thucte_line
#                 
#                 where loai='2_so' and giai='cuoi' and product_id=%s and slan_trung=%s and trathuong_id in (select id from tra_thuong_thucte where ngay='%s')
#             '''%(product[0],sl['slan_trung'], date)
            sql = '''
                select case when sum(sl_2_c)!=0 then sum(sl_2_c) else 0 end sl_trung,
                    case when sum(st_2_c)!=0 then sum(st_2_c) else 0 end st_trung
                    
                    from quyet_toan_ve_ngay_line
                
                where quyettoan_id in (select id from quyet_toan_ve_ngay where ngay_mo_thuong='%s' and product_id=%s)
            '''%(date, product[0])
            self.cr.execute(sql)
            datra_2_18 = self.cr.dictfetchone()
            res.append({
                        'so_lan':sl['slan_trung'],
                        'sl_phai_tra': phaitra_2_18['sl_trung'],
                        'stien_phai_tra': phaitra_2_18['st_trung'],
                        'sl_da_tra': datra_2_18['sl_trung'],
                        'stien_da_tra': datra_2_18['st_trung'],
                        'sl_con_lai': phaitra_2_18['sl_trung'] - datra_2_18['sl_trung'],
                        'stien_con_lai': phaitra_2_18['st_trung'] - datra_2_18['st_trung'],
                        })
            #'dung bien toan cuc de tim tong cong'
            self.sl_phai_tra_tong += phaitra_2_18['sl_trung']
            self.stien_phai_tra_tong += phaitra_2_18['st_trung']
            self.sl_da_tra_tong += datra_2_18['sl_trung']
            self.stien_da_tra_tong += datra_2_18['st_trung']
            self.sl_con_lai_tong += phaitra_2_18['sl_trung'] - datra_2_18['sl_trung']
            self.stien_con_lai_tong += phaitra_2_18['st_trung'] - datra_2_18['st_trung']
        if not res:
            res.append({
                'so_lan': '',
                'sl_phai_tra': 0,
                'stien_phai_tra': 0,
                'sl_da_tra': 0,
                'stien_da_tra': 0,
                'sl_con_lai': 0,
                'stien_con_lai': 0,
            })
        return res
    
    def get_2_dc(self):
        res = []
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        date = wizard_data['date']
        sql = '''
        select slan_trung
        
        from (
            select case when slan_trung!=0 then slan_trung else 1 end slan_trung
                from tra_thuong_line
                
                where loai='2_so' and giai='dau_cuoi' and product_id=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
        ) foo
                group by slan_trung
                order by slan_trung
        '''%(product[0], date)
        self.cr.execute(sql)
        
        for sl in self.cr.dictfetchall():#'so lan trung  ngay mo thuong order by tang dan':
            #'sql sum so tien, so luong phai tra'
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung*slan_trung*tong_tien)!=0 then sum(sl_trung*slan_trung*tong_tien) else 0 end st_trung
                    
                    from tra_thuong_line
                
                where loai='2_so' and giai='dau_cuoi' and product_id=%s and slan_trung=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
            '''%(product[0],sl['slan_trung'], date)
            self.cr.execute(sql)
            phaitra_2_18 = self.cr.dictfetchone()
            #'sql sum so tien, so luong da tra'
            sql = '''
                select case when sum(sl_2_dc)!=0 then sum(sl_2_dc) else 0 end sl_trung,
                    case when sum(st_2_dc)!=0 then sum(st_2_dc) else 0 end st_trung
                    
                    from quyet_toan_ve_ngay_line
                
                where slan_2_dc=%s and quyettoan_id in (select id from quyet_toan_ve_ngay where ngay_mo_thuong='%s' and product_id=%s)
            '''%(sl['slan_trung'], date, product[0])
            self.cr.execute(sql)
            datra_2_18 = self.cr.dictfetchone()
            res.append({
                        'so_lan':sl['slan_trung'],
                        'sl_phai_tra': phaitra_2_18['sl_trung'],
                        'stien_phai_tra': phaitra_2_18['st_trung'],
                        'sl_da_tra': datra_2_18['sl_trung'],
                        'stien_da_tra': datra_2_18['st_trung'],
                        'sl_con_lai': phaitra_2_18['sl_trung'] - datra_2_18['sl_trung'],
                        'stien_con_lai': phaitra_2_18['st_trung'] - datra_2_18['st_trung'],
                        })
            #'dung bien toan cuc de tim tong cong'
            self.sl_phai_tra_tong += phaitra_2_18['sl_trung']
            self.stien_phai_tra_tong += phaitra_2_18['st_trung']
            self.sl_da_tra_tong += datra_2_18['sl_trung']
            self.stien_da_tra_tong += datra_2_18['st_trung']
            self.sl_con_lai_tong += phaitra_2_18['sl_trung'] - datra_2_18['sl_trung']
            self.stien_con_lai_tong += phaitra_2_18['st_trung'] - datra_2_18['st_trung']
        if not res:
            res.append({
                'so_lan': '',
                'sl_phai_tra': 0,
                'stien_phai_tra': 0,
                'sl_da_tra': 0,
                'stien_da_tra': 0,
                'sl_con_lai': 0,
                'stien_con_lai': 0,
            })
        return res
    
    def get_2_18(self):
        res = []
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        date = wizard_data['date']
        sql = '''
        select slan_trung
        
        from (
            select case when slan_trung!=0 then slan_trung else 1 end slan_trung
                from tra_thuong_line
                
                where loai='2_so' and giai='18_lo' and product_id=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
        ) foo
                group by slan_trung
                order by slan_trung
        '''%(product[0], date)
        self.cr.execute(sql)
        
        for sl in self.cr.dictfetchall():#'so lan trung  ngay mo thuong order by tang dan':
            #'sql sum so tien, so luong phai tra'
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung*slan_trung*tong_tien)!=0 then sum(sl_trung*slan_trung*tong_tien) else 0 end st_trung
                    
                    from tra_thuong_line
                
                where loai='2_so' and giai='18_lo' and product_id=%s and slan_trung=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
            '''%(product[0],sl['slan_trung'], date)
            self.cr.execute(sql)
            phaitra_2_18 = self.cr.dictfetchone()
            #'sql sum so tien, so luong da tra'
            sql = '''
                select case when sum(sl_2_18)!=0 then sum(sl_2_18) else 0 end sl_trung,
                    case when sum(st_2_18)!=0 then sum(st_2_18) else 0 end st_trung
                    
                    from quyet_toan_ve_ngay_line
                
                where slan_2_18=%s and quyettoan_id in (select id from quyet_toan_ve_ngay where ngay_mo_thuong='%s' and product_id=%s)
            '''%(sl['slan_trung'], date, product[0])
            self.cr.execute(sql)
            datra_2_18 = self.cr.dictfetchone()
            res.append({
                        'so_lan':sl['slan_trung'],
                        'sl_phai_tra': phaitra_2_18['sl_trung'],
                        'stien_phai_tra': phaitra_2_18['st_trung'],
                        'sl_da_tra': datra_2_18['sl_trung'],
                        'stien_da_tra': datra_2_18['st_trung'],
                        'sl_con_lai': phaitra_2_18['sl_trung'] - datra_2_18['sl_trung'],
                        'stien_con_lai': phaitra_2_18['st_trung'] - datra_2_18['st_trung'],
                        })
            #'dung bien toan cuc de tim tong cong'
            self.sl_phai_tra_tong += phaitra_2_18['sl_trung']
            self.stien_phai_tra_tong += phaitra_2_18['st_trung']
            self.sl_da_tra_tong += datra_2_18['sl_trung']
            self.stien_da_tra_tong += datra_2_18['st_trung']
            self.sl_con_lai_tong += phaitra_2_18['sl_trung'] - datra_2_18['sl_trung']
            self.stien_con_lai_tong += phaitra_2_18['st_trung'] - datra_2_18['st_trung']
        if not res:
            res.append({
                'so_lan': '',
                'sl_phai_tra': 0,
                'stien_phai_tra': 0,
                'sl_da_tra': 0,
                'stien_da_tra': 0,
                'sl_con_lai': 0,
                'stien_con_lai': 0,
            })
        return res
    
    def get_3_d(self):
        res = []
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        date = wizard_data['date']
        sql = '''
        select slan_trung
        
        from (
            select case when slan_trung!=0 then slan_trung else 1 end slan_trung
                from tra_thuong_line
                
                where loai='3_so' and giai='dau' and product_id=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
        ) foo
                group by slan_trung
                order by slan_trung
        '''%(product[0], date)
        self.cr.execute(sql)
        
        for sl in self.cr.dictfetchall():#'so lan trung  ngay mo thuong order by tang dan':
            #'sql sum so tien, so luong phai tra'
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung*slan_trung*tong_tien)!=0 then sum(sl_trung*slan_trung*tong_tien) else 0 end st_trung
                    
                    from tra_thuong_line
                
                where loai='3_so' and giai='dau' and product_id=%s and slan_trung=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
            '''%(product[0],sl['slan_trung'], date)
            self.cr.execute(sql)
            phaitra_2_18 = self.cr.dictfetchone()
            #'sql sum so tien, so luong da tra'
            sql = '''
                select case when sum(sl_3_d)!=0 then sum(sl_3_d) else 0 end sl_trung,
                    case when sum(st_3_d)!=0 then sum(st_3_d) else 0 end st_trung
                    
                    from quyet_toan_ve_ngay_line
                
                where quyettoan_id in (select id from quyet_toan_ve_ngay where ngay_mo_thuong='%s' and product_id=%s)
            '''%(date, product[0])
            self.cr.execute(sql)
            datra_2_18 = self.cr.dictfetchone()
            res.append({
                        'so_lan':sl['slan_trung'],
                        'sl_phai_tra': phaitra_2_18['sl_trung'],
                        'stien_phai_tra': phaitra_2_18['st_trung'],
                        'sl_da_tra': datra_2_18['sl_trung'],
                        'stien_da_tra': datra_2_18['st_trung'],
                        'sl_con_lai': phaitra_2_18['sl_trung'] - datra_2_18['sl_trung'],
                        'stien_con_lai': phaitra_2_18['st_trung'] - datra_2_18['st_trung'],
                        })
            #'dung bien toan cuc de tim tong cong'
            self.sl_phai_tra_tong += phaitra_2_18['sl_trung']
            self.stien_phai_tra_tong += phaitra_2_18['st_trung']
            self.sl_da_tra_tong += datra_2_18['sl_trung']
            self.stien_da_tra_tong += datra_2_18['st_trung']
            self.sl_con_lai_tong += phaitra_2_18['sl_trung'] - datra_2_18['sl_trung']
            self.stien_con_lai_tong += phaitra_2_18['st_trung'] - datra_2_18['st_trung']
        if not res:
            res.append({
                'so_lan': '',
                'sl_phai_tra': 0,
                'stien_phai_tra': 0,
                'sl_da_tra': 0,
                'stien_da_tra': 0,
                'sl_con_lai': 0,
                'stien_con_lai': 0,
            })
        return res
    
    def get_3_c(self):
        res = []
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        date = wizard_data['date']
        sql = '''
        select slan_trung
        
        from (
            select case when slan_trung!=0 then slan_trung else 1 end slan_trung
                from tra_thuong_line
                
                where loai='3_so' and giai='cuoi' and product_id=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
        ) foo
                group by slan_trung
                order by slan_trung
        '''%(product[0], date)
        self.cr.execute(sql)
        
        for sl in self.cr.dictfetchall():#'so lan trung  ngay mo thuong order by tang dan':
            #'sql sum so tien, so luong phai tra'
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung*slan_trung*tong_tien)!=0 then sum(sl_trung*slan_trung*tong_tien) else 0 end st_trung
                    
                    from tra_thuong_line
                
                where loai='3_so' and giai='cuoi' and product_id=%s and slan_trung=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
            '''%(product[0],sl['slan_trung'], date)
            self.cr.execute(sql)
            phaitra_2_18 = self.cr.dictfetchone()
            #'sql sum so tien, so luong da tra'
            sql = '''
                select case when sum(sl_3_c)!=0 then sum(sl_3_c) else 0 end sl_trung,
                    case when sum(st_3_c)!=0 then sum(st_3_c) else 0 end st_trung
                    
                    from quyet_toan_ve_ngay_line
                
                where quyettoan_id in (select id from quyet_toan_ve_ngay where ngay_mo_thuong='%s' and product_id=%s)
            '''%(date, product[0])
            self.cr.execute(sql)
            datra_2_18 = self.cr.dictfetchone()
            res.append({
                        'so_lan':sl['slan_trung'],
                        'sl_phai_tra': phaitra_2_18['sl_trung'],
                        'stien_phai_tra': phaitra_2_18['st_trung'],
                        'sl_da_tra': datra_2_18['sl_trung'],
                        'stien_da_tra': datra_2_18['st_trung'],
                        'sl_con_lai': phaitra_2_18['sl_trung'] - datra_2_18['sl_trung'],
                        'stien_con_lai': phaitra_2_18['st_trung'] - datra_2_18['st_trung'],
                        })
            #'dung bien toan cuc de tim tong cong'
            self.sl_phai_tra_tong += phaitra_2_18['sl_trung']
            self.stien_phai_tra_tong += phaitra_2_18['st_trung']
            self.sl_da_tra_tong += datra_2_18['sl_trung']
            self.stien_da_tra_tong += datra_2_18['st_trung']
            self.sl_con_lai_tong += phaitra_2_18['sl_trung'] - datra_2_18['sl_trung']
            self.stien_con_lai_tong += phaitra_2_18['st_trung'] - datra_2_18['st_trung']
        if not res:
            res.append({
                'so_lan': '',
                'sl_phai_tra': 0,
                'stien_phai_tra': 0,
                'sl_da_tra': 0,
                'stien_da_tra': 0,
                'sl_con_lai': 0,
                'stien_con_lai': 0,
            })
        return res
    
    def get_3_dc(self):
        res = []
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        date = wizard_data['date']
        sql = '''
        select slan_trung
        
        from (
            select case when slan_trung!=0 then slan_trung else 1 end slan_trung
                from tra_thuong_line
                
                where loai='3_so' and giai='dau_cuoi' and product_id=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
        ) foo
                group by slan_trung
                order by slan_trung
        '''%(product[0], date)
        self.cr.execute(sql)
        
        for sl in self.cr.dictfetchall():#'so lan trung  ngay mo thuong order by tang dan':
            #'sql sum so tien, so luong phai tra'
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung*slan_trung*tong_tien)!=0 then sum(sl_trung*slan_trung*tong_tien) else 0 end st_trung
                    
                    from tra_thuong_line
                
                where loai='3_so' and giai='dau_cuoi' and product_id=%s and slan_trung=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
            '''%(product[0],sl['slan_trung'], date)
            self.cr.execute(sql)
            phaitra_2_18 = self.cr.dictfetchone()
            #'sql sum so tien, so luong da tra'
            sql = '''
                select case when sum(sl_3_dc)!=0 then sum(sl_3_dc) else 0 end sl_trung,
                    case when sum(st_3_dc)!=0 then sum(st_3_dc) else 0 end st_trung
                    
                    from quyet_toan_ve_ngay_line
                
                where slan_3_dc=%s and quyettoan_id in (select id from quyet_toan_ve_ngay where ngay_mo_thuong='%s' and product_id=%s)
            '''%(sl['slan_trung'], date, product[0])
            self.cr.execute(sql)
            datra_2_18 = self.cr.dictfetchone()
            res.append({
                        'so_lan':sl['slan_trung'],
                        'sl_phai_tra': phaitra_2_18['sl_trung'],
                        'stien_phai_tra': phaitra_2_18['st_trung'],
                        'sl_da_tra': datra_2_18['sl_trung'],
                        'stien_da_tra': datra_2_18['st_trung'],
                        'sl_con_lai': phaitra_2_18['sl_trung'] - datra_2_18['sl_trung'],
                        'stien_con_lai': phaitra_2_18['st_trung'] - datra_2_18['st_trung'],
                        })
            #'dung bien toan cuc de tim tong cong'
            self.sl_phai_tra_tong += phaitra_2_18['sl_trung']
            self.stien_phai_tra_tong += phaitra_2_18['st_trung']
            self.sl_da_tra_tong += datra_2_18['sl_trung']
            self.stien_da_tra_tong += datra_2_18['st_trung']
            self.sl_con_lai_tong += phaitra_2_18['sl_trung'] - datra_2_18['sl_trung']
            self.stien_con_lai_tong += phaitra_2_18['st_trung'] - datra_2_18['st_trung']
        if not res:
            res.append({
                'so_lan': '',
                'sl_phai_tra': 0,
                'stien_phai_tra': 0,
                'sl_da_tra': 0,
                'stien_da_tra': 0,
                'sl_con_lai': 0,
                'stien_con_lai': 0,
            })
        return res
    
    def get_3_7(self):
        res = []
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        date = wizard_data['date']
        sql = '''
        select slan_trung
        
        from (
            select case when slan_trung!=0 then slan_trung else 1 end slan_trung
                from tra_thuong_line
                
                where loai='3_so' and giai='7_lo' and product_id=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
        ) foo
                group by slan_trung
                order by slan_trung
        '''%(product[0], date)
        self.cr.execute(sql)
        
        for sl in self.cr.dictfetchall():#'so lan trung  ngay mo thuong order by tang dan':
            #'sql sum so tien, so luong phai tra'
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung*slan_trung*tong_tien)!=0 then sum(sl_trung*slan_trung*tong_tien) else 0 end st_trung
                    
                    from tra_thuong_line
                
                where loai='3_so' and giai='7_lo' and product_id=%s and slan_trung=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
            '''%(product[0],sl['slan_trung'], date)
            self.cr.execute(sql)
            phaitra_2_18 = self.cr.dictfetchone()
            #'sql sum so tien, so luong da tra'
            sql = '''
                select case when sum(sl_3_7)!=0 then sum(sl_3_7) else 0 end sl_trung,
                    case when sum(st_3_7)!=0 then sum(st_3_7) else 0 end st_trung
                    
                    from quyet_toan_ve_ngay_line
                
                where slan_3_7=%s and quyettoan_id in (select id from quyet_toan_ve_ngay where ngay_mo_thuong='%s' and product_id=%s)
            '''%(sl['slan_trung'], date, product[0])
            self.cr.execute(sql)
            datra_2_18 = self.cr.dictfetchone()
            res.append({
                        'so_lan':sl['slan_trung'],
                        'sl_phai_tra': phaitra_2_18['sl_trung'],
                        'stien_phai_tra': phaitra_2_18['st_trung'],
                        'sl_da_tra': datra_2_18['sl_trung'],
                        'stien_da_tra': datra_2_18['st_trung'],
                        'sl_con_lai': phaitra_2_18['sl_trung'] - datra_2_18['sl_trung'],
                        'stien_con_lai': phaitra_2_18['st_trung'] - datra_2_18['st_trung'],
                        })
            #'dung bien toan cuc de tim tong cong'
            self.sl_phai_tra_tong += phaitra_2_18['sl_trung']
            self.stien_phai_tra_tong += phaitra_2_18['st_trung']
            self.sl_da_tra_tong += datra_2_18['sl_trung']
            self.stien_da_tra_tong += datra_2_18['st_trung']
            self.sl_con_lai_tong += phaitra_2_18['sl_trung'] - datra_2_18['sl_trung']
            self.stien_con_lai_tong += phaitra_2_18['st_trung'] - datra_2_18['st_trung']
        if not res:
            res.append({
                'so_lan': '',
                'sl_phai_tra': 0,
                'stien_phai_tra': 0,
                'sl_da_tra': 0,
                'stien_da_tra': 0,
                'sl_con_lai': 0,
                'stien_con_lai': 0,
            })
        return res
    
    def get_3_17(self):
        res = []
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        date = wizard_data['date']
        sql = '''
        select slan_trung
        
        from (
            select case when slan_trung!=0 then slan_trung else 1 end slan_trung
                from tra_thuong_line
                
                where loai='3_so' and giai='17_lo' and product_id=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
        ) foo
                group by slan_trung
                order by slan_trung
        '''%(product[0], date)
        self.cr.execute(sql)
        
        for sl in self.cr.dictfetchall():#'so lan trung  ngay mo thuong order by tang dan':
            #'sql sum so tien, so luong phai tra'
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung*slan_trung*tong_tien)!=0 then sum(sl_trung*slan_trung*tong_tien) else 0 end st_trung
                    
                    from tra_thuong_line
                
                where loai='3_so' and giai='17_lo' and product_id=%s and slan_trung=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
            '''%(product[0],sl['slan_trung'], date)
            self.cr.execute(sql)
            phaitra_2_18 = self.cr.dictfetchone()
            #'sql sum so tien, so luong da tra'
            sql = '''
                select case when sum(sl_3_17)!=0 then sum(sl_3_17) else 0 end sl_trung,
                    case when sum(st_3_17)!=0 then sum(st_3_17) else 0 end st_trung
                    
                    from quyet_toan_ve_ngay_line
                
                where slan_3_17=%s and quyettoan_id in (select id from quyet_toan_ve_ngay where ngay_mo_thuong='%s' and product_id=%s)
            '''%(sl['slan_trung'], date, product[0])
            self.cr.execute(sql)
            datra_2_18 = self.cr.dictfetchone()
            res.append({
                        'so_lan':sl['slan_trung'],
                        'sl_phai_tra': phaitra_2_18['sl_trung'],
                        'stien_phai_tra': phaitra_2_18['st_trung'],
                        'sl_da_tra': datra_2_18['sl_trung'],
                        'stien_da_tra': datra_2_18['st_trung'],
                        'sl_con_lai': phaitra_2_18['sl_trung'] - datra_2_18['sl_trung'],
                        'stien_con_lai': phaitra_2_18['st_trung'] - datra_2_18['st_trung'],
                        })
            #'dung bien toan cuc de tim tong cong'
            self.sl_phai_tra_tong += phaitra_2_18['sl_trung']
            self.stien_phai_tra_tong += phaitra_2_18['st_trung']
            self.sl_da_tra_tong += datra_2_18['sl_trung']
            self.stien_da_tra_tong += datra_2_18['st_trung']
            self.sl_con_lai_tong += phaitra_2_18['sl_trung'] - datra_2_18['sl_trung']
            self.stien_con_lai_tong += phaitra_2_18['st_trung'] - datra_2_18['st_trung']
        if not res:
            res.append({
                'so_lan': '',
                'sl_phai_tra': 0,
                'stien_phai_tra': 0,
                'sl_da_tra': 0,
                'stien_da_tra': 0,
                'sl_con_lai': 0,
                'stien_con_lai': 0,
            })
        return res
    
    def get_4_16(self):
        res = []
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        date = wizard_data['date']
        sql = '''
        select slan_trung
        
        from (
            select case when slan_trung!=0 then slan_trung else 1 end slan_trung
                from tra_thuong_line
                
                where loai='4_so' and giai='16_lo' and product_id=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
        ) foo
                group by slan_trung
                order by slan_trung
        '''%(product[0], date)
        self.cr.execute(sql)
        
        for sl in self.cr.dictfetchall():#'so lan trung  ngay mo thuong order by tang dan':
            #'sql sum so tien, so luong phai tra'
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung*slan_trung*tong_tien)!=0 then sum(sl_trung*slan_trung*tong_tien) else 0 end st_trung
                    
                    from tra_thuong_line
                
                where loai='4_so' and giai='16_lo' and product_id=%s and slan_trung=%s and trathuong_id in (select id from tra_thuong where ngay='%s')
            '''%(product[0],sl['slan_trung'], date)
            self.cr.execute(sql)
            phaitra_2_18 = self.cr.dictfetchone()
            #'sql sum so tien, so luong da tra'
            sql = '''
                select case when sum(sl_4_16)!=0 then sum(sl_4_16) else 0 end sl_trung,
                    case when sum(st_4_16)!=0 then sum(st_4_16) else 0 end st_trung
                    
                    from quyet_toan_ve_ngay_line
                
                where slan_4_16=%s and quyettoan_id in (select id from quyet_toan_ve_ngay where ngay_mo_thuong='%s' and product_id=%s)
            '''%(sl['slan_trung'], date, product[0])
            self.cr.execute(sql)
            datra_2_18 = self.cr.dictfetchone()
            res.append({
                        'so_lan':sl['slan_trung'],
                        'sl_phai_tra': phaitra_2_18['sl_trung'],
                        'stien_phai_tra': phaitra_2_18['st_trung'],
                        'sl_da_tra': datra_2_18['sl_trung'],
                        'stien_da_tra': datra_2_18['st_trung'],
                        'sl_con_lai': phaitra_2_18['sl_trung'] - datra_2_18['sl_trung'],
                        'stien_con_lai': phaitra_2_18['st_trung'] - datra_2_18['st_trung'],
                        })
            #'dung bien toan cuc de tim tong cong'
            self.sl_phai_tra_tong += phaitra_2_18['sl_trung']
            self.stien_phai_tra_tong += phaitra_2_18['st_trung']
            self.sl_da_tra_tong += datra_2_18['sl_trung']
            self.stien_da_tra_tong += datra_2_18['st_trung']
            self.sl_con_lai_tong += phaitra_2_18['sl_trung'] - datra_2_18['sl_trung']
            self.stien_con_lai_tong += phaitra_2_18['st_trung'] - datra_2_18['st_trung']
        if not res:
            res.append({
                'so_lan': '',
                'sl_phai_tra': 0,
                'stien_phai_tra': 0,
                'sl_da_tra': 0,
                'stien_da_tra': 0,
                'sl_con_lai': 0,
                'stien_con_lai': 0,
            })
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
    