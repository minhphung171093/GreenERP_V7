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
        })
        
    def display_address_partner(self, partner):
        address = partner.street and partner.street + ' , ' or ''
        address += partner.street2 and partner.street2 + ' , ' or ''
        address += partner.city and partner.city.name + ' , ' or ''
        address += partner.state_id and partner.state_id.name + ' , ' or ''
        if address:
            address = address[:-3]
        return address
    
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
    
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        tu_ngay = wizard_data['tu_ngay']
        den_ngay = wizard_data['den_ngay']
        product_id = wizard_data['product_id'][0]
        location_id = wizard_data['location_id'][0]
        return []
