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
            'get_menhgia': self.get_menhgia,
            'get_date': self.get_date,
            'get_lines': self.get_lines,
            'get_date_now': self.get_date_now,
            'get_tong': self.get_tong,
        })
    
    def get_date_now(self):
        return time.strftime('%Y-%m-%d')
    
    def get_date(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date_from']
        return date[8:10]+'/'+date[5:7]+'/'+date[:4]

    def get_menhgia(self):
        menhgia_obj = self.pool.get('product.product')
        wizard_data = self.localcontext['data']['form']
        menhgia_id = wizard_data['menhgia_id'][0]
        return menhgia_obj.browse(self.cr, self.uid, menhgia_id)
    
    def sum_all(self):
        tt_tong = 0
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        menhgia_id = wizard_data['menhgia_id'][0]
        trathuong_obj = self.pool.get('tra.thuong')
        trathuong_ids = trathuong_obj.search(self.cr, self.uid, [('ngay','>=',date_from),('ngay','<=',date_to)],order='ngay')
        for trathuong in trathuong_obj.browse(self.cr, self.uid, trathuong_ids):
            for line in trathuong.tra_thuong_line:
                if line.product_id.id==menhgia_id:
                    tt_tong += line.tong
        return tt_tong
    
    def get_tong(self):
        sl_2_d = 0
        tt_2_d = 0
        sl_2_c = 0
        tt_2_c = 0
        sl_2_dc = 0
        slan_2_dc = 0
        tt_2_dc = 0
        sl_2_18 = 0
        slan_2_18 = 0
        tt_2_18 = 0
        sl_3_d = 0
        tt_3_d = 0
        sl_3_c = 0
        tt_3_c = 0
        sl_3_dc = 0
        slan_3_dc = 0
        tt_3_dc = 0
        sl_3_7 = 0
        slan_3_7 = 0
        tt_3_7 = 0
        sl_3_17 = 0
        slan_3_17 = 0
        tt_3_17 = 0
        sl_4_16 = 0
        slan_4_16 = 0
        tt_4_16 = 0
        sl_tong = 0
        tt_tong = 0
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        menhgia_id = wizard_data['menhgia_id'][0]
        trathuong_obj = self.pool.get('tra.thuong')
        trathuong_ids = trathuong_obj.search(self.cr, self.uid, [('ngay','>=',date_from),('ngay','<=',date_to)],order='ngay')
        res = []
        for trathuong in trathuong_obj.browse(self.cr, self.uid, trathuong_ids):
            for line in trathuong.tra_thuong_line:
                if line.product_id.id==menhgia_id:
                    if line.loai=='2_so':
                        if line.giai=='dau':
                            sl_2_d += line.sl_trung
                            tt_2_d += line.tong
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                        if line.giai=='cuoi':
                            sl_2_c += line.sl_trung
                            tt_2_c += line.tong
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                        if line.giai=='dau_cuoi':
                            sl_2_dc += line.sl_trung
                            slan_2_dc += line.slan_trung
                            tt_2_dc += line.tong
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                        if line.giai=='18_lo':
                            sl_2_18 += line.sl_trung
                            tt_2_18 += line.tong
                            slan_2_18 += line.slan_trung
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                    if line.loai=='3_so':
                        if line.giai=='dau':
                            sl_3_d += line.sl_trung
                            tt_3_d += line.tong
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                        if line.giai=='cuoi':
                            sl_3_c += line.sl_trung
                            tt_3_c += line.tong
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                        if line.giai=='dau_cuoi':
                            sl_3_dc += line.sl_trung
                            tt_3_dc += line.tong
                            slan_3_dc += line.slan_trung
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                        if line.giai=='7_lo':
                            sl_3_7 += line.sl_trung
                            tt_3_7 += line.tong
                            slan_3_7 += line.slan_trung
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                        if line.giai=='17_lo':
                            sl_3_17 += line.sl_trung
                            tt_3_17 += line.tong
                            slan_3_17 += line.slan_trung
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                    if line.loai=='4_so':
                        if line.giai=='16_lo':
                            sl_4_16 += line.sl_trung
                            tt_4_16 += line.tong
                            slan_4_16 += line.slan_trung
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
        res={
            'sl_2_d': sl_2_d,
            'tt_2_d': tt_2_d,
            'sl_2_c': sl_2_c,
            'tt_2_c': tt_2_c,
            'sl_2_dc': sl_2_dc,
            'slan_2_dc': slan_2_dc,
            'tt_2_dc': tt_2_dc,
            'sl_2_18': sl_2_18,
            'slan_2_18': slan_2_18,
            'tt_2_18': tt_2_18,
            'sl_3_d': sl_3_d,
            'tt_3_d': tt_3_d,
            'sl_3_c': sl_3_c,
            'tt_3_c': tt_3_c,
            'sl_3_dc': sl_3_dc,
            'slan_3_dc': slan_3_dc,
            'tt_3_dc': tt_3_dc,
            'sl_3_7': sl_3_7,
            'slan_3_7': slan_3_7,
            'tt_3_7': tt_3_7,
            'sl_3_17': sl_3_17,
            'slan_3_17': slan_3_17,
            'tt_3_17': tt_3_17,
            'sl_4_16': sl_4_16,
            'slan_4_16': slan_4_16,
            'tt_4_16': tt_4_16,
            'sl_tong': sl_tong,
            'tt_tong': tt_tong,
            'ty_le': self.sum_all() and tt_tong/self.sum_all()*100 or 0,
        }
        return res
    
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        menhgia_id = wizard_data['menhgia_id'][0]
        trathuong_obj = self.pool.get('tra.thuong')
        trathuong_ids = trathuong_obj.search(self.cr, self.uid, [('ngay','>=',date_from),('ngay','<=',date_to)],order='ngay')
        res = []
        trathuongs = trathuong_obj.browse(self.cr, self.uid, trathuong_ids)
        if trathuongs:
            ngay = trathuongs[0].ngay
        sl_2_d = 0
        tt_2_d = 0
        sl_2_c = 0
        tt_2_c = 0
        sl_2_dc = 0
        slan_2_dc = 0
        tt_2_dc = 0
        sl_2_18 = 0
        slan_2_18 = 0
        tt_2_18 = 0
        sl_3_d = 0
        tt_3_d = 0
        sl_3_c = 0
        tt_3_c = 0
        sl_3_dc = 0
        slan_3_dc = 0
        tt_3_dc = 0
        sl_3_7 = 0
        slan_3_7 = 0
        tt_3_7 = 0
        sl_3_17 = 0
        slan_3_17 = 0
        tt_3_17 = 0
        sl_4_16 = 0
        slan_4_16 = 0
        tt_4_16 = 0
        sl_tong = 0
        tt_tong = 0
        for trathuong in trathuongs:
            if trathuong.ngay!=ngay:
                date_1 = datetime.strptime(ngay, "%Y-%m-%d")
                end_date = date_1 + timedelta(days=30)
                end_date = str(end_date)
                res.append({
                    'ngay_mothuong': ngay[8:10]+'/'+ngay[5:7]+'/'+ngay[:4],
                    'ngay_denhan': end_date[8:10]+'/'+end_date[5:7]+'/'+end_date[:4],
                    'sl_2_d': sl_2_d,
                    'tt_2_d': tt_2_d,
                    'sl_2_c': sl_2_c,
                    'tt_2_c': tt_2_c,
                    'sl_2_dc': sl_2_dc,
                    'slan_2_dc': slan_2_dc,
                    'tt_2_dc': tt_2_dc,
                    'sl_2_18': sl_2_18,
                    'slan_2_18': slan_2_18,
                    'tt_2_18': tt_2_18,
                    'sl_3_d': sl_3_d,
                    'tt_3_d': tt_3_d,
                    'sl_3_c': sl_3_c,
                    'tt_3_c': tt_3_c,
                    'sl_3_dc': sl_3_dc,
                    'slan_3_dc': slan_3_dc,
                    'tt_3_dc': tt_3_dc,
                    'sl_3_7': sl_3_7,
                    'slan_3_7': slan_3_7,
                    'tt_3_7': tt_3_7,
                    'sl_3_17': sl_3_17,
                    'slan_3_17': slan_3_17,
                    'tt_3_17': tt_3_17,
                    'sl_4_16': sl_4_16,
                    'slan_4_16': slan_4_16,
                    'tt_4_16': tt_4_16,
                    'sl_tong': sl_tong,
                    'tt_tong': tt_tong,
                    'ty_le': self.sum_all() and tt_tong/self.sum_all()*100 or 0, 
                })
                ngay = trathuong.ngay
                sl_2_d = 0
                tt_2_d = 0
                sl_2_c = 0
                tt_2_c = 0
                sl_2_dc = 0
                slan_2_dc = 0
                tt_2_dc = 0
                sl_2_18 = 0
                slan_2_18 = 0
                tt_2_18 = 0
                sl_3_d = 0
                tt_3_d = 0
                sl_3_c = 0
                tt_3_c = 0
                sl_3_dc = 0
                slan_3_dc = 0
                tt_3_dc = 0
                sl_3_7 = 0
                slan_3_7 = 0
                tt_3_7 = 0
                sl_3_17 = 0
                slan_3_17 = 0
                tt_3_17 = 0
                sl_4_16 = 0
                slan_4_16 = 0
                tt_4_16 = 0
                sl_tong = 0
                tt_tong = 0
            for line in trathuong.tra_thuong_line:
                if line.product_id.id==menhgia_id:
                    if line.loai=='2_so':
                        if line.giai=='dau':
                            sl_2_d += line.sl_trung
                            tt_2_d += line.tong
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                        if line.giai=='cuoi':
                            sl_2_c += line.sl_trung
                            tt_2_c += line.tong
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                        if line.giai=='dau_cuoi':
                            sl_2_dc += line.sl_trung
                            slan_2_dc += line.slan_trung
                            tt_2_dc += line.tong
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                        if line.giai=='18_lo':
                            sl_2_18 += line.sl_trung
                            tt_2_18 += line.tong
                            slan_2_18 += line.slan_trung
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                    if line.loai=='3_so':
                        if line.giai=='dau':
                            sl_3_d += line.sl_trung
                            tt_3_d += line.tong
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                        if line.giai=='cuoi':
                            sl_3_c += line.sl_trung
                            tt_3_c += line.tong
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                        if line.giai=='dau_cuoi':
                            sl_3_dc += line.sl_trung
                            tt_3_dc += line.tong
                            slan_3_dc += line.slan_trung
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                        if line.giai=='7_lo':
                            sl_3_7 += line.sl_trung
                            tt_3_7 += line.tong
                            slan_3_7 += line.slan_trung
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                        if line.giai=='17_lo':
                            sl_3_17 += line.sl_trung
                            tt_3_17 += line.tong
                            slan_3_17 += line.slan_trung
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
                    if line.loai=='4_so':
                        if line.giai=='16_lo':
                            sl_4_16 += line.sl_trung
                            tt_4_16 += line.tong
                            slan_4_16 += line.slan_trung
                            sl_tong += line.sl_trung
                            tt_tong += line.tong
        if tt_tong:
            date_1 = datetime.strptime(ngay, "%Y-%m-%d")
            end_date = date_1 + timedelta(days=30)
            end_date = str(end_date)
            res.append({
                'ngay_mothuong': ngay[8:10]+'/'+ngay[5:7]+'/'+ngay[:4],
                'ngay_denhan': end_date[8:10]+'/'+end_date[5:7]+'/'+end_date[:4],
                'sl_2_d': sl_2_d,
                'tt_2_d': tt_2_d,
                'sl_2_c': sl_2_c,
                'tt_2_c': tt_2_c,
                'sl_2_dc': sl_2_dc,
                'slan_2_dc': slan_2_dc,
                'tt_2_dc': tt_2_dc,
                'sl_2_18': sl_2_18,
                'slan_2_18': slan_2_18,
                'tt_2_18': tt_2_18,
                'sl_3_d': sl_3_d,
                'tt_3_d': tt_3_d,
                'sl_3_c': sl_3_c,
                'tt_3_c': tt_3_c,
                'sl_3_dc': sl_3_dc,
                'slan_3_dc': slan_3_dc,
                'tt_3_dc': tt_3_dc,
                'sl_3_7': sl_3_7,
                'slan_3_7': slan_3_7,
                'tt_3_7': tt_3_7,
                'sl_3_17': sl_3_17,
                'slan_3_17': slan_3_17,
                'tt_3_17': tt_3_17,
                'sl_4_16': sl_4_16,
                'slan_4_16': slan_4_16,
                'tt_4_16': tt_4_16,
                'sl_tong': sl_tong,
                'tt_tong': tt_tong,
                'ty_le': self.sum_all() and tt_tong/self.sum_all()*100 or 0,     
            })
        return res
    