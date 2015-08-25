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
            'get_noicap': self.get_noicap,
            'get_loaivat': self.get_loaivat,
            'convert_date':self.convert_date,
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')  
        
    def get_tenho(self):
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        ten = self.pool.get('chan.nuoi').browse(self.cr,self.uid,ten_ho_id[0])
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
    
    def get_noicap(self, tram_id):
        return self.pool.get('tram.thu.y').browse(self.cr,self.uid,tram_id).name

    def get_ho_row(self):
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        tu_ngay = wizard_data['tu_ngay']
        den_ngay = wizard_data['den_ngay']
        ho = self.pool.get('chan.nuoi').browse(self.cr,self.uid,ten_ho_id[0])
        if tu_ngay and not den_ngay:
            sql='''
                select * from nhap_xuat_canh_giasuc 
                where ten_ho_id = %s and ngay_kiem_tra >= '%s' and ngay_kiem_tra is not null and loai = 'xuat'
                and loai_id in %s and trang_thai_id in (select id from trang_thai where stt = 3)
            '''%(ten_ho_id[0], tu_ngay, tuple(self.get_loaivat()),)
            self.cr.execute(sql)
        elif den_ngay and not tu_ngay:
            sql='''
                select * from nhap_xuat_canh_giasuc 
                where ten_ho_id = %s and ngay_kiem_tra <= '%s' and ngay_kiem_tra is not null and loai = 'xuat'
                and loai_id in %s and trang_thai_id in (select id from trang_thai where stt = 3)
            '''%(ten_ho_id[0], den_ngay, tuple(self.get_loaivat()),)
            self.cr.execute(sql)
        elif den_ngay and tu_ngay:
            sql='''
                select * from nhap_xuat_canh_giasuc 
                where ten_ho_id = %s and ngay_kiem_tra between '%s' and '%s' and ngay_kiem_tra is not null and loai = 'xuat'
                and loai_id in %s and trang_thai_id in (select id from trang_thai where stt = 3)
            '''%(ten_ho_id[0], tu_ngay, den_ngay, tuple(self.get_loaivat()),)
            self.cr.execute(sql)
        else:
            sql='''
                select * from nhap_xuat_canh_giasuc 
                where ten_ho_id = %s and ngay_kiem_tra is not null and loai = 'xuat'
                and loai_id in %s and trang_thai_id in (select id from trang_thai where stt = 3)
            '''%(ten_ho_id[0], tuple(self.get_loaivat()),)
            self.cr.execute(sql)
        tt_ho = self.cr.dictfetchall()
        if tt_ho:
            return tt_ho
        else:
            raise osv.except_osv(_('Warning!'),_('Không có thông tin nhập nào từ hộ %s')%(ho.name))
    
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
                                 'loaivat':u'Heo hậu bị','ct': ct['name']
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
                                 'loaivat':u'Nái sinh sản','ct': ct['name']
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
                                 'loaivat':u'Heo con','ct': ct['name']
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
                             'loaivat':u'Tổng cộng','ct': ''
                            }
                    ))
            
        sql = '''
            select * from chi_tiet_loai_benh where loai_id in (select id from loai_vat where id = %s)
        '''%(thit_id)
        self.cr.execute(sql)
        for seq,ct in enumerate(self.cr.dictfetchall()):
            if seq == 0:
                res.append((0,0,{
                                 'loaivat':u'ĐÃ TIÊM PHÒNG','ct': ct['name']
                                }
                        ))
            else:
                res.append((0,0,{
                                 'loaivat':'','ct': ct['name']
                                }
                        ))
        return res
    
    def get_cell(self,row,col,so_giay,loai):
        context = {}
        soluong = False
        sum = 0
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        if row:
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong from chi_tiet_loai_nhap_xuat 
                where name = '%s' and nhap_xuat_loai_id in (select id from nhap_xuat_canh_giasuc 
                where ten_ho_id = %s and ngay_kiem_tra = '%s' and name = '%s' and trang_thai_id in (select id from trang_thai where stt = 3))
            '''%(col, ten_ho_id[0], row, so_giay)
            self.cr.execute(sql)
            sl = self.cr.dictfetchone()
            if sl['so_luong']!=0:
                soluong = sl and sl['so_luong'] or False
                
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong from chi_tiet_da_tiem_phong
                where name = '%s' and nhap_xuat_tiemphong_id in (select id from nhap_xuat_canh_giasuc 
                where ten_ho_id = %s and ngay_kiem_tra = '%s' and name = '%s' and trang_thai_id in (select id from trang_thai where stt = 3))
            '''%(col, ten_ho_id[0], row, so_giay)
            self.cr.execute(sql)
            sl = self.cr.dictfetchone()
            if sl['so_luong']!=0:
                soluong = sl and sl['so_luong'] or False
                
            if loai == "Tổng cộng":
                context = {}
                sum = 0
                wizard_data = self.localcontext['data']['form']
                ten_ho_id = wizard_data['ten_ho_id']
                if row:
                    sql = '''
                        select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl from chi_tiet_loai_nhap_xuat 
                        where nhap_xuat_loai_id in (select id from nhap_xuat_canh_giasuc 
                        where ten_ho_id = %s and ngay_kiem_tra = '%s' and name = '%s' and loai_id in %s and trang_thai_id in (select id from trang_thai where stt = 3))
                    '''%(ten_ho_id[0], row, so_giay, tuple(self.get_loaivat()),)
                    self.cr.execute(sql)
                    soluong = self.cr.dictfetchone()['sl']
        return soluong
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

