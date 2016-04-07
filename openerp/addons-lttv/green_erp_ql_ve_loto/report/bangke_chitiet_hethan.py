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
        self.tong_nqt = [{'sl_tong': 0,'st_tong':0}]
        self.localcontext.update({
            'get_vietname_date': self.get_vietname_date,
            'convert': self.convert,
            'get_gt_menhgia': self.get_gt_menhgia,
            'get_so_nqt': self.get_so_nqt,
            'get_name_menhgia': self.get_name_menhgia,
            'get_ddt_name': self.get_ddt_name,
            'convert_amount':self.convert_amount,
            'get_2_dc': self.get_2_dc,
            'get_2_18': self.get_2_18,
            'get_2_d': self.get_2_d,
            'get_2_c': self.get_2_c,
            'get_3_d': self.get_3_d,
            'get_3_c': self.get_3_c,
            'get_3_dc': self.get_3_dc,
            'get_3_7': self.get_3_7,
            'get_3_17': self.get_3_17,
            'get_4_16': self.get_4_16,
            'get_khoitao_tong': self.get_khoitao_tong,
            'get_tong': self.get_tong,
        })
        
    def get_khoitao_tong(self):
        for nqt in self.get_so_nqt():
            self.tong_nqt[0][nqt['date_to']] = 0
        return True
    
    def get_tong(self):
        return self.tong_nqt
        
    def get_ddt_name(self, dai_duthuong_id):
        dai_duthuong = self.pool.get('dai.duthuong').browse(self.cr, self.uid, dai_duthuong_id)
        return dai_duthuong.name
        
    def get_so_nqt(self):
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
    
    def get_2_d(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        product = wizard_data['product_id']
        res = []
        slan_dict = {}
#         sql = '''
#                 select slan_2_d
#                  
#                     from quyet_toan_ve_ngay_line
#                      
#                     where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s)
#                      
#                     group by slan_2_d
#                     order by slan_2_d asc
#             '''%(date,product[0])
#         self.cr.execute(sql)
         #'so lan trung can phai group by so lan lai va order by tang dan'
        for seq,slan in enumerate([{'slan_2_d':1}]):
            slan_dict[int(slan['slan_2_d'])] = seq
            if seq==0:
                res.append({
                    'so':'2 số',
                    'name': 'Đầu',
                    'sl_tong': 0,
                    'slan': int(slan['slan_2_d']),
                    'st_tong': 0, 
                })
            else:
                res.append({
                    'so':'',
                    'name': '',
                    'sl_tong': 0,
                    'slan': slan['slan_2_d'],
                    'st_tong': 0, 
                })
            for nqt in self.get_so_nqt(): #('so ngay quyet toan, co ham roi'):
#                 res[nqt['date_to']] = 0
                res[seq][nqt['date_to']] = 0
                
        for nqt in self.get_so_nqt(): #'so ngay quyet toan, co ham roi'
            sql = '''
                select 1 as slan_2_d,
                        case when sum(sl_2_d)!=0 then sum(sl_2_d) else 0 end sl_2_d,
                        case when sum(st_2_d)!=0 then sum(st_2_d) else 0 end st_2_d
                 
                    from quyet_toan_ve_ngay_line
                     
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s and date_to='%s')
                     
                    group by slan_2_d
            '''%(date,product[0],nqt['date_to'])
            self.cr.execute(sql)
            #sql lay slan, soluong, sotien cua loai 2 so 18 lo group by theo so lan
            for slan_nqt in self.cr.dictfetchall():
                res[slan_dict[slan_nqt['slan_2_d']]][nqt['date_to']] += slan_nqt['sl_2_d']
                res[slan_dict[slan_nqt['slan_2_d']]]['sl_tong'] += slan_nqt['sl_2_d']
                res[slan_dict[slan_nqt['slan_2_d']]]['st_tong'] += slan_nqt['st_2_d']
                
                self.tong_nqt[0][nqt['date_to']] += slan_nqt['sl_2_d']
                self.tong_nqt[0]['sl_tong'] += slan_nqt['sl_2_d']
                self.tong_nqt[0]['st_tong'] += slan_nqt['st_2_d']
        if not res:
            res.append({
                    'so':'2 số',
                    'name': 'Đầu',
                    'sl_tong': '',
                    'slan': '',
                    'st_tong': '', 
                           })
        return res
    
    def get_2_c(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        product = wizard_data['product_id']
        res = []
        slan_dict = {}
#         sql = '''
#                 select slan_2_c
#                  
#                     from quyet_toan_ve_ngay_line
#                      
#                     where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s)
#                      
#                     group by slan_2_c
#                     order by slan_2_c asc
#             '''%(date,product[0])
#         self.cr.execute(sql)
         #'so lan trung can phai group by so lan lai va order by tang dan'
        for seq,slan in enumerate([{'slan_2_c':1}]):
            slan_dict[int(slan['slan_2_c'])] = seq
            if seq==0:
                res.append({
                    'so':'',
                    'name': 'Cuối',
                    'sl_tong': 0,
                    'slan': int(slan['slan_2_c']),
                    'st_tong': 0, 
                })
            else:
                res.append({
                    'so':'',
                    'name': '',
                    'sl_tong': 0,
                    'slan': slan['slan_2_c'],
                    'st_tong': 0, 
                })
            for nqt in self.get_so_nqt(): #('so ngay quyet toan, co ham roi'):
#                 res[nqt['date_to']] = 0
                res[seq][nqt['date_to']] = 0
                
        for nqt in self.get_so_nqt(): #'so ngay quyet toan, co ham roi'
            sql = '''
                select 1 as slan_2_c,
                        case when sum(sl_2_c)!=0 then sum(sl_2_c) else 0 end sl_2_c,
                        case when sum(st_2_c)!=0 then sum(st_2_c) else 0 end st_2_c
                 
                    from quyet_toan_ve_ngay_line
                     
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s and date_to='%s')
                     
                    group by slan_2_c
            '''%(date,product[0],nqt['date_to'])
            self.cr.execute(sql)
            #sql lay slan, soluong, sotien cua loai 2 so 18 lo group by theo so lan
            for slan_nqt in self.cr.dictfetchall():
                res[slan_dict[slan_nqt['slan_2_c']]][nqt['date_to']] += slan_nqt['sl_2_c']
                res[slan_dict[slan_nqt['slan_2_c']]]['sl_tong'] += slan_nqt['sl_2_c']
                res[slan_dict[slan_nqt['slan_2_c']]]['st_tong'] += slan_nqt['st_2_c']
                
                self.tong_nqt[0][nqt['date_to']] += slan_nqt['sl_2_c']
                self.tong_nqt[0]['sl_tong'] += slan_nqt['sl_2_c']
                self.tong_nqt[0]['st_tong'] += slan_nqt['st_2_c']
        if not res:
            res.append({
                    'so':'',
                    'name': 'Cuối',
                    'sl_tong': '',
                    'slan': '',
                    'st_tong': '', 
                           })
        return res
    
    def get_2_dc(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        product = wizard_data['product_id']
        res = []
        slan_dict = {}
        sql = '''
            select slan_2_dc from (
                select case when slan_2_dc!=0 then slan_2_dc else 1 end slan_2_dc 
                 
                    from quyet_toan_ve_ngay_line
                     
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s)
                )foo
                    group by slan_2_dc
                    order by slan_2_dc asc
            '''%(date,product[0])
        self.cr.execute(sql)
         #'so lan trung can phai group by so lan lai va order by tang dan'
        for seq,slan in enumerate(self.cr.dictfetchall()):
            slan_dict[int(slan['slan_2_dc'])] = seq
            if seq==0:
                res.append({
                    'so':'',
                    'name': 'Đ/C',
                    'sl_tong': 0,
                    'slan': int(slan['slan_2_dc']),
                    'st_tong': 0, 
                })
            else:
                res.append({
                    'so':'',
                    'name': '',
                    'sl_tong': 0,
                    'slan': slan['slan_2_dc'],
                    'st_tong': 0, 
                })
            for nqt in self.get_so_nqt(): #('so ngay quyet toan, co ham roi'):
#                 res[nqt['date_to']] = 0
                res[seq][nqt['date_to']] = 0
                
        for nqt in self.get_so_nqt(): #'so ngay quyet toan, co ham roi'
            sql = '''
            select slan_2_dc,case when sum(sl_2_dc)!=0 then sum(sl_2_dc) else 0 end sl_2_dc,
                        case when sum(st_2_dc)!=0 then sum(st_2_dc) else 0 end st_2_dc
            from (
                select case when slan_2_dc!=0 then slan_2_dc else 1 end slan_2_dc,
                        case when sl_2_dc!=0 then sl_2_dc else 0 end sl_2_dc,
                        case when st_2_dc!=0 then st_2_dc else 0 end st_2_dc
                 
                    from quyet_toan_ve_ngay_line
                     
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s and date_to='%s')
            )foo
                    group by slan_2_dc
                    order by slan_2_dc asc
            '''%(date,product[0],nqt['date_to'])
            self.cr.execute(sql)
            #sql lay slan, soluong, sotien cua loai 2 so 18 lo group by theo so lan
            for slan_nqt in self.cr.dictfetchall():
                res[slan_dict[slan_nqt['slan_2_dc']]][nqt['date_to']] += slan_nqt['sl_2_dc']
                res[slan_dict[slan_nqt['slan_2_dc']]]['sl_tong'] += slan_nqt['sl_2_dc']
                res[slan_dict[slan_nqt['slan_2_dc']]]['st_tong'] += slan_nqt['st_2_dc']
                
                self.tong_nqt[0][nqt['date_to']] += slan_nqt['sl_2_dc']
                self.tong_nqt[0]['sl_tong'] += slan_nqt['sl_2_dc']
                self.tong_nqt[0]['st_tong'] += slan_nqt['st_2_dc']
        if not res:
            res.append({
                    'so':'',
                    'name': 'Đ/C',
                    'sl_tong': '',
                    'slan': '',
                    'st_tong': '', 
                           })
        return res
    
    def get_2_18(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        product = wizard_data['product_id']
        res = []
        slan_dict = {}
        sql = '''
            select slan_2_18 from (
                select case when slan_2_18!=0 then slan_2_18 else 1 end slan_2_18  
                 
                    from quyet_toan_ve_ngay_line
                     
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s)
            )foo
                    group by slan_2_18
                    order by slan_2_18 asc
            '''%(date,product[0])
        self.cr.execute(sql)
         #'so lan trung can phai group by so lan lai va order by tang dan'
        for seq,slan in enumerate(self.cr.dictfetchall()):
            slan_dict[int(slan['slan_2_18'])] = seq
            if seq==0:
                res.append({
                    'so':'',
                    'name': '18 Lô',
                    'sl_tong': 0,
                    'slan': int(slan['slan_2_18']),
                    'st_tong': 0, 
                })
            else:
                res.append({
                    'so':'',
                    'name': '',
                    'sl_tong': 0,
                    'slan': slan['slan_2_18'],
                    'st_tong': 0, 
                })
            for nqt in self.get_so_nqt(): #('so ngay quyet toan, co ham roi'):
#                 res[nqt['date_to']] = 0
                res[seq][nqt['date_to']] = 0
                
        for nqt in self.get_so_nqt(): #'so ngay quyet toan, co ham roi'
            sql = '''
            select slan_2_18,case when sum(sl_2_18)!=0 then sum(sl_2_18) else 0 end sl_2_18,
                    case when sum(st_2_18)!=0 then sum(st_2_18) else 0 end st_2_18
            
            from (
                select case when slan_2_18!=0 then slan_2_18 else 1 end slan_2_18,
                        case when sl_2_18!=0 then sl_2_18 else 0 end sl_2_18,
                        case when st_2_18!=0 then st_2_18 else 0 end st_2_18
                 
                    from quyet_toan_ve_ngay_line
                     
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s and date_to='%s')
            )foo
                    group by slan_2_18
                    order by slan_2_18 asc
            '''%(date,product[0],nqt['date_to'])
            self.cr.execute(sql)
            #sql lay slan, soluong, sotien cua loai 2 so 18 lo group by theo so lan
            for slan_nqt in self.cr.dictfetchall():
                res[slan_dict[slan_nqt['slan_2_18']]][nqt['date_to']] += slan_nqt['sl_2_18']
                res[slan_dict[slan_nqt['slan_2_18']]]['sl_tong'] += slan_nqt['sl_2_18']
                res[slan_dict[slan_nqt['slan_2_18']]]['st_tong'] += slan_nqt['st_2_18']
                
                self.tong_nqt[0][nqt['date_to']] += slan_nqt['sl_2_18']
                self.tong_nqt[0]['sl_tong'] += slan_nqt['sl_2_18']
                self.tong_nqt[0]['st_tong'] += slan_nqt['st_2_18']
        if not res:
            res.append({
                    'so':'',
                    'name': '18 Lô',
                    'sl_tong': '',
                    'slan': '',
                    'st_tong': '', 
                           })
        return res
    
    def get_3_d(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        product = wizard_data['product_id']
        res = []
        slan_dict = {}
#         sql = '''
#                 select slan_3_d
#                  
#                     from quyet_toan_ve_ngay_line
#                      
#                     where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s)
#                      
#                     group by slan_3_d
#                     order by slan_3_d asc
#             '''%(date,product[0])
#         self.cr.execute(sql)
         #'so lan trung can phai group by so lan lai va order by tang dan'
        for seq,slan in enumerate([{'slan_3_d':1}]):
            slan_dict[int(slan['slan_3_d'])] = seq
            if seq==0:
                res.append({
                    'so':'3 số',
                    'name': 'Đầu',
                    'sl_tong': 0,
                    'slan': int(slan['slan_3_d']),
                    'st_tong': 0, 
                })
            else:
                res.append({
                    'so':'',
                    'name': '',
                    'sl_tong': 0,
                    'slan': slan['slan_3_d'],
                    'st_tong': 0, 
                })
            for nqt in self.get_so_nqt(): #('so ngay quyet toan, co ham roi'):
#                 res[nqt['date_to']] = 0
                res[seq][nqt['date_to']] = 0
                
        for nqt in self.get_so_nqt(): #'so ngay quyet toan, co ham roi'
            sql = '''
                select 1 as slan_3_d,
                        case when sum(sl_3_d)!=0 then sum(sl_3_d) else 0 end sl_3_d,
                        case when sum(st_3_d)!=0 then sum(st_3_d) else 0 end st_3_d
                 
                    from quyet_toan_ve_ngay_line
                     
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s and date_to='%s')
                     
                    group by slan_3_d
            '''%(date,product[0],nqt['date_to'])
            self.cr.execute(sql)
            #sql lay slan, soluong, sotien cua loai 2 so 18 lo group by theo so lan
            for slan_nqt in self.cr.dictfetchall():
                res[slan_dict[slan_nqt['slan_3_d']]][nqt['date_to']] += slan_nqt['sl_3_d']
                res[slan_dict[slan_nqt['slan_3_d']]]['sl_tong'] += slan_nqt['sl_3_d']
                res[slan_dict[slan_nqt['slan_3_d']]]['st_tong'] += slan_nqt['st_3_d']
                
                self.tong_nqt[0][nqt['date_to']] += slan_nqt['sl_3_d']
                self.tong_nqt[0]['sl_tong'] += slan_nqt['sl_3_d']
                self.tong_nqt[0]['st_tong'] += slan_nqt['st_3_d']
        if not res:
            res.append({
                    'so':'3 số',
                    'name': 'Đầu',
                    'sl_tong': '',
                    'slan': '',
                    'st_tong': '', 
                           })
        return res
    
    def get_3_c(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        product = wizard_data['product_id']
        res = []
        slan_dict = {}
#         sql = '''
#                 select slan_3_c
#                  
#                     from quyet_toan_ve_ngay_line
#                      
#                     where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s)
#                      
#                     group by slan_3_c
#                     order by slan_3_c asc
#             '''%(date,product[0])
#         self.cr.execute(sql)
         #'so lan trung can phai group by so lan lai va order by tang dan'
        for seq,slan in enumerate([{'slan_3_c':1}]):
            slan_dict[int(slan['slan_3_c'])] = seq
            if seq==0:
                res.append({
                    'so':'',
                    'name': 'Cuối',
                    'sl_tong': 0,
                    'slan': int(slan['slan_3_c']),
                    'st_tong': 0, 
                })
            else:
                res.append({
                    'so':'',
                    'name': '',
                    'sl_tong': 0,
                    'slan': slan['slan_3_c'],
                    'st_tong': 0, 
                })
            for nqt in self.get_so_nqt(): #('so ngay quyet toan, co ham roi'):
#                 res[nqt['date_to']] = 0
                res[seq][nqt['date_to']] = 0
                
        for nqt in self.get_so_nqt(): #'so ngay quyet toan, co ham roi'
            sql = '''
                select 1 as slan_3_c,
                        case when sum(sl_3_c)!=0 then sum(sl_3_c) else 0 end sl_3_c,
                        case when sum(st_3_c)!=0 then sum(st_3_c) else 0 end st_3_c
                 
                    from quyet_toan_ve_ngay_line
                     
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s and date_to='%s')
                     
                    group by slan_3_c
            '''%(date,product[0],nqt['date_to'])
            self.cr.execute(sql)
            #sql lay slan, soluong, sotien cua loai 2 so 18 lo group by theo so lan
            for slan_nqt in self.cr.dictfetchall():
                res[slan_dict[slan_nqt['slan_3_c']]][nqt['date_to']] += slan_nqt['sl_3_c']
                res[slan_dict[slan_nqt['slan_3_c']]]['sl_tong'] += slan_nqt['sl_3_c']
                res[slan_dict[slan_nqt['slan_3_c']]]['st_tong'] += slan_nqt['st_3_c']
                
                self.tong_nqt[0][nqt['date_to']] += slan_nqt['sl_3_c']
                self.tong_nqt[0]['sl_tong'] += slan_nqt['sl_3_c']
                self.tong_nqt[0]['st_tong'] += slan_nqt['st_3_c']
        if not res:
            res.append({
                    'so':'',
                    'name': 'Cuối',
                    'sl_tong': '',
                    'slan': '',
                    'st_tong': '', 
                           })
        return res
    
    def get_3_dc(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        product = wizard_data['product_id']
        res = []
        slan_dict = {}
        sql = '''
                select case when slan_3_dc!=0 then slan_3_dc else 1 end slan_3_dc
                from (
                    select case when slan_3_dc!=0 then slan_3_dc else 1 end slan_3_dc
                 
                    from quyet_toan_ve_ngay_line
                     
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s)
                ) foo
                     
                    group by slan_3_dc
                    order by slan_3_dc asc
            '''%(date,product[0])
        self.cr.execute(sql)
         #'so lan trung can phai group by so lan lai va order by tang dan'
        for seq,slan in enumerate(self.cr.dictfetchall()):
            slan_dict[int(slan['slan_3_dc'])] = seq
            if seq==0:
                res.append({
                    'so':'',
                    'name': 'Đ/C',
                    'sl_tong': 0,
                    'slan': int(slan['slan_3_dc']),
                    'st_tong': 0, 
                })
            else:
                res.append({
                    'so':'',
                    'name': '',
                    'sl_tong': 0,
                    'slan': slan['slan_3_dc'],
                    'st_tong': 0, 
                })
            for nqt in self.get_so_nqt(): #('so ngay quyet toan, co ham roi'):
#                 res[nqt['date_to']] = 0
                res[seq][nqt['date_to']] = 0
                
        for nqt in self.get_so_nqt(): #'so ngay quyet toan, co ham roi'
            sql = '''
                select case when slan_3_dc!=0 then slan_3_dc else 1 end slan_3_dc,
                        case when sum(sl_3_dc)!=0 then sum(sl_3_dc) else 0 end sl_3_dc,
                        case when sum(st_3_dc)!=0 then sum(st_3_dc) else 0 end st_3_dc
                from (
                    select case when slan_3_dc!=0 then slan_3_dc else 1 end slan_3_dc,
                        case when sl_3_dc!=0 then sl_3_dc else 0 end sl_3_dc,
                        case when st_3_dc!=0 then st_3_dc else 0 end st_3_dc
                 
                    from quyet_toan_ve_ngay_line
                     
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s and date_to='%s')
                ) foo
                     
                    group by slan_3_dc
                    order by slan_3_dc asc
            '''%(date,product[0],nqt['date_to'])
            self.cr.execute(sql)
            #sql lay slan, soluong, sotien cua loai 2 so 18 lo group by theo so lan
            for slan_nqt in self.cr.dictfetchall():
                res[slan_dict[slan_nqt['slan_3_dc']]][nqt['date_to']] += slan_nqt['sl_3_dc']
                res[slan_dict[slan_nqt['slan_3_dc']]]['sl_tong'] += slan_nqt['sl_3_dc']
                res[slan_dict[slan_nqt['slan_3_dc']]]['st_tong'] += slan_nqt['st_3_dc']
                
                self.tong_nqt[0][nqt['date_to']] += slan_nqt['sl_3_dc']
                self.tong_nqt[0]['sl_tong'] += slan_nqt['sl_3_dc']
                self.tong_nqt[0]['st_tong'] += slan_nqt['st_3_dc']
        if not res:
            res.append({
                    'so':'',
                    'name': 'Đ/C',
                    'sl_tong': '',
                    'slan': '',
                    'st_tong': '', 
                           })
        return res
    
    def get_3_7(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        product = wizard_data['product_id']
        res = []
        slan_dict = {}
        sql = '''
            select case when slan_3_7!=0 then slan_3_7 else 1 end slan_3_7 
                from (
                select case when slan_3_7!=0 then slan_3_7 else 1 end slan_3_7 
                 
                    from quyet_toan_ve_ngay_line
                     
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s)
                ) foo
                     
                    group by slan_3_7
                    order by slan_3_7 asc
            '''%(date,product[0])
        self.cr.execute(sql)
         #'so lan trung can phai group by so lan lai va order by tang dan'
        for seq,slan in enumerate(self.cr.dictfetchall()):
            slan_dict[int(slan['slan_3_7'])] = seq
            if seq==0:
                res.append({
                    'so':'',
                    'name': '7 Lô',
                    'sl_tong': 0,
                    'slan': int(slan['slan_3_7']),
                    'st_tong': 0, 
                })
            else:
                res.append({
                    'so':'',
                    'name': '',
                    'sl_tong': 0,
                    'slan': slan['slan_3_7'],
                    'st_tong': 0, 
                })
            for nqt in self.get_so_nqt(): #('so ngay quyet toan, co ham roi'):
#                 res[nqt['date_to']] = 0
                res[seq][nqt['date_to']] = 0
                
        for nqt in self.get_so_nqt(): #'so ngay quyet toan, co ham roi'
            sql = '''
                select case when slan_3_7!=0 then slan_3_7 else 1 end slan_3_7,
                        case when sum(sl_3_7)!=0 then sum(sl_3_7) else 0 end sl_3_7,
                        case when sum(st_3_7)!=0 then sum(st_3_7) else 0 end st_3_7
                from (
                select case when slan_3_7!=0 then slan_3_7 else 1 end slan_3_7,
                        case when sl_3_7!=0 then sl_3_7 else 0 end sl_3_7,
                        case when st_3_7!=0 then st_3_7 else 0 end st_3_7
                 
                    from quyet_toan_ve_ngay_line
                     
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s and date_to='%s')
                ) foo
                     
                    group by slan_3_7
                    order by slan_3_7 asc
            '''%(date,product[0],nqt['date_to'])
            self.cr.execute(sql)
            #sql lay slan, soluong, sotien cua loai 2 so 18 lo group by theo so lan
            for slan_nqt in self.cr.dictfetchall():
                res[slan_dict[slan_nqt['slan_3_7']]][nqt['date_to']] += slan_nqt['sl_3_7']
                res[slan_dict[slan_nqt['slan_3_7']]]['sl_tong'] += slan_nqt['sl_3_7']
                res[slan_dict[slan_nqt['slan_3_7']]]['st_tong'] += slan_nqt['st_3_7']
                
                self.tong_nqt[0][nqt['date_to']] += slan_nqt['sl_3_7']
                self.tong_nqt[0]['sl_tong'] += slan_nqt['sl_3_7']
                self.tong_nqt[0]['st_tong'] += slan_nqt['st_3_7']
        if not res:
            res.append({
                    'so':'',
                    'name': '7 Lô',
                    'sl_tong': '',
                    'slan': '',
                    'st_tong': '', 
                           })
        return res
    
    def get_3_17(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        product = wizard_data['product_id']
        res = []
        slan_dict = {}
        sql = '''
            select case when slan_3_17!=0 then slan_3_17 else 1 end slan_3_17 
                from (
                select case when slan_3_17!=0 then slan_3_17 else 1 end slan_3_17 
                 
                    from quyet_toan_ve_ngay_line
                     
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s)
                ) foo
                     
                    group by slan_3_17
                    order by slan_3_17 asc
            '''%(date,product[0])
        self.cr.execute(sql)
         #'so lan trung can phai group by so lan lai va order by tang dan'
        for seq,slan in enumerate(self.cr.dictfetchall()):
            slan_dict[int(slan['slan_3_17'])] = seq
            if seq==0:
                res.append({
                    'so':'',
                    'name': '17 Lô',
                    'sl_tong': 0,
                    'slan': int(slan['slan_3_17']),
                    'st_tong': 0, 
                })
            else:
                res.append({
                    'so':'',
                    'name': '',
                    'sl_tong': 0,
                    'slan': slan['slan_3_17'],
                    'st_tong': 0, 
                })
            for nqt in self.get_so_nqt(): #('so ngay quyet toan, co ham roi'):
#                 res[nqt['date_to']] = 0
                res[seq][nqt['date_to']] = 0
                
        for nqt in self.get_so_nqt(): #'so ngay quyet toan, co ham roi'
            sql = '''
                select case when slan_3_17!=0 then slan_3_17 else 1 end slan_3_17,
                        case when sum(sl_3_17)!=0 then sum(sl_3_17) else 0 end sl_3_17,
                        case when sum(st_3_17)!=0 then sum(st_3_17) else 0 end st_3_17
                from (
                select case when slan_3_17!=0 then slan_3_17 else 1 end slan_3_17,
                        case when sl_3_17!=0 then sl_3_17 else 0 end sl_3_17,
                        case when st_3_17!=0 then st_3_17 else 0 end st_3_17
                 
                    from quyet_toan_ve_ngay_line
                     
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s and date_to='%s')
                ) foo
                     
                    group by slan_3_17
                    order by slan_3_17 asc
            '''%(date,product[0],nqt['date_to'])
            self.cr.execute(sql)
            #sql lay slan, soluong, sotien cua loai 2 so 18 lo group by theo so lan
            for slan_nqt in self.cr.dictfetchall():
                res[slan_dict[slan_nqt['slan_3_17']]][nqt['date_to']] += slan_nqt['sl_3_17']
                res[slan_dict[slan_nqt['slan_3_17']]]['sl_tong'] += slan_nqt['sl_3_17']
                res[slan_dict[slan_nqt['slan_3_17']]]['st_tong'] += slan_nqt['st_3_17']
                
                self.tong_nqt[0][nqt['date_to']] += slan_nqt['sl_3_17']
                self.tong_nqt[0]['sl_tong'] += slan_nqt['sl_3_17']
                self.tong_nqt[0]['st_tong'] += slan_nqt['st_3_17']
        if not res:
            res.append({
                    'so':'',
                    'name': '17 Lô',
                    'sl_tong': '',
                    'slan': '',
                    'st_tong': '', 
                           })
        return res
    
    def get_4_16(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        product = wizard_data['product_id']
        res = []
        slan_dict = {}
        sql = '''
            select case when slan_4_16!=0 then slan_4_16 else 1 end slan_4_16 
            from (
                select case when slan_4_16!=0 then slan_4_16 else 1 end slan_4_16 
                 
                    from quyet_toan_ve_ngay_line
                     
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s)
            ) foo
                    group by slan_4_16
                    order by slan_4_16 asc
            '''%(date,product[0])
        self.cr.execute(sql)
         #'so lan trung can phai group by so lan lai va order by tang dan'
        for seq,slan in enumerate(self.cr.dictfetchall()):
            slan_dict[int(slan['slan_4_16'])] = seq
            if seq==0:
                res.append({
                    'so':'4 số',
                    'name': '16 Lô',
                    'sl_tong': 0,
                    'slan': int(slan['slan_4_16']),
                    'st_tong': 0, 
                })
            else:
                res.append({
                    'so':'',
                    'name': '',
                    'sl_tong': 0,
                    'slan': slan['slan_4_16'],
                    'st_tong': 0, 
                })
            for nqt in self.get_so_nqt(): #('so ngay quyet toan, co ham roi'):
#                 res[nqt['date_to']] = 0
                res[seq][nqt['date_to']] = 0
                
        for nqt in self.get_so_nqt(): #'so ngay quyet toan, co ham roi'
            sql = '''
                select case when slan_4_16!=0 then slan_4_16 else 1 end slan_4_16,
                        case when sum(sl_4_16)!=0 then sum(sl_4_16) else 0 end sl_4_16,
                        case when sum(st_4_16)!=0 then sum(st_4_16) else 0 end st_4_16
                from (
                select case when slan_4_16!=0 then slan_4_16 else 1 end slan_4_16,
                        case when sl_4_16=0 then sl_4_16 else 0 end sl_4_16,
                        case when st_4_16!=0 then st_4_16 else 0 end st_4_16
                 
                    from quyet_toan_ve_ngay_line
                     
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where product_id=%s and date_to='%s')
                ) foo
                    group by slan_4_16
                    order by slan_4_16 asc
            '''%(date,product[0],nqt['date_to'])
            self.cr.execute(sql)
            #sql lay slan, soluong, sotien cua loai 2 so 18 lo group by theo so lan
            for slan_nqt in self.cr.dictfetchall():
                res[slan_dict[slan_nqt['slan_4_16']]][nqt['date_to']] += slan_nqt['sl_4_16']
                res[slan_dict[slan_nqt['slan_4_16']]]['sl_tong'] += slan_nqt['sl_4_16']
                res[slan_dict[slan_nqt['slan_4_16']]]['st_tong'] += slan_nqt['st_4_16']
                
                self.tong_nqt[0][nqt['date_to']] += slan_nqt['sl_4_16']
                self.tong_nqt[0]['sl_tong'] += slan_nqt['sl_4_16']
                self.tong_nqt[0]['st_tong'] += slan_nqt['st_4_16']
        if not res:
            res.append({
                    'so':'4 số',
                    'name': '16 Lô',
                    'sl_tong': '',
                    'slan': '',
                    'st_tong': '', 
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
    
    def convert_amount(self, amount):
        if not amount:
            amount = 0.0
        amount = format(amount, ',').split('.')[0]
        return amount.replace(',','.')
    