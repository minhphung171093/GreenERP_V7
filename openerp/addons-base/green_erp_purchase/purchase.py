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

class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    def init(self, cr):
        cr.execute(''' select res_id from ir_model_data
            where name in ('group_purchase_pricelist')
                and model='res.groups' ''')
        implied_group = cr.fetchall()
        cr.execute(''' select res_id from ir_model_data
            where name in ('group_user') and module='base' and model='res.groups' ''')
        group = cr.fetchone()
        if implied_group and group:
            group_id = group[0]
            for implied_group in implied_group:
                implied_group_id = implied_group[0]
                self.pool.get('res.groups').write(cr, SUPERUSER_ID, [group_id], {'implied_ids': [(4, implied_group_id)]})
        ir_values = self.pool.get('ir.values')
        ir_values.set_default(cr, SUPERUSER_ID, 'purchase.order', 'invoice_method', 'picking')
        return True
    
    def action_invoice_create(self, cr, uid, ids, context=None):
        """Generates invoice for given ids of purchase orders and links that invoice ID to purchase order.
        :param ids: list of ids of purchase orders.
        :return: ID of created invoice.
        :rtype: int
        """
        if context is None:
            context = {}
        journal_obj = self.pool.get('account.journal')
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')

        res = False
        uid_company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        for order in self.browse(cr, uid, ids, context=context):
            context.pop('force_company', None)
            if order.company_id.id != uid_company_id:
                #if the company of the document is different than the current user company, force the company in the context
                #then re-do a browse to read the property fields for the good company.
                context['force_company'] = order.company_id.id
                order = self.browse(cr, uid, order.id, context=context)
            pay_acc_id = order.partner_id.property_account_payable.id
            journal_ids = journal_obj.search(cr, uid, [('type', '=', 'purchase'), ('company_id', '=', order.company_id.id)], limit=1)
            if not journal_ids:
                raise osv.except_osv(_('Error!'),
                    _('Define purchase journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))

            # generate invoice line correspond to PO line and link that to created invoice (inv_id) and PO line
            inv_lines = []
            for po_line in order.order_line:
                acc_id = self._choose_account_from_po_line(cr, uid, po_line, context=context)
                inv_line_data = self._prepare_inv_line(cr, uid, acc_id, po_line, context=context)
                inv_line_id = inv_line_obj.create(cr, uid, inv_line_data, context=context)
                inv_lines.append(inv_line_id)

                po_line.write({'invoice_lines': [(4, inv_line_id)]}, context=context)
                
            shop_ids = self.pool.get('sale.shop').search(cr, uid, [('warehouse_id','=',order.warehouse_id.id or False)])
            # get invoice data and create invoice
            inv_data = {
                'name': order.partner_ref or order.name,
                'reference': order.partner_ref or order.name,
                'account_id': pay_acc_id,
                'type': 'in_invoice',
                'partner_id': order.partner_id.id,
                'currency_id': order.pricelist_id.currency_id.id,
                'journal_id': len(journal_ids) and journal_ids[0] or False,
                'invoice_line': [(6, 0, inv_lines)],
                'origin': order.name,
                'fiscal_position': order.fiscal_position.id or False,
                'payment_term': order.payment_term_id.id or False,
                'company_id': order.company_id.id,
                'shop_id': shop_ids and shop_ids[0] or False,
            }
            inv_id = inv_obj.create(cr, uid, inv_data, context=context)

            # compute the invoice
            inv_obj.button_compute(cr, uid, [inv_id], context=context, set_total=True)

            # Link this new invoice to related purchase order
            order.write({'invoice_ids': [(4, inv_id)]}, context=context)
            res = inv_id
        return res
    
purchase_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: