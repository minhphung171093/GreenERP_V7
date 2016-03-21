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
        
        self.tong_ve_tondauky = 0.0
        self.tong_ve_nhantrongky = 0.0
        self.tong_ve_bantrongky = 0.0
        self.tong_ve_luuhanh = 0.0
        self.tong_tien = 0.0
        self.localcontext.update({
            'get_date':self.get_date,
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
    def get_tong_tien(self):
        return self.tong_tien
    
    def get_line_by_product(self,ky_ve,dai_ly_id):
        wizard_data = self.localcontext['data']['form']
        menh_gia_ids = wizard_data['menh_gia_ids']
        res =[]
        if ky_ve:
            self.cr.execute('''  
            SELECT pp.name_template,pp.id,
                sum(ton_dauky) ton_dauky,
                sum(nhan_trongky) nhan_trongky
                From
                (SELECT
                    stm.product_id,    
                    
                    case when loc1.usage = 'internal' and loc2.usage != 'internal' and stm.date < %s
                    then 1*stm.product_qty 
                    else 0.0
                    end ton_dauky,
                    
                    case when loc1.usage = 'internal' and loc2.usage != 'internal' and stm.date between %s and %s
                    then 1*stm.product_qty 
                    else 0.0
                    end nhan_trongky
                    
                FROM stock_move stm 
                    join stock_location loc1 on stm.location_id=loc1.id
                    join stock_location loc2 on stm.location_dest_id=loc2.id
                WHERE stm.state= 'done' and stm.partner_id in (select id from res_partner where id = %s or parent_id = %s)   )foo
                inner join product_product pp on foo.product_id = pp.id
                WHERE (pp.id in %s)
                group by pp.name_template,pp.id
                order by pp.id
            ''' ,(ky_ve.start_date,ky_ve.start_date,ky_ve.end_date,dai_ly_id,dai_ly_id,
                  tuple(menh_gia_ids),))
            for i in self.cr.dictfetchall():
                sql = '''
                    select sum(tong_cong) tong_cong
                    from ve_loto
                    where ky_ve_id = %s
                        and state='done'
                        and daily_id in (select id from res_partner where id = %s or parent_id = %s)
                        and product_id = %s
                    '''%(ky_ve.id,dai_ly_id,dai_ly_id,i['id'])
                self.cr.execute(sql)
                line = self.cr.dictfetchone()
                ve_cuoiky = (i['ton_dauky'] or 0.0)+(i['nhan_trongky'] or 0.0)-(line['tong_cong'] or 0.0)
                tien_cuoiky = ve_cuoiky*self.pool.get('product.product').browse(self.cr, self.uid, i['id']).standard_price
                self.tong_ve_cuoiky += tien_cuoiky
                
                res.append({
                    'name_template':i['name_template'],
                    'ton_dauky':i['ton_dauky'] or 0.0,
                   'nhan_trongky':i['nhan_trongky'] or 0.0,
                   've_trongky': line['tong_cong'] or 0.0,
                   've_cuoiky': ve_cuoiky,
                   'tien_cuoiky': tien_cuoiky,
                   })
        return res
        
    def get_tong(self,ky_ve):
        wizard_data = self.localcontext['data']['form']
        menh_gia_ids = wizard_data['menh_gia_ids']
        dai_ly_ids = wizard_data['dai_ly_ids']
        res =[]
        if ky_ve:
            self.cr.execute('''  
            SELECT pp.name_template,pp.id,
                sum(ton_dauky) ton_dauky,
                sum(nhan_trongky) nhan_trongky
                From
                (SELECT
                    stm.product_id,    
                    
                    case when loc1.usage = 'internal' and loc2.usage != 'internal' and stm.date < %s
                    then 1*stm.product_qty 
                    else 0.0
                    end ton_dauky,
                    
                    case when loc1.usage = 'internal' and loc2.usage != 'internal' and stm.date between %s and %s
                    then 1*stm.product_qty 
                    else 0.0
                    end nhan_trongky
                    
                FROM stock_move stm 
                    join stock_location loc1 on stm.location_id=loc1.id
                    join stock_location loc2 on stm.location_dest_id=loc2.id
                WHERE stm.state= 'done' and stm.partner_id in (select id from res_partner where id in %s or parent_id in %s)   )foo
                inner join product_product pp on foo.product_id = pp.id
                WHERE (pp.id in %s)
                group by pp.name_template,pp.id
                order by pp.id
            ''',(ky_ve.start_date,ky_ve.start_date,ky_ve.end_date,tuple(dai_ly_ids),tuple(dai_ly_ids),
                  tuple(menh_gia_ids),))
            for i in self.cr.dictfetchall():
                self.cr.execute('''
                    select sum(tong_cong) tong_cong
                    from ve_loto
                    where ngay between %s and %s
                        and state='done'
                        and daily_id in (select id from res_partner where id in %s or parent_id in %s)
                        and product_id = %s
                    ''',(ky_ve.start_date,ky_ve.end_date,tuple(dai_ly_ids),tuple(dai_ly_ids),i['id'],))
                line = self.cr.dictfetchone()
                ve_cuoiky = (i['ton_dauky'] or 0.0)+(i['nhan_trongky'] or 0.0)-(line['tong_cong'] or 0.0)
                tien_cuoiky = ve_cuoiky*self.pool.get('product.product').browse(self.cr, self.uid, i['id']).standard_price
                self.tong_ve_cuoiky += tien_cuoiky
                
                self.tong_ve_tondauky += (i['ton_dauky'] or 0.0)
                self.tong_ve_nhantrongky += (i['nhan_trongky'] or 0.0)
                self.tong_ve_bantrongky += (line['tong_cong'] or 0.0)
                self.tong_ve_luuhanh += ve_cuoiky
                self.tong_tien += tien_cuoiky
                
                res.append({
                    'name_template':i['name_template'],
                    'ton_dauky':i['ton_dauky'] or 0.0,
                   'nhan_trongky':i['nhan_trongky'] or 0.0,
                   've_trongky': line['tong_cong'] or 0.0,
                   've_cuoiky': ve_cuoiky,
                   'tien_cuoiky': tien_cuoiky,
                   })
        return res
    
    def get_line_by_product(self,dai_ly_id):
        res=[]
        wizard_data = self.localcontext['data']['form']
        menh_gia_ids = wizard_data['menh_gia_ids']
        sql = '''
            select id from res_partner where id =%s or parent_id=%s
        '''%(dai_ly_id,dai_ly_id)
        self.cr.execute(sql)
        dl_ids = [row[0] for row in self.cr.fetchall()]
        for line in menh_gia_ids:
            ddd
            
        return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
