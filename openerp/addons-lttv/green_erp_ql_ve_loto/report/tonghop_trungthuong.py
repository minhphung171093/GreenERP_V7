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
            'get_ddphongve_1':self.get_ddphongve_1,
            'get_ddphongve_2':self.get_ddphongve_2,
            'get_ddphong_trathuong_1':self.get_ddphong_trathuong_1,
            'get_ddphong_trathuong_2':self.get_ddphong_trathuong_2,
            'get_cv_ddphongve_1':self.get_cv_ddphongve_1,
            'get_cv_ddphongve_2':self.get_cv_ddphongve_2,
            'get_cv_ddphong_trathuong_1':self.get_cv_ddphong_trathuong_1,
            'get_cv_ddphong_trathuong_2':self.get_cv_ddphong_trathuong_2,
            'get_daiduthuong':self.get_daiduthuong,
            'get_menh_gia':self.get_menh_gia,
            'get_chitiet_2':self.get_chitiet_2,
            'get_chitiet_3':self.get_chitiet_3,
            'get_chitiet_4':self.get_chitiet_4,
            'get_trathuong_2':self.get_trathuong_2,
            'get_trathuong_3':self.get_trathuong_3,
            'get_trathuong_4':self.get_trathuong_4,
            'get_tong_trathuong_2':self.get_tong_trathuong_2,
            'get_tong_trathuong_3':self.get_tong_trathuong_3,
            'get_tong_trathuong_4':self.get_tong_trathuong_4,
        })
        
    def get_date(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_daiduthuong(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        ketqua_obj = self.pool.get('ketqua.xoso')
        ketqua_ids = ketqua_obj.search(self.cr ,self.uid, [('name','=',date),('state','=','validate')])
        if ketqua_ids:
            return ketqua_obj.browse(self.cr, self.uid, ketqua_ids[0]).dai_duthuong_id.name
        else:
            return False
    
    def get_ddphongve_1(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['ddphongve_1']
    
    def get_ddphongve_2(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['ddphongve_2']
    
    def get_ddphong_trathuong_1(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['ddphong_trathuong_1']
    
    def get_ddphong_trathuong_2(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['ddphong_trathuong_2']
    
    def get_cv_ddphongve_1(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['cv_ddphongve_1']
    
    def get_cv_ddphongve_2(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['cv_ddphongve_2']
    
    def get_cv_ddphong_trathuong_1(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['cv_ddphong_trathuong_1']
    
    def get_cv_ddphong_trathuong_2(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['cv_ddphong_trathuong_2']

    def get_menh_gia(self):
        product_product_obj = self.pool.get('product.product')
        product_product_ids = product_product_obj.search(self.cr ,self.uid, [('menh_gia','=',True)])
        return product_product_obj.browse(self.cr, self.uid, product_product_ids)
    
    def get_chitiet_2(self,date,menhgia):
        tong_ve = 0
        tong_thanhtien = 0
        sl_2_d = 0
        sl_2_c = 0
        sl_2_dc = 0
        sl_2_18 = 0
        sl_2_dc_trung = 0
        sl_2_18_trung = 0

        ve_loto_obj = self.pool.get('ve.loto')
        loto_line_obj = self.pool.get('ve.loto.line')
        ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done'),('product_id','=',menhgia.id)])
        loto_line_ids = loto_line_obj.search(self.cr, self.uid, [('ve_loto_id','in',ve_loto_ids)])
        gt_menhgia = menhgia.list_price/10000
        for line in loto_line_obj.browse(self.cr, self.uid, loto_line_ids):
            # 2 so
            if line.sl_2_d_trung:
                slan_trung = line.sl_2_d_trung
                sluong_trung = line.sl_2_d
                thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                
                sl_2_d += sluong_trung
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_2_c_trung:
                slan_trung = line.sl_2_c_trung
                sluong_trung = line.sl_2_c
                thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                
                sl_2_c += sluong_trung
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_2_dc_trung:
                slan_trung = line.sl_2_dc_trung
                sluong_trung = line.sl_2_dc
                thanhtien = slan_trung*sluong_trung*(350000*gt_menhgia)
                
                sl_2_dc += sluong_trung
                sl_2_dc_trung += slan_trung
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_2_18_trung:
                slan_trung = line.sl_2_18_trung
                sluong_trung = line.sl_2_18
                thanhtien = slan_trung*sluong_trung*(39000*gt_menhgia)
                
                sl_2_18 += sluong_trung
                sl_2_18_trung += slan_trung
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
        res = {
            'sl_2_d': sl_2_d,
            'sl_2_c': sl_2_c,
            'sl_2_dc': sl_2_dc,
            'sl_2_18': sl_2_18,
            'sl_2_dc_trung': sl_2_dc_trung,
            'sl_2_18_trung': sl_2_18_trung,
            'tong_ve': tong_ve,
            'tong_thanhtien': tong_thanhtien,
        }
        return res
    
    def get_chitiet_3(self,date,menhgia):
        tong_ve = 0
        tong_thanhtien = 0
        sl_3_d = 0
        sl_3_c = 0
        sl_3_dc = 0
        sl_3_7 = 0
        sl_3_17 = 0
        sl_3_dc_trung = 0
        sl_3_7_trung = 0
        sl_3_17_trung = 0

        ve_loto_obj = self.pool.get('ve.loto')
        loto_line_obj = self.pool.get('ve.loto.line')
        ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done'),('product_id','=',menhgia.id)])
        loto_line_ids = loto_line_obj.search(self.cr, self.uid, [('ve_loto_id','in',ve_loto_ids)])
        gt_menhgia = menhgia.list_price/10000
        for line in loto_line_obj.browse(self.cr, self.uid, loto_line_ids):
            # 3 so
            if line.sl_3_d_trung:
                slan_trung = line.sl_3_d_trung
                sluong_trung = line.sl_3_d
                thanhtien = slan_trung*sluong_trung*(5000000*gt_menhgia)
                
                sl_3_d += sluong_trung
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_3_c_trung:
                slan_trung = line.sl_3_c_trung
                sluong_trung = line.sl_3_c
                thanhtien = slan_trung*sluong_trung*(5000000*gt_menhgia)
                
                sl_3_c += sluong_trung
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_3_dc_trung:
                slan_trung = line.sl_3_dc_trung
                sluong_trung = line.sl_3_dc
                thanhtien = slan_trung*sluong_trung*(2500000*gt_menhgia)
                
                sl_3_dc += sluong_trung
                sl_3_dc_trung += slan_trung
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_3_7_trung:
                slan_trung = line.sl_3_7_trung
                sluong_trung = line.sl_3_7
                thanhtien = slan_trung*sluong_trung*(715000*gt_menhgia)
                
                sl_3_7 += sluong_trung
                sl_3_7_trung += slan_trung
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_3_17_trung:
                slan_trung = line.sl_3_17_trung
                sluong_trung = line.sl_3_17
                thanhtien = slan_trung*sluong_trung*(295000*gt_menhgia)
                
                sl_3_17 += sluong_trung
                sl_3_17_trung += slan_trung
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
        res = {
            'sl_3_d': sl_3_d,
            'sl_3_c': sl_3_c,
            'sl_3_dc': sl_3_dc,
            'sl_3_7': sl_3_7,
            'sl_3_17': sl_3_17,
            'sl_3_dc_trung': sl_3_dc_trung,
            'sl_3_7_trung': sl_3_7_trung,
            'sl_3_17_trung': sl_3_17_trung,
            'tong_ve': tong_ve,
            'tong_thanhtien': tong_thanhtien,
        }
        return res
    
    def get_chitiet_4(self,date,menhgia):
        tong_ve = 0
        tong_thanhtien = 0
        sl_4_16 = 0
        sl_4_16_trung = 0

        ve_loto_obj = self.pool.get('ve.loto')
        loto_line_obj = self.pool.get('ve.loto.line')
        ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done'),('product_id','=',menhgia.id)])
        loto_line_ids = loto_line_obj.search(self.cr, self.uid, [('ve_loto_id','in',ve_loto_ids)])
        gt_menhgia = menhgia.list_price/10000
        for line in loto_line_obj.browse(self.cr, self.uid, loto_line_ids):
            # 4 so
            if line.sl_4_16_trung:
                slan_trung = line.sl_4_16_trung
                sluong_trung = line.sl_4_16
                thanhtien = slan_trung*sluong_trung*(2000000*gt_menhgia)
                
                sl_4_16 += sluong_trung
                sl_4_16_trung += slan_trung
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
        res = {
            'sl_4_16': sl_4_16,
            'sl_4_16_trung': sl_4_16_trung,
            'tong_ve': tong_ve,
            'tong_thanhtien': tong_thanhtien,
        }
        return res
    
    def get_trathuong_2(self, menhgia):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        line = self.get_chitiet_2(date,menhgia)
        res = {
        'sl_2_d': line['sl_2_d'],
        'sl_2_c': line['sl_2_c'],
        'sl_2_dc': line['sl_2_dc'],
        'sl_2_18': line['sl_2_18'],
        'sl_2_dc_trung': line['sl_2_dc_trung'],
        'sl_2_18_trung': line['sl_2_18_trung'],
        'tong_ve': format(line['tong_ve'],','),
        'tong_thanhtien': format(line['tong_thanhtien'],','),
        }
        return res
    
    def get_trathuong_3(self, menhgia):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        line = self.get_chitiet_3(date,menhgia)
        res = {
        'sl_3_d': line['sl_3_d'],
        'sl_3_c': line['sl_3_c'],
        'sl_3_dc': line['sl_3_dc'],
        'sl_3_7': line['sl_3_7'],
        'sl_3_17': line['sl_3_17'],
        'sl_3_dc_trung': line['sl_3_dc_trung'],
        'sl_3_7_trung': line['sl_3_7_trung'],
        'sl_3_17_trung': line['sl_3_17_trung'],
        'tong_ve': format(line['tong_ve'],','),
        'tong_thanhtien': format(line['tong_thanhtien'],','),
        }
        return res
    
    def get_trathuong_4(self, menhgia):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        line = self.get_chitiet_4(date,menhgia)
        res = {
        'sl_4_16': line['sl_4_16'],
        'sl_4_16_trung': line['sl_4_16_trung'],
        'tong_ve': format(line['tong_ve'],','),
        'tong_thanhtien': format(line['tong_thanhtien'],','),
        }
        return res
    
    def get_tong_trathuong_2(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        menhgia_obj = self.pool.get('product.product')
        menhgia_ids = menhgia_obj.search(self.cr, self.uid, [('menh_gia','=',True)])
        sl_2_d = 0
        sl_2_c = 0
        sl_2_dc = 0
        sl_2_18 = 0
        sl_2_dc_trung = 0
        sl_2_18_trung = 0
        tongve = 0
        tongcong = 0
        for menhgia in menhgia_obj.browse(self.cr,self.uid,menhgia_ids):
            tongso = self.get_chitiet_2(date,menhgia)
            tongve += tongso['tong_ve']
            tongcong += tongso['tong_thanhtien']
            sl_2_d += tongso['sl_2_d']
            sl_2_c += tongso['sl_2_c']
            sl_2_dc += tongso['sl_2_dc']
            sl_2_18 += tongso['sl_2_18']
            sl_2_dc_trung += tongso['sl_2_dc_trung']
            sl_2_18_trung += tongso['sl_2_18_trung']
        return {
                'sl_2_d': sl_2_d,
                'sl_2_c': sl_2_c,
                'sl_2_dc': sl_2_dc,
                'sl_2_18': sl_2_18,
                'sl_2_dc_trung': sl_2_dc_trung,
                'sl_2_18_trung': sl_2_18_trung,
                'tongve': format(tongve, ','),
                'tongcong': format(tongcong, ','),
                }
        
    def get_tong_trathuong_3(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        menhgia_obj = self.pool.get('product.product')
        menhgia_ids = menhgia_obj.search(self.cr, self.uid, [('menh_gia','=',True)])
        sl_3_d = 0
        sl_3_c = 0
        sl_3_dc = 0
        sl_3_7 = 0
        sl_3_17 = 0
        sl_3_dc_trung = 0
        sl_3_7_trung = 0
        sl_3_17_trung = 0
        tongve = 0
        tongcong = 0
        for menhgia in menhgia_obj.browse(self.cr,self.uid,menhgia_ids):
            tongso = self.get_chitiet_3(date,menhgia)
            tongve += tongso['tong_ve']
            tongcong += tongso['tong_thanhtien']
            sl_3_d += tongso['sl_3_d']
            sl_3_c += tongso['sl_3_c']
            sl_3_dc += tongso['sl_3_dc']
            sl_3_7 += tongso['sl_3_7']
            sl_3_17 += tongso['sl_3_17']
            sl_3_dc_trung += tongso['sl_3_dc_trung']
            sl_3_7_trung += tongso['sl_3_7_trung']
            sl_3_17_trung += tongso['sl_3_17_trung']
        return {
                'sl_3_d': sl_3_d,
                'sl_3_c': sl_3_c,
                'sl_3_dc': sl_3_dc,
                'sl_3_7': sl_3_7,
                'sl_3_17': sl_3_17,
                'sl_3_dc_trung': sl_3_dc_trung,
                'sl_3_7_trung': sl_3_7_trung,
                'sl_3_17_trung': sl_3_17_trung,
                'tongve': format(tongve, ','),
                'tongcong': format(tongcong, ','),
                }
        
    def get_tong_trathuong_4(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        menhgia_obj = self.pool.get('product.product')
        menhgia_ids = menhgia_obj.search(self.cr, self.uid, [('menh_gia','=',True)])
        sl_4_16 = 0
        sl_4_16_trung = 0
        tongve = 0
        tongcong = 0
        for menhgia in menhgia_obj.browse(self.cr,self.uid,menhgia_ids):
            tongso = self.get_chitiet_4(date,menhgia)
            tongve += tongso['tong_ve']
            tongcong += tongso['tong_thanhtien']
            sl_4_16 += tongso['sl_4_16']
            sl_4_16_trung += tongso['sl_4_16_trung']
        return {
                'sl_4_16': sl_4_16,
                'sl_4_16_trung': sl_4_16_trung,
                'tongve': format(tongve, ','),
                'tongcong': format(tongcong, ','),
                }
    
     