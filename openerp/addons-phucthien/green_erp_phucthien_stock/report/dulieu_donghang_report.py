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
        self.localcontext.update({
            'get_data':self.get_data,
            'get_date_from':self.get_date_from,
            'get_date_to':self.get_date_to,
            
        })
        
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['tu_ngay'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['den_ngay'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_vietname_date(self, date):
        if not date:
            return ''
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
         
    def get_data(self):
        res = []
        wizard_data = self.localcontext['data']['form']
        partner_id = wizard_data['partner_id']
        da_nhan = wizard_data['da_nhan']
        chua_nhan = wizard_data['chua_nhan']
        tu_ngay = wizard_data['tu_ngay']
        den_ngay = wizard_data['den_ngay']
        if self.uid != 1:
            if self.uid == 24:
                sql = '''
                    select id from res_partner where 
                        customer = 't' and 
                        street LIKE '%Q.Gò Vấp%' or street LIKE '%Q. Gò Vấp%' or street LIKE '%Quận Gò Vấp%' or
                        street LIKE '%Q.Tân Bình%' or street LIKE '%Q. Tân Bình%' or street LIKE '%Quận Tân Bình%' or
                        street LIKE '%Q1%' or street LIKE '%Q.1%' or street LIKE '%Quận 1%' or
                        street LIKE '%Q.Tân Phú%' or street LIKE '%Q. Tân Phú%' or street LIKE '%Quận Tân Phú%' or
                        street LIKE '%Q3%' or street LIKE '%Q.3%' or street LIKE '%Quận 3%' or
                        street LIKE '%Q10%' or street LIKE '%Q.10%' or street LIKE '%Quận 10%' or
                        street LIKE '%Q11%' or street LIKE '%Q.11%' or street LIKE '%Quận 11%' or
                        street LIKE '%Q4%' or street LIKE '%Q.4%' or street LIKE '%Quận 4%' or
                        street LIKE '%Q5%' or street LIKE '%Q.5%' or street LIKE '%Quận 5%' or
                        street LIKE '%Q6%' or street LIKE '%Q.6%' or street LIKE '%Quận 6%' or
                        street LIKE '%Q8%' or street LIKE '%Q.8%' or street LIKE '%Quận 8%' or
                        street LIKE '%Q.Bình Tân%' or street LIKE '%Q. Bình Tân%' or street LIKE '%Quận Bình Tân%' or
                        street LIKE '%Q7%' or street LIKE '%Q.7%' or street LIKE '%Quận 7%' or
                        street LIKE '%H.Bình Chánh%' or street LIKE '%H. Bình Chánh%' or street LIKE '%Huyện Bình Chánh%' or
                        street LIKE '%H.Nhà Bè%' or street LIKE '%H. Nhà Bè%' or street LIKE '%Huyện Nhà Bè%' or
                        street LIKE '%H.Cần Giờ%' or street LIKE '%H. Cần Giờ%' or street LIKE '%Huyện Cần Giờ%' or
                        
                        street2 LIKE '%Q.Gò Vấp%' or street2 LIKE '%Q. Gò Vấp%' or street2 LIKE '%Quận Gò Vấp%' or
                        street2 LIKE '%Q.Tân Bình%' or street2 LIKE '%Q. Tân Bình%' or street2 LIKE '%Quận Tân Bình%' or
                        street2 LIKE '%Q1%' or street2 LIKE '%Q.1%' or street2 LIKE '%Quận 1%' or 
                        street2 LIKE '%Q.Tân Phú%' or street2 LIKE '%Q. Tân Phú%' or street2 LIKE '%Quận Tân Phú%' or
                        street2 LIKE '%Q3%' or street2 LIKE '%Q.3%' or street2 LIKE '%Quận 3%' or
                        street2 LIKE '%Q10%' or street2 LIKE '%Q.10%' or street2 LIKE '%Quận 10%' or
                        street2 LIKE '%Q11%' or street2 LIKE '%Q.11%' or street2 LIKE '%Quận 11%' or
                        street2 LIKE '%Q4%' or street2 LIKE '%Q.4%' or street2 LIKE '%Quận 4%' or
                        street2 LIKE '%Q5%' or street2 LIKE '%Q.5%' or street2 LIKE '%Quận 5%' or
                        street2 LIKE '%Q6%' or street2 LIKE '%Q.6%' or street2 LIKE '%Quận 6%' or
                        street2 LIKE '%Q8%' or street2 LIKE '%Q.8%' or street2 LIKE '%Quận 8%' or
                        street2 LIKE '%Q.Bình Tân%' or street2 LIKE '%Q. Bình Tân%' or street2 LIKE '%Quận Bình Tân%' or
                        street2 LIKE '%Q7%' or street2 LIKE '%Q.7%' or street2 LIKE '%Quận 7%' or
                        street2 LIKE '%H.Bình Chánh%' or street2 LIKE '%H. Bình Chánh%' or street2 LIKE '%Huyện Bình Chánh%' or
                        street2 LIKE '%H.Nhà Bè%' or street2 LIKE '%H. Nhà Bè%' or street2 LIKE '%Huyện Nhà Bè%' or
                        street2 LIKE '%H.Cần Giờ%' or street2 LIKE '%H. Cần Giờ%' or street2 LIKE '%Huyện Cần Giờ%'
                '''
                self.cr.execute(sql)
                thuy_ids = [row[0] for row in self.cr.fetchall()]
                thuy_ids = str(thuy_ids).replace('[', '(')
                thuy_ids = str(thuy_ids).replace(']', ')')
                sql ='''
                    select sp.name as so_phieuxuat,sp.ngay_gui, rp.name as ten_kh, rpu_so.name as tdv, rcs.name as tinh,   
                        sum(spp.sl_nhietke_conlai) as sl_nhietke_conlai,
                        case when sp.ngay_nhan is not null then 'Da nhan' else 'Chua nhan' end as bb_giaonhan
                    from stock_picking_packaging spp
                    left join stock_picking sp on sp.id = spp.picking_id
                    left join stock_move sm on sm.picking_id = sp.id
                    left join product_product pp on sm.product_id = pp.id
                    left join product_template pt on pp.product_tmpl_id = pt.id
                    left join product_category pc on pt.categ_id = pc.id
                    left join res_partner rp ON sp.partner_id = rp.id
                    left join res_users ru ON rp.user_id = ru.id
                    left join res_partner rpu ON ru.partner_id = rpu.id
                    left join res_country_state rcs ON rp.state_id = rcs.id
                    left join sale_order so ON sp.sale_id = so.id
                    left join res_users ru_so ON so.user_id = ru_so.id
                    left join res_partner rpu_so ON ru_so.partner_id = rpu_so.id
                    where sp.ngay_gui >= '%s' and (sp.ngay_nhan is null or sp.ngay_nhan <= '%s')
                    and rp.id in %s and pc.code='VC'
                ''' %(tu_ngay, den_ngay, thuy_ids)
                if partner_id:
                    sql+='''
                        and rp.id = %s 
                    '''%(partner_id[0])
                if da_nhan:
                    sql+='''
                        and sp.ngay_nhan is not null
                    '''
                if chua_nhan:
                    sql+='''
                        and sp.ngay_nhan is null
                    '''    
                sql+='''
                     group by sp.name,sp.ngay_gui, rp.name,rpu_so.name,rcs.name,case when sp.ngay_nhan is not null then 'Da nhan' else 'Chua nhan' end
                    order by sp.name
                    '''
                self.cr.execute(sql)
                for line in self.cr.dictfetchall():
                    res.append({
                                'so_phieuxuat': line['so_phieuxuat'],
                                'ten_kh':line['ten_kh'],
                                'ngay_gui':self.get_vietname_date(line['ngay_gui']),
                                'sl_nhietke_conlai':line['sl_nhietke_conlai'],
                                'bb_giaonhan':line['bb_giaonhan'],
                                'tdv':line['tdv'], 
                                'tinh':line['tinh'], 
                            })
#             elif self.uid == 34:
#                 sql ='''
#                     select sp.name as so_phieuxuat,sp.ngay_gui, rp.name as ten_kh, rpu.name as tdv, rcs.name as tinh,   
#                         sum(spp.sl_nhietke_conlai) as sl_nhietke_conlai,
#                         case when sp.ngay_nhan is not null then 'Da nhan' else 'Chua nhan' end as bb_giaonhan
#                     from stock_picking_packaging spp
#                     left join stock_picking sp on sp.id = spp.picking_id
#                     left join stock_move sm on sm.picking_id = sp.id
#                     left join product_product pp on sm.product_id = pp.id
#                     left join product_template pt on pp.product_tmpl_id = pt.id
#                     left join product_category pc on pt.categ_id = pc.id
#                     left join res_partner rp ON sp.partner_id = rp.id
#                     left join res_users ru ON rp.user_id = ru.id
#                     left join res_partner rpu ON ru.partner_id = rpu.id
#                     left join res_country_state rcs ON rp.state_id = rcs.id
#                     where sp.ngay_gui >= '%s' and (sp.ngay_nhan is null or sp.ngay_nhan <= '%s')
#                     and pc.code='NR'
#                 ''' %(tu_ngay, den_ngay)
#                 if partner_id:
#                     sql+='''
#                         and rp.id = %s 
#                     '''%(partner_id[0])
#                 if da_nhan:
#                     sql+='''
#                         and sp.ngay_nhan is not null
#                     '''
#                 if chua_nhan:
#                     sql+='''
#                         and sp.ngay_nhan is null
#                     '''    
#                 sql+='''
#                      group by sp.name,sp.ngay_gui, rp.name,rpu.name,rcs.name,case when sp.ngay_nhan is not null then 'Da nhan' else 'Chua nhan' end
#                     order by sp.name
#                     '''
#                 self.cr.execute(sql)
#                 for line in self.cr.dictfetchall():
#                     res.append({
#                                 'so_phieuxuat': line['so_phieuxuat'],
#                                 'ten_kh':line['ten_kh'],
#                                 'ngay_gui':self.get_vietname_date(line['ngay_gui']),
#                                 'sl_nhietke_conlai':line['sl_nhietke_conlai'],
#                                 'bb_giaonhan':line['bb_giaonhan'],
#                                 'tdv':line['tdv'], 
#                                 'tinh':line['tinh'], 
#                             })
            else:    
                sql ='''
                    select sp.name as so_phieuxuat,sp.ngay_gui, rp.name as ten_kh, rpu_so.name as tdv, rcs.name as tinh,   
                        sum(spp.sl_nhietke_conlai) as sl_nhietke_conlai,
                        case when sp.ngay_nhan is not null then 'Da nhan' else 'Chua nhan' end as bb_giaonhan
                    from stock_picking_packaging spp
                    left join stock_picking sp on sp.id = spp.picking_id
                    left join sale_order so on sp.sale_id = so.id
                    left join res_partner rp ON sp.partner_id = rp.id
                    left join res_users ru ON rp.user_id = ru.id
                    left join res_partner rpu ON ru.partner_id = rpu.id
                    left join res_country_state rcs ON rp.state_id = rcs.id
                    left join res_users ru_so ON so.user_id = ru_so.id
                    left join res_partner rpu_so ON ru_so.partner_id = rpu_so.id
                    where sp.ngay_gui >= '%s' and (sp.ngay_nhan is null or sp.ngay_nhan <= '%s') and so.user_id = %s
                ''' %(tu_ngay, den_ngay, self.uid)
                if partner_id:
                    sql+='''
                        and rp.id = %s 
                    '''%(partner_id[0])
                if da_nhan:
                    sql+='''
                        and sp.ngay_nhan is not null
                    '''
                if chua_nhan:
                    sql+='''
                        and sp.ngay_nhan is null
                    '''    
                sql+='''
                     group by sp.name,sp.ngay_gui, rp.name,rpu_so.name,rcs.name,case when sp.ngay_nhan is not null then 'Da nhan' else 'Chua nhan' end
                    order by sp.name
                    '''
                self.cr.execute(sql)
                for line in self.cr.dictfetchall():
                    res.append({
                                'so_phieuxuat': line['so_phieuxuat'],
                                'ten_kh':line['ten_kh'],
                                'ngay_gui':self.get_vietname_date(line['ngay_gui']),
                                'sl_nhietke_conlai':line['sl_nhietke_conlai'],
                                'bb_giaonhan':line['bb_giaonhan'],
                                'tdv':line['tdv'], 
                                'tinh':line['tinh'], 
                            })
                
        else:
            sql ='''
                select sp.name as so_phieuxuat,sp.ngay_gui, rp.name as ten_kh, rpu_so.name as tdv, rcs.name as tinh,   
                    sum(spp.sl_nhietke_conlai) as sl_nhietke_conlai,
                    case when sp.ngay_nhan is not null then 'Da nhan' else 'Chua nhan' end as bb_giaonhan
                from stock_picking_packaging spp
                left join stock_picking sp on sp.id = spp.picking_id
                left join sale_order so on sp.sale_id = so.id
                left join res_partner rp ON sp.partner_id = rp.id
                left join res_users ru ON rp.user_id = ru.id
                left join res_partner rpu ON ru.partner_id = rpu.id
                left join res_country_state rcs ON rp.state_id = rcs.id
                left join res_users ru_so ON so.user_id = ru_so.id
                left join res_partner rpu_so ON ru_so.partner_id = rpu_so.id
                where sp.ngay_gui >= '%s' and (sp.ngay_nhan is null or sp.ngay_nhan <= '%s')
            ''' %(tu_ngay, den_ngay)
            if partner_id:
                sql+='''
                    and rp.id = %s 
                '''%(partner_id[0])
            if da_nhan:
                sql+='''
                    and sp.ngay_nhan is not null
                '''
            if chua_nhan:
                sql+='''
                    and sp.ngay_nhan is null
                '''    
            sql+='''
                 group by sp.name,sp.ngay_gui, rp.name,rpu_so.name,rcs.name,case when sp.ngay_nhan is not null then 'Da nhan' else 'Chua nhan' end
                order by sp.name
                '''
            self.cr.execute(sql)
            for line in self.cr.dictfetchall():
                res.append({
                            'so_phieuxuat': line['so_phieuxuat'],
                            'ten_kh':line['ten_kh'],
                            'ngay_gui':self.get_vietname_date(line['ngay_gui']),
                            'sl_nhietke_conlai':line['sl_nhietke_conlai'],
                            'bb_giaonhan':line['bb_giaonhan'],
                            'tdv':line['tdv'], 
                            'tinh':line['tinh'], 
                        })
        return res
    
