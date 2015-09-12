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
            'get_tongcong': self.get_tongcong,
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
        quan_huyen_id = wizard_data['quan_huyen_id']
        phuong_xa_id = wizard_data['phuong_xa_id']
        khu_pho_id = wizard_data['khu_pho_id']
        ten_ho_id = wizard_data['ten_ho_id']
        sql='''
            select ten_ho_id from co_cau where trang_thai = 'new'
            and trang_thai_id in (select id from trang_thai where stt = 3)
            
        '''
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
                         'loaivat':'','ct': u'Cộng ' + loai_vat.name,'ct_id':'' 
                        }
                ))    
            
        return res
    
    def get_tongcong(self, row):
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        soluong = 0
        if row:
            sql = '''
                select case when sum(tong_sl)!=0 then sum(tong_sl) else 0 end tong_sl from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and trang_thai = 'new'
                    and trang_thai_id in (select id from trang_thai where stt = 3))
            '''%(row)
            self.cr.execute(sql)
            test = self.cr.dictfetchone()
            soluong = test and test['tong_sl'] or False
        return soluong
    
    def get_cell(self,row,col,cong):
        context = {}
        soluong = False
        wizard_data = self.localcontext['data']['form']
        if row:
            if col:
                sql = '''
                    select tong_sl from chi_tiet_loai_line
                    where ct_loai_id = %s and co_cau_id in (select id from co_cau where ten_ho_id = %s and trang_thai = 'new' and trang_thai_id in (select id from trang_thai where stt = 3))
                '''%(col, row)
                self.cr.execute(sql)
                tong_sl = self.cr.dictfetchone()
                soluong = tong_sl and tong_sl['tong_sl'] or False
        sql = '''
            select id from loai_vat
        '''
        self.cr.execute(sql)
        loaivat_ids = [r[0] for r in self.cr.fetchall()]
        for loai_vat in self.pool.get('loai.vat').browse(self.cr, self.uid, loaivat_ids):
            if cong == u'Cộng ' + loai_vat.name:
                sql = '''
                    select case when sum(tong_sl)!=0 then sum(tong_sl) else 0 end sl_loai from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and trang_thai = 'new' and chon_loai = %s
                    and trang_thai_id in (select id from trang_thai where stt = 3))
                '''%(row, loai_vat.id)
                self.cr.execute(sql)
                soluong = self.cr.dictfetchone()['sl_loai']
        return soluong
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

