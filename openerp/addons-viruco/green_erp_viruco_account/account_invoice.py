# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import time
from datetime import date
from datetime import timedelta
from datetime import datetime
import calendar
import openerp.addons.decimal_precision as dp
import codecs
import os
from xlrd import open_workbook,xldate_as_tuple
from openerp import modules

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    _columns = {
        'hop_dong_id':fields.many2one('hop.dong','Hợp đồng'),
        'shop_id': fields.many2one('sale.shop', 'Shop', readonly=True, states={'draft':[('readonly',False)]}),
        'date_document': fields.date('Document Date', readonly=True, states={'draft':[('readonly',False)]}),
        'reference_number': fields.char('Reference Number', size=64, readonly=True, states={'draft':[('readonly',False)]}),
        'ki_hieu_hd': fields.char('Kí hiệu hóa đơn', size=64, states={'draft':[('readonly',False)]}),
        'so_hd': fields.char('Số hóa đơn', size=64, states={'draft':[('readonly',False)]}),
    }
    
    def _get_shop_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.context_shop_id.id or False
    
    _defaults = {
         'shop_id': _get_shop_id,
         'date_document': fields.date.context_today,
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
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(account_invoice, self).write(cr, uid, ids, vals, context=context)    
        for inv in self.browse(cr, uid, ids, context=context):
            if 'state' in vals and vals['state']=='open':
                if not inv.ki_hieu_hd:
                    raise osv.except_osv(_('Cảnh báo!'),_('Bạn chưa nhập ký hiệu hoá đơn.!'))
                if not inv.so_hd:
                    raise osv.except_osv(_('Cảnh báo!'),_('Bạn chưa nhập số hoá đơn.!'))
                if inv.type=='out_invoice':
                    for line in inv.invoice_line:
#                         if line.stock_move_id and line.stock_move_id.picking_id.invoice_state!='invoiced':
#                             raise osv.except_osv(_('Cảnh báo!'),_('Phiếu nhập %s chưa có hoá đơn.!')%(line.stock_move_id.name))
                        if line.stock_move_id:
                            sql = '''
                                select * from account_invoice
                                    where type='in_invoice' and state in ('open','paid') and id in (select invoice_id from account_invoice_line where stock_move_id in (
                                         select id from stock_move where picking_id in(select picking_in_id from stock_move where id = %s)))
                            '''%(line.stock_move_id.id)
                            cr.execute(sql)              
                            inv_ids = cr.fetchall()
                            if inv_ids:
                                sql='''
                                    update account_invoice set state='open' where id = %s
                                '''%(inv.id)

                            else:
                                raise osv.except_osv(_('Cảnh báo!'),_('Phiếu nhập %s chưa có hoá đơn hoặc hoá đơn chưa được duyệt.!')%(line.stock_move_id.picking_in_id.origin))
        return new_write
account_invoice()

class group_invoice(osv.osv_memory):
    _name = "group.invoice"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(group_invoice, self).default_get(cr, uid, fields, context=context)
        invoice_ids = context.get('active_ids', [])
        partner_id = []
        for invoice in self.pool.get('account.invoice').browse(cr, uid, invoice_ids):
            if not partner_id:
                partner_id = invoice.partner_id.id
            if invoice.state != 'draft':
                raise osv.except_osv(_('Cảnh báo!'),_('Không thể gộp hóa đơn có trạng thái khác nháp!'))
            if partner_id != invoice.partner_id.id:
                if invoice.type in ['out_invoice','out_refund']:
                    raise osv.except_osv(_('Cảnh báo!'),_('Không thể gộp hóa đơn khác khách hàng!'))
                if invoice.type in ['in_invoice','in_refund']:
                    raise osv.except_osv(_('Cảnh báo!'),_('Không thể gộp hóa đơn khác nhà cung cấp!'))
        return res
    
    _columns = {
        'name':fields.text('Name'),
    }
    
    def bt_gop(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice_ids = context.get('active_ids', [])
        invoice_obj = self.pool.get('account.invoice')
        invoice_id = False
        for seq,invoice in enumerate(self.pool.get('account.invoice').browse(cr, uid, invoice_ids)):
            if seq == 0:
                invoice_id = invoice.id
                continue
            cr.execute(''' update account_invoice_line set invoice_id=%s where invoice_id=%s ''',(invoice_id,invoice.id,))
            cr.execute('delete from account_invoice where id=%s',(invoice.id,))
        if invoice_id:
            invoice_obj.button_reset_taxes(cr, uid, [invoice_id])
            invoice = invoice_obj.browse(cr, uid, invoice_id)
            model_data = self.pool.get('ir.model.data')
            if invoice.type=='out_invoice':
                tree_view = model_data.get_object_reference(cr, uid, 'account', 'invoice_tree')
                form_view = model_data.get_object_reference(cr, uid, 'account', 'invoice_form')
                return {
                        'name': 'Hóa đơn khách hàng',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'account.invoice',
                        'views': [(form_view and form_view[1] or False, 'form'), (tree_view and tree_view[1] or False, 'tree')],
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'res_id':invoice_id,
                    }
            if invoice.type=='in_invoice':
                tree_view = model_data.get_object_reference(cr, uid, 'account', 'invoice_tree')
                form_view = model_data.get_object_reference(cr, uid, 'account', 'invoice_supplier_form')
                return {
                        'name': 'Hóa đơn nhà cung cấp',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'views': [(form_view and form_view[1] or False, 'form'),(tree_view and tree_view[1] or False, 'tree')],
                        'res_model': 'account.invoice',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'res_id':invoice_id,
                    }
        return {'type': 'ir.actions.act_window_close'}
    
group_invoice()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
