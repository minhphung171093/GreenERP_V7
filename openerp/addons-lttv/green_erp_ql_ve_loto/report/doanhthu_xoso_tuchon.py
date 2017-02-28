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
            'convert_2f_amount': self.convert_2f_amount,
            'get_daiduthuong':self.get_daiduthuong,
            'get_giamsat1':self.get_giamsat1,
            'get_giamsat2':self.get_giamsat2,
            'get_giamsat3':self.get_giamsat3,
            'get_ctyxs1':self.get_ctyxs1,
            'get_ctyxs2':self.get_ctyxs2,
            'get_ctyxs3':self.get_ctyxs3,
            'get_cv_giamsat1':self.get_cv_giamsat1,
            'get_cv_giamsat2':self.get_cv_giamsat2,
            'get_cv_giamsat3':self.get_cv_giamsat3,
            'get_cv_ctyxs1':self.get_cv_ctyxs1,
            'get_cv_ctyxs2':self.get_cv_ctyxs2,
            'get_cv_ctyxs3':self.get_cv_ctyxs3,
            'get_doanhthu_tieuthu':self.get_doanhthu_tieuthu,
            'get_menh_gia':self.get_menh_gia,
            'get_tong': self.get_tong,
            'get_sai_kythuat': self.get_sai_kythuat,
            'get_tong_sai_kythuat': self.get_tong_sai_kythuat,
            
            'get_chitiet': self.get_chitiet,
            'get_trathuong': self.get_trathuong,
            'get_tong_trathuong': self.get_tong_trathuong,
            'get_tyle_trathuong': self.get_tyle_trathuong,
        })
    def get_date(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def convert_2f_amount(self, amount):
        if amount:
            amount_atr = '%.2f'%(amount)
            a1 = amount_atr.split('.')[0]
            a2 = amount_atr.split('.')[1]
            a = format(int(a1),',').split('.')[0].replace(',','.')
            return a+','+a2
        return ''
    
    def get_tyle_trathuong(self):
        tongdoanhthu = self.get_tong()['tongdoanhthu']
        tongtrathuong = self.get_tong_trathuong()['tongtrathuong']
        tyle = tongdoanhthu and float(tongtrathuong)/float(tongdoanhthu)*100.0
        return self.convert_2f_amount(tyle)
    
    def get_daiduthuong(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        ketqua_obj = self.pool.get('ketqua.xoso')
        ketqua_ids = ketqua_obj.search(self.cr ,self.uid, [('name','=',date),('state','=','validate')])
        if ketqua_ids:
            return ketqua_obj.browse(self.cr, self.uid, ketqua_ids[0]).dai_duthuong_id.name
        else:
            return False
    
    def get_giamsat1(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['giamsat_1']
    
    def get_giamsat2(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['giamsat_2']
    
    def get_giamsat3(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['giamsat_3']
    
    def get_ctyxs1(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['ctyxs_1']
    
    def get_ctyxs2(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['ctyxs_2']
    
    def get_ctyxs3(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['ctyxs_3']
    
    def get_cv_giamsat1(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['cv_giamsat_1']
    
    def get_cv_giamsat2(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['cv_giamsat_2']
    
    def get_cv_giamsat3(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['cv_giamsat_3']
    
    def get_cv_ctyxs1(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['cv_ctyxs_1']
    
    def get_cv_ctyxs2(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['cv_ctyxs_2']
    
    def get_cv_ctyxs3(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['cv_ctyxs_3']
    
    def get_menh_gia(self):
        menhgia_obj = self.pool.get('product.product')
        menh_gia_ids = menhgia_obj.search(self.cr, self.uid, [('menh_gia','=',True)])
        return menhgia_obj.browse(self.cr, self.uid, menh_gia_ids)
    
    def get_chitiet(self,date,menhgia):
        tong_ve = 0
        tong_thanhtien = 0
        
        ve_loto_obj = self.pool.get('ve.loto')
        loto_line_obj = self.pool.get('ve.loto.line')
        sql = '''
            select ltl.id as id
                from ve_loto_line ltl
                left join ve_loto lt on ltl.ve_loto_id=lt.id
                
                where lt.ngay='%s' and lt.state='done' and lt.product_id=%s
                    and (ltl.sl_2_d_trung!=0 or ltl.sl_2_c_trung!=0 or ltl.sl_2_dc_trung!=0 or ltl.sl_2_18_trung!=0
                         or ltl.sl_3_d_trung!=0 or ltl.sl_3_c_trung!=0 or ltl.sl_3_dc_trung!=0 or ltl.sl_3_7_trung!=0 or ltl.sl_3_17_trung!=0
                         or ltl.sl_4_16_trung!=0)
        '''%(date, menhgia.id)
        self.cr.execute(sql)
        loto_line_ids = [r[0] for r in self.cr.fetchall()]
#         ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('state','=','done'),('product_id','=',menhgia.id)])
#         loto_line_ids = loto_line_obj.search(self.cr, self.uid, [('ve_loto_id','in',ve_loto_ids)])
        gt_menhgia = int(menhgia.list_price)/10000
        for line in loto_line_obj.browse(self.cr, self.uid, loto_line_ids):
            # 2 so
            if line.sl_2_d_trung:
                slan_trung = line.sl_2_d_trung
                sluong_trung = line.sl_2_d
                thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_2_c_trung:
                slan_trung = line.sl_2_c_trung
                sluong_trung = line.sl_2_c
                thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_2_dc_trung:
                slan_trung = line.sl_2_dc_trung
                sluong_trung = line.sl_2_dc
                thanhtien = slan_trung*sluong_trung*(350000*gt_menhgia)
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_2_18_trung:
                slan_trung = line.sl_2_18_trung
                sluong_trung = line.sl_2_18
                thanhtien = slan_trung*sluong_trung*(39000*gt_menhgia)
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            # 3 so
            if line.sl_3_d_trung:
                slan_trung = line.sl_3_d_trung
                sluong_trung = line.sl_3_d
                thanhtien = slan_trung*sluong_trung*(5000000*gt_menhgia)
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_3_c_trung:
                slan_trung = line.sl_3_c_trung
                sluong_trung = line.sl_3_c
                thanhtien = slan_trung*sluong_trung*(5000000*gt_menhgia)
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_3_dc_trung:
                slan_trung = line.sl_3_dc_trung
                sluong_trung = line.sl_3_dc
                thanhtien = slan_trung*sluong_trung*(2500000*gt_menhgia)
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_3_7_trung:
                slan_trung = line.sl_3_7_trung
                sluong_trung = line.sl_3_7
                thanhtien = slan_trung*sluong_trung*(715000*gt_menhgia)
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line.sl_3_17_trung:
                slan_trung = line.sl_3_17_trung
                sluong_trung = line.sl_3_17
                thanhtien = slan_trung*sluong_trung*(295000*gt_menhgia)
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            # 4 so
            if line.sl_4_16_trung:
                slan_trung = line.sl_4_16_trung
                sluong_trung = line.sl_4_16
                thanhtien = slan_trung*sluong_trung*(2000000*gt_menhgia)

                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
        res = {
            'tong_ve': tong_ve,
            'tong_thanhtien': tong_thanhtien,
        }
        return res
    
    def get_doanhthu_tieuthu(self, menhgia_id):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        ve_loto_obj = self.pool.get('ve.loto')
        ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('product_id','=',menhgia_id),('state','=','done')])
        if ve_loto_ids:
            self.cr.execute("select sum(tong_cong) as tong from ve_loto where id in %s",(tuple(ve_loto_ids),))
            tongso = self.cr.dictfetchone()['tong']
            return format(tongso, ',').split('.')[0].replace(',','.')
        else:
            return ''
        
    def get_tong(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        ve_loto_obj = self.pool.get('ve.loto')
        menhgia_obj = self.pool.get('product.product')
        menhgia_ids = menhgia_obj.search(self.cr, self.uid, [('menh_gia','=',True)])
        tongve = 0
        tongcong = 0
        for menhgia in menhgia_obj.browse(self.cr,self.uid,menhgia_ids):
            ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('product_id','=',menhgia.id),('state','=','done')])
            if ve_loto_ids:
                self.cr.execute("select sum(tong_cong) as tong from ve_loto where id in %s",(tuple(ve_loto_ids),))
                ve = self.cr.dictfetchone()['tong']
                if ve:
                    tongve += ve
                    tongcong += int(menhgia.list_price)*ve
        return {
                'tongve': format(tongve, ',').split('.')[0].replace(',','.'),
                'tongcong': format(tongcong, ',').split('.')[0].replace(',','.'),
                'tongdoanhthu': tongcong,
                }
    
    def get_trathuong(self, menhgia):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        tongso = self.get_chitiet(date,menhgia)['tong_ve']
        return format(tongso, ',').split('.')[0].replace(',','.')
    
    def get_tong_trathuong(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        menhgia_obj = self.pool.get('product.product')
        menhgia_ids = menhgia_obj.search(self.cr, self.uid, [('menh_gia','=',True)])
        tongve = 0
        tongcong = 0
        for menhgia in menhgia_obj.browse(self.cr,self.uid,menhgia_ids):
            tongso = self.get_chitiet(date,menhgia)
            tongve += tongso['tong_ve']
            tongcong += tongso['tong_thanhtien']
        return {
                'tongve': format(tongve, ',').split('.')[0].replace(',','.'),
                'tongcong': format(tongcong, ',').split('.')[0].replace(',','.'),
                'tongtrathuong': tongcong,
                }
    
    def get_sai_kythuat(self, menhgia_id):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        ve_loto_obj = self.pool.get('ve.loto')
        ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('product_id','=',menhgia_id),('state','=','done')])
        if ve_loto_ids:
            self.cr.execute("select case when sum(tong_sai_kythuat)!=0 then sum(tong_sai_kythuat) else 0 end tong from ve_loto where id in %s",(tuple(ve_loto_ids),))
            tongso = self.cr.dictfetchone()['tong']
            return format(tongso, ',').split('.')[0].replace(',','.')
        else:
            return ''
        
    def get_tong_sai_kythuat(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        ve_loto_obj = self.pool.get('ve.loto')
        menhgia_obj = self.pool.get('product.product')
        menhgia_ids = menhgia_obj.search(self.cr, self.uid, [('menh_gia','=',True)])
        tongve = 0
        tongcong = 0
        for menhgia in menhgia_obj.browse(self.cr,self.uid,menhgia_ids):
            ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),('product_id','=',menhgia.id),('state','=','done')])
            if ve_loto_ids:
                self.cr.execute("select case when sum(tong_sai_kythuat)!=0 then sum(tong_sai_kythuat) else 0 end tong from ve_loto where id in %s",(tuple(ve_loto_ids),))
                ve = self.cr.dictfetchone()['tong']
                if ve:
                    tongve += ve
                    tongcong += int(menhgia.list_price)*ve
        return {
                'tongve': format(tongve, ',').split('.')[0].replace(',','.'),
                'tongcong': format(tongcong, ',').split('.')[0].replace(',','.'),
                }
