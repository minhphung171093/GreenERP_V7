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
        self.tong_ve_cuoiky = 0.0
        
        self.total_dky = 0.0
        self.total_nhan_ky = 0.0
        self.total_ban_ky = 0.0
        self.total_sai_ky = 0.0
        self.total_lh_cuoi = 0.0
        self.total_tien_cuoi = 0.0
        self.total_ve_e = 0.0
        self.localcontext.update({
            'get_date':self.get_date,
            'get_date_from':self.get_date_from,
            'get_date_to':self.get_date_to,
            'get_dai_ly':self.get_dai_ly,
            'get_ky_ve': self.get_ky_ve,
            'get_line_by_product': self.get_line_by_product,
            'get_tong_ve_cuoiky': self.get_tong_ve_cuoiky,
            'get_tong': self.get_tong,
            
            'get_tong_ve_tondauky': self.get_tong_ve_tondauky,
            'get_tong_ve_nhantrongky': self.get_tong_ve_nhantrongky,
            'get_tong_ve_bantrongky': self.get_tong_ve_bantrongky,
            'get_tong_ve_luuhanh': self.get_tong_ve_luuhanh,
            'get_tong_tien': self.get_tong_tien,
            'get_menh_gia': self.get_menh_gia,
        })
    def get_date(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_dai_ly(self):
        wizard_data = self.localcontext['data']['form']
        dai_ly_ids = wizard_data['dai_ly_ids']
        return self.pool.get('res.partner').browse(self.cr, self.uid, dai_ly_ids)
    
    def get_ky_ve(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        sql = '''
            select id from ky_ve where '%s' between start_date and end_date
        '''%(date)
        self.cr.execute(sql)
        kyve = self.cr.dictfetchone()
        if kyve:
            return self.pool.get('ky.ve').browse(self.cr, self.uid, kyve['id'])
        else:
            return False
    
    def get_tong_ve_cuoiky(self):
        tong = self.tong_ve_cuoiky
        self.tong_ve_cuoiky = 0.0
        return tong
    
    def get_tong_ve_tondauky(self):
        return self.tong_ve_tondauky
    def get_tong_ve_nhantrongky(self):
        return self.tong_ve_nhantrongky
    def get_tong_ve_bantrongky(self):
        return self.tong_ve_bantrongky
    def get_tong_ve_luuhanh(self):
        return self.tong_ve_luuhanh
    
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
        return menh_gia_ids
    
    def get_line_by_product(self,dai_ly_id):
        res=[]
        wizard_data = self.localcontext['data']['form']
        menh_gia_ids = wizard_data['menh_gia_ids']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select id from res_partner where id =%s or parent_id=%s
        '''%(dai_ly_id,dai_ly_id)
        self.cr.execute(sql)
        dl_ids = [row[0] for row in self.cr.fetchall()]
        dl_ids = str(dl_ids).replace('[','(')
        dl_ids = str(dl_ids).replace(']',')')
        for line in menh_gia_ids:
            product = self.pool.get('product.product').browse(self.cr, self.uid, line)
            sql='''
                select name, ((select case when sum(product_qty)!=0 then sum(product_qty) else 0 end sl from stock_move where picking_id in (select id from stock_picking where type='out') and product_id = %(product_id)s
                        and date(timezone('UTC',date))<'%(date_from)s' and partner_id in %(dl_ids)s and state='done') - (select case when sum(tong_cong)!=0 then sum(tong_cong) else 0 end sl from ve_loto where product_id=%(product_id)s and ngay<'%(date_from)s' and state='done' and daily_id in %(dl_ids)s)
                                    - (select case when sum(sl)!=0 then sum(sl) else 0 end sl from ve_e_line where product_id=%(product_id)s and ve_e_id in (select id from ve_e where ngay<'%(date_from)s' and state='done' and name in %(dl_ids)s))
                                    - (select case when sum(tong_sai_kythuat)!=0 then sum(tong_sai_kythuat) else 0 end sl from ve_loto where product_id=%(product_id)s and ngay<'%(date_from)s' and state='done' and daily_id in %(dl_ids)s)) dau_ky,
                        (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end sl from stock_move where picking_id in (select id from stock_picking where type='out') and product_id = %(product_id)s
                        and date(timezone('UTC',date)) between '%(date_from)s' and '%(date_to)s' and partner_id in %(dl_ids)s and state='done') nhan_trg_ky,
                        (select case when sum(tong_cong)!=0 then sum(tong_cong) else 0 end sl from ve_loto where product_id=%(product_id)s and ngay between '%(date_from)s' and '%(date_to)s' and state='done' and daily_id in %(dl_ids)s) ban_trg_ky, 
                        (select case when sum(tong_sai_kythuat)!=0 then sum(tong_sai_kythuat) else 0 end sl from ve_loto where product_id=%(product_id)s and ngay between '%(date_from)s' and '%(date_to)s' and state='done' and daily_id in %(dl_ids)s) sai_trg_ky,
                        (select case when sum(sl)!=0 then sum(sl) else 0 end sl from ve_e_line where product_id=%(product_id)s and ve_e_id in (select id from ve_e where ngay between '%(date_from)s' and '%(date_to)s' and state='done' and name in %(dl_ids)s)) e_trg_ky,
                        ((select case when sum(product_qty)!=0 then sum(product_qty) else 0 end sl from stock_move where picking_id in (select id from stock_picking where type='out') and product_id = %(product_id)s
                        and date(timezone('UTC',date))<='%(date_to)s' and partner_id in %(dl_ids)s and state='done') - (select case when sum(tong_cong)!=0 then sum(tong_cong) else 0 end sl from ve_loto where product_id=%(product_id)s and ngay<='%(date_to)s' and state='done' and daily_id in %(dl_ids)s)
                                    - (select case when sum(sl)!=0 then sum(sl) else 0 end sl from ve_e_line where product_id=%(product_id)s and ve_e_id in (select id from ve_e where ngay between '%(date_from)s' and '%(date_to)s' and state='done' and name in %(dl_ids)s))
                                    - (select case when sum(tong_sai_kythuat)!=0 then sum(tong_sai_kythuat) else 0 end sl from ve_loto where product_id=%(product_id)s and ngay<='%(date_to)s' and state='done' and daily_id in %(dl_ids)s)) luu_hanh_cuoi_ky,
                        (((select case when sum(product_qty)!=0 then sum(product_qty) else 0 end sl from stock_move where picking_id in (select id from stock_picking where type='out') and product_id = %(product_id)s
                        and date(timezone('UTC',date))<='%(date_to)s' and partner_id in %(dl_ids)s) - (select case when sum(tong_cong)!=0 then sum(tong_cong) else 0 end sl from ve_loto where product_id=%(product_id)s and ngay<='%(date_to)s' and state='done' and daily_id in %(dl_ids)s)
                                    - (select case when sum(sl)!=0 then sum(sl) else 0 end sl from ve_e_line where product_id=%(product_id)s and ve_e_id in (select id from ve_e where ngay between '%(date_from)s' and '%(date_to)s' and state='done' and name in %(dl_ids)s))
                                    - (select case when sum(tong_sai_kythuat)!=0 then sum(tong_sai_kythuat) else 0 end sl from ve_loto where product_id=%(product_id)s and ngay<='%(date_to)s' and state='done' and daily_id in %(dl_ids)s))*list_price::int) tien_cuoi_ky
                from product_product pp, product_template pt
                where pp.product_tmpl_id=pt.id and pp.id=%(product_id)s
            '''%{
                 'product_id': line,
                 'date_from': date_from,
                 'dl_ids': dl_ids,
                 'date_to': date_to,
            }
            self.cr.execute(sql)
            rs = self.cr.dictfetchone()
            if rs:
                tien_cuoi_ky = (rs['luu_hanh_cuoi_ky'] or 0)*product.list_price
                res.append({
                            'name':rs['name'],
                            'dau_ky':rs['dau_ky'],
                            'nhan_trg_ky':rs['nhan_trg_ky'],
                            'ban_trg_ky':rs['ban_trg_ky'],
                            'sai_trg_ky':rs['sai_trg_ky'],
                            'e_trg_ky':rs['e_trg_ky'],
                            'luu_hanh_cuoi_ky':rs['luu_hanh_cuoi_ky'],
#                             'tien_cuoi_ky':rs['tien_cuoi_ky'],
                            'tien_cuoi_ky':tien_cuoi_ky,
                            })
                self.tong_ve_cuoiky += tien_cuoi_ky#rs['tien_cuoi_ky'] and rs['tien_cuoi_ky'] or 0
            
        return res
    
    def get_tong(self,menh_gia_id):
        res = []
        wizard_data = self.localcontext['data']['form']
        menh_gia_ids = wizard_data['menh_gia_ids']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        dai_ly_ids = wizard_data['dai_ly_ids']
        dai_ly_ids = str(dai_ly_ids).replace('[','(')
        dai_ly_ids = str(dai_ly_ids).replace(']',')')
        sql = '''
            select id from res_partner where id in %s or parent_id in %s
        '''%(dai_ly_ids,dai_ly_ids)
        self.cr.execute(sql)
        dl_ids = [row[0] for row in self.cr.fetchall()]
        dl_ids = str(dl_ids).replace('[','(')
        dl_ids = str(dl_ids).replace(']',')')
        product = self.pool.get('product.product').browse(self.cr, self.uid, menh_gia_id)
        sql='''
                select name, ((select case when sum(product_qty)!=0 then sum(product_qty) else 0 end sl from stock_move where picking_id in (select id from stock_picking where type='out') and product_id = %(product_id)s
                        and date(timezone('UTC',date))<'%(date_from)s' and partner_id in %(dl_ids)s and state='done') - (select case when sum(tong_cong)!=0 then sum(tong_cong) else 0 end sl from ve_loto where product_id=%(product_id)s and ngay<'%(date_from)s' and state='done' and daily_id in %(dl_ids)s)
                                    - - (select case when sum(sl)!=0 then sum(sl) else 0 end sl from ve_e_line where product_id=%(product_id)s and ve_e_id in (select id from ve_e where ngay<'%(date_from)s' and state='done' and name in %(dl_ids)s))
                                    - (select case when sum(tong_sai_kythuat)!=0 then sum(tong_sai_kythuat) else 0 end sl from ve_loto where product_id=%(product_id)s and ngay<'%(date_from)s' and state='done' and daily_id in %(dl_ids)s)) dau_ky,
                        (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end sl  from stock_move where picking_id in (select id from stock_picking where type='out') and product_id = %(product_id)s
                        and date(timezone('UTC',date)) between '%(date_from)s' and '%(date_to)s' and partner_id in %(dl_ids)s and state='done') nhan_trg_ky,
                        (select case when sum(tong_cong)!=0 then sum(tong_cong) else 0 end sl from ve_loto where product_id=%(product_id)s and ngay between '%(date_from)s' and '%(date_to)s' and state='done' and daily_id in %(dl_ids)s) ban_trg_ky, 
                        (select case when sum(tong_sai_kythuat)!=0 then sum(tong_sai_kythuat) else 0 end sl from ve_loto where product_id=%(product_id)s and ngay between '%(date_from)s' and '%(date_to)s' and state='done' and daily_id in %(dl_ids)s) sai_trg_ky,
                        (select case when sum(sl)!=0 then sum(sl) else 0 end sl from ve_e_line where product_id=%(product_id)s and ve_e_id in (select id from ve_e where ngay between '%(date_from)s' and '%(date_to)s' and state='done' and name in %(dl_ids)s)) e_trg_ky,
                        ((select case when sum(product_qty)!=0 then sum(product_qty) else 0 end sl  from stock_move where picking_id in (select id from stock_picking where type='out') and product_id = %(product_id)s
                        and date(timezone('UTC',date))<='%(date_to)s' and partner_id in %(dl_ids)s and state='done') - (select case when sum(tong_cong)!=0 then sum(tong_cong) else 0 end sl from ve_loto where product_id=%(product_id)s and ngay<='%(date_to)s' and state='done' and daily_id in %(dl_ids)s)
                                    - (select case when sum(tong_sai_kythuat)!=0 then sum(tong_sai_kythuat) else 0 end sl from ve_loto where product_id=%(product_id)s and ngay<='%(date_to)s' and state='done' and daily_id in %(dl_ids)s)) luu_hanh_cuoi_ky,
                        (((select case when sum(product_qty)!=0 then sum(product_qty) else 0 end sl  from stock_move where picking_id in (select id from stock_picking where type='out') and product_id = %(product_id)s
                        and date(timezone('UTC',date))<='%(date_to)s' and partner_id in %(dl_ids)s and state='done') - (select case when sum(tong_cong)!=0 then sum(tong_cong) else 0 end sl from ve_loto where product_id=%(product_id)s and ngay<='%(date_to)s' and state='done' and daily_id in %(dl_ids)s)
                                    - (select case when sum(sl)!=0 then sum(sl) else 0 end sl from ve_e_line where product_id=%(product_id)s and ve_e_id in (select id from ve_e where ngay between '%(date_from)s' and '%(date_to)s' and state='done' and name in %(dl_ids)s))
                                    - (select case when sum(tong_sai_kythuat)!=0 then sum(tong_sai_kythuat) else 0 end sl from ve_loto where product_id=%(product_id)s and ngay<='%(date_to)s' and state='done' and daily_id in %(dl_ids)s))*list_price::int) tien_cuoi_ky
                from product_product pp, product_template pt
                where pp.product_tmpl_id=pt.id and pp.id=%(product_id)s
            '''%{
                 'product_id': menh_gia_id,
                 'date_from': date_from,
                 'dl_ids': dl_ids,
                 'date_to': date_to,
            }
        self.cr.execute(sql)
        rs = self.cr.dictfetchone()
        if rs:
            tien_cuoi_ky = (rs['luu_hanh_cuoi_ky'] or 0)*product.list_price
            res.append({
                        'name':rs['name'],
                        'dau_ky':rs['dau_ky'],
                        'nhan_trg_ky':rs['nhan_trg_ky'],
                        'ban_trg_ky':rs['ban_trg_ky'],
                        'sai_trg_ky':rs['sai_trg_ky'],
                        'e_trg_ky':rs['e_trg_ky'],
                        'luu_hanh_cuoi_ky':rs['luu_hanh_cuoi_ky'],
                        'tien_cuoi_ky':tien_cuoi_ky,
                        })
            self.total_dky += rs['dau_ky'] or 0.0
            self.total_nhan_ky += rs['nhan_trg_ky']or 0.0
            self.total_ban_ky += rs['ban_trg_ky'] or 0.0
            self.total_sai_ky += rs['sai_trg_ky'] or 0.0
            self.total_lh_cuoi += rs['luu_hanh_cuoi_ky'] or 0.0
            self.total_tien_cuoi += tien_cuoi_ky or 0.0
            self.total_ve_e += rs['e_trg_ky'] or 0.0
        return res
    
    def get_tong_tien(self):
        res = [{'dau_ky':self.total_dky,
                'nhan_trg_ky':self.total_nhan_ky,
                'ban_trg_ky':self.total_ban_ky,
                'sai_trg_ky':self.total_sai_ky,
                'e_trg_ky':self.total_ve_e,
                'luu_hanh_cuoi_ky':self.total_lh_cuoi,
                'tien_cuoi_ky':self.total_tien_cuoi,}]
        return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
