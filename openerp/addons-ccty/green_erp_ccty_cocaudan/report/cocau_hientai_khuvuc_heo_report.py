# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
            'get_tenho': self.get_tenho,
            'get_cell': self.get_cell,
            'get_col': self.get_col,
            'get_ho_row': self.get_ho_row,
            'get_loaivat': self.get_loaivat,
            'convert_date':self.convert_date,
            'get_sum': self.get_sum,
        })

    def convert_date(self, ten_ho_id):
        sql = '''
            select ngay_ghi_so from co_cau where ten_ho_id = %s and trang_thai_id in (select id from trang_thai where stt = 3)
            group by ngay_ghi_so
            order by ngay_ghi_so desc
        '''%(ten_ho_id)
        self.cr.execute(sql)
        date = self.cr.dictfetchone()['ngay_ghi_so']
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
        
    def get_tenho(self,ten_ho_id):
        ten = self.pool.get('chan.nuoi').browse(self.cr,self.uid,ten_ho_id)
        return ten.name
    
    def get_loaivat(self):
        loaivat = []
        context = {}
        duc_lamviec_model, duc_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_duc_lammviec')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [duc_id], 'read', context = context)
        heo_haubi_model, heo_haubi_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_heo_haubi')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [heo_haubi_id], 'read', context = context)
        nai_sinhsan_model, sinhsan_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_nai_sinhsan')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [sinhsan_id], 'read', context = context)
        heo_con_model, heo_con_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_heo_con')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [heo_con_id], 'read', context = context)
        heo_thit_model, thit_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_heo_thit')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [thit_id], 'read', context = context)
        loaivat = [duc_id, heo_haubi_id, sinhsan_id, heo_con_id, thit_id]
        return loaivat

    def get_ho_row(self):
        wizard_data = self.localcontext['data']['form']
        quan_huyen_id = wizard_data['quan_huyen_id']
        phuong_xa_id = wizard_data['phuong_xa_id']
        khu_pho_id = wizard_data['khu_pho_id']
        ten_ho_id = wizard_data['ten_ho_id']
        sql='''
            select ten_ho_id from co_cau where trang_thai = 'new' and chon_loai in %s
            and trang_thai_id in (select id from trang_thai where stt = 3)
            
        '''%(tuple(self.get_loaivat()),)
        if quan_huyen_id:
            sql+='''
                and quan_huyen_id = %s
            '''%(quan_huyen_id[0])
        if quan_huyen_id and phuong_xa_id:
            sql+='''
                and quan_huyen_id = %s and phuong_xa_id = %s
            '''%(quan_huyen_id[0],phuong_xa_id[0])
        if quan_huyen_id and phuong_xa_id and khu_pho_id:
            sql+='''
                and quan_huyen_id = %s and phuong_xa_id = %s and khu_pho_id = %s
            '''%(quan_huyen_id[0],phuong_xa_id[0], khu_pho_id[0])
        if quan_huyen_id and phuong_xa_id and khu_pho_id and ten_ho_id:
            sql+='''
                and quan_huyen_id = %s and phuong_xa_id = %s and khu_pho_id = %s and ten_ho_id = %s
            '''%(quan_huyen_id[0],phuong_xa_id[0], khu_pho_id[0], ten_ho_id[0])
        sql+='''
             group by ten_ho_id
            order by ten_ho_id 
        '''
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_col(self):
        res = []
        context = {}
        duc_lamviec_model, duc_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_duc_lammviec')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [duc_id], 'read', context = context)
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where id = %s)
        '''%(duc_id)
        self.cr.execute(sql)
        for ct in self.cr.dictfetchall():
            res.append((0,0,{
                             'loaivat':ct['name'],'ct':ct['name']
                            }
                    ))
        
        
        heo_haubi_model, heo_haubi_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_heo_haubi')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [heo_haubi_id], 'read', context = context)
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where id = %s)
        '''%(heo_haubi_id)
        self.cr.execute(sql)
        
        for seq,ct in enumerate(self.cr.dictfetchall()):
            if seq == 0:
                res.append((0,0,{
                                 'loaivat':'Heo hậu bị','ct': ct['name']
                                }
                        ))
            else:
                res.append((0,0,{
                                 'loaivat':'','ct': ct['name']
                                }
                        ))
        
        nai_sinhsan_model, sinhsan_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_nai_sinhsan')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [sinhsan_id], 'read', context = context)
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where id = %s)
        '''%(sinhsan_id)
        self.cr.execute(sql)
        for seq,ct in enumerate(self.cr.dictfetchall()):
            if seq == 0:
                res.append((0,0,{
                                 'loaivat':'Nái sinh sản','ct': ct['name']
                                }
                        ))
            else:
                res.append((0,0,{
                                 'loaivat':'','ct': ct['name']
                                }
                        ))
        
        heo_con_model, heo_con_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_heo_con')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [heo_con_id], 'read', context = context)
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where id = %s)
        '''%(heo_con_id)
        self.cr.execute(sql)
        for seq,ct in enumerate(self.cr.dictfetchall()):
            if seq == 0:
                res.append((0,0,{
                                 'loaivat':'Heo con','ct': ct['name']
                                }
                        ))
            else:
                res.append((0,0,{
                                 'loaivat':'','ct': ct['name']
                                }
                        ))
        heo_thit_model, thit_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_heo_thit')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [thit_id], 'read', context = context)
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where id = %s)
        '''%(thit_id)
        self.cr.execute(sql)
        for ct in self.cr.dictfetchall():
            res.append((0,0,{
                             'loaivat':ct['name'],'ct': ct['name']
                            }
                    ))
        return res
    
    def get_cell(self,row,col):
        context = {}
        soluong = False
        sum_bosua = 0
        sum_bota = 0
        wizard_data = self.localcontext['data']['form']
        if row:
            co_sl = False
            sql = '''
                select tong_sl from chi_tiet_loai_line
                where name = '%s' and co_cau_id in (select id from co_cau where ten_ho_id = %s and trang_thai = 'new' and trang_thai_id in (select id from trang_thai where stt = 3))
            '''%(col, row)
            self.cr.execute(sql)
            tong_sl = self.cr.dictfetchone()
            soluong = tong_sl and tong_sl['tong_sl'] or False
        return soluong
    
    def get_sum(self,row):
        context = {}
        soluong = 0
        soluong_tang = 0
        soluong_giam = 0
        wizard_data = self.localcontext['data']['form']
        if row:
            sql = '''
                select case when sum(tong_sl)!=0 then sum(tong_sl) else 0 end sl_heo from chi_tiet_loai_line where
                co_cau_id in (select id from co_cau where ten_ho_id = %s and chon_loai in %s and trang_thai = 'new'
                and trang_thai_id in (select id from trang_thai where stt = 3))
            '''%(row, tuple(self.get_loaivat()),)
            self.cr.execute(sql)
            sl_heo = self.cr.dictfetchone()
            soluong = sl_heo and sl_heo['sl_heo'] or False
        return soluong
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

