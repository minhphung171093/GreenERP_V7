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
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_date_from':self.get_date_from,
            'get_date_to':self.get_date_to,
            'get_dai_ly':self.get_dai_ly,
            'get_menh_gia':self.get_menh_gia,
            'get_line':self.get_line,
            'get_tong':self.get_tong,
            'get_line_tong':self.get_line_tong,
            'get_line_tong_all':self.get_line_tong_all,
        })
        
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
     
    def get_dai_ly(self):
        sql = '''
            select id from res_partner where dai_ly = True and parent_id is null order by ma_daily
        '''
        self.cr.execute(sql)
        res_partner_ids = [r[0] for r in self.cr.fetchall()]
        res_partner_obj = self.pool.get('res.partner')
        return res_partner_obj.browse(self.cr, self.uid, res_partner_ids)
     
    def get_menh_gia(self):
        sql = '''
            select id from product_product where menh_gia = True 
        '''
        self.cr.execute(sql)
        product_product_ids = [r[0] for r in self.cr.fetchall()]        
        product_product_obj = self.pool.get('product.product')
        return product_product_obj.browse(self.cr, self.uid, product_product_ids)
    
    def get_line(self, dlcha, menhgia):
        ve_loto_obj = self.pool.get('ve.loto')
        dl_ids = [dlcha.id]
        dlcon_ids = self.pool.get('res.partner').search(self.cr, self.uid, [('parent_id','=',dlcha.id)])
        dl_ids += dlcon_ids
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        dl_ids = str(dl_ids).replace('[','(')
        dl_ids = str(dl_ids).replace(']',')')
#         sql = '''
#             select id from ve_loto where (ngay between '%s' and '%s') and state = 'done' 
#             and product_id = %s and daily_id in %s
#         '''%(date_from,date_to,menhgia.id,dl_ids)
#         self.cr.execute(sql)
#         ve_loto_ids = [r[0] for r in self.cr.fetchall()]
        tong_sai_kythuat = 0
        sluong_2 = 0
        sluong_3 = 0
        sluong_4 = 0
        tongve = 0
        thanhtien = 0
        sql='''
            select case when sum(coalesce(tong_sai_kythuat,0))!=0 then sum(coalesce(tong_sai_kythuat,0)) else 0 end tong
            from ve_loto  
            where (ngay between '%s' and '%s') and state = 'done' and product_id = %s and daily_id in %s
        '''%(date_from,date_to,menhgia.id,dl_ids)
        self.cr.execute(sql)
        tong_sai_kythuat = self.cr.dictfetchone()['tong']
#         tong_sai_kythuat += ve
        sql='''
            select case when sum(coalesce(sl_2_d,0)+coalesce(sl_2_c,0)+coalesce(sl_2_dc,0)+coalesce(sl_2_18,0))!=0 
                        then sum(coalesce(sl_2_d,0)+coalesce(sl_2_c,0)+coalesce(sl_2_dc,0)+coalesce(sl_2_18,0)) else 0 end sluong_2,
                   case when sum(coalesce(sl_3_d,0)+coalesce(sl_3_c,0)+coalesce(sl_3_dc,0)+coalesce(sl_3_7,0)+coalesce(sl_3_17,0))!=0
                        then sum(coalesce(sl_3_d,0)+coalesce(sl_3_c,0)+coalesce(sl_3_dc,0)+coalesce(sl_3_7,0)+coalesce(sl_3_17,0)) else 0 end sluong_3,
                   case when sum(coalesce(sl_4_16,0))!=0
                        then sum(coalesce(sl_4_16,0)) else 0 end sluong_4
            from ve_loto_line  
            where ve_loto_id in (select id from ve_loto where (ngay between '%s' and '%s') and state = 'done'
            and product_id = %s and daily_id in %s)
        '''%(date_from,date_to,menhgia.id,dl_ids)
        self.cr.execute(sql)
        for line in self.cr.dictfetchall():
            sluong_2 = line['sluong_2']
            sluong_3 = line['sluong_3']
            sluong_4 = line['sluong_4']
        tongve = sluong_2 + sluong_3 + sluong_4
        thanhtien = tongve*int(menhgia.list_price)
#         for veloto in ve_loto_obj.browse(self.cr, self.uid, ve_loto_ids):
#             tong_sai_kythuat += veloto.tong_sai_kythuat
#             for lotoline in veloto.ve_loto_2_line:
#                 sluong_2 += lotoline.sl_2_d + lotoline.sl_2_c + lotoline.sl_2_dc + lotoline.sl_2_18
#                 sluong_3 += lotoline.sl_3_d + lotoline.sl_3_c + lotoline.sl_3_dc + lotoline.sl_3_7 + lotoline.sl_3_17
#                 sluong_4 += lotoline.sl_4_16
#         tongve = sluong_2 + sluong_3 + sluong_4
#         thanhtien = tongve*int(menhgia.list_price)
        return {
                'sl_2': format(sluong_2,',').split('.')[0],
                'sl_3': format(sluong_3,',').split('.')[0],
                'sl_4': format(sluong_4,',').split('.')[0],
                'tong_ve': format(tongve,',').split('.')[0],
                'thanhtien': format(thanhtien,',').split('.')[0],
                'tong_sai_kythuat': format(tong_sai_kythuat,',').split('.')[0],
                }
    
    def get_tong(self, dlcha):
        dl_ids = [dlcha.id]
        dlcon_ids = self.pool.get('res.partner').search(self.cr, self.uid, [('parent_id','=',dlcha.id)])
        dl_ids += dlcon_ids
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        product_product_obj = self.pool.get('product.product')
        ve_loto_obj = self.pool.get('ve.loto')
        sql = '''
            select id from product_product where menh_gia = True
        '''
        self.cr.execute(sql)
        menhgia_ids = [r[0] for r in self.cr.fetchall()]
        sl_2 = 0
        sl_3 = 0
        sl_4 = 0
        tongve = 0
        thanhtien = 0
        tong_sai_kythuat = 0
        dl_ids = str(dl_ids).replace('[','(')
        dl_ids = str(dl_ids).replace(']',')')
        for menhgia in product_product_obj.browse(self.cr, self.uid, menhgia_ids):
            sluong_2 = 0
            sluong_3 = 0
            sluong_4 = 0
            sql='''
                select case when sum(coalesce(tong_sai_kythuat,0))!=0 then sum(coalesce(tong_sai_kythuat,0)) else 0 end tong
                from ve_loto  
                where (ngay between '%s' and '%s') and state = 'done' and product_id = %s and daily_id in %s
            '''%(date_from,date_to,menhgia.id,dl_ids)
            self.cr.execute(sql)
            tong_sai_kythuat += self.cr.dictfetchone()['tong']
            sql='''
                select case when sum(coalesce(sl_2_d,0)+coalesce(sl_2_c,0)+coalesce(sl_2_dc,0)+coalesce(sl_2_18,0))!=0 
                            then sum(coalesce(sl_2_d,0)+coalesce(sl_2_c,0)+coalesce(sl_2_dc,0)+coalesce(sl_2_18,0)) else 0 end sluong_2,
                       case when sum(coalesce(sl_3_d,0)+coalesce(sl_3_c,0)+coalesce(sl_3_dc,0)+coalesce(sl_3_7,0)+coalesce(sl_3_17,0))!=0
                            then sum(coalesce(sl_3_d,0)+coalesce(sl_3_c,0)+coalesce(sl_3_dc,0)+coalesce(sl_3_7,0)+coalesce(sl_3_17,0)) else 0 end sluong_3,
                       case when sum(coalesce(sl_4_16,0))!=0
                            then sum(coalesce(sl_4_16,0)) else 0 end sluong_4
                from ve_loto_line  
                where ve_loto_id in (select id from ve_loto where (ngay between '%s' and '%s') and state = 'done'
                and product_id = %s and daily_id in %s)
            '''%(date_from,date_to,menhgia.id,dl_ids)
            self.cr.execute(sql)
            for line in self.cr.dictfetchall():
                sluong_2 = line['sluong_2']
                sluong_3 = line['sluong_3']
                sluong_4 = line['sluong_4']
            sl_2 += sluong_2
            sl_3 += sluong_3
            sl_4 += sluong_4
            tongve += sluong_2 + sluong_3 + sluong_4
            thanhtien += (sluong_2 + sluong_3 + sluong_4)*int(menhgia.list_price)
        return {
                'sl_2': format(sl_2,',').split('.')[0],
                'sl_3': format(sl_3,',').split('.')[0],
                'sl_4': format(sl_4,',').split('.')[0],
                'tong_ve': format(tongve,',').split('.')[0],
                'thanhtien': format(thanhtien,',').split('.')[0],
                'tong_sai_kythuat': format(tong_sai_kythuat,',').split('.')[0],
                }

    def get_line_tong(self, menhgia):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        ve_loto_obj = self.pool.get('ve.loto')
        sluong_2 = 0
        sluong_3 = 0
        sluong_4 = 0
        tongve = 0
        thanhtien = 0
        tong_sai_kythuat = 0
        sql='''
            select case when sum(coalesce(tong_sai_kythuat,0))!=0 then sum(coalesce(tong_sai_kythuat,0)) else 0 end tong
                from ve_loto  
                where (ngay between '%s' and '%s') and state = 'done' and product_id = %s 
        '''%(date_from,date_to,menhgia.id)
        self.cr.execute(sql)
        tong_sai_kythuat = self.cr.dictfetchone()['tong']
        sql='''
            select case when sum(coalesce(sl_2_d,0)+coalesce(sl_2_c,0)+coalesce(sl_2_dc,0)+coalesce(sl_2_18,0))!=0 
                        then sum(coalesce(sl_2_d,0)+coalesce(sl_2_c,0)+coalesce(sl_2_dc,0)+coalesce(sl_2_18,0)) else 0 end sluong_2,
                   case when sum(coalesce(sl_3_d,0)+coalesce(sl_3_c,0)+coalesce(sl_3_dc,0)+coalesce(sl_3_7,0)+coalesce(sl_3_17,0))!=0
                        then sum(coalesce(sl_3_d,0)+coalesce(sl_3_c,0)+coalesce(sl_3_dc,0)+coalesce(sl_3_7,0)+coalesce(sl_3_17,0)) else 0 end sluong_3,
                   case when sum(coalesce(sl_4_16,0))!=0
                        then sum(coalesce(sl_4_16,0)) else 0 end sluong_4
            from ve_loto_line  
            where ve_loto_id in (select id from ve_loto where (ngay between '%s' and '%s') and state = 'done'
            and product_id = %s )
        '''%(date_from,date_to,menhgia.id)
        self.cr.execute(sql)
        for line in self.cr.dictfetchall():
            sluong_2 = line['sluong_2']
            sluong_3 = line['sluong_3']
            sluong_4 = line['sluong_4']
        tongve = sluong_2 + sluong_3 + sluong_4
        thanhtien = tongve*int(menhgia.list_price)
#         for veloto in ve_loto_obj.browse(self.cr, self.uid, ve_loto_ids):
#             tong_sai_kythuat += veloto.tong_sai_kythuat
#             for lotoline in veloto.ve_loto_2_line:
#                 sl_2 += lotoline.sl_2_d + lotoline.sl_2_c + lotoline.sl_2_dc + lotoline.sl_2_18
#                 sl_3 += lotoline.sl_3_d + lotoline.sl_3_c + lotoline.sl_3_dc + lotoline.sl_3_7 + lotoline.sl_3_17
#                 sl_4 += lotoline.sl_4_16
#         tongve = sl_2 + sl_3 + sl_4
#         thanhtien = tongve*int(menhgia.list_price)
        return {
                'sl_2': format(sluong_2,',').split('.')[0],
                'sl_3': format(sluong_3,',').split('.')[0],
                'sl_4': format(sluong_4,',').split('.')[0],
                'tong_ve': format(tongve,',').split('.')[0],
                'thanhtien': format(thanhtien,',').split('.')[0],
                'tong_sai_kythuat': format(tong_sai_kythuat,',').split('.')[0],
                }
        
    def get_line_tong_all(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        product_product_obj = self.pool.get('product.product')
        ve_loto_obj = self.pool.get('ve.loto')
        sql = '''
            select id from product_product where menh_gia = True
        '''
        self.cr.execute(sql)
        menhgia_ids = [r[0] for r in self.cr.fetchall()]
        sl_2 = 0
        sl_3 = 0
        sl_4 = 0
        tongve = 0
        thanhtien = 0
        tong_sai_kythuat = 0
        for menhgia in product_product_obj.browse(self.cr, self.uid, menhgia_ids):
            sluong_2 = 0
            sluong_3 = 0
            sluong_4 = 0
            sql='''
                select case when sum(coalesce(tong_sai_kythuat,0))!=0 then sum(coalesce(tong_sai_kythuat,0)) else 0 end tong
                from ve_loto  
                where (ngay between '%s' and '%s') and state = 'done' and product_id = %s 
            '''%(date_from,date_to,menhgia.id)
            self.cr.execute(sql)
            tong_sai_kythuat += self.cr.dictfetchone()['tong']

            sql='''
                select case when sum(coalesce(sl_2_d,0)+coalesce(sl_2_c,0)+coalesce(sl_2_dc,0)+coalesce(sl_2_18,0))!=0 
                            then sum(coalesce(sl_2_d,0)+coalesce(sl_2_c,0)+coalesce(sl_2_dc,0)+coalesce(sl_2_18,0)) else 0 end sluong_2,
                       case when sum(coalesce(sl_3_d,0)+coalesce(sl_3_c,0)+coalesce(sl_3_dc,0)+coalesce(sl_3_7,0)+coalesce(sl_3_17,0))!=0
                            then sum(coalesce(sl_3_d,0)+coalesce(sl_3_c,0)+coalesce(sl_3_dc,0)+coalesce(sl_3_7,0)+coalesce(sl_3_17,0)) else 0 end sluong_3,
                       case when sum(coalesce(sl_4_16,0))!=0
                            then sum(coalesce(sl_4_16,0)) else 0 end sluong_4
                from ve_loto_line  
                where ve_loto_id in (select id from ve_loto where (ngay between '%s' and '%s') and state = 'done'
                and product_id = %s)
            '''%(date_from,date_to,menhgia.id)
            self.cr.execute(sql)
            for line in self.cr.dictfetchall():
                sluong_2 = line['sluong_2']
                sluong_3 = line['sluong_3']
                sluong_4 = line['sluong_4']
            sl_2 += sluong_2
            sl_3 += sluong_3
            sl_4 += sluong_4
            tongve += sluong_2 + sluong_3 + sluong_4
            thanhtien += (sluong_2 + sluong_3 + sluong_4)*int(menhgia.list_price)
#             for veloto in ve_loto_obj.browse(self.cr, self.uid, ve_loto_ids):
#                 tong_sai_kythuat += veloto.tong_sai_kythuat
#                 for lotoline in veloto.ve_loto_2_line:
#                     sluong_2 += lotoline.sl_2_d + lotoline.sl_2_c + lotoline.sl_2_dc + lotoline.sl_2_18
#                     sluong_3 += lotoline.sl_3_d + lotoline.sl_3_c + lotoline.sl_3_dc + lotoline.sl_3_7 + lotoline.sl_3_17
#                     sluong_4 += lotoline.sl_4_16
#             sl_2 += sluong_2
#             sl_3 += sluong_3
#             sl_4 += sluong_4
#             tongve += sluong_2 + sluong_3 + sluong_4
#             thanhtien += (sluong_2 + sluong_3 + sluong_4)*int(menhgia.list_price)
        return {
                'sl_2': format(sl_2,',').split('.')[0],
                'sl_3': format(sl_3,',').split('.')[0],
                'sl_4': format(sl_4,',').split('.')[0],
                'tong_ve': format(tongve,',').split('.')[0],
                'thanhtien': format(thanhtien,',').split('.')[0],
                'tong_sai_kythuat': format(tong_sai_kythuat,',').split('.')[0],
                }
     