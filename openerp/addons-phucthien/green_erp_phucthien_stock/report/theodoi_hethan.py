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
            'get_lines': self.get_lines,
            'display_address_partner': self.display_address_partner,
            'get_product': self.get_product,
            'get_location': self.get_location,
            'get_diachi': self.get_diachi,
            'get_hsx': self.get_hsx,
            'get_dvt': self.get_dvt,
            'get_vietname_date':self.get_vietname_date,
            'get_date_hd': self.get_date_hd,
            'get_htxl': self.get_htxl,
            'get_chungtu': self.get_chungtu,
            'get_ngayxuat': self.get_ngayxuat,
        })
        
    def display_address_partner(self, partner):
        address = partner.street and partner.street + ' , ' or ''
        address += partner.street2 and partner.street2 + ' , ' or ''
        address += partner.city and partner.city.name + ' , ' or ''
        address += partner.state_id and partner.state_id.name + ' , ' or ''
        if address:
            address = address[:-3]
        return address
    
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_product(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['product_id'][1]
    
    def get_location(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['location_id'][1]
    
    def get_diachi(self):
        wizard_data = self.localcontext['data']['form']
        location_id = wizard_data['location_id'][0]
        location=self.pool.get('stock.location').browse(self.cr, self.uid, location_id)
        return location.partner_id and self.display_address_partner(location.partner_id) or ''
    
    def get_hsx(self):
        wizard_data = self.localcontext['data']['form']
        product_id = wizard_data['product_id'][0]
        product = self.pool.get('product.product').browse(self.cr, self.uid, product_id)
        return product.manufacturer_product_id and product.manufacturer_product_id.name or ''
    
    def get_dvt(self):
        wizard_data = self.localcontext['data']['form']
        product_id = wizard_data['product_id'][0]
        product = self.pool.get('product.product').browse(self.cr, self.uid, product_id)
        return product.uom_id and product.uom_id.name or ''
    
    def get_date_hd(self,date):
        if not date:
            date = time.strftime('%Y-%m-%d')
        else:
            date = date[:10]
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%m/%Y')
    
    def get_htxl(self, loaixuly):
        if loaixuly=='trahang_ncc':
            return u'Trả hàng cho nhà cung cấp'
        return u'Hủy hàng'
    
    def get_chungtu(self, origin):
        invoice_ids = self.pool.get('account.invoice').search(self.cr,self.uid,[('name','=',origin)])
        if invoice_ids:
            invoice = self.pool.get('account.invoice').browse(self.cr,self.uid,invoice_ids[0])
            so = invoice.number
            ngay = self.get_vietname_date(invoice.date_invoice)
            khachhang = invoice.partner_id.name
        else:
            so = ''
            ngay = ''
            khachhang = ''
        return {'so': so,
                'ngay': ngay,
                'khachhang': khachhang}
    
    def get_ngayxuat(self,picking_id):
        picking_obj = self.pool.get('stock.picking')
        picking = picking_obj.browse(self.cr, self.uid, picking_id)
        date = ''
        if picking.loai_xuly=='trahang_ncc':
            trahang_ids = picking_obj.search(self.cr, self.uid, [('origin','=',picking.name),('state','=',done)])
            if trahang_ids:
                trahang = picking_obj.browse(self.cr, self.uid, trahang_ids[0])
                date = self.get_vietname_date(trahang.date[:10])
        else:
            if picking.xuly_huyhang_id.state=='done':
                date = self.get_vietname_date(picking.xuly_huyhang_id.date[:10])
        return date
        
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        tu_ngay = wizard_data['tu_ngay']
        den_ngay = wizard_data['den_ngay']
        product_id = wizard_data['product_id'][0]
        location_id = wizard_data['location_id'][0]
        sql = '''
            select sp.id as id, sp.origin as origin, sp.date as ngaynhap, spl.name as solo, spl.life_date as handung, sm.product_qty as soluong,
                sp.tinhtrang_chatluong as tinhtrangchatluong, sp.note as ghichu, sp.loai_xuly as loaixuly
                from stock_move sm
                left join stock_picking sp on sp.id=sm.picking_id
                left join stock_production_lot spl on spl.id = sm.prodlot_id 
                where sp.return='customer' and sp.type='in' and sp.state='done' and sm.location_dest_id=%s and sm.product_id=%s
                    and date(timezone('UTC',sp.date)) between '%s' and '%s'
        '''%(location_id,product_id,tu_ngay,den_ngay)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
