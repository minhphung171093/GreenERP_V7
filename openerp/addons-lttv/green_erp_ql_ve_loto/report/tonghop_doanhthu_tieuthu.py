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
        self.data_dict = {}
        self.data_line = {}
        self.data_tong_dict = {}
        self.data_tong = {}
        self.data_tong_product_dict = {}
        self.data_tong_product = {}
        self.data_tong_all_dict = {
            'sl_2': 0,
            'sl_3': 0,
            'sl_4': 0,
            'tong_ve': 0,
            'thanhtien': 0,
            'tong_sai_kythuat': 0,
        }
        self.localcontext.update({
            'get_date':self.get_date,
            'get_dai_ly':self.get_dai_ly,
            'get_menh_gia':self.get_menh_gia,
            'get_line':self.get_line,
            'get_data_line': self.get_data_line,
            'get_tong':self.get_tong,
            'get_data_tong': self.get_data_tong,
            'get_line_tong':self.get_line_tong,
            'get_line_tong_all':self.get_line_tong_all,
            'get_datas': self.get_datas,
            'get_data_line_tong': self.get_data_line_tong,
        })
        
    def get_date(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
     
    def get_dai_ly(self):
        res_partner_ids = self.data_dict.keys()
        res_partner_obj = self.pool.get('res.partner')
        res_partner_ids = res_partner_obj.search(self.cr ,self.uid, [('id','in',res_partner_ids)],order='ma_daily')
        return res_partner_obj.browse(self.cr, self.uid, res_partner_ids)
     
    def get_menh_gia(self):
        product_product_obj = self.pool.get('product.product')
        product_product_ids = product_product_obj.search(self.cr ,self.uid, [('menh_gia','=',True)])
        return product_product_obj.browse(self.cr, self.uid, product_product_ids)
    
    def get_datas(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        sql = '''
            select lt.product_id as product_id, lt.daily_id as daily_id, pt.list_price as list_price, rp.parent_id as daily_cha_id,
                sum(COALESCE(ltl.sl_2_d,0)) as sl_2_d, sum(COALESCE(ltl.sl_2_c,0)) as sl_2_c, sum(COALESCE(ltl.sl_2_dc,0)) as sl_2_dc,
                sum(COALESCE(ltl.sl_2_18,0)) as sl_2_18, sum(COALESCE(ltl.sl_3_d,0)) as sl_3_d, sum(COALESCE(ltl.sl_3_c,0)) as sl_3_c,
                sum(COALESCE(ltl.sl_3_dc,0)) as sl_3_dc, sum(COALESCE(ltl.sl_3_7,0)) as sl_3_7, sum(COALESCE(ltl.sl_3_17,0)) as sl_3_17,
                sum(COALESCE(ltl.sl_4_16,0)) as sl_4_16, sum(COALESCE(lt.tong_sai_kythuat,0)) as tong_sai_kythuat
                
                from ve_loto_line ltl
                left join ve_loto lt on ltl.ve_loto_id=lt.id
                left join product_product pp on lt.product_id=pp.id
                left join product_template pt on pp.product_tmpl_id=pt.id
                left join res_partner rp on lt.daily_id=rp.id
                
                where lt.state='done' and lt.ngay='%s'
                
                group by lt.product_id, lt.daily_id, pt.list_price, rp.parent_id
        '''%(date)
        self.cr.execute(sql)
        for line in self.cr.dictfetchall():
            sluong_2 = line['sl_2_d'] + line['sl_2_c'] + line['sl_2_dc'] + line['sl_2_18']
            sluong_3 = line['sl_3_d'] + line['sl_3_c'] + line['sl_3_dc'] + line['sl_3_7'] + line['sl_3_17']
            sluong_4 = line['sl_4_16']
            tongve = sluong_2 + sluong_3 + sluong_4
            thanhtien = tongve*line['list_price']
            tong_sai_kythuat = line['tong_sai_kythuat']
            if self.data_dict.get(line['daily_cha_id'], False):
                if self.data_dict[line['daily_cha_id']].get(line['product_id'], False):
                    self.data_dict[line['daily_cha_id']][line['product_id']]['sl_2'] += sluong_2
                    self.data_dict[line['daily_cha_id']][line['product_id']]['sl_3'] += sluong_3
                    self.data_dict[line['daily_cha_id']][line['product_id']]['sl_4'] += sluong_4
                    self.data_dict[line['daily_cha_id']][line['product_id']]['tong_ve'] += tongve
                    self.data_dict[line['daily_cha_id']][line['product_id']]['thanhtien'] += thanhtien
                    self.data_dict[line['daily_cha_id']][line['product_id']]['tong_sai_kythuat'] += tong_sai_kythuat
                else:
                    self.data_dict[line['daily_cha_id']][line['product_id']] = {
                            'sl_2': sluong_2,
                            'sl_3': sluong_3,
                            'sl_4': sluong_4,
                            'tong_ve': tongve,
                            'thanhtien': thanhtien,
                            'tong_sai_kythuat': tong_sai_kythuat,
                        }
            else:
                self.data_dict[line['daily_cha_id']] = {
                        line['product_id']: {
                                'sl_2': sluong_2,
                                'sl_3': sluong_3,
                                'sl_4': sluong_4,
                                'tong_ve': tongve,
                                'thanhtien': thanhtien,
                                'tong_sai_kythuat': tong_sai_kythuat,
                            }
                    }
            
            if self.data_tong_product_dict.get(line['product_id'], False):
                self.data_tong_product_dict[line['product_id']]['sl_2'] += sluong_2
                self.data_tong_product_dict[line['product_id']]['sl_3'] += sluong_3
                self.data_tong_product_dict[line['product_id']]['sl_4'] += sluong_4
                self.data_tong_product_dict[line['product_id']]['tong_ve'] += tongve
                self.data_tong_product_dict[line['product_id']]['thanhtien'] += thanhtien
                self.data_tong_product_dict[line['product_id']]['tong_sai_kythuat'] += tong_sai_kythuat
            else:
                self.data_tong_product_dict[line['product_id']] = {
                    'sl_2': sluong_2,
                    'sl_3': sluong_3,
                    'sl_4': sluong_4,
                    'tong_ve': tongve,
                    'thanhtien': thanhtien,
                    'tong_sai_kythuat': tong_sai_kythuat,
                }
                
        return True
    
#     def get_line(self, dlcha, menhgia):
#         dl_ids = [dlcha.id]
#         dlcon_ids = self.pool.get('res.partner').search(self.cr, self.uid, [('parent_id','=',dlcha.id)])
#         dl_ids += dlcon_ids
#         wizard_data = self.localcontext['data']['form']
#         date = wizard_data['date']
#         ve_loto_obj = self.pool.get('ve.loto')
#         ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done'),('product_id','=',menhgia.id),('daily_id','in',dl_ids)])
#         tong_sai_kythuat = 0
#         sluong_2 = 0
#         sluong_3 = 0
#         sluong_4 = 0
#         tongve = 0
#         thanhtien = 0
#         for veloto in ve_loto_obj.browse(self.cr, self.uid, ve_loto_ids):
#             tong_sai_kythuat += veloto.tong_sai_kythuat
#             for lotoline in veloto.ve_loto_2_line:
#                 sluong_2 += lotoline.sl_2_d + lotoline.sl_2_c + lotoline.sl_2_dc + lotoline.sl_2_18
#                 sluong_3 += lotoline.sl_3_d + lotoline.sl_3_c + lotoline.sl_3_dc + lotoline.sl_3_7 + lotoline.sl_3_17
#                 sluong_4 += lotoline.sl_4_16
#         tongve = sluong_2 + sluong_3 + sluong_4
#         thanhtien = tongve*int(menhgia.list_price)
#         return {
#                 'sl_2': format(sluong_2,',').split('.')[0].replace(',','.'),
#                 'sl_3': format(sluong_3,',').split('.')[0].replace(',','.'),
#                 'sl_4': format(sluong_4,',').split('.')[0].replace(',','.'),
#                 'tong_ve': format(tongve,',').split('.')[0].replace(',','.'),
#                 'thanhtien': format(thanhtien,',').split('.')[0].replace(',','.'),
#                 'tong_sai_kythuat': format(tong_sai_kythuat,',').split('.')[0].replace(',','.'),
#                 }

    def get_data_line(self, dlcha, menhgia):
        sluong_2 = 0
        sluong_3 = 0
        sluong_4 = 0
        tongve = 0
        thanhtien = 0
        tong_sai_kythuat = 0
        if self.data_dict.get(dlcha.id, False):
            if self.data_dict[dlcha.id].get(menhgia.id, False):
                res = self.data_dict[dlcha.id][menhgia.id]
                sluong_2 = res['sl_2']
                sluong_3 = res['sl_3']
                sluong_4 = res['sl_4']
                tongve = res['tong_ve']
                thanhtien = res['thanhtien']
                tong_sai_kythuat = res['tong_sai_kythuat']
                if self.data_tong_dict.get(dlcha.id, False):
                    self.data_tong_dict[dlcha.id]['sl_2'] += sluong_2
                    self.data_tong_dict[dlcha.id]['sl_3'] += sluong_3
                    self.data_tong_dict[dlcha.id]['sl_4'] += sluong_4
                    self.data_tong_dict[dlcha.id]['tong_ve'] += tongve
                    self.data_tong_dict[dlcha.id]['thanhtien'] += thanhtien
                    self.data_tong_dict[dlcha.id]['tong_sai_kythuat'] += tong_sai_kythuat
                else:
                    self.data_tong_dict[dlcha.id] = {
                        'sl_2': sluong_2,
                        'sl_3': sluong_3,
                        'sl_4': sluong_4,
                        'tong_ve': tongve,
                        'thanhtien': thanhtien,
                        'tong_sai_kythuat': tong_sai_kythuat,
                    }
        self.data_line = {
            'sl_2': format(sluong_2,',').split('.')[0].replace(',','.'),
            'sl_3': format(sluong_3,',').split('.')[0].replace(',','.'),
            'sl_4': format(sluong_4,',').split('.')[0].replace(',','.'),
            'tong_ve': format(tongve,',').split('.')[0].replace(',','.'),
            'thanhtien': format(thanhtien,',').split('.')[0].replace(',','.'),
            'tong_sai_kythuat': format(tong_sai_kythuat,',').split('.')[0].replace(',','.'),
        }
        return True
    
    def get_line(self, dlcha, menhgia):
        return self.data_line
        
    def get_data_tong(self, dlcha):
        sluong_2 = 0
        sluong_3 = 0
        sluong_4 = 0
        tongve = 0
        thanhtien = 0
        tong_sai_kythuat = 0
        if self.data_dict.get(dlcha.id, False):
            res = self.data_dict[dlcha.id]
            sluong_2 = res['sl_2']
            sluong_3 = res['sl_3']
            sluong_4 = res['sl_4']
            tongve = res['tong_ve']
            thanhtien = res['thanhtien']
            tong_sai_kythuat = res['tong_sai_kythuat']
            if self.data_tong_dict.get(dlcha.id, False):
                self.data_tong_all_dict['sl_2'] += sluong_2
                self.data_tong_all_dict['sl_3'] += sluong_3
                self.data_tong_all_dict['sl_4'] += sluong_4
                self.data_tong_all_dict['tong_ve'] += tongve
                self.data_tong_all_dict['thanhtien'] += thanhtien
                self.data_tong_all_dict['tong_sai_kythuat'] += tong_sai_kythuat
        self.data_tong = {
            'sl_2': format(sluong_2,',').split('.')[0].replace(',','.'),
            'sl_3': format(sluong_3,',').split('.')[0].replace(',','.'),
            'sl_4': format(sluong_4,',').split('.')[0].replace(',','.'),
            'tong_ve': format(tongve,',').split('.')[0].replace(',','.'),
            'thanhtien': format(thanhtien,',').split('.')[0].replace(',','.'),
            'tong_sai_kythuat': format(tong_sai_kythuat,',').split('.')[0].replace(',','.'),
        }
        return True
    
    def get_tong(self, dlcha):
        return self.data_tong
    
#     def get_tong(self, dlcha):
#         dl_ids = [dlcha.id]
#         dlcon_ids = self.pool.get('res.partner').search(self.cr, self.uid, [('parent_id','=',dlcha.id)])
#         dl_ids += dlcon_ids
#         wizard_data = self.localcontext['data']['form']
#         date = wizard_data['date']
#         product_product_obj = self.pool.get('product.product')
#         ve_loto_obj = self.pool.get('ve.loto')
#         product_product_ids = product_product_obj.search(self.cr ,self.uid, [('menh_gia','=',True)])
#         sl_2 = 0
#         sl_3 = 0
#         sl_4 = 0
#         tongve = 0
#         thanhtien = 0
#         tong_sai_kythuat = 0
#         for menhgia in product_product_obj.browse(self.cr, self.uid, product_product_ids):
#             ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done'),('product_id','=',menhgia.id),('daily_id','in',dl_ids)])
#             sluong_2 = 0
#             sluong_3 = 0
#             sluong_4 = 0
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
#         return {
#                 'sl_2': format(sl_2,',').split('.')[0].replace(',','.'),
#                 'sl_3': format(sl_3,',').split('.')[0].replace(',','.'),
#                 'sl_4': format(sl_4,',').split('.')[0].replace(',','.'),
#                 'tong_ve': format(tongve,',').split('.')[0].replace(',','.'),
#                 'thanhtien': format(thanhtien,',').split('.')[0].replace(',','.'),
#                 'tong_sai_kythuat': format(tong_sai_kythuat,',').split('.')[0].replace(',','.'),
#                 }

    def get_data_line_tong(self, menhgia):
        sluong_2 = 0
        sluong_3 = 0
        sluong_4 = 0
        tongve = 0
        thanhtien = 0
        tong_sai_kythuat = 0
        if self.data_tong_product_dict.get(menhgia.id, False):
            res = self.data_tong_product_dict[menhgia.id]
            sluong_2 = res['sl_2']
            sluong_3 = res['sl_3']
            sluong_4 = res['sl_4']
            tongve = res['tong_ve']
            thanhtien = res['thanhtien']
            tong_sai_kythuat = res['tong_sai_kythuat']
        self.data_tong_product = {
            'sl_2': format(sluong_2,',').split('.')[0].replace(',','.'),
            'sl_3': format(sluong_3,',').split('.')[0].replace(',','.'),
            'sl_4': format(sluong_4,',').split('.')[0].replace(',','.'),
            'tong_ve': format(tongve,',').split('.')[0].replace(',','.'),
            'thanhtien': format(thanhtien,',').split('.')[0].replace(',','.'),
            'tong_sai_kythuat': format(tong_sai_kythuat,',').split('.')[0].replace(',','.'),
        }
        return True

    def get_line_tong(self, menhgia):
        return self.data_tong_product

#     def get_line_tong(self, menhgia):
#         wizard_data = self.localcontext['data']['form']
#         date = wizard_data['date']
#         ve_loto_obj = self.pool.get('ve.loto')
#         ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done'),('product_id','=',menhgia.id)])
#         sl_2 = 0
#         sl_3 = 0
#         sl_4 = 0
#         tong_sai_kythuat = 0
#         for veloto in ve_loto_obj.browse(self.cr, self.uid, ve_loto_ids):
#             tong_sai_kythuat += veloto.tong_sai_kythuat
#             for lotoline in veloto.ve_loto_2_line:
#                 sl_2 += lotoline.sl_2_d + lotoline.sl_2_c + lotoline.sl_2_dc + lotoline.sl_2_18
#                 sl_3 += lotoline.sl_3_d + lotoline.sl_3_c + lotoline.sl_3_dc + lotoline.sl_3_7 + lotoline.sl_3_17
#                 sl_4 += lotoline.sl_4_16
#         tongve = sl_2 + sl_3 + sl_4
#         thanhtien = tongve*int(menhgia.list_price)
#         return {
#                 'sl_2': format(sl_2,',').split('.')[0].replace(',','.'),
#                 'sl_3': format(sl_3,',').split('.')[0].replace(',','.'),
#                 'sl_4': format(sl_4,',').split('.')[0].replace(',','.'),
#                 'tong_ve': format(tongve,',').split('.')[0].replace(',','.'),
#                 'thanhtien': format(thanhtien,',').split('.')[0].replace(',','.'),
#                 'tong_sai_kythuat': format(tong_sai_kythuat,',').split('.')[0].replace(',','.'),
#                 }
        
    def get_line_tong_all(self):
        return self.data_tong_all_dict
    
#     def get_line_tong_all(self):
#         wizard_data = self.localcontext['data']['form']
#         date = wizard_data['date']
#         product_product_obj = self.pool.get('product.product')
#         ve_loto_obj = self.pool.get('ve.loto')
#         product_product_ids = product_product_obj.search(self.cr ,self.uid, [('menh_gia','=',True)])
#         sl_2 = 0
#         sl_3 = 0
#         sl_4 = 0
#         tongve = 0
#         thanhtien = 0
#         tong_sai_kythuat = 0
#         for menhgia in product_product_obj.browse(self.cr, self.uid, product_product_ids):
#             ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done'),('product_id','=',menhgia.id)])
#             sluong_2 = 0
#             sluong_3 = 0
#             sluong_4 = 0
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
#         return {
#                 'sl_2': format(sl_2,',').split('.')[0].replace(',','.'),
#                 'sl_3': format(sl_3,',').split('.')[0].replace(',','.'),
#                 'sl_4': format(sl_4,',').split('.')[0].replace(',','.'),
#                 'tong_ve': format(tongve,',').split('.')[0].replace(',','.'),
#                 'thanhtien': format(thanhtien,',').split('.')[0].replace(',','.'),
#                 'tong_sai_kythuat': format(tong_sai_kythuat,',').split('.')[0].replace(',','.'),
#                 }
     