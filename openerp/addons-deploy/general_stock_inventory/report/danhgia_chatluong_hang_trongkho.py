# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

import time
from report import report_sxw
import pooler
from osv import osv
from tools.translate import _
import random
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.user_obj = pooler.get_pool(self.cr.dbname).get('res.users')
        
        self.localcontext.update({
            'get_tinhtrang':self.get_tinhtrang,
            'get_hd': self.get_hd,
            'get_line_kho': self.get_line_kho,
            'get_line': self.get_line,
            'get_name_kho': self.get_name_kho,
        })
    
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)        
        return date.strftime('%d-%m-%Y')
    
    def get_name_kho(self,kho_id):
        return self.pool.get('stock.location').browse(self.cr, self.uid, kho_id).name
    
    def get_line_kho(self,o):
        sql = '''
            select location_id from stock_inventory_line where inventory_id=%s group by location_id
        '''%(o.id)
        self.cr.execute(sql)
        return [r[0] for r in self.cr.fetchall()]
    
    def get_line(self,location_id,o):
        stock_inventory_line_obj = self.pool.get('stock.inventory.line')
        sql = '''
            select id from stock_inventory_line where inventory_id=%s and location_id=%s
        '''%(o.id,location_id)
        self.cr.execute(sql)
        stock_inventory_line_ids = [r[0] for r in self.cr.fetchall()]
        return stock_inventory_line_obj.browse(self.cr, self.uid, stock_inventory_line_ids)
    
    def get_tinhtrang(self,line):
        if line.khong_dat:
            return u'Không đạt'
        return u'Đạt'
    
    def get_hd(self,prod_lot):
        if prod_lot and prod_lot.life_date:
            date = datetime.strptime(prod_lot.life_date, DATETIME_FORMAT) + timedelta(hours=7)
            return date.strftime('%m/%Y')
        return ''
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
