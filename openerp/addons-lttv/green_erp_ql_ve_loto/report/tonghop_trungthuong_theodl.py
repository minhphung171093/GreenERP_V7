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
            'get_menh_gia':self.get_menh_gia,
            'get_daiduthuong':self.get_daiduthuong,
            'get_chitiet':self.get_chitiet,
            'get_tong': self.get_tong,
            'get_daily': self.get_daily,
            'get_tong_dl': self.get_tong_dl,
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
        
    def get_menh_gia(self):
        product_product_obj = self.pool.get('product.product')
        product_product_ids = product_product_obj.search(self.cr ,self.uid, [('menh_gia','=',True)])
        return product_product_obj.browse(self.cr, self.uid, product_product_ids)
    
    def get_daily(self):
        dai_ly_obj = self.pool.get('res.partner')
        dai_ly_ids = dai_ly_obj.search(self.cr ,self.uid, [('dai_ly','=',True),('parent_id','=',False)])
        return dai_ly_obj.browse(self.cr, self.uid, dai_ly_ids)
    
    
    def get_tong_dl(self,dlcha):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        menhgia_obj = self.pool.get('product.product')
        menhgia_ids = menhgia_obj.search(self.cr, self.uid, [('menh_gia','=',True)])
        tong_sl = 0
        tong_sl_trung = 0
        tong_thanhtien = 0
        ve_loto_obj = self.pool.get('ve.loto')
        loto_line_obj = self.pool.get('ve.loto.line')
        dl_ids = [dlcha.id]
        dlcon_ids = self.pool.get('res.partner').search(self.cr, self.uid, [('parent_id','=',dlcha.id)])
        dl_ids += dlcon_ids
        for menhgia in menhgia_obj.browse(self.cr,self.uid,menhgia_ids):
            ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done'),('product_id','=',menhgia.id),('daily_id','in',dl_ids)])
            loto_line_ids = loto_line_obj.search(self.cr, self.uid, [('ve_loto_id','in',ve_loto_ids)])
            gt_menhgia = menhgia.list_price/10000
            for line in loto_line_obj.browse(self.cr, self.uid, loto_line_ids):
                # 2 so
                if line.sl_2_d_trung:
                    slan_trung = line.sl_2_d_trung
                    sluong_trung = line.sl_2_d
                    thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                if line.sl_2_c_trung:
                    slan_trung = line.sl_2_c_trung
                    sluong_trung = line.sl_2_c
                    thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                if line.sl_2_dc_trung:
                    slan_trung = line.sl_2_dc_trung
                    sluong_trung = line.sl_2_dc
                    thanhtien = slan_trung*sluong_trung*(350000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                if line.sl_2_18_trung:
                    slan_trung = line.sl_2_18_trung
                    sluong_trung = line.sl_2_18
                    thanhtien = slan_trung*sluong_trung*(40000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                # 3 so
                if line.sl_3_d_trung:
                    slan_trung = line.sl_3_d_trung
                    sluong_trung = line.sl_3_d
                    thanhtien = slan_trung*sluong_trung*(5000000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                if line.sl_3_c_trung:
                    slan_trung = line.sl_3_c_trung
                    sluong_trung = line.sl_3_c
                    thanhtien = slan_trung*sluong_trung*(5000000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                if line.sl_3_dc_trung:
                    slan_trung = line.sl_3_dc_trung
                    sluong_trung = line.sl_3_dc
                    thanhtien = slan_trung*sluong_trung*(2500000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                if line.sl_3_7_trung:
                    slan_trung = line.sl_3_7_trung
                    sluong_trung = line.sl_3_7
                    thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                if line.sl_3_17_trung:
                    slan_trung = line.sl_3_17_trung
                    sluong_trung = line.sl_3_17
                    thanhtien = slan_trung*sluong_trung*(300000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                # 4 so
                if line.sl_4_16_trung:
                    slan_trung = line.sl_4_16_trung
                    sluong_trung = line.sl_4_16
                    thanhtien = slan_trung*sluong_trung*(2000000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
        res = {
            'tong_sl': format(tong_sl,','),
            'tong_sl_trung': format(tong_sl_trung,','),
            'tong_thanhtien': format(tong_thanhtien,','),
        }
        return res
    
    def get_tong(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        menhgia_obj = self.pool.get('product.product')
        menhgia_ids = menhgia_obj.search(self.cr, self.uid, [('menh_gia','=',True)])
        tong_sl = 0
        tong_sl_trung = 0
        tong_thanhtien = 0
        ve_loto_obj = self.pool.get('ve.loto')
        loto_line_obj = self.pool.get('ve.loto.line')
        for menhgia in menhgia_obj.browse(self.cr,self.uid,menhgia_ids):
            ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done'),('product_id','=',menhgia.id)])
            loto_line_ids = loto_line_obj.search(self.cr, self.uid, [('ve_loto_id','in',ve_loto_ids)])
            gt_menhgia = menhgia.list_price/10000
            for line in loto_line_obj.browse(self.cr, self.uid, loto_line_ids):
                # 2 so
                if line.sl_2_d_trung:
                    slan_trung = line.sl_2_d_trung
                    sluong_trung = line.sl_2_d
                    thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                if line.sl_2_c_trung:
                    slan_trung = line.sl_2_c_trung
                    sluong_trung = line.sl_2_c
                    thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                if line.sl_2_dc_trung:
                    slan_trung = line.sl_2_dc_trung
                    sluong_trung = line.sl_2_dc
                    thanhtien = slan_trung*sluong_trung*(350000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                if line.sl_2_18_trung:
                    slan_trung = line.sl_2_18_trung
                    sluong_trung = line.sl_2_18
                    thanhtien = slan_trung*sluong_trung*(40000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                # 3 so
                if line.sl_3_d_trung:
                    slan_trung = line.sl_3_d_trung
                    sluong_trung = line.sl_3_d
                    thanhtien = slan_trung*sluong_trung*(5000000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                if line.sl_3_c_trung:
                    slan_trung = line.sl_3_c_trung
                    sluong_trung = line.sl_3_c
                    thanhtien = slan_trung*sluong_trung*(5000000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                if line.sl_3_dc_trung:
                    slan_trung = line.sl_3_dc_trung
                    sluong_trung = line.sl_3_dc
                    thanhtien = slan_trung*sluong_trung*(2500000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                if line.sl_3_7_trung:
                    slan_trung = line.sl_3_7_trung
                    sluong_trung = line.sl_3_7
                    thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                if line.sl_3_17_trung:
                    slan_trung = line.sl_3_17_trung
                    sluong_trung = line.sl_3_17
                    thanhtien = slan_trung*sluong_trung*(300000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
                # 4 so
                if line.sl_4_16_trung:
                    slan_trung = line.sl_4_16_trung
                    sluong_trung = line.sl_4_16
                    thanhtien = slan_trung*sluong_trung*(2000000*gt_menhgia)
                    
                    tong_sl += sluong_trung
                    tong_sl_trung += slan_trung
                    tong_thanhtien += thanhtien
        res = {
            'tong_sl': format(tong_sl,','),
            'tong_sl_trung': format(tong_sl_trung,','),
            'tong_thanhtien': format(tong_thanhtien,','),
        }
        return res
    
    def get_chitiet(self,menhgia,dlcha):
        # 2 so
        tong_sl_2_d = 0
        tong_sl_2_d_trung = 0
        tong_tien_2_d = 0
        tong_sl_2_c = 0
        tong_sl_2_c_trung = 0
        tong_tien_2_c = 0
        tong_sl_2_dc = 0
        tong_sl_2_dc_trung = 0
        tong_tien_2_dc = 0
        tong_sl_2_18 = 0
        tong_sl_2_18_trung = 0
        tong_tien_2_18 = 0
        
        tong_sl_2 = 0
        tong_sl_2_trung = 0
        tong_tien_2 = 0
        
        # 3 so
        tong_sl_3_d = 0
        tong_sl_3_d_trung = 0
        tong_tien_3_d = 0
        tong_sl_3_c = 0
        tong_sl_3_c_trung = 0
        tong_tien_3_c = 0
        tong_sl_3_dc = 0
        tong_sl_3_dc_trung = 0
        tong_tien_3_dc = 0
        tong_sl_3_7 = 0
        tong_sl_3_7_trung = 0
        tong_tien_3_7 = 0
        tong_sl_3_17 = 0
        tong_sl_3_17_trung = 0
        tong_tien_3_17 = 0
        
        tong_sl_3 = 0
        tong_sl_3_trung = 0
        tong_tien_3 = 0
        #4 so
        tong_sl_4_16 = 0
        tong_sl_4_16_trung = 0
        tong_tien_4_16 = 0
        
        tong_sl_4 = 0
        tong_sl_4_trung = 0
        tong_tien_4 = 0
        
        # tong cong
        tong_slan_trung = 0
        tong_sluong_trung = 0
        tong_thanhtien = 0
        
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        
        dl_ids = [dlcha.id]
        dlcon_ids = self.pool.get('res.partner').search(self.cr, self.uid, [('parent_id','=',dlcha.id)])
        dl_ids += dlcon_ids
        
        ve_loto_obj = self.pool.get('ve.loto')
        loto_line_obj = self.pool.get('ve.loto.line')
        ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done'),('product_id','=',menhgia.id),('daily_id','in',dl_ids)])
        loto_line_ids = loto_line_obj.search(self.cr, self.uid, [('ve_loto_id','in',ve_loto_ids)])
        gt_menhgia = menhgia.list_price/10000
        for line in loto_line_obj.browse(self.cr, self.uid, loto_line_ids):
            # 2 so
            if line.sl_2_d_trung:
                slan_trung = line.sl_2_d_trung
                sluong_trung = line.sl_2_d
                thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                
                tong_sl_2_d += sluong_trung
                tong_sl_2_d_trung += slan_trung
                tong_tien_2_d += thanhtien
                
                tong_sl_2 += sluong_trung
                tong_sl_2_trung += slan_trung
                tong_tien_2 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_2_c_trung:
                slan_trung = line.sl_2_c_trung
                sluong_trung = line.sl_2_c
                thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                
                tong_sl_2_c += sluong_trung
                tong_sl_2_c_trung += slan_trung
                tong_tien_2_c += thanhtien
                
                tong_sl_2 += sluong_trung
                tong_sl_2_trung += slan_trung
                tong_tien_2 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_2_dc_trung:
                slan_trung = line.sl_2_dc_trung
                sluong_trung = line.sl_2_dc
                thanhtien = slan_trung*sluong_trung*(350000*gt_menhgia)
                
                tong_sl_2_dc += sluong_trung
                tong_sl_2_dc_trung += slan_trung
                tong_tien_2_dc += thanhtien
                
                tong_sl_2 += sluong_trung
                tong_sl_2_trung += slan_trung
                tong_tien_2 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_2_18_trung:
                slan_trung = line.sl_2_18_trung
                sluong_trung = line.sl_2_18
                thanhtien = slan_trung*sluong_trung*(40000*gt_menhgia)
                
                tong_sl_2_18 += sluong_trung
                tong_sl_2_18_trung += slan_trung
                tong_tien_2_18 += thanhtien
                
                tong_sl_2 += sluong_trung
                tong_sl_2_trung += slan_trung
                tong_tien_2 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
            # 3 so
            if line.sl_3_d_trung:
                slan_trung = line.sl_3_d_trung
                sluong_trung = line.sl_3_d
                thanhtien = slan_trung*sluong_trung*(5000000*gt_menhgia)
                
                tong_sl_3_d += sluong_trung
                tong_sl_3_d_trung += slan_trung
                tong_tien_3_d += thanhtien
                
                tong_sl_3 += sluong_trung
                tong_sl_3_trung += slan_trung
                tong_tien_3 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_3_c_trung:
                slan_trung = line.sl_3_c_trung
                sluong_trung = line.sl_3_c
                thanhtien = slan_trung*sluong_trung*(5000000*gt_menhgia)
                
                tong_sl_3_c += sluong_trung
                tong_sl_3_c_trung += slan_trung
                tong_tien_3_c += thanhtien
                
                tong_sl_3 += sluong_trung
                tong_sl_3_trung += slan_trung
                tong_tien_3 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_3_dc_trung:
                slan_trung = line.sl_3_dc_trung
                sluong_trung = line.sl_3_dc
                thanhtien = slan_trung*sluong_trung*(2500000*gt_menhgia)
                
                tong_sl_3_dc += sluong_trung
                tong_sl_3_dc_trung += slan_trung
                tong_tien_3_dc += thanhtien
                
                tong_sl_3 += sluong_trung
                tong_sl_3_trung += slan_trung
                tong_tien_3 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_3_7_trung:
                slan_trung = line.sl_3_7_trung
                sluong_trung = line.sl_3_7
                thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                
                tong_sl_3_7 += sluong_trung
                tong_sl_3_7_trung += slan_trung
                tong_tien_3_7 += thanhtien
                
                tong_sl_3 += sluong_trung
                tong_sl_3_trung += slan_trung
                tong_tien_3 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_3_17_trung:
                slan_trung = line.sl_3_17_trung
                sluong_trung = line.sl_3_17
                thanhtien = slan_trung*sluong_trung*(300000*gt_menhgia)
                
                tong_sl_3_17 += sluong_trung
                tong_sl_3_17_trung += slan_trung
                tong_tien_3_17 += thanhtien
                
                tong_sl_3 += sluong_trung
                tong_sl_3_trung += slan_trung
                tong_tien_3 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
            # 4 so
            if line.sl_4_16_trung:
                slan_trung = line.sl_4_16_trung
                sluong_trung = line.sl_4_16
                thanhtien = slan_trung*sluong_trung*(2000000*gt_menhgia)
                
                tong_sl_4_16 += sluong_trung
                tong_sl_4_16_trung += slan_trung
                tong_tien_4_16 += thanhtien
                
                tong_sl_4 += sluong_trung
                tong_sl_4_trung += slan_trung
                tong_tien_4 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
        res = {
            'tong_sl_2_d': format(tong_sl_2_d, ','),
            'tong_sl_2_d_trung': format(tong_sl_2_d_trung, ','),
            'tong_tien_2_d': format(tong_tien_2_d, ','),
            'tong_sl_2_c': format(tong_sl_2_c, ','),
            'tong_sl_2_c_trung': format(tong_sl_2_c_trung, ','),
            'tong_tien_2_c': format(tong_tien_2_c, ','),
            'tong_sl_2_dc': format(tong_sl_2_dc, ','),
            'tong_sl_2_dc_trung': format(tong_sl_2_dc_trung, ','),
            'tong_tien_2_dc': format(tong_tien_2_dc, ','),
            'tong_sl_2_18': format(tong_sl_2_18, ','),
            'tong_sl_2_18_trung': format(tong_sl_2_18_trung, ','),
            'tong_tien_2_18': format(tong_tien_2_18, ','),
            'tong_sl_2': format(tong_sl_2, ','),
            'tong_sl_2_trung': format(tong_sl_2_trung, ','),
            'tong_tien_2': format(tong_tien_2, ','),
            'tong_sl_3_d': format(tong_sl_3_d, ','),
            'tong_sl_3_d_trung': format(tong_sl_3_d_trung, ','),
            'tong_tien_3_d': format(tong_tien_3_d, ','),
            'tong_sl_3_c': format(tong_sl_3_c, ','),
            'tong_sl_3_c_trung': format(tong_sl_3_c_trung, ','),
            'tong_tien_3_c': format(tong_tien_3_c, ','),
            'tong_sl_3_dc': format(tong_sl_3_dc, ','),
            'tong_sl_3_dc_trung': format(tong_sl_3_dc_trung, ','),
            'tong_tien_3_dc': format(tong_tien_3_dc, ','),
            'tong_sl_3_7': format(tong_sl_3_7, ','),
            'tong_sl_3_7_trung': format(tong_sl_3_7_trung, ','),
            'tong_tien_3_7': format(tong_tien_3_7, ','),
            'tong_sl_3_17': format(tong_sl_3_17, ','),
            'tong_sl_3_17_trung': format(tong_sl_3_17_trung, ','),
            'tong_tien_3_17': format(tong_tien_3_17, ','),
            'tong_sl_3': format(tong_sl_3, ','),
            'tong_sl_3_trung': format(tong_sl_3_trung, ','),
            'tong_tien_3': format(tong_tien_3, ','),
            'tong_sl_4_16': format(tong_sl_4_16, ','),
            'tong_sl_4_16_trung': format(tong_sl_4_16_trung, ','),
            'tong_tien_4_16': format(tong_tien_4_16, ','),
            'tong_sl_4': format(tong_sl_4, ','),
            'tong_sl_4_trung': format(tong_sl_4_trung, ','),
            'tong_tien_4': format(tong_tien_4, ','),
            'tong_slan_trung': format(tong_slan_trung, ','),
            'tong_sluong_trung': format(tong_sluong_trung, ','),
            'tong_thanhtien': format(tong_thanhtien, ','),
        }
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

    
     