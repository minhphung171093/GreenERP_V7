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
            'get_col_loai': self.get_col_loai,
            'get_ho_row': self.get_ho_row,
        })
        
    def get_tenho(self):
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        ten = self.pool.get('chan.nuoi').browse(self.cr,self.uid,ten_ho_id[0])
        return ten.name

    def get_ho_row(self):
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        tu_ngay = wizard_data['tu_ngay']
        den_ngay = wizard_data['den_ngay']
        if tu_ngay and not den_ngay:
            sql='''
                select ngay_ghi_so from co_cau where ten_ho_id = %s and ngay_ghi_so >= '%s' group by ngay_ghi_so order by ngay_ghi_so
            '''%(ten_ho_id[0], tu_ngay)
            self.cr.execute(sql)
        elif den_ngay and not tu_ngay:
            sql='''
                select ngay_ghi_so from co_cau where ten_ho_id = %s and ngay_ghi_so <= '%s' group by ngay_ghi_so order by ngay_ghi_so
            '''%(ten_ho_id[0], den_ngay)
            self.cr.execute(sql)
        elif den_ngay and tu_ngay:
            sql='''
                select ngay_ghi_so from co_cau where ten_ho_id = %s and ngay_ghi_so between '%s' and '%s' group by ngay_ghi_so order by ngay_ghi_so
            '''%(ten_ho_id[0], tu_ngay, den_ngay)
            self.cr.execute(sql)
        else:
            sql='''
                select ngay_ghi_so from co_cau where ten_ho_id = %s group by ngay_ghi_so order by ngay_ghi_so
            '''%(ten_ho_id[0])
            self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_col(self):
        res = []
        context = {}
        bosua_model, bosua_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_bosua')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [bosua_id], 'read', context = context)
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where id = %s)
        '''%(bosua_id)
        self.cr.execute(sql)
        
        for ct in self.cr.dictfetchall():
            res.append((0,0,{
                             'loaivat':'Bò Sữa','ct': ct['name']
                            }
                    ))
        res.append((0,0,{
                             'loaivat':'','ct': 'Cộng bò sữa'
                            }
                    ))    
        
        bota_model, bota_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_bota')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [bota_id], 'read', context = context)
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where id = %s)
        '''%(bota_id)
        self.cr.execute(sql)
        for ct in self.cr.dictfetchall():
            res.append((0,0,{
                             'loaivat':'Bò Ta','ct': ct['name']
                            }
                    ))
        res.append((0,0,{
                             'loaivat':'','ct': 'Cộng bò ta'
                            }
                    ))   
        
        bolai_model, bolai_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_bolai')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [bolai_id], 'read', context = context)
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where id = %s)
        '''%(bolai_id)
        self.cr.execute(sql)
        for ct in self.cr.dictfetchall():
            res.append((0,0,{
                             'loaivat':'Bò lai sind','ct': ct['name']
                            }
                    ))
        res.append((0,0,{
                             'loaivat':'','ct': 'Cộng bò lai sind'
                            }
                    )) 
        trau_model, trau_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_trau')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [trau_id], 'read', context = context)
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where id = %s)
        '''%(trau_id)
        self.cr.execute(sql)
        for ct in self.cr.dictfetchall():
            res.append((0,0,{
                             'loaivat':'Trâu','ct': ct['name']
                            }
                    ))
        res.append((0,0,{
                             'loaivat':'','ct': 'Cộng trâu'
                            }
                    )) 
        
        de_model, de_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_de')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [de_id], 'read', context = context)
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where id = %s)
        '''%(de_id)
        self.cr.execute(sql)
        for ct in self.cr.dictfetchall():
            res.append((0,0,{
                             'loaivat':ct['name'],'ct':''
                            }
                    ))
            
        cuu_model, cuu_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_cuu')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [cuu_id], 'read', context = context)
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where id = %s)
        '''%(cuu_id)
        self.cr.execute(sql)
        for ct in self.cr.dictfetchall():
            res.append((0,0,{
                             'loaivat':ct['name'],'ct':''
                            }
                    ))
        return res
    
    
    
    def get_col_loai(self):
        
        {'loaivat': 'trau',
         'ct': 'duc',
         }
        return [{'loaivat': 'bo sua',},
                {'loaivat': 'bo ta',}
                ]
                
    
#     def get_row(self):
#         
#         return [1,2,3,4,5,6]
    
    def get_cell(self,row,col,loai):
        context = {}
        soluong = 0
        sum = 0
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        if row:
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong from chi_tiet_loai_line 
                where name = '%s' and co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so = '%s')
            '''%(col, ten_ho_id[0], row)
            self.cr.execute(sql)
            sl = self.cr.dictfetchone()
            if sl['so_luong']!=0:
                soluong = sl['so_luong']
            else:
                if col == "Cộng bò sữa":
                    bosua_model, bosua_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_bosua')
                    self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [bosua_id], 'read', context = context)
                    sql = '''
                        select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay from chi_tiet_loai_line where
                        co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so = '%s' and chon_loai = %s)
                    '''%(ten_ho_id[0], row, bosua_id)
                    self.cr.execute(sql)
                    soluong = self.cr.dictfetchone()['sl_trong_ngay']
                if col == "Cộng bò ta":
                    bota_model, bota_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_bota')
                    self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [bota_id], 'read', context = context)
                    sql = '''
                        select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay from chi_tiet_loai_line where
                        co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so = '%s' and chon_loai = %s)
                    '''%(ten_ho_id[0], row, bota_id)
                    self.cr.execute(sql)
                    soluong = self.cr.dictfetchone()['sl_trong_ngay']
                if col == "Cộng bò lai sind":
                    bolai_model, bolai_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_bolai')
                    self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [bolai_id], 'read', context = context)
                    sql = '''
                        select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay from chi_tiet_loai_line where
                        co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so = '%s' and chon_loai = %s)
                    '''%(ten_ho_id[0], row, bolai_id)
                    self.cr.execute(sql)
                    soluong = self.cr.dictfetchone()['sl_trong_ngay']
                if col == "Cộng trâu":
                    trau_model, trau_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_trau')
                    self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [trau_id], 'read', context = context)
                    sql = '''
                        select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay from chi_tiet_loai_line where
                        co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so = '%s' and chon_loai = %s)
                    '''%(ten_ho_id[0], row, trau_id)
                    self.cr.execute(sql)
                    soluong = self.cr.dictfetchone()['sl_trong_ngay']
            if loai == "Dê":
                de_model, de_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_de')
                self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [de_id], 'read', context = context)
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so = '%s' and chon_loai = %s)
                '''%(ten_ho_id[0], row, de_id)
                self.cr.execute(sql)
                soluong = self.cr.dictfetchone()['sl_trong_ngay']
            if loai == "Cừu":
                cuu_model, cuu_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_cuu')
                self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [cuu_id], 'read', context = context)
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_trong_ngay from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so = '%s' and chon_loai = %s)
                '''%(ten_ho_id[0], row, cuu_id)
                self.cr.execute(sql)
                soluong = self.cr.dictfetchone()['sl_trong_ngay']
        return soluong
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

