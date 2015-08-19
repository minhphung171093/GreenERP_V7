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
            'get_cocau': self.get_cocau,
            'get_cell': self.get_cell,
            'get_col': self.get_col,
            'get_ho_row': self.get_ho_row,
            'get_tenho':self.get_tenho,
            'get_sum':self.get_sum,
            'get_loaivat': self.get_loaivat,
        })

    def get_tenho(self):
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        ten = self.pool.get('chan.nuoi').browse(self.cr,self.uid,ten_ho_id[0])
        return ten.name
        
    def get_cocau(self):
        return {}

    def get_ho_row(self):
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        tu_ngay = wizard_data['tu_ngay']
        den_ngay = wizard_data['den_ngay']
        if tu_ngay and not den_ngay:
            sql='''
                select ngay_ghi_so from co_cau where ten_ho_id = %s and ngay_ghi_so >= '%s' and ngay_ghi_so is not null and chon_loai in %s
                group by ngay_ghi_so order by ngay_ghi_so
            '''%(ten_ho_id[0], tu_ngay, tuple(self.get_loaivat()),)
            self.cr.execute(sql)
        elif den_ngay and not tu_ngay:
            sql='''
                select ngay_ghi_so from co_cau where ten_ho_id = %s and ngay_ghi_so <= '%s' and ngay_ghi_so is not null and chon_loai in %s
                group by ngay_ghi_so order by ngay_ghi_so
            '''%(ten_ho_id[0], den_ngay, tuple(self.get_loaivat()),)
            self.cr.execute(sql)
        elif den_ngay and tu_ngay:
            sql='''
                select ngay_ghi_so from co_cau where ten_ho_id = %s and ngay_ghi_so between '%s' and '%s' and ngay_ghi_so is not null and chon_loai in %s
                group by ngay_ghi_so order by ngay_ghi_so
            '''%(ten_ho_id[0], tu_ngay, den_ngay, tuple(self.get_loaivat()),)
            self.cr.execute(sql)
        else:
            sql='''
                select ngay_ghi_so from co_cau where ten_ho_id = %s and ngay_ghi_so is not null and chon_loai in %s
                group by ngay_ghi_so order by ngay_ghi_so 
            '''%(ten_ho_id[0], tuple(self.get_loaivat()),)
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
        sum = 0
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        if row:
            sql = '''
                select so_luong from chi_tiet_loai_line 
                where name = '%s' and co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so = '%s')
            '''%(col, ten_ho_id[0], row)
            self.cr.execute(sql)
            test = self.cr.dictfetchone()
            co_sl = test and test['so_luong'] or False
            if co_sl:
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end tong_sl from chi_tiet_loai_line
                        where name = '%s' and co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so <= '%s' and tang_giam = 'a')
                '''%(col, ten_ho_id[0], row)
                self.cr.execute(sql)
                sl = self.cr.dictfetchone()
                soluong_tang = sl and sl['tong_sl'] or False
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end tong_sl_giam from chi_tiet_loai_line
                        where name = '%s' and co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so <= '%s' and tang_giam = 'b')
                '''%(col, ten_ho_id[0], row)
                self.cr.execute(sql)
                sl = self.cr.dictfetchone()
                soluong_giam = sl and sl['tong_sl_giam'] or False
                soluong = soluong_tang - soluong_giam
        return soluong
    
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
    
    def get_sum(self,row):
        context = {}
        soluong = 0
        soluong_tang = 0
        soluong_giam = 0
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        if row:
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so = '%s' and chon_loai = %s)
            '''%(ten_ho_id[0], row, self.get_loaivat()[0])
            self.cr.execute(sql)
            test = self.cr.dictfetchone()
            co_sl = test and test['sl_trong_ngay'] or False
            if co_sl:
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so <= '%s' and chon_loai = %s and tang_giam = 'a')
                '''%(ten_ho_id[0], row, self.get_loaivat()[0])
                self.cr.execute(sql)
                soluong_tang += self.cr.dictfetchone()['sl_trong_ngay']
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay_giam from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so <= '%s' and chon_loai = %s and tang_giam = 'b')
                '''%(ten_ho_id[0], row, self.get_loaivat()[0])
                self.cr.execute(sql)
                soluong_giam += self.cr.dictfetchone()['sl_trong_ngay_giam']
                
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so = '%s' and chon_loai = %s)
            '''%(ten_ho_id[0], row, self.get_loaivat()[1])
            self.cr.execute(sql)
            test = self.cr.dictfetchone()
            co_sl = test and test['sl_trong_ngay'] or False
            if co_sl:
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so <= '%s' and chon_loai = %s and tang_giam = 'a')
                '''%(ten_ho_id[0], row, self.get_loaivat()[1])
                self.cr.execute(sql)
                soluong_tang += self.cr.dictfetchone()['sl_trong_ngay']
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay_giam from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so <= '%s' and chon_loai = %s and tang_giam = 'b')
                '''%(ten_ho_id[0], row, self.get_loaivat()[1])
                self.cr.execute(sql)
                soluong_giam += self.cr.dictfetchone()['sl_trong_ngay_giam']
            
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so = '%s' and chon_loai = %s)
            '''%(ten_ho_id[0], row, self.get_loaivat()[2])
            self.cr.execute(sql)
            test = self.cr.dictfetchone()
            co_sl = test and test['sl_trong_ngay'] or False
            if co_sl:
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so <= '%s' and chon_loai = %s and tang_giam = 'a')
                '''%(ten_ho_id[0], row, self.get_loaivat()[2])
                self.cr.execute(sql)
                soluong_tang += self.cr.dictfetchone()['sl_trong_ngay']
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay_giam from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so <= '%s' and chon_loai = %s and tang_giam = 'b')
                '''%(ten_ho_id[0], row, self.get_loaivat()[2])
                self.cr.execute(sql)
                soluong_giam += self.cr.dictfetchone()['sl_trong_ngay_giam']
            
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so = '%s' and chon_loai = %s)
            '''%(ten_ho_id[0], row, self.get_loaivat()[3])
            self.cr.execute(sql)
            test = self.cr.dictfetchone()
            co_sl = test and test['sl_trong_ngay'] or False
            if co_sl:
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so <= '%s' and chon_loai = %s and tang_giam = 'a')
                '''%(ten_ho_id[0], row, self.get_loaivat()[3])
                self.cr.execute(sql)
                soluong_tang += self.cr.dictfetchone()['sl_trong_ngay']
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay_giam from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so <= '%s' and chon_loai = %s and tang_giam = 'b')
                '''%(ten_ho_id[0], row, self.get_loaivat()[3])
                self.cr.execute(sql)
                soluong_giam += self.cr.dictfetchone()['sl_trong_ngay_giam']
                
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so = '%s' and chon_loai = %s)
            '''%(ten_ho_id[0], row, self.get_loaivat()[4])
            self.cr.execute(sql)
            test = self.cr.dictfetchone()
            co_sl = test and test['sl_trong_ngay'] or False
            if co_sl:
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so <= '%s' and chon_loai = %s and tang_giam = 'a')
                '''%(ten_ho_id[0], row, self.get_loaivat()[4])
                self.cr.execute(sql)
                soluong_tang += self.cr.dictfetchone()['sl_trong_ngay']
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay_giam from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so <= '%s' and chon_loai = %s and tang_giam = 'b')
                '''%(ten_ho_id[0], row, self.get_loaivat()[4])
                self.cr.execute(sql)
                soluong_giam += self.cr.dictfetchone()['sl_trong_ngay_giam']
        soluong = soluong_tang - soluong_giam
        return soluong
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

