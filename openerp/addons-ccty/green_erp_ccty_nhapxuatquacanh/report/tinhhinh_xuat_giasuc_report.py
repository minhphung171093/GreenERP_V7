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
    
    def get_noicap(self, nguon_tinh_thanh_id, nguon_phuong_xa_id, nguon_khu_pho_id, nguon_quan_huyen_id):
        tinh = self.pool.get('tinh.tp').browse(self.cr,self.uid,nguon_tinh_thanh_id).name
        quan = self.pool.get('quan.huyen').browse(self.cr,self.uid,nguon_quan_huyen_id).name
        phuong = self.pool.get('phuong.xa').browse(self.cr,self.uid,nguon_phuong_xa_id).name
        khu_pho = self.pool.get('khu.pho').browse(self.cr,self.uid,nguon_khu_pho_id).name
        return (tinh or '') + ' - ' + (quan or '') + ' - ' + (phuong or '') + ' - ' + (khu_pho or '')

    def get_loaivat(self):
        loaivat = []
        context = {}
        bosua_model, bosua_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'green_erp_ccty_base', 'loaivat_bosua')
        self.pool.get('loai.vat').check_access_rule(self.cr, self.uid, [bosua_id], 'read', context = context)
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
        loaivat = [bosua_id, bota_id, bolai_id, trau_id, de_id, cuu_id]
        return loaivat

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
                and trang_thai_id in (select id from trang_thai where stt = 3)
            '''%(ten_ho_id[0], tu_ngay)
            self.cr.execute(sql)
        elif den_ngay and not tu_ngay:
            sql='''
                select * from nhap_xuat_canh_giasuc 
                where ten_ho_id = %s and ngay_kiem_tra <= '%s' and ngay_kiem_tra is not null and loai = 'xuat'
                and trang_thai_id in (select id from trang_thai where stt = 3)
            '''%(ten_ho_id[0], den_ngay)
            self.cr.execute(sql)
        elif den_ngay and tu_ngay:
            sql='''
                select * from nhap_xuat_canh_giasuc 
                where ten_ho_id = %s and ngay_kiem_tra between '%s' and '%s' and ngay_kiem_tra is not null and loai = 'xuat'
                and trang_thai_id in (select id from trang_thai where stt = 3)
            '''%(ten_ho_id[0], tu_ngay, den_ngay)
            self.cr.execute(sql)
        else:
            sql='''
                select * from nhap_xuat_canh_giasuc 
                where ten_ho_id = %s and ngay_kiem_tra is not null and loai = 'xuat'
                and trang_thai_id in (select id from trang_thai where stt = 3)
            '''%(ten_ho_id[0])
            self.cr.execute(sql)
        tt_ho = self.cr.dictfetchall()
        if tt_ho:
            return tt_ho
        else:
            raise osv.except_osv(_('Warning!'),_('Không có thông tin nhập nào từ hộ %s')%(ho.name))
    
    def get_col(self):
        res = []
        context = {}
        sql = '''
            select id from loai_vat
        '''
        self.cr.execute(sql)
        loaivat_ids = [r[0] for r in self.cr.fetchall()]
        for loai_vat in self.pool.get('loai.vat').browse(self.cr, self.uid, loaivat_ids):
#             seq = 0
            for seq,line in enumerate(loai_vat.chitiet_loaivat):
                if seq == 0:
                    res.append((0,0,{
                                 'loaivat':line.loai_id.name,'ct': line.name,'ct_id': line.id
                                }
                        ))
                else:
                    res.append((0,0,{
                                     'loaivat':'','ct': line.name,'ct_id': line.id
                                    }
                            ))
            
            res.append((0,0,{
                                'loaivat':u'Cộng '+ loai_vat.name,'ct': '','ct_id': ''
                                }
                        ))
            
        return res
    
    def get_cell(self,row,col,nhap_id,loai_id,tong):
        context = {}
        soluong = False
        sum = 0
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        if row:
            if col:
                sql = '''
                    select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong from chi_tiet_loai_nhap_xuat 
                    where ct_loai_id = %s and nhap_xuat_loai_id in (select id from nhap_xuat_canh_giasuc 
                    where ten_ho_id = %s and ngay_kiem_tra = '%s' and id = %s and loai_id = %s and trang_thai_id in (select id from trang_thai where stt = 3))
                '''%(col, ten_ho_id[0], row, nhap_id, loai_id)
                self.cr.execute(sql)
                sl = self.cr.dictfetchone()
                if sl['so_luong']!=0:
                    soluong = sl and sl['so_luong'] or False
                
#             sql = '''
#                 select case when sum(so_luong)!=0 then sum(so_luong) else 0 end so_luong from chi_tiet_da_tiem_phong
#                 where loai_benh_id in (select id from chi_tiet_loai_benh where name = '%s') and nhap_xuat_tiemphong_id in (select id from nhap_xuat_canh_giasuc 
#                 where ten_ho_id = %s and ngay_kiem_tra = '%s' and id = %s and trang_thai_id in (select id from trang_thai where stt = 3))
#             '''%(col, ten_ho_id[0], row, nhap_id)
#             self.cr.execute(sql)
#             sl = self.cr.dictfetchone()
#             if sl['so_luong']!=0:
#                 soluong = sl and sl['so_luong'] or False
                
        sql = '''
            select id from loai_vat
        '''
        self.cr.execute(sql)
        loaivat_ids = [r[0] for r in self.cr.fetchall()]
        for loai_vat in self.pool.get('loai.vat').browse(self.cr, self.uid, loaivat_ids):                
            if tong == u'Cộng '+ loai_vat.name:
                context = {}
                sum = 0
                wizard_data = self.localcontext['data']['form']
                ten_ho_id = wizard_data['ten_ho_id']
                if row:
                    sql = '''
                        select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl from chi_tiet_loai_nhap_xuat 
                        where nhap_xuat_loai_id in (select id from nhap_xuat_canh_giasuc 
                        where ten_ho_id = %s and ngay_kiem_tra = '%s' and id = %s and loai_id = %s and trang_thai_id in (select id from trang_thai where stt = 3))
                    '''%(ten_ho_id[0], row, nhap_id,loai_vat.id)
                    self.cr.execute(sql)
                    soluong = self.cr.dictfetchone()['sl']
        return soluong
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

