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

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    _columns = {
        'reference_number': fields.char('Reference Number', size=64, readonly=True, states={'draft':[('readonly',False)]}),
        'date_document': fields.date('Document Date', readonly=True, states={'draft':[('readonly',False)]}),
    }
    
    _defaults = {
        'date_document': fields.date.context_today,
    }
    
account_invoice()

class account_journal(osv.osv):
    _inherit = "account.journal"
 
    _columns = {
        'shop_ids': fields.many2many('sale.shop', 'account_journal_shop_rel', 'journal_id', 'shop_id', 'Shops'),
    }
     
account_journal()

class account_invoice(osv.osv):
    _inherit = "account.invoice"
 
    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop', readonly=True, states={'draft':[('readonly',False)]}),
    }
    
    def _get_shop_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.context_shop_id.id or False
    
    _defaults = {
         'shop_id': _get_shop_id,
    }
    
    def action_move_create(self, cr, uid, ids, context=None):
        """Creates invoice related analytics and financial move lines"""
        ait_obj = self.pool.get('account.invoice.tax')
        cur_obj = self.pool.get('res.currency')
        period_obj = self.pool.get('account.period')
        payment_term_obj = self.pool.get('account.payment.term')
        journal_obj = self.pool.get('account.journal')
        move_obj = self.pool.get('account.move')
        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids, context=context):
            if not inv.journal_id.sequence_id:
                raise osv.except_osv(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise osv.except_osv(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = context.copy()
            ctx.update({'lang': inv.partner_id.lang})
            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice': fields.date.context_today(self, cr, uid, context=context)}, context=ctx)
                inv.refresh()
            company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
            # create the analytical lines
            # one move line per invoice line
            iml = self._get_analytic_lines(cr, uid, inv.id, context=ctx)
            # check if taxes are all computed
            compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)
            self.check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)

            # I disabled the check_total feature
            if self.pool['res.users'].has_group(cr, uid, 'account.group_supplier_inv_check_total'):
                if (inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0)):
                    raise osv.except_osv(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise osv.except_osv(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # one move line per tax line
            iml += ait_obj.move_line_get(cr, uid, inv.id)

            entry_type = ''
            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
                entry_type = 'journal_pur_voucher'
                if inv.type == 'in_refund':
                    entry_type = 'cont_voucher'
            else:
                ref = self._convert_ref(cr, uid, inv.number)
                entry_type = 'journal_sale_vou'
                if inv.type == 'out_refund':
                    entry_type = 'cont_voucher'

            diff_currency_p = inv.currency_id.id <> company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total = 0
            total_currency = 0
            total, total_currency, iml = self.compute_invoice_totals(cr, uid, inv, company_currency, ref, iml, context=ctx)
            acc_id = inv.account_id.id

            name = inv['name'] or inv['supplier_invoice_number'] or '/'
            totlines = False
            if inv.payment_term:
                totlines = payment_term_obj.compute(cr,
                        uid, inv.payment_term.id, total, inv.date_invoice or False, context=ctx)
            if totlines:
                res_amount_currency = total_currency
                i = 0
                ctx.update({'date': inv.date_invoice})
                for t in totlines:
                    if inv.currency_id.id != company_currency:
                        amount_currency = cur_obj.compute(cr, uid, company_currency, inv.currency_id.id, t[1], context=ctx)
                    else:
                        amount_currency = False

                    # last line add the diff
                    res_amount_currency -= amount_currency or 0
                    i += 1
                    if i == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': acc_id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency_p \
                                and amount_currency or False,
                        'currency_id': diff_currency_p \
                                and inv.currency_id.id or False,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': acc_id,
                    'date_maturity': inv.date_due or False,
                    'amount_currency': diff_currency_p \
                            and total_currency or False,
                    'currency_id': diff_currency_p \
                            and inv.currency_id.id or False,
                    'ref': ref
            })

            part = self.pool.get("res.partner")._find_accounting_partner(inv.partner_id)

            line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part.id, inv.date_invoice, context=ctx)),iml)

            line = self.group_lines(cr, uid, iml, line, inv)

            journal_id = inv.journal_id.id
            journal = journal_obj.browse(cr, uid, journal_id, context=ctx)
            if journal.centralisation:
                raise osv.except_osv(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = self.finalize_invoice_move_lines(cr, uid, inv, line)

            move = {
                'ref': inv.reference and inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal_id,
                'date': inv.date_invoice,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
                # Phung them shop cho account_move
                'date_document': inv.date_document,
                'shop_id': inv.shop_id.id or False,
            }
            period_id = inv.period_id and inv.period_id.id or False
            ctx.update(company_id=inv.company_id.id,
                       account_period_prefer_normal=True)
            if not period_id:
                period_ids = period_obj.find(cr, uid, inv.date_invoice, context=ctx)
                period_id = period_ids and period_ids[0] or False
            if period_id:
                move['period_id'] = period_id
                for i in line:
                    i[2]['period_id'] = period_id

            ctx.update(invoice=inv)
            move_id = move_obj.create(cr, uid, move, context=ctx)
            new_move_name = move_obj.browse(cr, uid, move_id, context=ctx).name
            # make the invoice point to that move
            self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name}, context=ctx)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move_obj.post(cr, uid, [move_id], context=ctx)
        self._log_event(cr, uid, ids)
        return True
     
    def invoice_pay_customer(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_dialog_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'payment_expected_currency': inv.currency_id.id,
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                'default_reference': inv.name,
                'default_shop_id':inv.shop_id.id or False,
                'close_after_process': True,
                'invoice_type': inv.type,
                'invoice_id': inv.id,
                'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }
     
account_invoice()

class account_move(osv.osv):
    _inherit = "account.move"

    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop', states={'posted':[('readonly',True)]}),
        'date_document': fields.date('Document Date', states={'posted':[('readonly',True)]}),
    }
    
    def _get_shop_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.context_shop_id.id or False
    
    _defaults = {
        'shop_id': _get_shop_id,
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('date',False) and not vals.get('date_document',False):
            vals.update({'date_document': vals['date']})
        return super(account_move, self).create(cr, uid, vals, context)
    
    def _auto_init(self, cr, context=None):
        super(account_move, self)._auto_init(cr, context)
        cr.execute('''
        UPDATE account_move
        SET date_document = date
        where date_document IS NULL
        ''')
    
account_move()

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    
    _columns = {
        'shop_id': fields.related('move_id', 'shop_id', type='many2one', relation='sale.shop', string='Shop', readonly=True, store=True),
    }
    
account_move_line()

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
        if not journal_id:
            return False
        res = super(account_voucher, self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=context)
        if journal_id:
            journal_data = self.pool.get('account.journal').browse(cr, uid,journal_id)
            res['value']['account_id'] = journal_data.default_debit_account_id.id or journal_data.default_credit_account_id.id or False
        return res
    
    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'date_document': fields.date('Document Date', readonly=True, states={'draft':[('readonly',False)]},),
        
        'reference_number': fields.char('Number', size=32, readonly=True, states={'draft':[('readonly',False)]}),
        'batch_id': fields.many2one('account.voucher.batch', 'Related Batch', ondelete='cascade'),
        'partner_bank_id':fields.many2one('res.partner.bank', 'Partner Bank', required=False, readonly=True, states={'draft':[('readonly',False)]}),
        'company_bank_id':fields.many2one('res.partner.bank', 'Company Bank', required=False, readonly=True, states={'draft':[('readonly',False)]}),
        'unshow_financial_report':fields.boolean('Không khai báo thuế'),
    }

    def _get_shop_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.context_shop_id.id or False
    
    _defaults = {
        'shop_id': _get_shop_id,
        
        'unshow_financial_report':False,
    }
    
    def account_move_get(self, cr, uid, voucher_id, context=None):
        '''
        This method prepare the creation of the account move related to the given voucher.

        :param voucher_id: Id of voucher for which we are creating account_move.
        :return: mapping between fieldname and value of account move to create
        :rtype: dict
        '''
        seq_obj = self.pool.get('ir.sequence')
        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        if voucher.number:
            name = voucher.number
        elif voucher.journal_id.sequence_id:
            if not voucher.journal_id.sequence_id.active:
                raise osv.except_osv(_('Configuration Error !'),
                    _('Please activate the sequence of selected journal !'))
            c = dict(context)
            c.update({'fiscalyear_id': voucher.period_id.fiscalyear_id.id})
            name = seq_obj.next_by_id(cr, uid, voucher.journal_id.sequence_id.id, context=c)
        else:
            raise osv.except_osv(_('Error!'),
                        _('Please define a sequence on the journal.'))
        if not voucher.reference:
            ref = name.replace('/','')
        else:
            ref = voucher.reference

        move = {
            'name': name,
            'journal_id': voucher.journal_id.id,
            'narration': voucher.narration,
            'date': voucher.date,
            'ref': ref,
            'period_id': voucher.period_id.id,
            'shop_id': voucher.shop_id.id or False,
            'date_document': voucher.date_document,
        }
        return move
    
    def _auto_init(self, cr, context=None):
        super(account_voucher, self)._auto_init(cr, context)
        cr.execute('''
        UPDATE account_voucher
        SET date_document = date
        where date_document IS NULL
        ''')
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('date',False) and not vals.get('date_document',False):
            vals.update({'date_document': vals['date']})
        return super(account_voucher, self).create(cr, uid, vals, context)
    
account_voucher()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: