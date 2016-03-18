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
            'get_menh_gia':self.get_menh_gia,
            'get_ky_ve': self.get_ky_ve,
            'get_line_by_product': self.get_line_by_product,
            'get_total_start_val':self.get_total_start_val,
            'get_total_nhap_val':self.get_total_nhap_val,
            'get_total_xuat_val':self.get_total_xuat_val,
            'get_total_end_val':self.get_total_end_val,
            'get_total_start_qty':self.get_total_start_qty,
            'get_total_nhap_qty':self.get_total_nhap_qty,
            'get_total_xuat_qty':self.get_total_xuat_qty,
            'get_total_end_qty':self.get_total_end_qty,
        })
    def get_date(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_menh_gia(self):
        wizard_data = self.localcontext['data']['form']
        menh_gia_ids = wizard_data['menh_gia_ids']
        return self.pool.get('product.product').browse(self.cr, self.uid, menh_gia_ids)
    
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
    
    def get_total_start_val(self):
        return self.total_start_val
    def get_total_nhap_val(self):
        return self.total_nhap_val
    def get_total_xuat_val(self):
        return self.total_xuat_val
    def get_total_end_val(self):
        return self.total_end_val
    
    def get_total_start_qty(self):
        return self.total_start_qty
    def get_total_nhap_qty(self):
        return self.total_nhap_qty
    def get_total_xuat_qty(self):
        return self.total_xuat_qty
    def get_total_end_qty(self):
        return self.total_end_qty
    
    def get_line_by_product(self,ky_ve):
        wizard_data = self.localcontext['data']['form']
        menh_gia_ids = wizard_data['menh_gia_ids']
        res =[]
        if ky_ve:
            self.cr.execute('''  
            SELECT pp.name_template,sum(start_onhand_qty) start_onhand_qty, sum(start_val) start_val, 
                sum(nhaptk_qty) nhaptk_qty, sum(nhaptk_val) nhaptk_val,
                sum(xuattk_qty) xuattk_qty, sum(xuattk_val) xuattk_val,    
                sum(end_onhand_qty) end_onhand_qty,
                sum(end_val) end_val
                From
                (SELECT
                    stm.product_id,stm.product_uom,    
                    case when loc1.usage != 'internal' and loc2.usage = 'internal' and stm.date < %s
                    then stm.product_qty
                    else
                    case when loc1.usage = 'internal' and loc2.usage != 'internal' and stm.date < %s
                    then -1*stm.product_qty 
                    else 0.0 end
                    end start_onhand_qty,
                    
                    case when loc1.usage != 'internal' and loc2.usage = 'internal' and stm.date < %s
                    then (stm.price_unit * stm.product_qty)
                    else
                    case when loc1.usage = 'internal' and loc2.usage != 'internal' and stm.date < %s
                    then -1*(stm.price_unit * stm.product_qty)
                    else 0.0 end
                    end start_val,
                    
                    case when loc1.usage != 'internal' and loc2.usage = 'internal' and stm.date between %s and %s
                    then stm.product_qty
                    else 0.0 end nhaptk_qty,
                    
                    case when loc1.usage = 'internal' and loc2.usage != 'internal' and stm.date between %s and %s
                    then 1*stm.product_qty 
                    else 0.0
                    end xuattk_qty,
            
                    case when loc1.usage != 'internal' and loc2.usage = 'internal' and stm.date between %s and %s
                    then (stm.price_unit * stm.product_qty)
                    else 0.0 end nhaptk_val,
                    
                    case when loc1.usage = 'internal' and loc2.usage != 'internal' and stm.date between %s and %s
                    then 1*(stm.price_unit * stm.product_qty)
                    else 0.0
                    end xuattk_val,        
                     
                    case when loc1.usage != 'internal' and loc2.usage = 'internal' and stm.date < %s
                    then stm.product_qty
                    else
                    case when loc1.usage = 'internal' and loc2.usage != 'internal' and stm.date < %s
                    then -1*stm.product_qty 
                    else 0.0 end
                    end end_onhand_qty,
                    
                    case when loc1.usage != 'internal' and loc2.usage = 'internal' and stm.date < %s
                    then (stm.price_unit * stm.product_qty)
                    else
                    case when loc1.usage = 'internal' and loc2.usage != 'internal' and stm.date < %s
                    then -1*(stm.price_unit * stm.product_qty)
                    else 0.0 end
                    end end_val            
                FROM stock_move stm 
                    join stock_location loc1 on stm.location_id=loc1.id
                    join stock_location loc2 on stm.location_dest_id=loc2.id
                WHERE stm.state= 'done'    )foo
                inner join product_product pp on foo.product_id = pp.id
                inner join product_uom pu on foo.product_uom = pu.id
                WHERE (pp.id in %s)
                group by pp.name_template
            
            ''',(ky_ve.start_date,ky_ve.start_date,ky_ve.start_date,ky_ve.start_date,
                  ky_ve.start_date,ky_ve.end_date,ky_ve.start_date,ky_ve.end_date,ky_ve.start_date,ky_ve.end_date,ky_ve.start_date,ky_ve.end_date,
                  ky_ve.end_date,ky_ve.end_date,ky_ve.end_date,ky_ve.end_date,
                  tuple(menh_gia_ids),))
            for i in self.cr.dictfetchall():
                self.total_start_qty = self.total_start_qty + (i['start_onhand_qty'] or 0)
                self.total_nhap_qty = self.total_nhap_qty +(i['nhaptk_qty'] or 0.0)
                self.total_xuat_qty = self.total_xuat_qty +(i['xuattk_qty'] or 0.0)
                self.total_end_qty = self.total_end_qty +(i['end_onhand_qty'] or 0.0)
                
                self.total_start_val = self.total_start_val + (i['start_val'] or 0)
                self.total_nhap_val = self.total_nhap_val +(i['nhaptk_val'] or 0.0)
                self.total_xuat_val = self.total_xuat_val +(i['xuattk_val'] or 0.0)
                self.total_end_val = self.total_end_val +(i['end_val'] or 0.0)
                res.append({
                    'name_template':i['name_template'],
                   'start_onhand_qty':i['start_onhand_qty'] or 0.0,
                   'start_val':i['start_val'] or 0.0,
                   'nhaptk_qty':i['nhaptk_qty'] or 0.0,
                   'nhaptk_val':i['nhaptk_val'] or 0.0,
                   'xuattk_qty':i['xuattk_qty'] or 0.0,
                   'xuattk_val':i['xuattk_val'] or 0.0,
                   'end_onhand_qty':i['end_onhand_qty'] or 0.0,
                   'end_val':i['end_val'] or 0.0
                   })
        return res
    
    def get_line_by_product(self,ky_ve):
        res =[]
#         wizard_data = self.localcontext['data']['form']
#         menh_gia_ids = wizard_data['menh_gia_ids']
#         for line in menh_gia_ids:
#             cr.execute('''
#                         select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from
#                             (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl
#                             
#                             
#                             
#                             
#                             
#                             st.product_qty
#                                 from stock_move st
#                                 where st.state='done' and st.product_id=%s and st.location_dest_id = %s and prodlot_id = %s
#                                 and st.picking_id not in %s
#                             union all
#                             select st.product_qty*-1
#                                 from stock_move st
#                                 where st.state='done' and st.product_id=%s and st.location_id = %s and prodlot_id = %s
#                                 and st.picking_id not in %s
#                             )foo
#                         ''',(move_line['product_id'],picking.location_id.id,move_line['prodlot_id'] or 'null',tuple(ids),move_line['product_id'],picking.location_id.id,move_line['prodlot_id'] or 'null',tuple(ids)),)
        return res
        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
