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
        self.total_start_val = 0.0
        self.total_nhap_val = 0.0
        self.total_xuat_val = 0.0
        self.total_end_val = 0.0
        self.total_start_qty = 0.0
        self.total_nhap_qty = 0.0
        self.total_xuat_qty = 0.0
        self.total_end_qty = 0.0
        self.localcontext.update({
            'get_date':self.get_date,
            'get_date_from':self.get_date_from,
            'get_date_to':self.get_date_to,
            'get_menh_gia':self.get_menh_gia,
            'get_line_by_product': self.get_line_by_product,
            'get_total':self.get_total,
        })
        
    def get_date(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_menh_gia(self):
        wizard_data = self.localcontext['data']['form']
        menh_gia_ids = wizard_data['menh_gia_ids']
        return self.pool.get('product.product').browse(self.cr, self.uid, menh_gia_ids)
    
    def get_line_by_product(self):
        res =[]
        wizard_data = self.localcontext['data']['form']
        menh_gia_ids = wizard_data['menh_gia_ids']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        ky_ve_id = wizard_data['ky_ve_id']
        for line in menh_gia_ids:
            sql = '''
                    select pt.name as name,
                    
                        case when sum(ky.dau_ky)>0 then sum(ky.dau_ky) else 0 end dau_ky,
                        case when sum(ky.dau_ky)>0 then sum(ky.dau_ky)*pt.list_price::int else 0 end tien_dau_ky,
                        
                        case when sum(ky.nhan_trong_ky)>0 then sum(ky.nhan_trong_ky) else 0 end nhan_trong_ky,
                        case when sum(ky.nhan_trong_ky)>0 then sum(ky.nhan_trong_ky)*pt.list_price::int else 0 end tien_nhan_trong_ky,
                        
                        case when sum(ky.xuat_trong_ky)>0 then sum(ky.xuat_trong_ky) else 0 end xuat_trong_ky,
                        case when sum(ky.xuat_trong_ky)>0 then sum(ky.xuat_trong_ky)*pt.list_price::int else 0 end tien_xuat_trong_ky,
                        
                        case when sum(ky.cuoi_ky)>0 then sum(ky.cuoi_ky) else 0 end cuoi_ky,
                        case when sum(ky.cuoi_ky)>0 then sum(ky.cuoi_ky)*pt.list_price else 0 end tien_cuoi_ky
                    from
                        (select product_id,(select case when sum(product_qty)>0 then sum(product_qty) else 0 end sl from stock_move where product_id = %s and state='done' and date(timezone('UTC',date)) < '%s' and picking_id in (select id from stock_picking where type='in' and ky_ve_id=%s)) dau_ky,
                        (select case when sum(product_qty)>0 then sum(product_qty) else 0 end sl from stock_move where product_id = %s and date(timezone('UTC',date)) between '%s' and '%s' and state='done' and picking_id in (select id from stock_picking where type='in' and ky_ve_id=%s)) nhan_trong_ky,
                        (select case when sum(product_qty)>0 then sum(product_qty) else 0 end sl from stock_move where product_id = %s and date(timezone('UTC',date)) between '%s' and '%s' and state='done' and picking_id in (select id from stock_picking where type='out' and ky_ve_id=%s)) xuat_trong_ky,
                        (select case when sum(product_qty)>0 then sum(product_qty) else 0 end sl from stock_move where product_id = %s and state='done' and date(timezone('UTC',date)) <= '%s' and picking_id in (select id from stock_picking where type='in' and ky_ve_id=%s)) cuoi_ky
                            from stock_move where product_id = %s
                        union
                        select product_id,(select case when sum(product_qty)>0 then sum(product_qty)*-1 else 0 end sl from stock_move where product_id = %s and state='done' and date(timezone('UTC',date)) < '%s' and picking_id in (select id from stock_picking where type='out' and ky_ve_id=%s)) dau_ky,
                        0 as nhan_trong_ky,
                        0 as xuat_trong_ky,
                        (select case when sum(product_qty)>0 then sum(product_qty)*-1 else 0 end sl from stock_move where product_id = %s and state='done' and date(timezone('UTC',date)) <= '%s' and picking_id in (select id from stock_picking where type='out' and ky_ve_id=%s)) cuoi_ky
                            from stock_move where product_id = %s) ky, product_product pp ,product_template pt
                    where pp.id = ky.product_id and pp.product_tmpl_id=pt.id and pp.id = %s
                    group by name,pt.list_price
                    '''%(line,date_from,ky_ve_id[0],line,date_from,date_to,ky_ve_id[0],line,date_from,date_to,ky_ve_id[0],line,date_to,ky_ve_id[0],line,line,date_from,ky_ve_id[0],line,date_to,ky_ve_id[0],line,line)
            self.cr.execute(sql)
            rs = self.cr.dictfetchone()
            if rs:
                self.total_start_qty = self.total_start_qty + (rs['dau_ky'] or 0.0)
                self.total_nhap_qty = self.total_nhap_qty +(rs['nhan_trong_ky'] or 0.0)
                self.total_xuat_qty = self.total_xuat_qty +(rs['xuat_trong_ky'] or 0.0)
                self.total_end_qty = self.total_end_qty +(rs['cuoi_ky'] or 0.0)
                
                self.total_start_val = self.total_start_val + (rs['tien_dau_ky'] or 0.0)
                self.total_nhap_val = self.total_nhap_val +(rs['tien_nhan_trong_ky'] or 0.0)
                self.total_xuat_val = self.total_xuat_val +(rs['tien_xuat_trong_ky'] or 0.0)
                self.total_end_val = self.total_end_val +(rs['tien_cuoi_ky'] or 0.0)
                res.append({
                            'name':rs['name'],
                            'dau_ky':rs['dau_ky'],
                            'tien_dau_ky':rs['tien_dau_ky'],
                            'nhan_trong_ky':rs['nhan_trong_ky'],
                            'tien_nhan_trong_ky':rs['tien_nhan_trong_ky'],
                            'xuat_trong_ky':rs['xuat_trong_ky'],
                            'tien_xuat_trong_ky':rs['tien_xuat_trong_ky'],
                            'cuoi_ky':rs['cuoi_ky'],
                            'tien_cuoi_ky':rs['tien_cuoi_ky'],
                            })
        return res
    
    def get_total(self):
        res = [{
                'dau_ky':self.total_start_qty,
                'tien_dau_ky':self.total_start_val,
                'nhan_trong_ky':self.total_nhap_qty,
                'tien_nhan_trong_ky':self.total_nhap_val,
                'xuat_trong_ky':self.total_xuat_qty,
                'tien_xuat_trong_ky':self.total_xuat_val,
                'cuoi_ky':self.total_end_qty,
                'tien_cuoi_ky':self.total_end_val,
               }]
        return res
        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
