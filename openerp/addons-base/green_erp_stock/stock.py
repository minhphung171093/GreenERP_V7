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

class stock_location(osv.osv):
    _inherit = "stock.location"

    _columns = {
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse'),
    }
    
stock_location()

class stock_journal(osv.osv):
    _inherit = "stock.journal"
    _columns = {
        'name': fields.char('Stock Journal', size=32, required=True),
        'user_id': fields.many2one('res.users', 'Responsible'),
        'source_type': fields.selection([
                                        ('in', 'Getting Goods'), 
                                        ('out', 'Sending Goods'),
                                        ('return_customer', 'Return from customer'), 
                                        ('return_supplier', 'Return to supplier'), 
                                        ('internal', 'Internal'),
                                        ('production', 'Production'),
                                        ('phys_adj', 'Physical Adjustment'),], 'Source Type', size=16, required=True),
        'sequence_id': fields.many2one('ir.sequence', 'Sequence'),
        
        'from_location_id':fields.many2many('stock.location','stock_journal_from_location_ref', 
                                                 'journal_id','location_id','From Location',required = True), 
        'to_location_id':fields.many2many('stock.location','stock_journal_to_location_ref', 
                                                 'journal_id','location_id','From Location',required = True), 
    }
    _defaults = {
        'user_id': lambda s, c, u, ctx: u
    }
    
stock_journal()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def init(self, cr):
        cr.execute(''' select res_id from ir_model_data
            where name in ('group_locations')
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
        return True
    
    def _get_location_info(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        shop_id = False
        warehouse_id = False
        for pick in self.browse(cr, uid, ids, context=context):
            
            res[pick.id] = {
                            'shop_id': False,
                            'warehouse_id': False,
                            }
            
            if pick.location_id.usage =='internal':
                warehouse_id = pick.location_id and pick.location_id.warehouse_id.id or False
            if not warehouse_id:
                if pick.location_dest_id.usage =='internal':
                    warehouse_id = pick.location_dest_id and pick.location_dest_id.warehouse_id.id or False
                
            
            if warehouse_id:
                res[pick.id]['warehouse_id'] = warehouse_id
                sql='''
                    SELECT id FROM sale_shop WHERE warehouse_id = %s
                '''%(warehouse_id)
                cr.execute(sql)
                shop_res = cr.fetchone()
                shop_id = shop_res and shop_res[0] or False
            if shop_id:
                res[pick.id]['shop_id'] = shop_id
        return res
    
    _columns = {
        'shop_id': fields.function(_get_location_info, type='many2one', relation='sale.shop', string='Shop',
            store={
                'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['location_id','location_dest_id'], 10),
            }, readonly=True, multi='lo_info'),
        'warehouse_id': fields.function(_get_location_info, type='many2one', relation='stock.warehouse', string='Warehouse',
            store={
                'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['location_id','location_dest_id'], 10),
            }, readonly=True, multi='lo_info'),
                
        'stock_journal_id': fields.many2one('stock.journal','Stock Journal', required=True, select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
    }
    
#     def _get_journal(self, cr, uid, context=None):
#         journal_domain = []
#         if context.get('default_type',False) and context.get('default_return',False):
#             default_type = context['default_type']
#             default_return = context['default_return']
#             if default_type == 'in':
#                 journal_domain = [('source_type', '=', 'in')]
#                 if default_return == 'customer':
#                     journal_domain = [('source_type', '=', 'return_customer')]
#             if default_type == 'out':
#                 journal_domain = [('source_type', '=', 'out')]
#                 if default_return == 'supplier':
#                     journal_domain = [('source_type', '=', 'return_supplier')]
#         else:
#             journal_domain = [('source_type', '=', 'internal')]
#         journal_ids = self.pool.get('stock.journal').search(cr, uid, journal_domain)
#         return journal_ids and journal_ids[0] or False
#     
#     _defaults = {    
#         'stock_journal_id': _get_journal,
#     }
    
    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        """ Builds the dict containing the values for the invoice
            @param picking: picking object
            @param partner: object of the partner to invoice
            @param inv_type: type of the invoice ('out_invoice', 'in_invoice', ...)
            @param journal_id: ID of the accounting journal
            @return: dict that will be used to create the invoice object
        """
        if isinstance(partner, int):
            partner = self.pool.get('res.partner').browse(cr, uid, partner, context=context)
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = partner.property_account_receivable.id
            payment_term = partner.property_payment_term.id or False
        else:
            account_id = partner.property_account_payable.id
            payment_term = partner.property_supplier_payment_term.id or False
        comment = self._get_comment_invoice(cr, uid, picking)
        
        warehouse_id = picking.location_id.warehouse_id and picking.location_id.warehouse_id.id or False
        if not warehouse_id:
            warehouse_id = picking.location_dest_id.warehouse_id.id or False
        shop_ids = self.pool.get('sale.shop').search(cr, uid, [('warehouse_id','=',warehouse_id)])
        invoice_vals = {
            'name': picking.name,
            'origin': (picking.name or '') + (picking.origin and (':' + picking.origin) or ''),
            'type': inv_type,
            'account_id': account_id,
            'partner_id': partner.id,
            'comment': comment,
            'payment_term': payment_term,
            'fiscal_position': partner.property_account_position.id,
            'date_invoice': context.get('date_inv', False),
            'company_id': picking.company_id.id,
            'user_id': uid,
            'shop_id': shop_ids and shop_ids[0] or False,
        }
        cur_id = self.get_currency_id(cr, uid, picking)
        if cur_id:
            invoice_vals['currency_id'] = cur_id
        if journal_id:
            invoice_vals['journal_id'] = journal_id
        return invoice_vals
    
stock_picking()

class stock_picking_in(osv.osv):
    _inherit = 'stock.picking.in'
    
    def _get_location_info(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        shop_id = False
        warehouse_id = False
        for pick in self.browse(cr, uid, ids, context=context):
            
            res[pick.id] = {
                            'shop_id': False,
                            'warehouse_id': False,
                            }
            
            if pick.location_id.usage =='internal':
                warehouse_id = pick.location_id and pick.location_id.warehouse_id and pick.location_id.warehouse_id.id or False
            if not warehouse_id:
                if pick.location_dest_id.usage =='internal':
                    warehouse_id = pick.location_dest_id and pick.location_dest_id.warehouse_id and pick.location_dest_id.warehouse_id.id or False
                
            
            if warehouse_id:
                res[pick.id]['warehouse_id'] = warehouse_id
                sql='''
                    SELECT id FROM sale_shop WHERE warehouse_id = %s
                '''%(warehouse_id)
                cr.execute(sql)
                shop_res = cr.fetchone()
                shop_id = shop_res and shop_res[0] or False
            if shop_id:
                res[pick.id]['shop_id'] = shop_id
        return res
    
    _columns = {
        'shop_id': fields.function(_get_location_info, type='many2one', relation='sale.shop', string='Shop',
            store={
                'stock.picking.in': (lambda self, cr, uid, ids, c={}: ids, ['location_id','location_dest_id'], 10),
            }, readonly=True, multi='pro_info'),
        'warehouse_id': fields.function(_get_location_info, type='many2one', relation='stock.warehouse', string='Warehouse',
            store={
                'stock.picking.in': (lambda self, cr, uid, ids, c={}: ids, ['location_id','location_dest_id'], 10),
            }, readonly=True, multi='pro_info'),
    }
    
stock_picking_in()

class stock_picking_out(osv.osv):
    _inherit = 'stock.picking.out'
    
    def _get_location_info(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        shop_id = False
        warehouse_id = False
        for pick in self.browse(cr, uid, ids, context=context):
            
            res[pick.id] = {
                            'shop_id': False,
                            'warehouse_id': False,
                            }
            
            if pick.location_id.usage =='internal':
                warehouse_id = pick.location_id and pick.location_id.warehouse_id and pick.location_id.warehouse_id.id or False
            if not warehouse_id:
                if pick.location_dest_id.usage =='internal':
                    warehouse_id = pick.location_dest_id and pick.location_dest_id.warehouse_id and pick.location_dest_id.warehouse_id.id or False
                
            
            if warehouse_id:
                res[pick.id]['warehouse_id'] = warehouse_id
                sql='''
                    SELECT id FROM sale_shop WHERE warehouse_id = %s
                '''%(warehouse_id)
                cr.execute(sql)
                shop_res = cr.fetchone()
                shop_id = shop_res and shop_res[0] or False
            if shop_id:
                res[pick.id]['shop_id'] = shop_id
        return res
    
    _columns = {
        'shop_id': fields.function(_get_location_info, type='many2one', relation='sale.shop', string='Shop',
            store={
                'stock.picking.in': (lambda self, cr, uid, ids, c={}: ids, ['location_id','location_dest_id'], 10),
            }, readonly=True, multi='pro_info'),
        'warehouse_id': fields.function(_get_location_info, type='many2one', relation='stock.warehouse', string='Warehouse',
            store={
                'stock.picking.in': (lambda self, cr, uid, ids, c={}: ids, ['location_id','location_dest_id'], 10),
            }, readonly=True, multi='pro_info'),
    }
    
stock_picking_out()

class stock_move(osv.osv):
    _inherit = 'stock.move'
    
    def _create_product_valuation_moves(self, cr, uid, move, context=None):
        """
        Generate the appropriate accounting moves if the product being moves is subject
        to real_time valuation tracking, and the source or destination location is
        a transit location or is outside of the company.
        """
        if move.product_id.valuation == 'real_time': # FIXME: product valuation should perhaps be a property?
            if context is None:
                context = {}
            src_company_ctx = dict(context,force_company=move.location_id.company_id.id)
            dest_company_ctx = dict(context,force_company=move.location_dest_id.company_id.id)
            # do not take the company of the one of the user
            # used to select the correct period
            company_ctx = dict(context, company_id=move.company_id.id)
            account_moves = []
            # Outgoing moves (or cross-company output part)
            if move.location_id.company_id \
                and (move.location_id.usage == 'internal' and move.location_dest_id.usage != 'internal'\
                     or move.location_id.company_id != move.location_dest_id.company_id):
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, src_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
                #returning goods to supplier
                if move.location_dest_id.usage == 'supplier':
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_valuation, acc_src, reference_amount, reference_currency_id, context))]
                else:
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_valuation, acc_dest, reference_amount, reference_currency_id, context))]

            # Incoming moves (or cross-company input part)
            if move.location_dest_id.company_id \
                and (move.location_id.usage != 'internal' and move.location_dest_id.usage == 'internal'\
                     or move.location_id.company_id != move.location_dest_id.company_id):
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, dest_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
                #goods return from customer
                if move.location_id.usage == 'customer':
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_dest, acc_valuation, reference_amount, reference_currency_id, context))]
                else:
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_src, acc_valuation, reference_amount, reference_currency_id, context))]

            move_obj = self.pool.get('account.move')
            for j_id, move_lines in account_moves:
                move_obj.create(cr, uid,
                        {
                         'journal_id': j_id,
                         'line_id': move_lines,
                         'company_id': move.company_id.id,
                         'shop_id':move.picking_id and move.picking_id.shop_id and move.picking_id.shop_id.id or False,
                         'ref': move.picking_id and move.picking_id.name}, context=company_ctx)
    
stock_move()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: