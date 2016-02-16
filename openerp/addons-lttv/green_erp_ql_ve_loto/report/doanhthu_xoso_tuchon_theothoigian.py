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
            'get_doanhthu_tieuthu':self.get_doanhthu_tieuthu,
            'get_menh_gia':self.get_menh_gia,
            'get_tong': self.get_tong,
            'get_sai_kythuat': self.get_sai_kythuat,
            'get_tong_sai_kythuat': self.get_tong_sai_kythuat,
            
            'get_chitiet': self.get_chitiet,
            'get_trathuong': self.get_trathuong,
            'get_tong_trathuong': self.get_tong_trathuong,
        })
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_menh_gia(self):
        menhgia_obj = self.pool.get('product.product')
        menh_gia_ids = menhgia_obj.search(self.cr, self.uid, [('menh_gia','=',True)])
        return menhgia_obj.browse(self.cr, self.uid, menh_gia_ids)
    
    def get_chitiet(self,date_from,date_to,menhgia):
        tong_ve = 0
        tong_thanhtien = 0
        gt_menhgia = menhgia.list_price/10000
        sql = '''
            select sl_2_d_trung,sl_2_d,sl_2_c_trung,sl_2_c,sl_2_dc_trung,sl_2_dc,sl_2_18_trung,sl_2_18,sl_3_d_trung,sl_3_d,sl_3_c_trung,sl_3_c,sl_3_dc_trung,sl_3_dc,
                    sl_3_7_trung,sl_3_7,sl_3_17_trung,sl_3_17,sl_4_16_trung,sl_4_16
             from ve_loto_line where ve_loto_id in (select id from ve_loto where (ngay between '%s' and '%s') and state = 'done' and product_id = %s)
        '''%(date_from,date_to,menhgia.id)
        self.cr.execute(sql)
#         ve_loto_obj = self.pool.get('ve.loto')
#         loto_line_obj = self.pool.get('ve.loto.line')
#         ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','>=',date_from),('ngay','<=',date_to),('state','=','done'),('product_id','=',menhgia.id)])
#         loto_line_ids = loto_line_obj.search(self.cr, self.uid, [('ve_loto_id','in',ve_loto_ids)])

        for line in self.cr.dictfetchall():
            # 2 so
            if line['sl_2_d_trung']:
                slan_trung = line['sl_2_d_trung']
                sluong_trung = line['sl_2_d']
                thanhtien = round(slan_trung*sluong_trung*(700000*gt_menhgia))
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line['sl_2_c_trung']:
                slan_trung = line['sl_2_c_trung']
                sluong_trung = line['sl_2_c']
                thanhtien = round(slan_trung*sluong_trung*(700000*gt_menhgia))
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line['sl_2_dc_trung']:
                slan_trung = line['sl_2_dc_trung']
                sluong_trung = line['sl_2_dc']
                thanhtien = round(slan_trung*sluong_trung*(350000*gt_menhgia))
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line['sl_2_18_trung'] :
                slan_trung = line['sl_2_18_trung']
                sluong_trung = line['sl_2_18']
                thanhtien = round(slan_trung*sluong_trung*(40000*gt_menhgia))
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            # 3 so
            if line['sl_3_d_trung']:
                slan_trung = line['sl_3_d_trung']
                sluong_trung = line['sl_3_d']
                thanhtien = round(slan_trung*sluong_trung*(5000000*gt_menhgia))
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line['sl_3_c_trung']:
                slan_trung = line['sl_3_c_trung']
                sluong_trung = line['sl_3_c']
                thanhtien = round(slan_trung*sluong_trung*(5000000*gt_menhgia))
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line['sl_3_dc_trung']:
                slan_trung = line['sl_3_dc_trung']
                sluong_trung = line['sl_3_dc']
                thanhtien = slan_trung*sluong_trung*(2500000*gt_menhgia)
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line['sl_3_7_trung']:
                slan_trung = line['sl_3_7_trung']
                sluong_trung = line['sl_3_7']
                thanhtien = slan_trung*sluong_trung*(700000*gt_menhgia)
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            if line['sl_3_17_trung']:
                slan_trung = line['sl_3_17_trung']
                sluong_trung = line['sl_3_17']
                thanhtien = slan_trung*sluong_trung*(300000*gt_menhgia)
                
                tong_ve += sluong_trung
                tong_thanhtien += thanhtien
            # 4 so
            if line['sl_4_16_trung']:
                slan_trung = line['sl_4_16_trung']
                sluong_trung = line['sl_4_16']
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
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select id from ve_loto where ngay between '%s' and '%s' and product_id = %s and state = 'done'
        '''%(date_from,date_to,menhgia_id)
        self.cr.execute(sql)
        ve_loto_ids = [r[0] for r in self.cr.fetchall()]
        if ve_loto_ids:
            self.cr.execute("select sum(tong_cong) as tong from ve_loto where id in %s",(tuple(ve_loto_ids),))
            tongso = self.cr.dictfetchone()['tong']
            return format(tongso, ',')
        else:
            return ''
        
    def get_tong(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        ve_loto_obj = self.pool.get('ve.loto')
        sql= '''
            select id from product_product where menh_gia = True
        '''
        self.cr.execute(sql)
        tongve = 0
        tongcong = 0
        menhgia_ids = [r[0] for r in self.cr.fetchall()]
        for menhgia in self.pool.get('product.product').browse(self.cr,self.uid,menhgia_ids):
            sql = '''
                select id from ve_loto where ngay between '%s' and '%s' and product_id = %s and state = 'done'
            '''%(date_from,date_to,menhgia.id)
            self.cr.execute(sql)
            ve_loto_ids = [r[0] for r in self.cr.fetchall()]
            if ve_loto_ids:
                self.cr.execute("select sum(tong_cong) as tong from ve_loto where id in %s",(tuple(ve_loto_ids),))
                ve = self.cr.dictfetchone()['tong']
                if ve:
                    tongve += ve
                    tongcong += menhgia.list_price*ve
        return {
                'tongve': format(tongve, ','),
                'tongcong': format(tongcong, ','),
                }
    
    def get_trathuong(self, menhgia):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        tongso = self.get_chitiet(date_from,date_to,menhgia)['tong_ve']
        return format(tongso, ',')
    def get_tong_trathuong(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        menhgia_obj = self.pool.get('product.product')
        menhgia_ids = menhgia_obj.search(self.cr, self.uid, [('menh_gia','=',True)])
        tongve = 0
        tongcong = 0
        for menhgia in menhgia_obj.browse(self.cr,self.uid,menhgia_ids):
            tongso = self.get_chitiet(date_from,date_to,menhgia)
            tongve += tongso['tong_ve']
            tongcong += tongso['tong_thanhtien']
        return {
                'tongve': format(tongve, ','),
                'tongcong': format(tongcong, ','),
                }    
#     def get_tong_trathuong(self):
#         wizard_data = self.localcontext['data']['form']
#         date_from = wizard_data['date_from']
#         date_to = wizard_data['date_to']
#         sql= '''
#             select id from product_product where menh_gia = True
#         '''
#         self.cr.execute(sql)
#         tongve = 0
#         tongcong = 0
#         menhgia_ids = [r[0] for r in self.cr.fetchall()]
#         for menhgia in self.pool.get('product.product').browse(self.cr,self.uid,menhgia_ids):
#             tongso = self.get_chitiet(date_from,date_to,menhgia)
#             tongve += tongso['tong_ve']
#             tongcong += tongso['tong_thanhtien']
#         return {
#                 'tongve': format(tongve, ','),
#                 'tongcong': format(tongcong, ','),
#                 }
    
    def get_sai_kythuat(self, menhgia_id):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select id from ve_loto where ngay between '%s' and '%s' and product_id = %s and state = 'done'
        '''%(date_from,date_to,menhgia_id)
        self.cr.execute(sql)
        ve_loto_ids = [r[0] for r in self.cr.fetchall()]
        if ve_loto_ids:
            self.cr.execute("select case when sum(tong_sai_kythuat)!=0 then sum(tong_sai_kythuat) else 0 end tong from ve_loto where id in %s",(tuple(ve_loto_ids),))
            tongso = self.cr.dictfetchone()['tong']
            return format(tongso, ',')
        else:
            return ''
        
    def get_tong_sai_kythuat(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        ve_loto_obj = self.pool.get('ve.loto')
        sql= '''
            select id from product_product where menh_gia = True
        '''
        self.cr.execute(sql)
        tongve = 0
        tongcong = 0
        menhgia_ids = [r[0] for r in self.cr.fetchall()]
        for menhgia in self.pool.get('product.product').browse(self.cr,self.uid,menhgia_ids):
            sql = '''
                select id from ve_loto where ngay between '%s' and '%s' and product_id = %s and state = 'done'
            '''%(date_from,date_to,menhgia.id)
            self.cr.execute(sql)
            ve_loto_ids = [r[0] for r in self.cr.fetchall()]
            if ve_loto_ids:
                self.cr.execute("select case when sum(tong_sai_kythuat)!=0 then sum(tong_sai_kythuat) else 0 end tong from ve_loto where id in %s",(tuple(ve_loto_ids),))
                ve = self.cr.dictfetchone()['tong']
                if ve:
                    tongve += ve
                    tongcong += menhgia.list_price*ve
        return {
                'tongve': format(tongve, ','),
                'tongcong': format(tongcong, ','),
                }
