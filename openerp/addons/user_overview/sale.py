# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2013 OpenERP s.a. (<http://openerp.com>).
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

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True, readonly=False),
        'date_order': fields.date('Date', required=True, readonly=False, select=True),
        'user_id': fields.many2one('res.users', 'Salesperson', readonly=False, select=True, track_visibility='onchange'),
        'partner_id': fields.many2one('res.partner', 'Customer', readonly=False, required=True, change_default=True, select=True, track_visibility='always'),
        'partner_invoice_id': fields.many2one('res.partner', 'Invoice Address', readonly=False, required=True, help="Invoice address for current sales order."),
        'partner_shipping_id': fields.many2one('res.partner', 'Delivery Address', readonly=False, required=True, help="Delivery address for current sales order."),
        'order_policy': fields.selection([
                ('manual', 'On Demand'),
            ], 'Create Invoice', required=True, readonly=False,
            help="""This field controls how invoice and delivery operations are synchronized."""),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=False, help="Pricelist for current sales order."),
        'project_id': fields.many2one('account.analytic.account', 'Contract / Analytic', readonly=False, help="The analytic account related to a sales order."),

        'order_line': fields.one2many('sale.order.line', 'order_id', 'Order Lines', readonly=False),
        }
sale_order()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns = {
        'name': fields.text('Description', required=True, readonly=False),
        'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Product Price'), readonly=False),
        'product_uom_qty': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True, readonly=False),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True, readonly=False),
        'product_uos_qty': fields.float('Quantity (UoS)' ,digits_compute= dp.get_precision('Product UoS'), readonly=False),
        'tax_id': fields.many2many('account.tax', 'sale_order_tax', 'order_line_id', 'tax_id', 'Taxes', readonly=False),
        }
sale_order_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
