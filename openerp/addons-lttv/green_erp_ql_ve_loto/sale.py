# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP SA (<http://openerp.com>).
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

import base64
import re
import threading
from openerp.tools.safe_eval import safe_eval as eval
from openerp import tools
import openerp.modules
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

class sale_order(osv.osv):
    _inherit = 'sale.order'

    def init(self, cr):
        ir_values = self.pool.get('ir.values')
        ir_values.set_default(cr, SUPERUSER_ID, 'sale.order', 'order_policy', 'picking')
        return True
    
    def onchange_dl_loto(self, cr, uid, ids,partner_id, pricelist_id, date_order,fiscal_position,context=None):
        vals = {}
        res = []
        results = self.onchange_partner_id(cr,uid,ids,partner_id,context)['value']
        if ids:
            cr.execute('delete from sale_order_line where order_id in (%s)',(ids),)
        if partner_id:
            partner_ids = self.pool.get('res.partner').search(cr, uid, [('parent_id','=',partner_id)], context=context)
            for partner in  partner_ids:
                menhgia_ids = self.pool.get('product.product').search(cr, uid, [('menh_gia','=',True)], context=context)
                for menhgia in menhgia_ids:
                    rs = self.pool.get('sale.order.line').product_id_change(cr, uid, ids, pricelist_id, menhgia, 1, False, False, False, False, partner_id, False, True, date_order, fiscal_position, False, context)
                    vals=rs['value']
                    vals.update({
                                 'daily_id': partner,
                                 'product_id': menhgia,
                                 'state': 'draft',
                                 'product_uom_qty': 1,
                                 })
                    res.append((0,0,vals))
            results.update({ 'order_line': res})
            
        return {'value': results}
    
sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns = {
        'daily_id': fields.many2one('res.partner','Đại lý',domain="[('dai_ly','=',True)]",states={'draft':[('readonly',False)]}),
        }
    
sale_order_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: