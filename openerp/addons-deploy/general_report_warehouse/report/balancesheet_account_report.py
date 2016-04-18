# -*- coding: utf-8 -*-
##############################################################################
#
#    HLVSolution, Open Source Management Solution
#
##############################################################################

import time
from report import report_sxw
import pooler
from osv import osv
from tools.translate import _
import random
from datetime import datetime
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.shop_ids =False
        self.shop_name =False
        self.category_ids = False
        self.category_name = False
        
        self.product_id = False
        self.start_date = False
        self.date_end = False
        self.short_by = False
        self.company_name = False
        self.company_address = False
        self.location_id = False
        self.total_start_val = 0.0
        self.total_nhap_val = 0.0
        self.total_xuat_val = 0.0
        self.total_end_val = 0.0
        self.get_company(cr, uid)
        
        self.localcontext.update({
            'get_company_name':self.get_company_name,
            'get_company_address':self.get_company_address,
            'get_date_start':self.get_date_start,
            'get_date_end':self.get_date_end,
            'get_total_start_val':self.get_total_start_val,
            'get_total_nhap_val':self.get_total_nhap_val,
            'get_total_xuat_val':self.get_total_xuat_val,
            'get_total_end_val':self.get_total_end_val,
            'get_line_by_product':self.get_line_by_product,
            'get_current_date':self.get_current_date,
            'get_warehouse_name':self.get_warehouse_name,
            'get_category_name':self.get_category_name,
            'get_line_category':self.get_line_category,
            'get_line_product_by_categ':self.get_line_product_by_categ,
            'get_uom_name':self.get_uom_name,
            'check_cate': self.check_cate,
        })
    
    
    def get_current_date(self):
        date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_total_start_val(self):
        return self.total_start_val
    def get_total_nhap_val(self):
        return self.total_nhap_val
    def get_total_xuat_val(self):
        return self.total_xuat_val
    def get_total_end_val(self):
        return self.total_end_val
    
    def get_company(self,cr,uid):
        user_obj = self.pool.get('res.users').browse(cr,uid,uid)
        self.company_name = user_obj and user_obj.company_id and user_obj.company_id.name or ''
        self.company_address = user_obj and user_obj.company_id and user_obj.company_id.street or ''
        self.vat = user_obj and user_obj.company_id and user_obj.company_id.vat or ''
         
    def get_company_name(self):
        return self.company_name
    def get_company_address(self):
        return self.company_address 
    
    def get_date_start(self):
        if not self.start_date:
            self.get_header()
        return self.get_vietname_date(self.start_date)
    
    def get_date_end(self):
        if not self.date_end:
            self.get_header()
        return self.get_vietname_date(self.date_end)
    
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_warehouse_name(self):
        if not self.shop_name:
            self.get_header()
        return self.shop_name 
    
    
    def get_category_name(self):
        return self.category_name 
    
    
    def get_header(self):
        wizard_data = self.localcontext['data']['form']
        self.shop_ids = wizard_data['shop_ids'] 
        shop_obj = self.pool.get('sale.shop').browse(self.cr,self.uid,self.shop_ids)
        self.shop_name = shop_obj and shop_obj[0].name or False
        self.shop_ids = (','.join(map(str, self.shop_ids)))
        self.short_by = wizard_data['short_by'] and wizard_data['short_by'] or False
        self.start_date = wizard_data['date_start']
        self.date_end = wizard_data['date_end']
        self.location_id = wizard_data['location_id'] and wizard_data['location_id'][0] or False
        self.category_ids = wizard_data['categ_ids'] or False
        if self.category_ids:
            #self.category_ids = self.pool.get('product.category').search(self.cr, self.uid, [('id','child_of',self.category_ids)])
            self.category_ids = (','.join(map(str, self.category_ids)))
        return True
    
    def get_line_category(self):
        sql = False
        if self.category_ids:
            sql ='''
                SELECT name,id FROM product_category 
                WHERE id in (%s)
                order by name
            '''%(self.category_ids)
        else:
            sql ='''
                SELECT name,id FROM product_category 
                order by name
            '''
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_line_product_by_categ(self):
        sql = False
        cate_ids = []
        location_model, location_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'stock', 'stock_location_customers')
        self.pool.get('stock.location').check_access_rule(self.cr, self.uid, [location_id], 'read')
        if self.category_ids:
            sql ='''
                SELECT name,id FROM product_category 
                WHERE id in (%s)
                order by name
            '''%(self.category_ids)
        else:
            sql ='''
                SELECT name,id FROM product_category where parent_id in (select id from product_category where code = 'HH')
                order by name
            '''
        self.cr.execute(sql)
        for cate_parent in self.cr.dictfetchall():
            ds_cateson_ids = []
            parent_total_ton_dau_sl = 0
            parent_total_ton_dau_gt = 0
            parent_total_nhap_sl = 0
            parent_total_nhap_gt = 0
            parent_total_xuat_sl = 0
            parent_total_xuat_gt = 0
            parent_total_ton_cuoi_sl = 0
            parent_total_ton_cuoi_gt = 0
            sql ='''
                SELECT name,id FROM product_category where parent_id = %s
                order by name
            '''%(cate_parent['id'])
            self.cr.execute(sql)
            for cate_son in self.cr.dictfetchall():
                sql = '''
                    select id from stock_move where state = 'done' and (picking_id is not null or id in (select move_id from stock_inventory_move_rel)) 
                    and product_id in (select id from product_product where product_tmpl_id in (select id from product_template where categ_id = %s))
                    and date(timezone('UTC',date::timestamp)) between '%s' and '%s'
                '''%(cate_son['id'], self.start_date, self.date_end)
                self.cr.execute(sql)
                cate_id = self.cr.dictfetchall()
                if cate_id:
                    product_ids = []
                    total_ton_dau_sl = 0
                    total_ton_dau_gt = 0
                    total_nhap_sl = 0
                    total_nhap_gt = 0
                    total_xuat_sl = 0
                    total_xuat_gt = 0
                    total_ton_cuoi_sl = 0
                    total_ton_cuoi_gt = 0
                    
                    sql ='''  
                        SELECT pp.id,pp.default_code, pp.name_template,sum(start_onhand_qty) start_onhand_qty, round(sum(start_val)) start_val, 
                            sum(nhaptk_qty) nhaptk_qty, round(sum(nhaptk_val)) nhaptk_val,
                            sum(xuattk_qty) xuattk_qty, round(sum(xuattk_val)) xuattk_val,    
                            sum(end_onhand_qty) end_onhand_qty,
                            round(sum(end_val)) end_val
                            From
                            (SELECT
                                stm.product_id,stm.product_uom,    
                                case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
                                then stm.primary_qty
                                else
                                case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
                                then -1*stm.primary_qty 
                                else 0.0 end
                                end start_onhand_qty,
                                
                                case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
                                then round(stm.price_unit * stm.product_qty)
                                else
                                case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
                                then -1*(stm.price_unit * stm.product_qty)
                                else 0.0 end
                                end start_val,
                                
                                case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
                                and ai.state in ('open','paid')
                                then stm.primary_qty
                                else 0.0 end nhaptk_qty,
                                
                                case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
                                and ai.state in ('open','paid') then round(stm.price_unit * stm.product_qty)
                                else 0.0 end nhaptk_val,
                                
                                case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
                                and ai.state in ('open','paid')
                                then 1*stm.primary_qty 
                                else 0.0
                                end xuattk_qty,
                        
                                
                                case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
                                and ai.state in ('open','paid') then 1*(stm.price_unit * stm.product_qty)
                                else 0.0
                                end xuattk_val,        
                                 
                                case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
                                and ai.state in ('open','paid')
                                then stm.primary_qty
                                else
                                case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
                                and ai.state in ('open','paid')    
                                then -1*stm.primary_qty 
                                else 0.0 end
                                end end_onhand_qty,
                                
                                case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
                                and ai.state in ('open','paid')
                                then round(stm.price_unit * stm.product_qty)
                                else
                                case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
                                and ai.state in ('open','paid')
                                then -1*(stm.price_unit * stm.product_qty)
                                else 0.0 end
                                end end_val            
                            FROM stock_move stm 
                                join stock_location loc1 on stm.location_id=loc1.id
                                join stock_location loc2 on stm.location_dest_id=loc2.id
                                left join account_invoice_line ail on ail.source_id=stm.id
                                left join account_invoice ai on ai.id=ail.invoice_id
                            WHERE stm.state= 'done' and stm.id in (select move_id from stock_inventory_move_rel)
                            
                            UNION ALL
                        
                            SELECT
                                stm.product_id,stm.product_uom,    
                                case when ai.type in ('in_invoice','out_refund') and rel_invoice_id is null 
                                and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
                                then ail.quantity
                                else
                                case when ai.type in ('out_refund') and rel_invoice_id is not null 
                                and date(timezone('UTC',ai.ngay_nhap::timestamp)) < '%(start_date)s'
                                then ail.quantity
                                else
                                case when ai.type in ('out_invoice','in_refund') and rel_invoice_id is null 
                                and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
                                then -1*ail.quantity 
                                else
                                case when ai.type in ('out_invoice') and rel_invoice_id is not null 
                                and date(timezone('UTC',ai.date_invoice::timestamp)) < '%(start_date)s'
                                then -1*ail.quantity 
                                else 0.0 end end end
                                end start_onhand_qty,
                                
                                case when ai.type in ('in_invoice','out_refund') and rel_invoice_id is null 
                                and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
                                then round(stm.price_unit * ail.quantity)
                                else
                                case when ai.type in ('out_refund') and rel_invoice_id is not null 
                                and date(timezone('UTC',ai.ngay_nhap::timestamp)) < '%(start_date)s'
                                then round(stm.price_unit * ail.quantity)
                                else
                                case when ai.type in ('out_invoice','in_refund')
                                and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
                                then -1*round(stm.price_unit * ail.quantity)
                                else
                                case when ai.type in ('out_invoice') and rel_invoice_id is not null 
                                and date(timezone('UTC',ai.date_invoice::timestamp)) < '%(start_date)s'
                                then -1*round(stm.price_unit * ail.quantity)
                                else 0.0 end end end
                                end start_val,
                                
                                case when ai.type in ('in_invoice','out_refund') and rel_invoice_id is null 
                                and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
                                then ail.quantity
                                else 
                                case when ai.type = 'out_refund' and rel_invoice_id is not null 
                                and date(timezone('UTC',ai.ngay_nhap::timestamp)) between '%(start_date)s' and '%(end_date)s' 
                                then ail.quantity
                                else 0 end
                                end nhaptk_qty,
                                
                                case when ai.type in ('out_invoice','in_refund') and rel_invoice_id is null 
                                and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
                                then 1*ail.quantity 
                                else
                                case when ai.type in ('out_invoice') and rel_invoice_id is not null 
                                and date(timezone('UTC',ai.date_invoice::timestamp)) between '%(start_date)s' and '%(end_date)s'
                                then 1*ail.quantity 
                                else 0.0 end
                                end xuattk_qty,
                        
                                case when ai.type in ('in_invoice','out_refund') and rel_invoice_id is null 
                                and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
                                then round(stm.price_unit * ail.quantity)
                                else 
                                case when ai.type = 'out_refund' and rel_invoice_id is not null 
                                and date(timezone('UTC',ai.ngay_nhap::timestamp)) between '%(start_date)s' and '%(end_date)s' 
                                then round(stm.price_unit * ail.quantity)
                                else 0.0 end
                                end nhaptk_val,
                                
                                case when ai.type in ('out_invoice','in_refund') and rel_invoice_id is null 
                                and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
                                then 1*round(stm.price_unit * ail.quantity)
                                else
                                case when ai.type in ('out_invoice') and rel_invoice_id is not null 
                                and date(timezone('UTC',ai.date_invoice::timestamp)) between '%(start_date)s' and '%(end_date)s'
                                then 1*round(stm.price_unit * ail.quantity)
                                else 0.0 end
                                end xuattk_val,        
                                 
                                case when date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
                                and ai.type in ('in_invoice','out_refund')
                                then ail.quantity
                                else
                                case when date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
                                and ai.type in ('out_invoice','in_refund')
                                then -1*ail.quantity
                                else 0.0 end
                                end end_onhand_qty,
                                
                                case when date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
                                and ai.type in ('in_invoice','out_refund')
                                then round(stm.price_unit * ail.quantity)
                                else
                                case when date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
                                and ai.type in ('out_invoice','in_refund')
                                then -1*round(stm.price_unit * ail.quantity)
                                else 0.0 end
                                end end_val            
                            FROM stock_move stm 
                                left join stock_location loc1 on stm.location_id=loc1.id
                                left join stock_location loc2 on stm.location_dest_id=loc2.id
                                left join account_invoice_line ail on ail.source_id=stm.id
                                left join account_invoice ai on ai.id=ail.invoice_id
                                left join stock_picking sp on sp.id=stm.picking_id
                            WHERE stm.state= 'done' and stm.picking_id is not null  
                            and ail.source_id is not null and ai.state in ('open','paid')
                               
                            )foo
                            inner join product_product pp on foo.product_id = pp.id
                            inner join product_uom pu on foo.product_uom = pu.id
                            inner join  (
                                    SELECT pt.id from  product_template pt inner join product_category pc on pt.categ_id = pc.id
                                        where pc.id in ('%(categ_ids)s')
                            )categ on pp.product_tmpl_id = categ.id
                            WHERE (pp.id in (select product_id  from product_shop_rel where shop_id in('%(shop_ids)s'))
                                   or pp.id not in (select product_id  from product_shop_rel))
                            group by pp.default_code,pp.name_template,pp.id
                            order by pp.default_code,pp.name_template,pp.id
                        '''%({
                          'start_date': self.start_date,
                          'end_date': self.date_end,
                          'shop_ids':self.shop_ids,
                          'categ_ids':cate_son['id'],
                          'cus_stock':location_id,
                          }) 
                        
                    self.cr.execute(sql)
                    
                    res =[]
                
                    for seq,line in enumerate(self.cr.dictfetchall()):
                        self.total_start_val = self.total_start_val + (line['start_val'] or 0)
                        self.total_nhap_val = self.total_nhap_val +(line['nhaptk_val'] or 0.0)
                        self.total_xuat_val = self.total_xuat_val +(line['xuattk_val'] or 0.0)
                        self.total_end_val = self.total_end_val +(line['end_val'] or 0.0)
                        
                        sql ='''
                            SELECT sum(ail.quantity) as qty_hoantien, sum(ail.quantity*sm.price_unit) as total_hoantien
                                FROM
                                    account_invoice_line ail left join account_invoice ai on ail.invoice_id = ai.id
                                    left join stock_move sm on ail.source_id = sm.id
                                WHERE 
                                    ail.product_id = %s and ai.type = 'out_refund'
                                    and date(timezone('UTC',ai.date_invoice)) between '%s' and '%s'
                                    and ai.state not in ('draft','cancel')
                        '''%(line['id'],self.start_date,self.date_end)
                        self.cr.execute(sql)
                        nhap_ht_res = self.cr.fetchone()
                        line['nhaptk_qty'] += nhap_ht_res and nhap_ht_res[0] or 0
                        line['nhaptk_val'] += nhap_ht_res and nhap_ht_res[1] or 0
                        
                        sql ='''
                            SELECT sum(ail.quantity) qty_dieuchinh, sum(ail.quantity*sm.price_unit) as total_dieuchinh
                                FROM
                                    account_invoice_line ail left join account_invoice ai on ail.invoice_id = ai.id
                                    left join stock_move sm on ail.source_id = sm.id 
                                WHERE 
                                    ail.product_id = %s and ai.type = 'out_invoice'
                                    and ai.rel_invoice_id is not null
                                    and date(timezone('UTC',ai.date_invoice)) between '%s' and '%s'
                                    and ai.state not in ('draft','cancel')
                        '''%(line['id'],self.start_date,self.date_end)
                        self.cr.execute(sql)
                        xuat_dc_res = self.cr.fetchone()
                        line['xuattk_qty'] += xuat_dc_res and xuat_dc_res[0] or 0
                        line['xuattk_val'] += xuat_dc_res and xuat_dc_res[1] or 0
                        
                        product_ids.append({
                                            'stt': seq+1,
                                            'product_name': line['name_template'] or '',
                                            'dvt': self.get_uom_name(line['default_code']),
                                            'ton_dau_sl': line['start_onhand_qty'] or 0.0,
                                            'ton_dau_gt': line['start_onhand_qty'] and line['start_val'] or 0.0,
                                            'nhap_sl': line['nhaptk_qty'] or 0.0,
                                            'nhap_gt': line['nhaptk_val'] or 0.0,
                                            'xuat_sl': line['xuattk_qty'] or 0.0,
                                            'xuat_gt': line['xuattk_val'] or 0.0,
                                            'ton_cuoi_sl': line['end_onhand_qty'] or 0.0,
                                            'ton_cuoi_gt': line['end_onhand_qty'] and line['end_val'] or 0.0,
                                            })
                    
                        total_ton_dau_sl += line['start_onhand_qty']
                        total_ton_dau_gt += line['start_val']
                        total_nhap_sl += line['nhaptk_qty']
                        total_nhap_gt += line['nhaptk_val']
                        total_xuat_sl += line['xuattk_qty']
                        total_xuat_gt += line['xuattk_val']
                        total_ton_cuoi_sl += line['end_onhand_qty']
                        total_ton_cuoi_gt += line['end_val']
                        
                    ds_cateson_ids.append({
                                'stt': cate_son['name'],
                                'product_name': '', 
                                'dvt': '',
                                'ton_dau_sl': total_ton_dau_sl,
                                'ton_dau_gt': total_ton_dau_gt,
                                'nhap_sl': total_nhap_sl,
                                'nhap_gt': total_nhap_gt,
                                'xuat_sl': total_xuat_sl,
                                'xuat_gt': total_xuat_gt,
                                'ton_cuoi_sl': total_ton_cuoi_sl,
                                'ton_cuoi_gt': total_ton_cuoi_gt,
                                      
                                      })
                    for pro in product_ids:
                        ds_cateson_ids.append({
                                    'stt': pro['stt'],
                                    'product_name': pro['product_name'], 
                                    'dvt': pro['dvt'],
                                    'ton_dau_sl': pro['ton_dau_sl'],
                                    'ton_dau_gt': pro['ton_dau_gt'],
                                    'nhap_sl': pro['nhap_sl'],
                                    'nhap_gt': pro['nhap_gt'],
                                    'xuat_sl': pro['xuat_sl'],
                                    'xuat_gt': pro['xuat_gt'],
                                    'ton_cuoi_sl': pro['ton_cuoi_sl'],
                                    'ton_cuoi_gt': pro['ton_cuoi_gt'],
                                         })
                        
                    parent_total_ton_dau_sl += total_ton_dau_sl
                    parent_total_ton_dau_gt += total_ton_dau_gt
                    parent_total_nhap_sl += total_nhap_sl
                    parent_total_nhap_gt += total_nhap_gt
                    parent_total_xuat_sl += total_xuat_sl
                    parent_total_xuat_gt += total_xuat_gt
                    parent_total_ton_cuoi_sl += total_ton_cuoi_sl
                    parent_total_ton_cuoi_gt += total_ton_cuoi_gt
            if ds_cateson_ids:        
                cate_ids.append({
                            'stt': cate_parent['name'],
                            'product_name': '', 
                            'dvt': '',
                            'ton_dau_sl': parent_total_ton_dau_sl,
                            'ton_dau_gt': parent_total_ton_dau_gt,
                            'nhap_sl': parent_total_nhap_sl,
                            'nhap_gt': parent_total_nhap_gt,
                            'xuat_sl': parent_total_xuat_sl,
                            'xuat_gt': parent_total_xuat_gt,
                            'ton_cuoi_sl': parent_total_ton_cuoi_sl,
                            'ton_cuoi_gt': parent_total_ton_cuoi_gt,
                                 })
                        
                for cateson in ds_cateson_ids:
                    cate_ids.append({
                                'stt': cateson['stt'],
                                'product_name': cateson['product_name'], 
                                'dvt': cateson['dvt'],
                                'ton_dau_sl': cateson['ton_dau_sl'],
                                'ton_dau_gt': cateson['ton_dau_gt'],
                                'nhap_sl': cateson['nhap_sl'],
                                'nhap_gt': cateson['nhap_gt'],
                                'xuat_sl': cateson['xuat_sl'],
                                'xuat_gt': cateson['xuat_gt'],
                                'ton_cuoi_sl': cateson['ton_cuoi_sl'],
                                'ton_cuoi_gt': cateson['ton_cuoi_gt'],
                                     })
                            
#                     cate_ids.append({
#                                     'stt': cate_son['name'],
#                                     'product_name': '', 
#                                     'dvt': '',
#                                     'ton_dau_sl': total_ton_dau_sl,
#                                     'ton_dau_gt': total_ton_dau_gt,
#                                     'nhap_sl': total_nhap_sl,
#                                     'nhap_gt': total_nhap_gt,
#                                     'xuat_sl': total_xuat_sl,
#                                     'xuat_gt': total_xuat_gt,
#                                     'ton_cuoi_sl': total_ton_cuoi_sl,
#                                     'ton_cuoi_gt': total_ton_cuoi_gt,
#                                          })
#                     for pro in product_ids:
#                         cate_ids.append({
#                                     'stt': pro['stt'],
#                                     'product_name': pro['product_name'], 
#                                     'dvt': pro['dvt'],
#                                     'ton_dau_sl': pro['ton_dau_sl'],
#                                     'ton_dau_gt': pro['ton_dau_gt'],
#                                     'nhap_sl': pro['nhap_sl'],
#                                     'nhap_gt': pro['nhap_gt'],
#                                     'xuat_sl': pro['xuat_sl'],
#                                     'xuat_gt': pro['xuat_gt'],
#                                     'ton_cuoi_sl': pro['ton_cuoi_sl'],
#                                     'ton_cuoi_gt': pro['ton_cuoi_gt'],
#                                          })
                
                
                
#                 cate_ids.append({
#                                 'stt': cate_parent['name'],
#                                 'product_name': '', 
#                                 'dvt': '',
#                                 'ton_dau_sl': parent_total_ton_dau_sl,
#                                 'ton_dau_gt': parent_total_ton_dau_gt,
#                                 'nhap_sl': parent_total_nhap_sl,
#                                 'nhap_gt': parent_total_nhap_gt,
#                                 'xuat_sl': parent_total_xuat_sl,
#                                 'xuat_gt': parent_total_xuat_gt,
#                                 'ton_cuoi_sl': parent_total_ton_cuoi_sl,
#                                 'ton_cuoi_gt': parent_total_ton_cuoi_gt,
#                                      })
                
        return cate_ids
                    
    
    def check_cate(self,cate_id):
        sql = False
        cate_ids = []
#         sql ='''  
#                 SELECT pp.id,pp.default_code, pp.name_template,sum(start_onhand_qty) start_onhand_qty, round(sum(start_val)) start_val, 
#                     sum(nhaptk_qty) nhaptk_qty, round(sum(nhaptk_val)) nhaptk_val,
#                     sum(xuattk_qty) xuattk_qty, round(sum(xuattk_val)) xuattk_val,    
#                     sum(end_onhand_qty) end_onhand_qty,
#                     round(sum(end_val)) end_val
#                     From
#                     (SELECT
#                         stm.product_id,stm.product_uom,    
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
#                         then stm.primary_qty
#                         else
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
#                         then -1*stm.primary_qty 
#                         else 0.0 end
#                         end start_onhand_qty,
#                         
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
#                         then (stm.price_unit * stm.product_qty)
#                         else
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
#                         then -1*(stm.price_unit * stm.product_qty)
#                         else 0.0 end
#                         end start_val,
#                         
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
#                         then stm.primary_qty
#                         else 0.0 end nhaptk_qty,
#                         
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
#                         then 1*stm.primary_qty 
#                         else 0.0
#                         end xuattk_qty,
#                 
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
#                         then round(stm.price_unit * stm.product_qty)
#                         else 0.0 end nhaptk_val,
#                         
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
#                         then 1*(stm.price_unit * stm.product_qty)
#                         else 0.0
#                         end xuattk_val,        
#                          
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
#                         then stm.primary_qty
#                         else
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
#                         then -1*stm.primary_qty 
#                         else 0.0 end
#                         end end_onhand_qty,
#                         
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
#                         then round(stm.price_unit * stm.product_qty)
#                         else
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
#                         then -1*(stm.price_unit * stm.product_qty)
#                         else 0.0 end
#                         end end_val            
#                     FROM stock_move stm 
#                         join stock_location loc1 on stm.location_id=loc1.id
#                         join stock_location loc2 on stm.location_dest_id=loc2.id
#                     WHERE stm.state= 'done' and (stm.picking_id is not null or stm.id in (select move_id from stock_inventory_move_rel))   )foo
#                     inner join product_product pp on foo.product_id = pp.id
#                     inner join product_uom pu on foo.product_uom = pu.id
#                     inner join  (
#                             SELECT pt.id from  product_template pt inner join product_category pc on pt.categ_id = pc.id
#                                 where pc.id in ('%(categ_ids)s')
#                     )categ on pp.product_tmpl_id = categ.id
#                     WHERE (pp.id in (select product_id  from product_shop_rel where shop_id in('%(shop_ids)s'))
#                            or pp.id not in (select product_id  from product_shop_rel))
#                     group by pp.default_code,pp.name_template,pp.id
#                     order by pp.default_code,pp.name_template,pp.id
#                 '''%({
#                   'start_date': self.start_date,
#                   'end_date': self.date_end,
#                   'shop_ids':self.shop_ids,
#                   'categ_ids':cate_id
#                   }) 

        sql = '''
            select id from stock_move where state = 'done' and (picking_id is not null or id in (select move_id from stock_inventory_move_rel)) 
            and product_id in (select id from product_product where product_tmpl_id in (select id from product_template where categ_id = %s))
        '''%(cate_id)
        self.cr.execute(sql)
        cate_ids = self.cr.dictfetchall()
        if cate_ids:
            return 'co'
        else:
            return 'khong'
    
    def get_uom_name(self,name):
        sql='''
            SELECT pu.name 
            FROM product_template pt inner join product_uom pu on pt.uom_id = pu.id
            inner join product_product pp on pp.id = pt.id
            WHERE pp.default_code= '%s'
        ''' %(name)
        self.cr.execute(sql)
        for i in self.cr.dictfetchall():
            return i['name']
        return ''
    
#     def get_line_product_by_categ(self,category_id):
#         
#         if self.location_id:
#             sql ='''  
#                 SELECT pp.id,pp.default_code, pp.name_template,sum(start_onhand_qty) start_onhand_qty, sum(start_val) start_val, 
#                     sum(nhaptk_qty) nhaptk_qty, sum(nhaptk_val) nhaptk_val,
#                     sum(xuattk_qty) xuattk_qty, sum(xuattk_val) xuattk_val,    
#                     sum(end_onhand_qty) end_onhand_qty,
#                     sum(end_val) end_val
#                     From
#                     (SELECT
#                         stm.product_id,stm.product_uom,    
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
#                         then stm.primary_qty
#                         else
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
#                         then -1*stm.primary_qty 
#                         else 0.0 end
#                         end start_onhand_qty,
#                         
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
#                         then (stm.price_unit * stm.product_qty)
#                         else
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
#                         then -1*(stm.price_unit * stm.product_qty)
#                         else 0.0 end
#                         end start_val,
#                         
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
#                         then stm.primary_qty
#                         else 0.0 end nhaptk_qty,
#                         
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
#                         then 1*stm.primary_qty 
#                         else 0.0
#                         end xuattk_qty,
#                 
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
#                         then (stm.price_unit * stm.product_qty)
#                         else 0.0 end nhaptk_val,
#                         
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
#                         then 1*(stm.price_unit * stm.product_qty)
#                         else 0.0
#                         end xuattk_val,        
#                          
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
#                         then stm.primary_qty
#                         else
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
#                         then -1*stm.primary_qty 
#                         else 0.0 end
#                         end end_onhand_qty,
#                         
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
#                         then (stm.price_unit * stm.product_qty)
#                         else
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
#                         then -1*(stm.price_unit * stm.product_qty)
#                         else 0.0 end
#                         end end_val            
#                     FROM stock_move stm 
#                         join stock_location loc1 on stm.location_id=loc1.id
#                         join stock_location loc2 on stm.location_dest_id=loc2.id
#                     WHERE stm.state= 'done')foo
#                     inner join product_product pp on foo.product_id = pp.id
#                     inner join product_uom pu on foo.product_uom = pu.id
#                     inner join  (
#                             SELECT pt.id from  product_template pt inner join product_category pc on pt.categ_id = pc.id
#                                 where pc.id in ('%(categ_ids)s')
#                     )categ on pp.product_tmpl_id = categ.id
#                     WHERE (pp.id in (select product_id  from product_shop_rel where shop_id in('%(shop_ids)s'))
#                            or pp.id not in (select product_id  from product_shop_rel))
#                     group by pp.default_code,pp.name_template,pp.id
#                     order by pp.default_code,pp.name_template,pp.id
#                 
#                  '''%({
#                   'start_date': self.start_date,
#                   'end_date': self.date_end,
#                   'shop_ids':self.shop_ids,
#                   'categ_ids':category_id
#                   }) 
#         else:
#             sql ='''  
#                 SELECT pp.id,pp.default_code, pp.name_template,sum(start_onhand_qty) start_onhand_qty, round(sum(start_val)) start_val, 
#                     sum(nhaptk_qty) nhaptk_qty, round(sum(nhaptk_val)) nhaptk_val,
#                     sum(xuattk_qty) xuattk_qty, round(sum(xuattk_val)) xuattk_val,    
#                     sum(end_onhand_qty) end_onhand_qty,
#                     round(sum(end_val)) end_val
#                     From
#                     (SELECT
#                         stm.product_id,stm.product_uom,    
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
#                         then stm.primary_qty
#                         else
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
#                         then -1*stm.primary_qty 
#                         else 0.0 end
#                         end start_onhand_qty,
#                         
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
#                         then (stm.price_unit * stm.product_qty)
#                         else
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
#                         then -1*(stm.price_unit * stm.product_qty)
#                         else 0.0 end
#                         end start_val,
#                         
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
#                         then stm.primary_qty
#                         else 0.0 end nhaptk_qty,
#                         
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
#                         then 1*stm.primary_qty 
#                         else 0.0
#                         end xuattk_qty,
#                 
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
#                         then round(stm.price_unit * stm.product_qty)
#                         else 0.0 end nhaptk_val,
#                         
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
#                         then 1*(stm.price_unit * stm.product_qty)
#                         else 0.0
#                         end xuattk_val,        
#                          
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
#                         then stm.primary_qty
#                         else
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
#                         then -1*stm.primary_qty 
#                         else 0.0 end
#                         end end_onhand_qty,
#                         
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
#                         then round(stm.price_unit * stm.product_qty)
#                         else
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
#                         then -1*(stm.price_unit * stm.product_qty)
#                         else 0.0 end
#                         end end_val            
#                     FROM stock_move stm 
#                         join stock_location loc1 on stm.location_id=loc1.id
#                         join stock_location loc2 on stm.location_dest_id=loc2.id
#                     WHERE stm.state= 'done' and (stm.picking_id is not null or stm.id in (select move_id from stock_inventory_move_rel))   )foo
#                     inner join product_product pp on foo.product_id = pp.id
#                     inner join product_uom pu on foo.product_uom = pu.id
#                     inner join  (
#                             SELECT pt.id from  product_template pt inner join product_category pc on pt.categ_id = pc.id
#                                 where pc.id in ('%(categ_ids)s')
#                     )categ on pp.product_tmpl_id = categ.id
#                     WHERE (pp.id in (select product_id  from product_shop_rel where shop_id in('%(shop_ids)s'))
#                            or pp.id not in (select product_id  from product_shop_rel))
#                     group by pp.default_code,pp.name_template,pp.id
#                     order by pp.default_code,pp.name_template,pp.id
#                 '''%({
#                   'start_date': self.start_date,
#                   'end_date': self.date_end,
#                   'shop_ids':self.shop_ids,
#                   'categ_ids':category_id
#                   }) 
#                 
#         self.cr.execute(sql)
#         res =[]
#             
#         for i in self.cr.dictfetchall():
#             self.total_start_val = self.total_start_val + (i['start_val'] or 0)
#             self.total_nhap_val = self.total_nhap_val +(i['nhaptk_val'] or 0.0)
#             self.total_xuat_val = self.total_xuat_val +(i['xuattk_val'] or 0.0)
#             self.total_end_val = self.total_end_val +(i['end_val'] or 0.0)
#             
#             sql ='''
#                 SELECT sum(ail.quantity) as qty_hoantien, sum(ail.quantity*sm.price_unit) as total_hoantien
#                     FROM
#                         account_invoice_line ail left join account_invoice ai on ail.invoice_id = ai.id
#                         left join stock_move sm on ail.source_id = sm.id
#                     WHERE 
#                         ail.product_id = %s and ai.type = 'out_refund'
#                         and date(timezone('UTC',ai.date_invoice)) between '%s' and '%s'
#                         and ai.state not in ('draft','cancel')
#             '''%(i['id'],self.start_date,self.date_end)
#             self.cr.execute(sql)
#             nhap_ht_res = self.cr.fetchone()
#             i['nhaptk_qty'] += nhap_ht_res and nhap_ht_res[0] or 0
#             i['nhaptk_val'] += nhap_ht_res and nhap_ht_res[1] or 0
#             
#             sql ='''
#                 SELECT sum(ail.quantity) qty_dieuchinh, sum(ail.quantity*sm.price_unit) as total_dieuchinh
#                     FROM
#                         account_invoice_line ail left join account_invoice ai on ail.invoice_id = ai.id
#                         left join stock_move sm on ail.source_id = sm.id 
#                     WHERE 
#                         ail.product_id = %s and ai.type = 'out_invoice'
#                         and ai.rel_invoice_id is not null
#                         and date(timezone('UTC',ai.date_invoice)) between '%s' and '%s'
#                         and ai.state not in ('draft','cancel')
#             '''%(i['id'],self.start_date,self.date_end)
#             self.cr.execute(sql)
#             xuat_dc_res = self.cr.fetchone()
#             i['xuattk_qty'] += xuat_dc_res and xuat_dc_res[0] or 0
#             i['xuattk_val'] += xuat_dc_res and xuat_dc_res[1] or 0
#             
#             res.append(
#                    {
#                    'default_code':i['default_code'],
#                    'name_template':i['name_template'],
#                    'start_onhand_qty':i['start_onhand_qty'],
#                    'start_val':i['start_val'] or 0.0,
#                    'nhaptk_qty':i['nhaptk_qty'] or 0.0,
#                    'nhaptk_val':i['nhaptk_val'] or 0.0,
#                    'xuattk_qty':i['xuattk_qty'] or 0.0,
#                    'xuattk_val':i['xuattk_val'] or 0.0,
#                    'end_onhand_qty':i['end_onhand_qty'] or 0.0,
#                    'end_val':i['end_val'] or 0.0
#                    })
#         return res
    
    def get_line_by_product(self):
        location_model, location_id = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'stock', 'stock_location_customers')
        self.pool.get('stock.location').check_access_rule(self.cr, self.uid, [location_id], 'read')
        if not self.category_ids:
            if not self.location_id:
                sql ='''  
                SELECT pp.id,pp.default_code,pp.name_template,sum(start_onhand_qty) start_onhand_qty, round(sum(start_val)) start_val, 
                    sum(nhaptk_qty) nhaptk_qty, round(sum(nhaptk_val)) nhaptk_val,
                    sum(xuattk_qty) xuattk_qty, round(sum(xuattk_val)) xuattk_val,    
                    sum(end_onhand_qty) end_onhand_qty,
                    round(sum(end_val)) end_val
                    From
                    (
                    SELECT
                            stm.product_id,stm.product_uom,    
                            case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
                            then stm.primary_qty
                            else
                            case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
                            then -1*stm.primary_qty 
                            else 0.0 end
                            end start_onhand_qty,
                             
                            case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
                            then round(stm.price_unit * stm.product_qty)
                            else
                            case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
                            then -1*stm.price_unit * stm.product_qty
                            else 0.0 end
                            end start_val,
                             
                            case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
                            and ai.state in ('open','paid')
                            then stm.primary_qty
                            else 0.0 end nhaptk_qty,
                             
                            case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
                            and ai.state in ('open','paid')
                            then 1*stm.primary_qty 
                            else 0.0
                            end xuattk_qty,
                     
                            case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
                            and ai.state in ('open','paid')
                            then round(stm.price_unit * stm.product_qty)
                            else 0.0 end nhaptk_val,
                             
                            case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
                            and ai.state in ('open','paid')
                            then 1*stm.price_unit * stm.product_qty
                            else 0.0
                            end xuattk_val,        
                              
                            case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
                            and ai.state in ('open','paid')
                            then stm.primary_qty
                            else
                            case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
                            and ai.state in ('open','paid')
                            then -1*stm.primary_qty 
                            else 0.0 end
                            end end_onhand_qty,
                             
                            case when loc1.usage != 'internal' and loc2.usage = 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
                            and ai.state in ('open','paid')
                            then round(stm.price_unit * stm.product_qty)
                            else
                            case when loc1.usage = 'internal' and loc2.usage != 'internal' and date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
                            and ai.state in ('open','paid')
                            then -1*stm.price_unit * stm.product_qty
                            else 0.0 end
                            end end_val            
                        FROM stock_move stm 
                            join stock_location loc1 on stm.location_id=loc1.id
                            join stock_location loc2 on stm.location_dest_id=loc2.id
                            left join account_invoice_line ail on ail.source_id=stm.id
                            left join account_invoice ai on ai.id=ail.invoice_id
                        WHERE stm.state= 'done' and stm.id in (select move_id from stock_inventory_move_rel)
                        
                        
                    UNION ALL
                    
                    SELECT
                        stm.product_id,stm.product_uom,    
                        case when ai.type in ('in_invoice','out_refund') and rel_invoice_id is null 
                        and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
                        then ail.quantity
                        else
                        case when ai.type in ('out_refund') and rel_invoice_id is not null 
                        and date(timezone('UTC',ai.ngay_nhap::timestamp)) < '%(start_date)s'
                        then ail.quantity
                        else
                        case when ai.type in ('out_invoice','in_refund') and rel_invoice_id is null 
                        and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
                        then -1*ail.quantity 
                        else
                        case when ai.type in ('out_invoice') and rel_invoice_id is not null 
                        and date(timezone('UTC',ai.date_invoice::timestamp)) < '%(start_date)s'
                        then -1*ail.quantity 
                        else 0.0 end end end
                        end start_onhand_qty,
                        
                        case when ai.type in ('in_invoice','out_refund') and rel_invoice_id is null 
                        and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
                        then round(stm.price_unit * ail.quantity)
                        else
                        case when ai.type in ('out_refund') and rel_invoice_id is not null 
                        and date(timezone('UTC',ai.ngay_nhap::timestamp)) < '%(start_date)s'
                        then round(stm.price_unit * ail.quantity)
                        else
                        case when ai.type in ('out_invoice','in_refund')
                        and date(timezone('UTC',stm.date::timestamp)) < '%(start_date)s'
                        then -1*round(stm.price_unit * ail.quantity)
                        else
                        case when ai.type in ('out_invoice') and rel_invoice_id is not null 
                        and date(timezone('UTC',ai.date_invoice::timestamp)) < '%(start_date)s'
                        then -1*round(stm.price_unit * ail.quantity)
                        else 0.0 end end end
                        end start_val,
                        
                        case when ai.type in ('in_invoice','out_refund') and rel_invoice_id is null 
                        and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
                        then ail.quantity
                        else 
                        case when ai.type = 'out_refund' and rel_invoice_id is not null 
                        and date(timezone('UTC',ai.ngay_nhap::timestamp)) between '%(start_date)s' and '%(end_date)s' 
                        then ail.quantity
                        else 0 end
                        end nhaptk_qty,
                        
                        case when ai.type in ('out_invoice','in_refund') and rel_invoice_id is null 
                        and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
                        then 1*ail.quantity 
                        else
                        case when ai.type in ('out_invoice') and rel_invoice_id is not null 
                        and date(timezone('UTC',ai.date_invoice::timestamp)) between '%(start_date)s' and '%(end_date)s'
                        then 1*ail.quantity 
                        else 0.0 end
                        end xuattk_qty,
                
                        case when ai.type in ('in_invoice','out_refund') and rel_invoice_id is null 
                        and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
                        then round(stm.price_unit * ail.quantity)
                        else 
                        case when ai.type = 'out_refund' and rel_invoice_id is not null 
                        and date(timezone('UTC',ai.ngay_nhap::timestamp)) between '%(start_date)s' and '%(end_date)s' 
                        then round(stm.price_unit * ail.quantity)
                        else 0.0 end
                        end nhaptk_val,
                        
                        case when ai.type in ('out_invoice','in_refund') and rel_invoice_id is null 
                        and date(timezone('UTC',stm.date::timestamp)) between '%(start_date)s' and '%(end_date)s'
                        then 1*round(stm.price_unit * ail.quantity)
                        else
                        case when ai.type in ('out_invoice') and rel_invoice_id is not null 
                        and date(timezone('UTC',ai.date_invoice::timestamp)) between '%(start_date)s' and '%(end_date)s'
                        then 1*round(stm.price_unit * ail.quantity)
                        else 0.0 end
                        end xuattk_val,        
                         
                        case when date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
                        and ai.type in ('in_invoice','out_refund')
                        then ail.quantity
                        else
                        case when date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
                        and ai.type in ('out_invoice','in_refund')
                        then -1*ail.quantity
                        else 0.0 end
                        end end_onhand_qty,
                        
                        case when date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
                        and ai.type in ('in_invoice','out_refund')
                        then round(stm.price_unit * ail.quantity)
                        else
                        case when date(timezone('UTC',stm.date::timestamp)) <= '%(end_date)s'
                        and ai.type in ('out_invoice','in_refund')
                        then -1*round(stm.price_unit * ail.quantity)
                        else 0.0 end
                        end end_val            
                    FROM stock_move stm 
                        left join stock_location loc1 on stm.location_id=loc1.id
                        left join stock_location loc2 on stm.location_dest_id=loc2.id
                        left join account_invoice_line ail on ail.source_id=stm.id
                        left join account_invoice ai on ai.id=ail.invoice_id
                        left join stock_picking sp on sp.id=stm.picking_id
                    WHERE stm.state= 'done' and stm.picking_id is not null  
                    and ail.source_id is not null and ai.state in ('open','paid')
                     )foo
                     
                     
                    inner join product_product pp on foo.product_id = pp.id
                    inner join product_uom pu on foo.product_uom = pu.id
                    WHERE (pp.id in (select product_id  from product_shop_rel where shop_id in('%(shop_ids)s'))
                           or pp.id not in (select product_id  from product_shop_rel))
                    group by pp.default_code,pp.name_template,pp.id
                    order by pp.default_code,pp.name_template,pp.id
                
                '''%({
                  'start_date': self.start_date,
                  'end_date': self.date_end,
                  'shop_ids':self.shop_ids,
                  'cus_stock':location_id,
                  })
               
            
        self.cr.execute(sql)
        res =[]
        for i in self.cr.dictfetchall():
            self.total_start_val = self.total_start_val + (i['start_val'] or 0)
            self.total_nhap_val = self.total_nhap_val +(i['nhaptk_val'] or 0.0)
            self.total_xuat_val = self.total_xuat_val +(i['xuattk_val'] or 0.0)
            self.total_end_val = self.total_end_val +(i['end_val'] or 0.0)
#             sql ='''
#                 SELECT sum(ail.quantity) as qty_hoantien, sum(ail.quantity*sm.price_unit) as total_hoantien
#                     FROM
#                         account_invoice_line ail left join account_invoice ai on ail.invoice_id = ai.id
#                         left join stock_move sm on ail.source_id = sm.id
#                     WHERE 
#                         ail.product_id = %s and ai.type = 'out_refund'
#                         and date(timezone('UTC',ai.ngay_nhap)) between '%s' and '%s'
#                         and ai.trang_thai in ('paid')
#             '''%(i['id'],self.start_date,self.date_end)
#             self.cr.execute(sql)
#             nhap_ht_res = self.cr.fetchone()
#             i['nhaptk_qty'] += nhap_ht_res and nhap_ht_res[0] or 0
#             i['nhaptk_val'] += nhap_ht_res and nhap_ht_res[1] or 0
            
#             sql ='''
#                 SELECT sum(ail.quantity) qty_dieuchinh, sum(ail.quantity*sm.price_unit) as total_dieuchinh
#                     FROM
#                         account_invoice_line ail left join account_invoice ai on ail.invoice_id = ai.id
#                         left join stock_move sm on ail.source_id = sm.id 
#                     WHERE 
#                         ail.product_id = %s and ai.type = 'out_invoice'
#                         and ai.rel_invoice_id is not null
#                         and date(timezone('UTC',ai.date_invoice)) between '%s' and '%s'
#                         and ai.state not in ('draft','cancel')
#             '''%(i['id'],self.start_date,self.date_end)
#             self.cr.execute(sql)
#             xuat_dc_res = self.cr.fetchone()
#             i['xuattk_qty'] += xuat_dc_res and xuat_dc_res[0] or 0
#             i['xuattk_val'] += xuat_dc_res and xuat_dc_res[1] or 0
            
            
            end_onhand_qty = i['start_onhand_qty']+i['nhaptk_qty']-i['xuattk_qty']
            end_val = i['start_val']+i['nhaptk_val']-i['xuattk_val']
            res.append(
                   {
                   'default_code':i['default_code'], 
                   'name_template':i['name_template'],
                   'start_onhand_qty':i['start_onhand_qty'],
                   'start_val':i['start_onhand_qty'] and i['start_val'] or 0.0,
                   'nhaptk_qty':i['nhaptk_qty'] or 0.0,
                   'nhaptk_val':i['nhaptk_val'] or 0.0,
                   'xuattk_qty':i['xuattk_qty'] or 0.0,
                   'xuattk_val':i['xuattk_val'] or 0.0,
                   'end_onhand_qty':end_onhand_qty or 0.0,
                   'end_val':end_onhand_qty and end_val or 0.0
                   })
        return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
