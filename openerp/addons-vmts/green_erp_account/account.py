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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import datetime
from datetime import date
from openerp import tools

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def _get_product(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            product_id=False
            for line in invoice.invoice_line:
                if line.product_id:
                    product_id=line.product_id.id
                    break
            res[invoice.id] = product_id
        return res
    
    _columns = {
        'product_id': fields.function(_get_product, type='many2one', string='Product',relation='product.product',store=True),
        'vmts_partner_ref': fields.related('partner_id', 'ref', string="Reference",readonly=True,type='char'),
        }
account_invoice() 

class sale_order(osv.osv):
    _inherit = 'sale.order'
    
    def _get_product(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            product_id=False
            for line in order.order_line:
                if line.product_id:
                    product_id=line.product_id.id
                    break
            res[order.id] = product_id
        return res
    
    _columns = {
        'product_id': fields.function(_get_product, type='many2one', string='Product',relation='product.product',store=True),
        'vmts_partner_ref': fields.related('partner_id', 'ref', string="Reference",readonly=True,type='char'),
        }
sale_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
