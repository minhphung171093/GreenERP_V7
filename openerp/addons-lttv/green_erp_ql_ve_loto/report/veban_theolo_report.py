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
            'get_date': self.get_date,
            'get_chitiet': self.get_chitiet,
        })
    
    def get_date(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_chitiet(self):
        res = []
        # 2 so
        tong_dt_2_d = 0
        tong_tt_2_d = 0
        tong_dt_2_c = 0
        tong_tt_2_c = 0
        tong_dt_2_dc = 0
        tong_tt_2_dc = 0
        tong_dt_2_18 = 0
        tong_tt_2_18 = 0
        
        tong_dt_2 = 0
        tong_tt_2 = 0
        
        # 3 so
        tong_dt_3_d = 0
        tong_tt_3_d = 0
        tong_dt_3_c = 0
        tong_tt_3_c = 0
        tong_dt_3_dc = 0
        tong_tt_3_dc = 0
        tong_dt_3_7 = 0
        tong_tt_3_7 = 0
        tong_dt_3_17 = 0
        tong_tt_3_17 = 0
        
        tong_dt_3 = 0
        tong_tt_3 = 0
        #4 so
        tong_dt_4_16 = 0
        tong_tt_4_16 = 0
        
        tong_dt_4 = 0
        tong_tt_4 = 0
        
        # tong cong
        tong_dt = 0
        tong_tt = 0
        
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        ve_loto_obj = self.pool.get('ve.loto')
        ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done')])
        for loto in ve_loto_obj.browse(self.cr, self.uid, ve_loto_ids):
            gt_menhgia = loto.product_id.list_price/10000
            menhgia = loto.product_id.list_price
            for line in loto.ve_loto_2_line:
                # 2 so
                tong_dt_2_d += line.sl_2_d*menhgia
                tong_dt_2_c += line.sl_2_c*menhgia
                tong_dt_2_dc += line.sl_2_dc*menhgia
                tong_dt_2_18 += line.sl_2_18*menhgia
                tong_dt_2 += line.sl_2_d*menhgia + line.sl_2_c*menhgia + line.sl_2_dc*menhgia + line.sl_2_18*menhgia
                # 3 so
                tong_dt_3_d += line.sl_3_d*menhgia
                tong_dt_3_c += line.sl_3_c*menhgia
                tong_dt_3_dc += line.sl_3_dc*menhgia
                tong_dt_3_7 += line.sl_3_7*menhgia
                tong_dt_3_17 += line.sl_3_17*menhgia
                tong_dt_3 += line.sl_3_d*menhgia + line.sl_3_c*menhgia + line.sl_3_dc*menhgia + line.sl_3_7*menhgia + line.sl_3_17*menhgia
                #4 so
                tong_dt_4_16 += line.sl_4_16*menhgia
                
                tong_dt_4 += line.sl_4_16*menhgia
                
                tong_dt += line.sl_2_d*menhgia + line.sl_2_c*menhgia + line.sl_2_dc*menhgia + line.sl_2_18*menhgia + line.sl_3_d*menhgia + line.sl_3_c*menhgia + line.sl_3_dc*menhgia + line.sl_3_7*menhgia + line.sl_3_17*menhgia+ line.sl_4_16*menhgia
                
                # 2 so
                if line.sl_2_d_trung:
                    slan_trung = line.sl_2_d_trung
                    sluong_trung = line.sl_2_d
                    thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                    
                    tong_tt_2_d += thanhtien
                    tong_tt += thanhtien
                    tong_tt_2 += thanhtien

                if line.sl_2_c_trung:
                    slan_trung = line.sl_2_c_trung
                    sluong_trung = line.sl_2_c
                    thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                    
                    tong_tt_2_c += thanhtien
                    tong_tt += thanhtien
                    tong_tt_2 += thanhtien
                    
                if line.sl_2_dc_trung:
                    slan_trung = line.sl_2_dc_trung
                    sluong_trung = line.sl_2_dc
                    thanhtien = slan_trung*sluong_trung*(350000*gt_menhgia)
                    
                    tong_tt_2_dc += thanhtien
                    tong_tt += thanhtien
                    tong_tt_2 += thanhtien
                    
                if line.sl_2_18_trung:
                    slan_trung = line.sl_2_18_trung
                    sluong_trung = line.sl_2_18
                    thanhtien = slan_trung*sluong_trung*(39000*gt_menhgia)
                    
                    tong_tt_2_18 += thanhtien
                    tong_tt += thanhtien
                    tong_tt_2 += thanhtien
                    
                # 3 so
                if line.sl_3_d_trung:
                    slan_trung = line.sl_3_d_trung
                    sluong_trung = line.sl_3_d
                    thanhtien = slan_trung*sluong_trung*(5000000*gt_menhgia)
                    
                    tong_tt_3_d += thanhtien
                    tong_tt += thanhtien
                    tong_tt_3 += thanhtien
                    
                if line.sl_3_c_trung:
                    slan_trung = line.sl_3_c_trung
                    sluong_trung = line.sl_3_c
                    thanhtien = slan_trung*sluong_trung*(5000000*gt_menhgia)
                    
                    tong_tt_3_c += thanhtien
                    tong_tt += thanhtien
                    tong_tt_3 += thanhtien
                    
                if line.sl_3_dc_trung:
                    slan_trung = line.sl_3_dc_trung
                    sluong_trung = line.sl_3_dc
                    thanhtien = slan_trung*sluong_trung*(2500000*gt_menhgia)
                    
                    tong_tt_3_dc += thanhtien
                    tong_tt += thanhtien
                    tong_tt_3 += thanhtien
                    
                if line.sl_3_7_trung:
                    slan_trung = line.sl_3_7_trung
                    sluong_trung = line.sl_3_7
                    thanhtien = slan_trung*sluong_trung*(715000*gt_menhgia)
                    
                    tong_tt_3_7 += thanhtien
                    tong_tt += thanhtien
                    tong_tt_3 += thanhtien
                    
                if line.sl_3_17_trung:
                    slan_trung = line.sl_3_17_trung
                    sluong_trung = line.sl_3_17
                    thanhtien = slan_trung*sluong_trung*(295000*gt_menhgia)
                    
                    tong_tt_3_17 += thanhtien
                    tong_tt += thanhtien
                    tong_tt_3 += thanhtien
                
                # 4 so
                if line.sl_4_16_trung:
                    slan_trung = line.sl_4_16_trung
                    sluong_trung = line.sl_4_16
                    thanhtien = slan_trung*sluong_trung*(2000000*gt_menhgia)
                    
                    tong_tt_4_16 += thanhtien
                    tong_tt += thanhtien
                    tong_tt_4 += thanhtien
                    
        res = {
            'tong_dt_2_d': tong_dt_2_d,
            'tong_tt_2_d': tong_tt_2_d,
            'tong_dt_2_c': tong_dt_2_c,
            'tong_tt_2_c': tong_tt_2_c,
            'tong_dt_2_dc': tong_dt_2_dc,
            'tong_tt_2_dc': tong_tt_2_dc,
            'tong_dt_2_18': tong_dt_2_18,
            'tong_tt_2_18': tong_tt_2_18,
            'tong_dt_2': tong_dt_2,
            'tong_tt_2': tong_tt_2,
            'tong_dt_3_d': tong_dt_3_d,
            'tong_tt_3_d': tong_tt_3_d,
            'tong_dt_3_c': tong_dt_3_c,
            'tong_tt_3_c': tong_tt_3_c,
            'tong_dt_3_dc': tong_dt_3_dc,
            'tong_tt_3_dc': tong_tt_3_dc,
            'tong_dt_3_7': tong_dt_3_7,
            'tong_tt_3_7': tong_tt_3_7,
            'tong_dt_3_17': tong_dt_3_17,
            'tong_tt_3_17': tong_tt_3_17,
            'tong_dt_3': tong_dt_3,
            'tong_tt_3': tong_tt_3,
            'tong_dt_4_16': tong_dt_4_16,
            'tong_tt_4_16': tong_tt_4_16,
            'tong_dt_4': tong_dt_4,
            'tong_tt_4': tong_tt_4,
            'tong_dt': tong_dt,
            'tong_tt': tong_tt,
        }
        return res
    
    