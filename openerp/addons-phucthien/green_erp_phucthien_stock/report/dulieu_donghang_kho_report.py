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
        tu_ngay = wizard_data['tu_ngay']
        den_ngay = wizard_data['den_ngay']
        sql ='''
            select sp.ngay_gui, rp.name as ten_kh, rpu.name as tdv, rr.name as employee, nghrr.name as nguoigiaohang,
                sum(spp.sl_nhietke_conlai) as sl_nhietke_conlai,
                sum(spp.sl_nhietke) as sl_giao,
                sum(spp.sl_nhietke)-sum(spp.sl_nhietke_conlai) as sl_da_nhan,
                lt.name as loai_thung,
                sum(spp.sl_da) as sl_da,
                sum(spp.sl_thung) as sl_thung,
                sum(spp.chi_phi_thung) as chi_phi_thung,
                sum(spp.chi_phi_da) as chi_phi_da,
                sum(spp.chi_phi_gui_hang) as chi_phi_gui_hang,
                sum(spp.chiphi_vanchuyen) as chiphi_vanchuyen,
                sum(spp.chi_phi_thung)+sum(spp.chi_phi_da)+sum(spp.chi_phi_gui_hang)+sum(spp.chiphi_vanchuyen) as thanh_tien,
                case when sp.ngay_nhan is not null then 'danhan' else 'chuanhan' end bb_giaonhan
                
            from stock_picking_packaging spp
            left join stock_picking sp on sp.id = spp.picking_id
            left join res_partner rp ON sp.partner_id = rp.id
            left join res_users ru ON rp.user_id = ru.id
            left join res_partner rpu ON ru.partner_id = rpu.id
            left join loai_thung lt ON spp.loai_thung_id = lt.id
            left join hr_employee hre ON spp.employee_id = hre.id
            left join hr_employee ngh ON sp.nguoi_giao_hang = ngh.id
            left join resource_resource nghrr ON ngh.resource_id = nghrr.id
            left join resource_resource rr ON hre.resource_id = rr.id
            where sp.ngay_gui >= '%s' and (sp.ngay_nhan is null or sp.ngay_nhan <= '%s')
        ''' %(tu_ngay, den_ngay)
        if partner_id:
            sql+='''
                and rp.id = %s 
            '''%(partner_id[0])
        sql+='''
             group by sp.ngay_gui, rp.name, rpu.name, lt.name, case when sp.ngay_nhan is not null then 'danhan' else 'chuanhan' end,
             rr.name, nghrr.name
            order by sp.ngay_gui
            '''
        self.cr.execute(sql)
        for line in self.cr.dictfetchall():
            res.append({
                        'ngay_gui':self.get_vietname_date(line['ngay_gui']),
                        'ten_kh':line['ten_kh'],
                        'tdv':line['tdv'], 
                        'sl_giao':line['sl_giao'], 
                        'sl_da_nhan':line['sl_da_nhan'], 
                        'sl_nhietke_conlai':line['sl_nhietke_conlai'],
                        'loai_thung':line['loai_thung'],
                        'sl_da':line['sl_da'],
                        'sl_thung':line['sl_thung'],
                        'chi_phi_thung':line['chi_phi_thung'],
                        'chi_phi_da':line['chi_phi_da'],
                        'bb_giaonhan':line['bb_giaonhan'],
                        'chiphi_trungchuyen': line['chi_phi_gui_hang'],
                        'chiphi_vanchuyen': line['chiphi_vanchuyen'],
                        'thanh_tien': line['thanh_tien'],
                        'nguoi_gui':line['employee'],
                        'nguoi_giao_hang':line['nguoigiaohang'],
                    })
        return res
    
