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
            'get_dai_ly_cha':self.get_dai_ly_cha,
            'get_menh_gia':self.get_menh_gia,
            'get_daiduthuong':self.get_daiduthuong,
            'get_chitiet':self.get_chitiet,
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
    
    def get_dai_ly_cha(self):
        wizard_data = self.localcontext['data']['form']
        dai_ly_ids = wizard_data['dai_ly_ids']
        return self.pool.get('res.partner').browse(self.cr, self.uid, dai_ly_ids)
    
    def get_menh_gia(self):
        wizard_data = self.localcontext['data']['form']
        menh_gia_ids = wizard_data['menh_gia_ids']
        return self.pool.get('product.product').browse(self.cr, self.uid, menh_gia_ids)
    
    def get_chitiet(self,dlcha,menhgia):
        res = {
            'line': [],
            'tong': {},
        }
        # 2 so
        tong_sl_2_d = 0
        tong_tien_2_d = 0
        tong_sl_2_c = 0
        tong_tien_2_c = 0
        tong_sl_2_dc = 0
        tong_tien_2_dc = 0
        tong_sl_2_18 = 0
        tong_tien_2_18 = 0
        
        tong_sl_2 = 0
        tong_tien_2 = 0
        
        # 3 so
        tong_sl_3_d = 0
        tong_tien_3_d = 0
        tong_sl_3_c = 0
        tong_tien_3_c = 0
        tong_sl_3_dc = 0
        tong_tien_3_dc = 0
        tong_sl_3_7 = 0
        tong_tien_3_7 = 0
        tong_sl_3_17 = 0
        tong_tien_3_17 = 0
        
        tong_sl_3 = 0
        tong_tien_3 = 0
        #4 so
        tong_sl_4_16 = 0
        tong_tien_4_16 = 0
        
        tong_sl_4 = 0
        tong_tien_4 = 0
        
        # tong cong
        tong_slan_trung = 0
        tong_sluong_trung = 0
        tong_thanhtien = 0
        
        dl_ids = [dlcha.id]
        dlcon_ids = self.pool.get('res.partner').search(self.cr, self.uid, [('parent_id','=',dlcha.id)])
        dl_ids += dlcon_ids
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        ve_loto_obj = self.pool.get('ve.loto')
        loto_line_obj = self.pool.get('ve.loto.line')
        daily_dk = ''
        if dl_ids:
            dls = dl_ids
            dls = str(dls).replace('[', '(')
            dls = str(dls).replace(']', ')')
            daily_dk = '''
                and daily_id in %s
            '''%(dls)
        sql = '''
            select ltl.id as id
                from ve_loto_line ltl
                left join ve_loto lt on ltl.ve_loto_id=lt.id
                
                where lt.ngay='%s' and lt.state='done' and lt.product_id=%s %s
                    and (ltl.sl_2_d_trung!=0 or ltl.sl_2_c_trung!=0 or ltl.sl_2_dc_trung!=0 or ltl.sl_2_18_trung!=0
                         or ltl.sl_3_d_trung!=0 or ltl.sl_3_c_trung!=0 or ltl.sl_3_dc_trung!=0 or ltl.sl_3_7_trung!=0 or ltl.sl_3_17_trung!=0
                         or ltl.sl_4_16_trung!=0)
        '''%(date, menhgia.id,daily_dk)
        self.cr.execute(sql)
        loto_line_ids = [r[0] for r in self.cr.fetchall()]
#         ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done'),('product_id','=',menhgia.id),('daily_id','in',dl_ids)])
#         loto_line_ids = loto_line_obj.search(self.cr, self.uid, [('ve_loto_id','in',ve_loto_ids)])
        gt_menhgia = int(menhgia.list_price)/10000
        for line in loto_line_obj.browse(self.cr, self.uid, loto_line_ids):
            # 2 so
            if line.sl_2_d_trung:
                slan_trung = line.sl_2_d_trung
                sluong_trung = line.sl_2_d
                thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                
                tong_sl_2_d += slan_trung*sluong_trung
                tong_tien_2_d += thanhtien
                
                tong_sl_2 += slan_trung*sluong_trung
                tong_tien_2 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
                
                res['line'].append({
                    'so_dt_2_d': line.so_dt_2_d,
                    'so_dt_2_c': '',
                    'so_dt_2_dc': '',
                    'so_dt_2_18': '',
                    'so_dt_3_d': '',
                    'so_dt_3_c': '',
                    'so_dt_3_dc': '',
                    'so_dt_3_7': '',
                    'so_dt_3_17': '',
                    'so_dt_4_16': '',
                    'slan_trung': slan_trung,
                    'sluong_trung': sluong_trung,
                    'so_phieu': line.ve_loto_id.sophieu,
                    'dai_ly': line.ve_loto_id.daily_id.name,
                    'thanhtien': format(thanhtien, ',').split('.')[0].replace(',','.'),
                    })
            if line.sl_2_c_trung:
                slan_trung = line.sl_2_c_trung
                sluong_trung = line.sl_2_c
                thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                
                tong_sl_2_c += slan_trung*sluong_trung
                tong_tien_2_c += thanhtien
                
                tong_sl_2 += slan_trung*sluong_trung
                tong_tien_2 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
                
                res['line'].append({
                    'so_dt_2_d': '',
                    'so_dt_2_c': line.so_dt_2_c,
                    'so_dt_2_dc': '',
                    'so_dt_2_18': '',
                    'so_dt_3_d': '',
                    'so_dt_3_c': '',
                    'so_dt_3_dc': '',
                    'so_dt_3_7': '',
                    'so_dt_3_17': '',
                    'so_dt_4_16': '',
                    'slan_trung': slan_trung,
                    'sluong_trung': sluong_trung,
                    'so_phieu': line.ve_loto_id.sophieu,
                    'dai_ly': line.ve_loto_id.daily_id.name,
                    'thanhtien': format(thanhtien, ',').split('.')[0].replace(',','.'),
                    })
            if line.sl_2_dc_trung:
                slan_trung = line.sl_2_dc_trung
                sluong_trung = line.sl_2_dc
                thanhtien = slan_trung*sluong_trung*(350000*gt_menhgia)
                
                tong_sl_2_dc += slan_trung*sluong_trung
                tong_tien_2_dc += thanhtien
                
                tong_sl_2 += slan_trung*sluong_trung
                tong_tien_2 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
                
                res['line'].append({
                    'so_dt_2_d': '',
                    'so_dt_2_c': '',
                    'so_dt_2_dc': line.so_dt_2_dc,
                    'so_dt_2_18': '',
                    'so_dt_3_d': '',
                    'so_dt_3_c': '',
                    'so_dt_3_dc': '',
                    'so_dt_3_7': '',
                    'so_dt_3_17': '',
                    'so_dt_4_16': '',
                    'slan_trung': slan_trung,
                    'sluong_trung': sluong_trung,
                    'so_phieu': line.ve_loto_id.sophieu,
                    'dai_ly': line.ve_loto_id.daily_id.name,
                    'thanhtien': format(thanhtien, ',').split('.')[0].replace(',','.'),
                    })
            if line.sl_2_18_trung:
                slan_trung = line.sl_2_18_trung
                sluong_trung = line.sl_2_18
                thanhtien = slan_trung*sluong_trung*(39000*gt_menhgia)
                
                tong_sl_2_18 += slan_trung*sluong_trung
                tong_tien_2_18 += thanhtien
                
                tong_sl_2 += slan_trung*sluong_trung
                tong_tien_2 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
                
                res['line'].append({
                    'so_dt_2_d': '',
                    'so_dt_2_c': '',
                    'so_dt_2_dc': '',
                    'so_dt_2_18': line.so_dt_2_18,
                    'so_dt_3_d': '',
                    'so_dt_3_c': '',
                    'so_dt_3_dc': '',
                    'so_dt_3_7': '',
                    'so_dt_3_17': '',
                    'so_dt_4_16': '',
                    'slan_trung': slan_trung,
                    'sluong_trung': sluong_trung,
                    'so_phieu': line.ve_loto_id.sophieu,
                    'dai_ly': line.ve_loto_id.daily_id.name,
                    'thanhtien': format(thanhtien, ',').split('.')[0].replace(',','.'),
                    })
            # 3 so
            if line.sl_3_d_trung:
                slan_trung = line.sl_3_d_trung
                sluong_trung = line.sl_3_d
                thanhtien = slan_trung*sluong_trung*(5000000*gt_menhgia)
                
                tong_sl_3_d += slan_trung*sluong_trung
                tong_tien_3_d += thanhtien
                
                tong_sl_3 += slan_trung*sluong_trung
                tong_tien_3 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
                
                res['line'].append({
                    'so_dt_2_d': '',
                    'so_dt_2_c': '',
                    'so_dt_2_dc': '',
                    'so_dt_2_18': '',
                    'so_dt_3_d': line.so_dt_3_d,
                    'so_dt_3_c': '',
                    'so_dt_3_dc': '',
                    'so_dt_3_7': '',
                    'so_dt_3_17': '',
                    'so_dt_4_16': '',
                    'slan_trung': slan_trung,
                    'sluong_trung': sluong_trung,
                    'so_phieu': line.ve_loto_id.sophieu,
                    'dai_ly': line.ve_loto_id.daily_id.name,
                    'thanhtien': format(thanhtien, ',').split('.')[0].replace(',','.'),
                    })
            if line.sl_3_c_trung:
                slan_trung = line.sl_3_c_trung
                sluong_trung = line.sl_3_c
                thanhtien = slan_trung*sluong_trung*(5000000*gt_menhgia)
                
                tong_sl_3_c += slan_trung*sluong_trung
                tong_tien_3_c += thanhtien
                
                tong_sl_3 += slan_trung*sluong_trung
                tong_tien_3 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
                
                res['line'].append({
                    'so_dt_2_d': '',
                    'so_dt_2_c': '',
                    'so_dt_2_dc': '',
                    'so_dt_2_18': '',
                    'so_dt_3_d': '',
                    'so_dt_3_c': line.so_dt_3_c,
                    'so_dt_3_dc': '',
                    'so_dt_3_7': '',
                    'so_dt_3_17': '',
                    'so_dt_4_16': '',
                    'slan_trung': slan_trung,
                    'sluong_trung': sluong_trung,
                    'so_phieu': line.ve_loto_id.sophieu,
                    'dai_ly': line.ve_loto_id.daily_id.name,
                    'thanhtien': format(thanhtien, ',').split('.')[0].replace(',','.'),
                    })
            if line.sl_3_dc_trung:
                slan_trung = line.sl_3_dc_trung
                sluong_trung = line.sl_3_dc
                thanhtien = slan_trung*sluong_trung*(2500000*gt_menhgia)
                
                tong_sl_3_dc += slan_trung*sluong_trung
                tong_tien_3_dc += thanhtien
                
                tong_sl_3 += slan_trung*sluong_trung
                tong_tien_3 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
                
                res['line'].append({
                    'so_dt_2_d': '',
                    'so_dt_2_c': '',
                    'so_dt_2_dc': '',
                    'so_dt_2_18': '',
                    'so_dt_3_d': '',
                    'so_dt_3_c': '',
                    'so_dt_3_dc': line.so_dt_3_dc,
                    'so_dt_3_7': '',
                    'so_dt_3_17': '',
                    'so_dt_4_16': '',
                    'slan_trung': slan_trung,
                    'sluong_trung': sluong_trung,
                    'so_phieu': line.ve_loto_id.sophieu,
                    'dai_ly': line.ve_loto_id.daily_id.name,
                    'thanhtien': format(thanhtien, ',').split('.')[0].replace(',','.'),
                    })
            if line.sl_3_7_trung:
                slan_trung = line.sl_3_7_trung
                sluong_trung = line.sl_3_7
                thanhtien = slan_trung*sluong_trung*(715000*gt_menhgia)
                
                tong_sl_3_7 += slan_trung*sluong_trung
                tong_tien_3_7 += thanhtien
                
                tong_sl_3 += slan_trung*sluong_trung
                tong_tien_3 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
                
                res['line'].append({
                    'so_dt_2_d': '',
                    'so_dt_2_c': '',
                    'so_dt_2_dc': '',
                    'so_dt_2_18': '',
                    'so_dt_3_d': '',
                    'so_dt_3_c': '',
                    'so_dt_3_dc': '',
                    'so_dt_3_7': line.so_dt_3_7,
                    'so_dt_3_17': '',
                    'so_dt_4_16': '',
                    'slan_trung': slan_trung,
                    'sluong_trung': sluong_trung,
                    'so_phieu': line.ve_loto_id.sophieu,
                    'dai_ly': line.ve_loto_id.daily_id.name,
                    'thanhtien': format(thanhtien, ',').split('.')[0].replace(',','.'),
                    })
            if line.sl_3_17_trung:
                slan_trung = line.sl_3_17_trung
                sluong_trung = line.sl_3_17
                thanhtien = slan_trung*sluong_trung*(295000*gt_menhgia)
                
                tong_sl_3_17 += slan_trung*sluong_trung
                tong_tien_3_17 += thanhtien
                
                tong_sl_3 += slan_trung*sluong_trung
                tong_tien_3 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
                
                res['line'].append({
                    'so_dt_2_d': '',
                    'so_dt_2_c': '',
                    'so_dt_2_dc': '',
                    'so_dt_2_18': '',
                    'so_dt_3_d': '',
                    'so_dt_3_c': '',
                    'so_dt_3_dc': '',
                    'so_dt_3_7': '',
                    'so_dt_3_17': line.so_dt_3_17,
                    'so_dt_4_16': '',
                    'slan_trung': slan_trung,
                    'sluong_trung': sluong_trung,
                    'so_phieu': line.ve_loto_id.sophieu,
                    'dai_ly': line.ve_loto_id.daily_id.name,
                    'thanhtien': format(thanhtien, ',').split('.')[0].replace(',','.'),
                    })
            
            # 4 so
            if line.sl_4_16_trung:
                slan_trung = line.sl_4_16_trung
                sluong_trung = line.sl_4_16
                thanhtien = slan_trung*sluong_trung*(2000000*gt_menhgia)
                
                tong_sl_4_16 += slan_trung*sluong_trung
                tong_tien_4_16 += thanhtien
                
                tong_sl_4 += slan_trung*sluong_trung
                tong_tien_4 += thanhtien
                
                tong_slan_trung += slan_trung
                tong_sluong_trung += sluong_trung
                tong_thanhtien += thanhtien
                
                res['line'].append({
                    'so_dt_2_d': '',
                    'so_dt_2_c': '',
                    'so_dt_2_dc': '',
                    'so_dt_2_18': '',
                    'so_dt_3_d': '',
                    'so_dt_3_c': '',
                    'so_dt_3_dc': '',
                    'so_dt_3_7': '',
                    'so_dt_3_17': '',
                    'so_dt_4_16': line.so_dt_4_16,
                    'slan_trung': slan_trung,
                    'sluong_trung': sluong_trung,
                    'so_phieu': line.ve_loto_id.sophieu,
                    'dai_ly': line.ve_loto_id.daily_id.name,
                    'thanhtien': format(thanhtien, ',').split('.')[0].replace(',','.'),
                    })
        res['tong'] = {
            'tong_sl_2_d': format(tong_sl_2_d, ',').split('.')[0].replace(',','.'),
            'tong_tien_2_d': format(tong_tien_2_d, ',').split('.')[0].replace(',','.'),
            'tong_sl_2_c': format(tong_sl_2_c, ',').split('.')[0].replace(',','.'),
            'tong_tien_2_c': format(tong_tien_2_c, ',').split('.')[0].replace(',','.'),
            'tong_sl_2_dc': format(tong_sl_2_dc, ',').split('.')[0].replace(',','.'),
            'tong_tien_2_dc': format(tong_tien_2_dc, ',').split('.')[0].replace(',','.'),
            'tong_sl_2_18': format(tong_sl_2_18, ',').split('.')[0].replace(',','.'),
            'tong_tien_2_18': format(tong_tien_2_18, ',').split('.')[0].replace(',','.'),
            'tong_sl_2': format(tong_sl_2, ',').split('.')[0].replace(',','.'),
            'tong_tien_2': format(tong_tien_2, ',').split('.')[0].replace(',','.'),
            'tong_sl_3_d': format(tong_sl_3_d, ',').split('.')[0].replace(',','.'),
            'tong_tien_3_d': format(tong_tien_3_d, ',').split('.')[0].replace(',','.'),
            'tong_sl_3_c': format(tong_sl_3_c, ',').split('.')[0].replace(',','.'),
            'tong_tien_3_c': format(tong_tien_3_c, ',').split('.')[0].replace(',','.'),
            'tong_sl_3_dc': format(tong_sl_3_dc, ',').split('.')[0].replace(',','.'),
            'tong_tien_3_dc': format(tong_tien_3_dc, ',').split('.')[0].replace(',','.'),
            'tong_sl_3_7': format(tong_sl_3_7, ',').split('.')[0].replace(',','.'),
            'tong_tien_3_7': format(tong_tien_3_7, ',').split('.')[0].replace(',','.'),
            'tong_sl_3_17': format(tong_sl_3_17, ',').split('.')[0].replace(',','.'),
            'tong_tien_3_17': format(tong_tien_3_17, ',').split('.')[0].replace(',','.'),
            'tong_sl_3': format(tong_sl_3, ',').split('.')[0].replace(',','.'),
            'tong_tien_3': format(tong_tien_3, ',').split('.')[0].replace(',','.'),
            'tong_sl_4_16': format(tong_sl_4_16, ',').split('.')[0].replace(',','.'),
            'tong_tien_4_16': format(tong_tien_4_16, ',').split('.')[0].replace(',','.'),
            'tong_sl_4': format(tong_sl_4, ',').split('.')[0].replace(',','.'),
            'tong_tien_4': format(tong_tien_4, ',').split('.')[0].replace(',','.'),
            'tong_slan_trung': format(tong_slan_trung, ',').split('.')[0].replace(',','.'),
            'tong_sluong_trung': format(tong_sluong_trung, ',').split('.')[0].replace(',','.'),
            'tong_thanhtien': format(tong_thanhtien, ',').split('.')[0].replace(',','.'),
        }
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
