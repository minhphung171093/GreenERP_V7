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
            'get_cell_tongdan': self.get_cell_tongdan,
            'get_col': self.get_col,
            'get_ho_row': self.get_ho_row,
            'get_loaivat': self.get_loaivat,
            'get_ngay': self.get_ngay,
            'get_cell_ngoaidien': self.get_cell_ngoaidien,
            'get_cell_miendich': self.get_cell_miendich,
            'get_cell_thuctiem': self.get_cell_thuctiem,
            'convert_datetime':self.convert_datetime,
            'convert_date':self.convert_date,
            'get_ten_vaccine': self.get_ten_vaccine,
            'get_ten_solo': self.get_ten_solo,
            'get_han_su_dung': self.get_han_su_dung,
        })
        
    def convert_datetime(self, date):
        if date:
            date = datetime.strptime(date, DATETIME_FORMAT)
            return date.strftime('%d/%m/%Y %H:%M:%S')  
        
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
                and to_char(name, 'YYYY-MM-DD') >= '%s' and loai_id in %s
                order by name
            '''%(ten_ho_id[0], tu_ngay, tuple(self.get_loaivat()),)
            self.cr.execute(sql)
        elif den_ngay and not tu_ngay:
            sql='''
                select * from tiem_phong_lmlm where ho_chan_nuoi_id = %s 
                and to_char(name, 'YYYY-MM-DD') <= '%s' and loai_id in %s
                order by name
            '''%(ten_ho_id[0], den_ngay, tuple(self.get_loaivat()),)
            self.cr.execute(sql)
        elif den_ngay and tu_ngay:
            sql='''
                select * from tiem_phong_lmlm where ho_chan_nuoi_id = %s 
                and to_char(name, 'YYYY-MM-DD') between '%s' and '%s' and loai_id in %s
                order by name
            '''%(ten_ho_id[0], tu_ngay, den_ngay, tuple(self.get_loaivat()),)
            self.cr.execute(sql)
        else:
            sql='''
                select * from tiem_phong_lmlm where ho_chan_nuoi_id = %s and loai_id in %s
                order by name
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
        
        res.append((0,0,{
                             'loaivat':'Tổng cộng','ct': ''
                            }
                    ))
        return res
    
    def get_cell_tongdan(self,row_id,col,col_tongcong):
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
        if col_tongcong == 'Tổng cộng':
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sum_sl 
                from ct_tiem_phong_lmlm_line where tp_lmlm_id = %s 
            '''%(row_id)
            self.cr.execute(sql)
            soluong = self.cr.dictfetchone()['sum_sl']
        return soluong
    
    def get_cell_ngoaidien(self,row_id,col,col_tongcong):
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
        if col_tongcong == 'Tổng cộng':
            sql = '''
                select case when sum(sl_ngoai_dien)!=0 then sum(sl_ngoai_dien) else 0 end sum_sl_ngoai_dien
                from ct_tiem_phong_lmlm_line where tp_lmlm_id = %s 
            '''%(row_id)
            self.cr.execute(sql)
            soluong = self.cr.dictfetchone()['sum_sl_ngoai_dien']
        return soluong
    
    def get_cell_miendich(self,row_id,col,col_tongcong):
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
        if col_tongcong == 'Tổng cộng':
            sql = '''
                select case when sum(sl_mien_dich)!=0 then sum(sl_mien_dich) else 0 end sum_sl_mien_dich
                from ct_tiem_phong_lmlm_line where tp_lmlm_id = %s 
            '''%(row_id)
            self.cr.execute(sql)
            soluong = self.cr.dictfetchone()['sum_sl_mien_dich']
        return soluong
    
    def get_cell_thuctiem(self,row_id,col,col_tongcong):
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
        if col_tongcong == 'Tổng cộng':
            sql = '''
                select case when sum(sl_thuc_tiem)!=0 then sum(sl_thuc_tiem) else 0 end sum_sl_thuc_tiem
                from ct_tiem_phong_lmlm_line where tp_lmlm_id = %s 
            '''%(row_id)
            self.cr.execute(sql)
            soluong = self.cr.dictfetchone()['sum_sl_thuc_tiem']
        return soluong
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
