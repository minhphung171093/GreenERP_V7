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
import datetime

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_tenho': self.get_tenho,
            'get_cell_tongdan': self.get_cell_tongdan,
            'get_col': self.get_col,
            'get_ho_row': self.get_ho_row,
            'get_loaivat': self.get_loaivat,
            'get_ngay': self.get_ngay,
            'get_cell_ngoaidien': self.get_cell_ngoaidien,
            'get_cell_miendich': self.get_cell_miendich,
            'get_cell_thuctiem': self.get_cell_thuctiem,
            'convert_date':self.convert_date,
            'convert_datetime': self.convert_datetime,
            'get_ten_vaccine': self.get_ten_vaccine,
            'get_ten_solo': self.get_ten_solo,
            'get_han_su_dung': self.get_han_su_dung,
        })
        
    def convert_datetime(self, date):
        if date:
            date_time = datetime.datetime.strptime(date, DATETIME_FORMAT) + timedelta(hours=7)
            return date_time.strftime('%d/%m/%Y %H:%M:%S')  
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')  
        
    def get_ten_vaccine(self, loai_vaccine_id):
        if loai_vaccine_id:
            return self.pool.get('loai.vacxin').browse(self.cr,self.uid,loai_vaccine_id).name
        
    def get_ten_solo(self, so_lo_id):
        if so_lo_id:
            return self.pool.get('so.lo').browse(self.cr,self.uid,so_lo_id).name
        
    def get_han_su_dung(self, lmlm_id):
        if lmlm_id:
            return self.pool.get('tiem.phong.lmlm').browse(self.cr,self.uid,lmlm_id).han_su_dung_rel
        
        
    def get_tenho(self):
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        ten = self.pool.get('chan.nuoi').browse(self.cr,self.uid,ten_ho_id[0])
        return ten.name
    
    def get_ngay(self, tp_lmlm_id):
        lmlm_ids = []
        lmlm = self.pool.get('tiem.phong.lmlm').browse(self.cr,self.uid,tp_lmlm_id)
        lmlm_ids = [lmlm.name, lmlm.loai_vaccine_id.name, lmlm.so_lo_id.name, lmlm.han_su_dung_rel]
        return lmlm_ids
    
    
    def get_loaivat(self):
        loaivat = []
        context = {}
        bota_model, bota_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_bota')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [bota_id], 'read', context = context)
        bolai_model, bolai_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_bolai')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [bolai_id], 'read', context = context)
        trau_model, trau_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_trau')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [trau_id], 'read', context = context)
        de_model, de_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_de')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [de_id], 'read', context = context)
        cuu_model, cuu_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_cuu')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [cuu_id], 'read', context = context)
        loaivat = [bota_id, bolai_id, trau_id, de_id, cuu_id]
        return loaivat

#     def get_ho_row(self):
#         wizard_data = self.localcontext['data']['form']
#         ten_ho_id = wizard_data['ten_ho_id']
#         tu_ngay = wizard_data['tu_ngay']
#         den_ngay = wizard_data['den_ngay']
#         if tu_ngay and not den_ngay:
#             sql='''
#                 select * from ct_tiem_phong_lmlm_line where tp_lmlm_id in (select id from tiem_phong_lmlm 
#                 where ho_chan_nuoi_id = %s and to_char(name, 'YYYY-MM-DD') >= '%s' and loai_id in %s) and so_luong !=0
#             '''%(ten_ho_id[0], tu_ngay, tuple(self.get_loaivat()),)
#             self.cr.execute(sql)
#         elif den_ngay and not tu_ngay:
#             sql='''
#                 select * from ct_tiem_phong_lmlm_line where tp_lmlm_id in (select id from tiem_phong_lmlm 
#                 where ho_chan_nuoi_id = %s and to_char(name, 'YYYY-MM-DD') <= '%s' and loai_id in %s) and so_luong !=0
#             '''%(ten_ho_id[0], den_ngay, tuple(self.get_loaivat()),)
#             self.cr.execute(sql)
#         elif den_ngay and tu_ngay:
#             sql='''
#                 select * from ct_tiem_phong_lmlm_line where tp_lmlm_id in (select id from tiem_phong_lmlm 
#                 where ho_chan_nuoi_id = %s and to_char(name, 'YYYY-MM-DD') between '%s' and '%s' and loai_id in %s) and so_luong !=0
#             '''%(ten_ho_id[0], tu_ngay, den_ngay, tuple(self.get_loaivat()),)
#             self.cr.execute(sql)
#         else:
#             sql='''
#                 select * from ct_tiem_phong_lmlm_line where tp_lmlm_id in (select id from tiem_phong_lmlm 
#                 where ho_chan_nuoi_id = %s and loai_id in %s) and so_luong !=0
#                 
#             '''%(ten_ho_id[0], tuple(self.get_loaivat()),)
#             self.cr.execute(sql)
#         return self.cr.dictfetchall()
    
    def get_ho_row(self):
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        tu_ngay = wizard_data['tu_ngay']
        den_ngay = wizard_data['den_ngay']
        if tu_ngay and not den_ngay:
            sql='''
                select * from tiem_phong_lmlm where ho_chan_nuoi_id = %s 
                and to_char(name, 'YYYY-MM-DD') >= '%s' and loai_id in %s and trang_thai_id in (select id from trang_thai where stt = 3)
                order by name
            '''%(ten_ho_id[0], tu_ngay, tuple(self.get_loaivat()),)
            self.cr.execute(sql)
        elif den_ngay and not tu_ngay:
            sql='''
                select * from tiem_phong_lmlm where ho_chan_nuoi_id = %s 
                and to_char(name, 'YYYY-MM-DD') <= '%s' and loai_id in %s and trang_thai_id in (select id from trang_thai where stt = 3)
                order by name
            '''%(ten_ho_id[0], den_ngay, tuple(self.get_loaivat()),)
            self.cr.execute(sql)
        elif den_ngay and tu_ngay:
            sql='''
                select * from tiem_phong_lmlm where ho_chan_nuoi_id = %s 
                and to_char(name, 'YYYY-MM-DD') between '%s' and '%s' and loai_id in %s and trang_thai_id in (select id from trang_thai where stt = 3)
                order by name
            '''%(ten_ho_id[0], tu_ngay, den_ngay, tuple(self.get_loaivat()),)
            self.cr.execute(sql)
        else:
            sql='''
                select * from tiem_phong_lmlm where ho_chan_nuoi_id = %s and loai_id in %s and trang_thai_id in (select id from trang_thai where stt = 3)
                order by name
            '''%(ten_ho_id[0], tuple(self.get_loaivat()),)
            self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_col(self):
        res = []
        context = {}
        bota_model, bota_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_bota')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [bota_id], 'read', context = context)
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where id = %s)
        '''%(bota_id)
        self.cr.execute(sql)
        for seq,ct in enumerate(self.cr.dictfetchall()):
            if seq == 0:
                res.append((0,0,{
                                 'loaivat':'Bò Ta','ct': ct['name']
                                }
                        ))
            else:
                res.append((0,0,{
                                 'loaivat':'','ct': ct['name']
                                }
                        ))
        
        bolai_model, bolai_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_bolai')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [bolai_id], 'read', context = context)
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where id = %s)
        '''%(bolai_id)
        self.cr.execute(sql)
        for seq,ct in enumerate(self.cr.dictfetchall()):
            if seq == 0:
                res.append((0,0,{
                                 'loaivat':'Bò lai sind','ct': ct['name']
                                }
                        ))
            else:
                res.append((0,0,{
                                 'loaivat':'','ct': ct['name']
                                }
                        ))
        trau_model, trau_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_trau')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [trau_id], 'read', context = context)
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where id = %s)
        '''%(trau_id)
        self.cr.execute(sql)
        for seq,ct in enumerate(self.cr.dictfetchall()):
            if seq == 0:
                res.append((0,0,{
                                 'loaivat':'Trâu','ct': ct['name']
                                }
                        ))
            else:
                res.append((0,0,{
                                 'loaivat':'','ct': ct['name']
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
                             'loaivat':ct['name'],'ct':ct['name']
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
                             'loaivat':ct['name'],'ct':ct['name']
                            }
                    ))
        return res
    
    def get_cell_tongdan(self,row_id,col):
        context = {}
        soluong = False
        sum = 0
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        sql = '''
            select so_luong from ct_tiem_phong_lmlm_line where name = '%s' and tp_lmlm_id = %s 
        '''%(col, row_id)
        self.cr.execute(sql)
        sl = self.cr.dictfetchone()
        if sl:
            soluong = sl and sl['so_luong'] or False
        return soluong
    
    def get_cell_ngoaidien(self,row_id,col):
        context = {}
        soluong = False
        sum = 0
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        sql = '''
            select sl_ngoai_dien from ct_tiem_phong_lmlm_line where name = '%s' and tp_lmlm_id = %s 
        '''%(col, row_id)
        self.cr.execute(sql)
        sl = self.cr.dictfetchone()
        if sl:
            soluong = sl and sl['sl_ngoai_dien'] or False
        return soluong
    
    def get_cell_miendich(self,row_id,col):
        context = {}
        soluong = False
        sum = 0
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        sql = '''
            select sl_mien_dich from ct_tiem_phong_lmlm_line where name = '%s' and tp_lmlm_id = %s 
        '''%(col, row_id)
        self.cr.execute(sql)
        sl = self.cr.dictfetchone()
        if sl:
            soluong = sl and sl['sl_mien_dich'] or False
        return soluong
    
    def get_cell_thuctiem(self,row_id,col):
        context = {}
        soluong = False
        sum = 0
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        sql = '''
            select sl_thuc_tiem from ct_tiem_phong_lmlm_line where name = '%s' and tp_lmlm_id = %s 
        '''%(col, row_id)
        self.cr.execute(sql)
        sl = self.cr.dictfetchone()
        if sl:
            soluong = sl and sl['sl_thuc_tiem'] or False
        return soluong
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

