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
        self.total_sluong = 0.0
        self.total_slan = 0.0
        self.total_thanhtien = 0.0
        self.localcontext.update({
            'get_date':self.get_date,
            'get_date_to':self.get_date_to,
            'get_menh_gia':self.get_menh_gia,
            'get_daiduthuong':self.get_daiduthuong,
            'get_chitiet':self.get_chitiet,
            'get_tong': self.get_tong,
            'get_daily': self.get_daily,
        })
        
    def get_date(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
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
    
    def get_tong(self):
        rs = [{'tong_sluong_trung': format(self.total_sluong,',').split('.')[0],
               'tong_slan_trung': format(self.total_slan,',').split('.')[0],
               'tong_thanhtien': format(self.total_thanhtien,',').split('.')[0],
               }]
        
        return rs
    
    def get_chitiet(self,dlcha):
        # 2 so
        tong_sl_2 = 0
        tong_sl_2_trung = 0
        tong_tien_2 = 0
        
        # 3 so
        tong_sl_3 = 0
        tong_sl_3_trung = 0
        tong_tien_3 = 0
        #4 so
        tong_sl_4 = 0
        tong_sl_4_trung = 0
        tong_tien_4 = 0
        
        # tong cong
        tong_slan_trung = 0
        tong_sluong_trung = 0
        tong_thanhtien = 0
        
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date']
        date_to = wizard_data['date_to']
        
        dl_ids = [dlcha.id]
        dlcon_ids = self.pool.get('res.partner').search(self.cr, self.uid, [('parent_id','=',dlcha.id)])
        dl_ids += dlcon_ids
        dl_ids = str(dl_ids).replace('[','(')
        dl_ids = str(dl_ids).replace(']',')')
        
        ve_loto_obj = self.pool.get('ve.loto')
        loto_line_obj = self.pool.get('ve.loto.line')
        res = []
        product_product_obj = self.pool.get('product.product')
        product_product_ids = product_product_obj.search(self.cr ,self.uid, [('menh_gia','=',True)])
        for menhgia in product_product_ids:
            product_id = product_product_obj.browse(self.cr, self.uid, menhgia)
            gt_menhgia = int(product_id.list_price or 0)/10000
                
            sql ='''
                select case when sum(case when coalesce(sl_2_d_trung,0)!=0 then coalesce(sl_2_d,0) else 0 end)!=0 then sum(case when coalesce(sl_2_d_trung,0)!=0 then coalesce(sl_2_d,0) else 0 end) else 0 end tong_sl_2_d,
                    case when sum(coalesce(sl_2_d_trung,0))!=0 then sum(coalesce(sl_2_d_trung,0)) else 0 end tong_sl_2_d_trung,
                    case when sum(coalesce(sl_2_d,0)*coalesce(sl_2_d_trung,0)*700000*%(gt_menhgia)s)!=0 then sum(coalesce(sl_2_d,0)*coalesce(sl_2_d_trung,0)*700000*%(gt_menhgia)s) else 0 end tong_tien_2_d,
                    
                    case when sum(case when coalesce(sl_2_c_trung,0)!=0 then coalesce(sl_2_c,0) else 0 end)!=0 then sum(case when coalesce(sl_2_c_trung,0)!=0 then coalesce(sl_2_c,0) else 0 end) else 0 end tong_sl_2_c,
                    case when sum(coalesce(sl_2_c_trung,0))!=0 then sum(coalesce(sl_2_c_trung,0)) else 0 end tong_sl_2_c_trung,
                    case when sum(coalesce(sl_2_c,0)*coalesce(sl_2_c_trung,0)*700000*%(gt_menhgia)s)!=0 then sum(coalesce(sl_2_c,0)*coalesce(sl_2_c_trung,0)*700000*%(gt_menhgia)s) else 0 end tong_tien_2_c,
                    
                    case when sum(case when coalesce(sl_2_dc_trung,0)!=0 then coalesce(sl_2_dc,0) else 0 end)!=0 then sum(case when coalesce(sl_2_dc_trung,0)!=0 then coalesce(sl_2_dc,0) else 0 end) else 0 end tong_sl_2_dc,
                    case when sum(coalesce(sl_2_dc_trung,0))!=0 then sum(coalesce(sl_2_dc_trung,0)) else 0 end tong_sl_2_dc_trung,
                    case when sum(coalesce(sl_2_dc,0)*coalesce(sl_2_dc_trung,0)*350000*%(gt_menhgia)s)!=0 then sum(coalesce(sl_2_dc,0)*coalesce(sl_2_dc_trung,0)*350000*%(gt_menhgia)s) else 0 end tong_tien_2_dc,
                    
                    case when sum(case when coalesce(sl_2_18_trung,0)!=0 then coalesce(sl_2_18,0) else 0 end)!=0 then sum(case when coalesce(sl_2_18_trung,0)!=0 then coalesce(sl_2_18,0) else 0 end) else 0 end tong_sl_2_18,
                    case when sum(coalesce(sl_2_18_trung,0))!=0 then sum(coalesce(sl_2_18_trung,0)) else 0 end tong_sl_2_18_trung,
                    case when sum(coalesce(sl_2_18,0)*coalesce(sl_2_18_trung,0)*39000*%(gt_menhgia)s)!=0 then sum(coalesce(sl_2_18,0)*coalesce(sl_2_18_trung,0)*39000*%(gt_menhgia)s) else 0 end tong_tien_2_18,
                    
                    case when sum(case when coalesce(sl_3_d_trung,0)!=0 then coalesce(sl_3_d,0) else 0 end)!=0 then sum(case when coalesce(sl_3_d_trung,0)!=0 then coalesce(sl_3_d,0) else 0 end) else 0 end tong_sl_3_d,
                    case when sum(coalesce(sl_3_d_trung,0))!=0 then sum(coalesce(sl_3_d_trung,0)) else 0 end tong_sl_3_d_trung,
                    case when sum(coalesce(sl_3_d,0)*coalesce(sl_3_d_trung,0)*5000000*%(gt_menhgia)s)!=0 then sum(coalesce(sl_3_d,0)*coalesce(sl_3_d_trung,0)*5000000*%(gt_menhgia)s) else 0 end tong_tien_3_d,
                    
                    case when sum(case when coalesce(sl_3_c_trung,0)!=0 then coalesce(sl_3_c,0) else 0 end)!=0 then sum(case when coalesce(sl_3_c_trung,0)!=0 then coalesce(sl_3_c,0) else 0 end) else 0 end tong_sl_3_c,
                    case when sum(coalesce(sl_3_c_trung,0))!=0 then sum(coalesce(sl_3_c_trung,0)) else 0 end tong_sl_3_c_trung,
                    case when sum(coalesce(sl_3_c,0)*coalesce(sl_3_c_trung,0)*5000000*%(gt_menhgia)s)!=0 then sum(coalesce(sl_3_c,0)*coalesce(sl_3_c_trung,0)*5000000*%(gt_menhgia)s) else 0 end tong_tien_3_c,
                    
                    case when sum(case when coalesce(sl_3_dc_trung,0)!=0 then coalesce(sl_3_dc,0) else 0 end)!=0 then sum(case when coalesce(sl_3_dc_trung,0)!=0 then coalesce(sl_3_dc,0) else 0 end) else 0 end tong_sl_3_dc,
                    case when sum(coalesce(sl_3_dc_trung,0))!=0 then sum(coalesce(sl_3_dc_trung,0)) else 0 end tong_sl_3_dc_trung,
                    case when sum(coalesce(sl_3_dc,0)*coalesce(sl_3_dc_trung,0)*2500000*%(gt_menhgia)s)!=0 then sum(coalesce(sl_3_dc,0)*coalesce(sl_3_dc_trung,0)*2500000*%(gt_menhgia)s) else 0 end tong_tien_3_dc,
                    
                    case when sum(case when coalesce(sl_3_7_trung,0)!=0 then coalesce(sl_3_7,0) else 0 end)!=0 then sum(case when coalesce(sl_3_7_trung,0)!=0 then coalesce(sl_3_7,0) else 0 end) else 0 end tong_sl_3_7,
                    case when sum(coalesce(sl_3_7_trung,0))!=0 then sum(coalesce(sl_3_7_trung,0)) else 0 end tong_sl_3_7_trung,
                    case when sum(coalesce(sl_3_7,0)*coalesce(sl_3_7_trung,0)*715000*%(gt_menhgia)s)!=0 then sum(coalesce(sl_3_7,0)*coalesce(sl_3_7_trung,0)*715000*%(gt_menhgia)s) else 0 end tong_tien_3_7,
                    
                    case when sum(case when coalesce(sl_3_17_trung,0)!=0 then coalesce(sl_3_17,0) else 0 end)!=0 then sum(case when coalesce(sl_3_17_trung,0)!=0 then coalesce(sl_3_17,0) else 0 end) else 0 end tong_sl_3_17,
                    case when sum(coalesce(sl_3_17_trung,0))!=0 then sum(coalesce(sl_3_17_trung,0)) else 0 end tong_sl_3_17_trung,
                    case when sum(coalesce(sl_3_17,0)*coalesce(sl_3_17_trung,0)*295000*%(gt_menhgia)s)!=0 then sum(coalesce(sl_3_17,0)*coalesce(sl_3_17_trung,0)*295000*%(gt_menhgia)s) else 0 end tong_tien_3_17,
                    
                    case when sum(case when coalesce(sl_4_16_trung,0)!=0 then coalesce(sl_4_16,0) else 0 end)!=0 then sum(case when coalesce(sl_4_16_trung,0)!=0 then coalesce(sl_4_16,0) else 0 end) else 0 end tong_sl_4_16,
                    case when sum(coalesce(sl_4_16_trung,0))!=0 then sum(coalesce(sl_4_16_trung,0)) else 0 end tong_sl_4_16_trung,
                    case when sum(coalesce(sl_4_16,0)*coalesce(sl_4_16_trung,0)*2000000*%(gt_menhgia)s)!=0 then sum(coalesce(sl_4_16,0)*coalesce(sl_4_16_trung,0)*2000000*%(gt_menhgia)s) else 0 end tong_tien_4_16
                    
                from ve_loto_line where ve_loto_id in (select id from ve_loto where ngay between '%(date_from)s' and '%(date_to)s' 
                                and product_id=%(product_id)s and daily_id in %(dl_ids)s and state = 'done')
            '''%{
                 'product_id': menhgia,
                 'date_from': date_from,
                 'date_to': date_to,
                 'dl_ids': dl_ids,
                 'gt_menhgia': gt_menhgia,
                 }
            self.cr.execute(sql)
            kq = self.cr.dictfetchone()
            if kq:
                tong_slan_trung += kq['tong_sl_2_d_trung'] + kq['tong_sl_2_c_trung'] + kq['tong_sl_2_dc_trung'] + kq['tong_sl_2_18_trung'] + kq['tong_sl_3_d_trung'] + kq['tong_sl_3_c_trung'] + kq['tong_sl_3_dc_trung'] + kq['tong_sl_3_7_trung'] + kq['tong_sl_3_17_trung'] + kq['tong_sl_4_16_trung']
                tong_sluong_trung += kq['tong_sl_2_d'] + kq['tong_sl_2_c'] + kq['tong_sl_2_dc'] + kq['tong_sl_2_18'] +\
                        + kq['tong_sl_3_d'] + kq['tong_sl_3_c'] + kq['tong_sl_3_dc'] + kq['tong_sl_3_7'] + kq['tong_sl_3_17'] +\
                        + kq['tong_sl_4_16']
                tong_thanhtien += kq['tong_tien_2_d'] + kq['tong_tien_2_c'] + kq['tong_tien_2_dc'] + kq['tong_tien_2_18'] +\
                        + kq['tong_tien_3_d'] + kq['tong_tien_3_c'] + kq['tong_tien_3_dc'] + kq['tong_tien_3_7'] + kq['tong_tien_3_17'] +\
                        + kq['tong_tien_4_16']
                        
                tong_sl_2 = kq['tong_sl_2_d'] + kq['tong_sl_2_c'] + kq['tong_sl_2_dc'] + kq['tong_sl_2_18']
                tong_sl_2_trung = kq['tong_sl_2_d_trung'] + kq['tong_sl_2_c_trung'] + kq['tong_sl_2_dc_trung'] + kq['tong_sl_2_18_trung']
                tong_tien_2 = kq['tong_tien_2_d'] + kq['tong_tien_2_c'] + kq['tong_tien_2_dc'] + kq['tong_tien_2_18']
                
                tong_sl_3 =  kq['tong_sl_3_d'] + kq['tong_sl_3_c'] + kq['tong_sl_3_dc'] + kq['tong_sl_3_7'] + kq['tong_sl_3_17']
                tong_sl_3_trung = kq['tong_sl_3_d_trung'] + kq['tong_sl_3_c_trung'] + kq['tong_sl_3_dc_trung'] + kq['tong_sl_3_7_trung'] + kq['tong_sl_3_17_trung']
                tong_tien_3 = kq['tong_tien_3_d'] + kq['tong_tien_3_c'] + kq['tong_tien_3_dc'] + kq['tong_tien_3_7'] + kq['tong_tien_3_17']
                
                tong_sl_4 = kq['tong_sl_4_16']
                tong_sl_4_trung = kq['tong_sl_4_16_trung']
                tong_tien_4 = kq['tong_tien_4_16']
                
                self.total_sluong += tong_sluong_trung
                self.total_slan += tong_slan_trung
                self.total_thanhtien += tong_thanhtien
                res.append(({
                    'name': product_id.name_template or '',
                    'tong_sl_2_d': format(kq['tong_sl_2_d'], ',').split('.')[0],
                    'tong_sl_2_d_trung': format(kq['tong_sl_2_d_trung'], ',').split('.')[0],
                    'tong_tien_2_d': format(kq['tong_tien_2_d'], ',').split('.')[0],
                    'tong_sl_2_c': format(kq['tong_sl_2_c'], ',').split('.')[0],
                    'tong_sl_2_c_trung': format(kq['tong_sl_2_c_trung'], ',').split('.')[0],
                    'tong_tien_2_c': format(kq['tong_tien_2_c'], ',').split('.')[0],
                    'tong_sl_2_dc': format(kq['tong_sl_2_dc'], ',').split('.')[0],
                    'tong_sl_2_dc_trung': format(kq['tong_sl_2_dc_trung'], ',').split('.')[0],
                    'tong_tien_2_dc': format(kq['tong_tien_2_dc'], ',').split('.')[0],
                    'tong_sl_2_18': format(kq['tong_sl_2_18'], ',').split('.')[0],
                    'tong_sl_2_18_trung': format(kq['tong_sl_2_18_trung'], ',').split('.')[0],
                    'tong_tien_2_18': format(kq['tong_tien_2_18'], ',').split('.')[0],
                    'tong_sl_2': format(tong_sl_2, ',').split('.')[0],
                    'tong_sl_2_trung': format(tong_sl_2_trung, ',').split('.')[0],
                    'tong_tien_2': format(tong_tien_2, ',').split('.')[0],
                    'tong_sl_3_d': format(kq['tong_sl_3_d'], ',').split('.')[0],
                    'tong_sl_3_d_trung': format(kq['tong_sl_3_d_trung'], ',').split('.')[0],
                    'tong_tien_3_d': format(kq['tong_tien_3_d'], ',').split('.')[0],
                    'tong_sl_3_c': format(kq['tong_sl_3_c'], ',').split('.')[0],
                    'tong_sl_3_c_trung': format(kq['tong_sl_3_c_trung'], ',').split('.')[0],
                    'tong_tien_3_c': format(kq['tong_tien_3_c'], ',').split('.')[0],
                    'tong_sl_3_dc': format(kq['tong_sl_3_dc'], ',').split('.')[0],
                    'tong_sl_3_dc_trung': format(kq['tong_sl_3_dc_trung'], ',').split('.')[0],
                    'tong_tien_3_dc': format(kq['tong_tien_3_dc'], ',').split('.')[0],
                    'tong_sl_3_7': format(kq['tong_sl_3_7'], ',').split('.')[0],
                    'tong_sl_3_7_trung': format(kq['tong_sl_3_7_trung'], ',').split('.')[0],
                    'tong_tien_3_7': format(kq['tong_tien_3_7'], ',').split('.')[0],
                    'tong_sl_3_17': format(kq['tong_sl_3_17'], ',').split('.')[0],
                    'tong_sl_3_17_trung': format(kq['tong_sl_3_17_trung'], ',').split('.')[0],
                    'tong_tien_3_17': format(kq['tong_tien_3_17'], ',').split('.')[0],
                    'tong_sl_3': format(tong_sl_3, ',').split('.')[0],
                    'tong_sl_3_trung': format(tong_sl_3_trung, ',').split('.')[0],
                    'tong_tien_3': format(tong_tien_3, ',').split('.')[0],
                    'tong_sl_4_16': format(kq['tong_sl_4_16'], ',').split('.')[0],
                    'tong_sl_4_16_trung': format(kq['tong_sl_4_16_trung'], ',').split('.')[0],
                    'tong_tien_4_16': format(kq['tong_tien_4_16'], ',').split('.')[0],
                    'tong_sl_4': format(tong_sl_4, ',').split('.')[0],
                    'tong_sl_4_trung': format(tong_sl_4_trung, ',').split('.')[0],
                    'tong_tien_4': format(tong_tien_4, ',').split('.')[0],
                    'tong_slan_trung': format(tong_slan_trung, ',').split('.')[0],
                    'tong_sluong_trung': format(tong_sluong_trung, ',').split('.')[0],
                    'tong_thanhtien': format(tong_thanhtien, ',').split('.')[0],
                }))
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

    
     