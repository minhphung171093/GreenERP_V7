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


class sale_order(osv.osv):
    _inherit = "sale.order"
	
    def _get_nam(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            if order.date_order:
                nam_order = order.date_order[:4]
	    else:
		nam_order = ''
            res[order.id] = nam_order
        return res
	
    _columns = {
        'product_ralate': fields.related('order_line','product_id',type='many2one',relation='product.product',string='Product',store=True,readonly=True),
		'nam_order': fields.function(_get_nam,type='char', string='Năm',store=True),
    }
sale_order()

class account_report_general_ledger(osv.osv_memory):
    _inherit = "account.report.general.ledger"

    _defaults = {
        'target_move': 'all',
    }
    
account_report_general_ledger()

class account_balance_report(osv.osv_memory):
    _inherit = "account.balance.report"

    _defaults = {
        'target_move': 'all',
    }
    
account_balance_report()

class accounting_report(osv.osv_memory):
    _inherit = "accounting.report"

    _defaults = {
        'target_move': 'all',
    }
    
accounting_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
