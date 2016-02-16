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
            'get_date':self.get_date,
            'get_dai_ly':self.get_dai_ly,
            'get_menh_gia':self.get_menh_gia,
            'get_line':self.get_line,
            'get_tong':self.get_tong,
            'get_line_tong':self.get_line_tong,
            'get_line_tong_all':self.get_line_tong_all,
        })
        
    def get_date(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
     
    def get_dai_ly(self):
        res_partner_obj = self.pool.get('res.partner')
        res_partner_ids = res_partner_obj.search(self.cr ,self.uid, [('dai_ly','=',True)],order='ma_daily')
        return res_partner_obj.browse(self.cr, self.uid, res_partner_ids)
     
    def get_menh_gia(self):
        product_product_obj = self.pool.get('product.product')
        product_product_ids = product_product_obj.search(self.cr ,self.uid, [('menh_gia','=',True)])
        return product_product_obj.browse(self.cr, self.uid, product_product_ids)
     
    def get_line(self, dl, menhgia):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        ve_loto_obj = self.pool.get('ve.loto')
        ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done'),('product_id','=',menhgia.id),('daily_id','=',dl.id)])
        tong_sai_kythuat = 0
        sluong_2 = 0
        sluong_3 = 0
        sluong_4 = 0
        tongve = 0
        thanhtien = 0
        for veloto in ve_loto_obj.browse(self.cr, self.uid, ve_loto_ids):
            tong_sai_kythuat += veloto.tong_sai_kythuat
            for lotoline in veloto.ve_loto_2_line:
                sluong_2 += lotoline.sl_2_d + lotoline.sl_2_c + lotoline.sl_2_dc + lotoline.sl_2_18
                sluong_3 += lotoline.sl_3_d + lotoline.sl_3_c + lotoline.sl_3_dc + lotoline.sl_3_7 + lotoline.sl_3_17
                sluong_4 += lotoline.sl_4_16
        tongve = sluong_2 + sluong_3 + sluong_4
        thanhtien = tongve*menhgia.list_price
        return {
                'sl_2': format(sluong_2,','),
                'sl_3': format(sluong_3,','),
                'sl_4': format(sluong_4,','),
                'tong_ve': format(tongve,','),
                'thanhtien': format(thanhtien,','),
                'tong_sai_kythuat': format(tong_sai_kythuat,','),
                }

    def get_tong(self, dl):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        product_product_obj = self.pool.get('product.product')
        ve_loto_obj = self.pool.get('ve.loto')
        product_product_ids = product_product_obj.search(self.cr ,self.uid, [('menh_gia','=',True)])
        sl_2 = 0
        sl_3 = 0
        sl_4 = 0
        tongve = 0
        thanhtien = 0
        tong_sai_kythuat = 0
        for menhgia in product_product_obj.browse(self.cr, self.uid, product_product_ids):
            ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done'),('product_id','=',menhgia.id),('daily_id','=',dl.id)])
            sluong_2 = 0
            sluong_3 = 0
            sluong_4 = 0
            for veloto in ve_loto_obj.browse(self.cr, self.uid, ve_loto_ids):
                tong_sai_kythuat += veloto.tong_sai_kythuat
                for lotoline in veloto.ve_loto_2_line:
                    sluong_2 += lotoline.sl_2_d + lotoline.sl_2_c + lotoline.sl_2_dc + lotoline.sl_2_18
                    sluong_3 += lotoline.sl_3_d + lotoline.sl_3_c + lotoline.sl_3_dc + lotoline.sl_3_7 + lotoline.sl_3_17
                    sluong_4 += lotoline.sl_4_16
            sl_2 += sluong_2
            sl_3 += sluong_3
            sl_4 += sluong_4
            tongve += sluong_2 + sluong_3 + sluong_4
            thanhtien += (sluong_2 + sluong_3 + sluong_4)*menhgia.list_price
        return {
                'sl_2': format(sl_2,','),
                'sl_3': format(sl_3,','),
                'sl_4': format(sl_4,','),
                'tong_ve': format(tongve,','),
                'thanhtien': format(thanhtien,','),
                'tong_sai_kythuat': format(tong_sai_kythuat,','),
                }

    def get_line_tong(self, menhgia):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        ve_loto_obj = self.pool.get('ve.loto')
        ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done'),('product_id','=',menhgia.id)])
        sl_2 = 0
        sl_3 = 0
        sl_4 = 0
        tong_sai_kythuat = 0
        for veloto in ve_loto_obj.browse(self.cr, self.uid, ve_loto_ids):
            tong_sai_kythuat += veloto.tong_sai_kythuat
            for lotoline in veloto.ve_loto_2_line:
                sl_2 += lotoline.sl_2_d + lotoline.sl_2_c + lotoline.sl_2_dc + lotoline.sl_2_18
                sl_3 += lotoline.sl_3_d + lotoline.sl_3_c + lotoline.sl_3_dc + lotoline.sl_3_7 + lotoline.sl_3_17
                sl_4 += lotoline.sl_4_16
        tongve = sl_2 + sl_3 + sl_4
        thanhtien = tongve*menhgia.list_price
        return {
                'sl_2': format(sl_2,','),
                'sl_3': format(sl_2,','),
                'sl_4': format(sl_2,','),
                'tong_ve': format(tongve,','),
                'thanhtien': format(thanhtien,','),
                'tong_sai_kythuat': format(tong_sai_kythuat,','),
                }
        
    def get_line_tong_all(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        product_product_obj = self.pool.get('product.product')
        ve_loto_obj = self.pool.get('ve.loto')
        product_product_ids = product_product_obj.search(self.cr ,self.uid, [('menh_gia','=',True)])
        sl_2 = 0
        sl_3 = 0
        sl_4 = 0
        tongve = 0
        thanhtien = 0
        tong_sai_kythuat = 0
        for menhgia in product_product_obj.browse(self.cr, self.uid, product_product_ids):
            ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done'),('product_id','=',menhgia.id)])
            sluong_2 = 0
            sluong_3 = 0
            sluong_4 = 0
            for veloto in ve_loto_obj.browse(self.cr, self.uid, ve_loto_ids):
                tong_sai_kythuat += veloto.tong_sai_kythuat
                for lotoline in veloto.ve_loto_2_line:
                    sluong_2 += lotoline.sl_2_d + lotoline.sl_2_c + lotoline.sl_2_dc + lotoline.sl_2_18
                    sluong_3 += lotoline.sl_3_d + lotoline.sl_3_c + lotoline.sl_3_dc + lotoline.sl_3_7 + lotoline.sl_3_17
                    sluong_4 += lotoline.sl_4_16
            sl_2 += sluong_2
            sl_3 += sluong_3
            sl_4 += sluong_4
            tongve += sluong_2 + sluong_3 + sluong_4
            thanhtien += (sluong_2 + sluong_3 + sluong_4)*menhgia.list_price
        return {
                'sl_2': format(sl_2,','),
                'sl_3': format(sl_3,','),
                'sl_4': format(sl_4,','),
                'tong_ve': format(tongve,','),
                'thanhtien': format(thanhtien,','),
                'tong_sai_kythuat': format(tong_sai_kythuat,','),
                }
