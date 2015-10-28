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

class account_voucher(osv.osv):
    _inherit = "account.voucher"
    
    _columns = {
        'hop_dong_id':fields.many2one('hop.dong','Hợp đồng',readonly=True,states={'draft': [('readonly', False)]}),
        'nguoi_de_nghi_id':fields.many2one('res.users','Người đề nghị'),
        'dot_thanhtoan_ids':fields.many2many('account.voucher', 'cac_dot_thanh_toan_ref', 'parent_id', 'voucher_id','Các đợt thanh toán',readonly=True),
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'date_document': fields.date('Document Date', readonly=True, states={'draft':[('readonly',False)]},),
'account_id':fields.many2one('account.account', 'Account', readonly=True, states={'draft':[('readonly',False)]}),
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
        'nguoi_de_nghi_id': lambda self, cr, uid, context=None: uid,
        'shop_id': _get_shop_id,

        'unshow_financial_report':False
    }
    
    def onchange_hopdong_id(self, cr, uid, ids, hop_dong_id, context=None):
        if context is None:
            context = {}
        vals = {}
        vals['dot_thanhtoan_ids'] = False
        if hop_dong_id:
            hop_dong = self.pool.get('hop.dong').browse(cr, uid, hop_dong_id)
            dot_thanhtoan_ids = []
            if ids:
                voucher_ids = self.search(cr, uid, [('hop_dong_id','=',hop_dong_id),('id','not in',ids),('state','=','posted')],order='id')
            else:
                voucher_ids = self.search(cr, uid, [('hop_dong_id','=',hop_dong_id),('state','=','posted')],order='id')
            vals['dot_thanhtoan_ids']=[(6,0,voucher_ids)]
            vals['partner_id']=hop_dong.partner_id.id
        return {'value':vals}
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('date',False) and not vals.get('date_document',False):
            vals.update({'date_document': vals['date']})
        if vals.get('hop_dong_id',False):
            voucher_ids = self.search(cr, uid, [('hop_dong_id','=',vals['hop_dong_id']),('state','=','posted')])
            vals['dot_thanhtoan_ids']=[(6,0,voucher_ids)]
        new_id = super(account_voucher, self).create(cr, uid, vals, context) 
        if context.get('phieuthu_chi',False):
            self.compute_tax(cr, uid, [new_id], context)
        return new_id
    
    def compute_tax_pt(self, cr, uid, voucher_id, context=None):
        tax_pool = self.pool.get('account.tax')
        partner_pool = self.pool.get('res.partner')
        position_pool = self.pool.get('account.fiscal.position')
        voucher_line_pool = self.pool.get('account.voucher.line')
        voucher_pool = self.pool.get('account.voucher')
        if context is None: context = {}

        voucher = voucher_pool.browse(cr, uid, voucher_id, context=context)
        voucher_amount = 0.0
        for line in voucher.line_ids:
            voucher_amount += line.untax_amount or line.amount
            line.amount = line.untax_amount or line.amount
            voucher_line_pool.write(cr, uid, [line.id], {'amount':line.amount, 'untax_amount':line.untax_amount})

        if not voucher.tax_id:
            return {'amount':voucher_amount, 'tax_amount':0.0}

        tax = [tax_pool.browse(cr, uid, voucher.tax_id.id, context=context)]
        partner = partner_pool.browse(cr, uid, voucher.partner_id.id, context=context) or False
        taxes = position_pool.map_tax(cr, uid, partner and partner.property_account_position or False, tax)
        tax = tax_pool.browse(cr, uid, taxes, context=context)

        total = voucher_amount
        total_tax = 0.0

        if not tax[0].price_include:
            for line in voucher.line_ids:
                for tax_line in tax_pool.compute_all(cr, uid, tax, line.amount, 1).get('taxes', []):
                    total_tax += tax_line.get('amount', 0.0)
            total += total_tax
        else:
            for line in voucher.line_ids:
                line_total = 0.0
                line_tax = 0.0

                for tax_line in tax_pool.compute_all(cr, uid, tax, line.untax_amount or line.amount, 1).get('taxes', []):
                    line_tax += tax_line.get('amount', 0.0)
                    line_total += tax_line.get('price_unit')
                total_tax += line_tax
                untax_amount = line.untax_amount or line.amount
                voucher_line_pool.write(cr, uid, [line.id], {'amount':line_total, 'untax_amount':untax_amount})

        return {'amount':total, 'tax_amount':total_tax}
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if vals.get('hop_dong_id',False):
            voucher_ids = self.search(cr, uid, [('hop_dong_id','=',vals['hop_dong_id']),('state','=','posted'),('id','not in',ids)])
            vals['dot_thanhtoan_ids']=[(6,0,voucher_ids)]
        new_id = super(account_voucher, self).write(cr, uid, ids, vals, context)
        if context.get('phieuthu_chi',False):
            for id in ids: 
                amount_val = self.compute_tax_pt(cr, uid, id, context)
                cr.execute('update account_voucher set amount=%s, tax_amount=%s',(amount_val['amount'],amount_val['tax_amount'],))
        return new_id
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, hop_dong_id=False, context=None):
        if not journal_id:
            return {}
        if context is None:
            context = {}
        #TODO: comment me and use me directly in the sales/purchases views
        res = self.basic_onchange_partner(cr, uid, ids, partner_id, journal_id, ttype, context=context)
        if ttype in ['sale', 'purchase']:
            return res
        ctx = context.copy()
        # not passing the payment_rate currency and the payment_rate in the context but it's ok because they are reset in recompute_payment_rate
        ctx.update({'date': date})
        vals = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=ctx)
        vals2 = self.recompute_payment_rate(cr, uid, ids, vals, currency_id, date, ttype, journal_id, amount, context=context)
        for key in vals.keys():
            res[key].update(vals[key])
        for key in vals2.keys():
            res[key].update(vals2[key])
        #TODO: can probably be removed now
        #TODO: onchange_partner_id() should not returns [pre_line, line_dr_ids, payment_rate...] for type sale, and not 
        # [pre_line, line_cr_ids, payment_rate...] for type purchase.
        # We should definitively split account.voucher object in two and make distinct on_change functions. In the 
        # meanwhile, bellow lines must be there because the fields aren't present in the view, what crashes if the 
        # onchange returns a value for them
        if ttype == 'sale':
            del(res['value']['line_dr_ids'])
            del(res['value']['pre_line'])
            del(res['value']['payment_rate'])
        elif ttype == 'purchase':
            del(res['value']['line_cr_ids'])
            del(res['value']['pre_line'])
            del(res['value']['payment_rate'])
        res['value']['line_dr_ids'] = False
        res['value']['line_cr_ids'] = False
        if partner_id and hop_dong_id:
            hop_dong = self.pool.get('hop.dong').browse(cr, uid, hop_dong_id)
            if partner_id!=hop_dong.partner_id.id:
                res['value']['hop_dong_id'] = False
        return res
    
    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ctx.update({'date': date})
        #read the voucher rate with the right date in the context
        currency_id = currency_id or self.pool.get('res.company').browse(cr, uid, company_id, context=ctx).currency_id.id
        voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        ctx.update({
            'voucher_special_currency': payment_rate_currency_id,
            'voucher_special_currency_rate': rate * voucher_rate})
        res = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=ctx)
        vals = self.onchange_rate(cr, uid, ids, rate, amount, currency_id, payment_rate_currency_id, company_id, context=ctx)
        for key in vals.keys():
            res[key].update(vals[key])
        res['value']['line_dr_ids'] = False
        res['value']['line_cr_ids'] = False
        return res
    
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
        if context is None:
            context = {}
        if not journal_id:
            return False
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        if ttype in ('sale', 'receipt'):
            account_id = journal.default_debit_account_id
        elif ttype in ('purchase', 'payment'):
            account_id = journal.default_credit_account_id
        else:
            account_id = journal.default_credit_account_id or journal.default_debit_account_id
        tax_id = False
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id

        vals = {'value':{} }
        if ttype in ('sale', 'purchase'):
            vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
            vals['value'].update({'tax_id':tax_id,'amount': amount})
        currency_id = False
        if journal.currency:
            currency_id = journal.currency.id
        else:
            currency_id = journal.company_id.currency_id.id
        vals['value'].update({'currency_id': currency_id, 'payment_rate_currency_id': currency_id})
        #in case we want to register the payment directly from an invoice, it's confusing to allow to switch the journal 
        #without seeing that the amount is expressed in the journal currency, and not in the invoice currency. So to avoid
        #this common mistake, we simply reset the amount to 0 if the currency is not the invoice currency.
        if context.get('payment_expected_currency') and currency_id != context.get('payment_expected_currency'):
            vals['value']['amount'] = 0
            amount = 0
#         if partner_id:
#             res = self.onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context)
#             for key in res.keys():
#                 vals[key].update(res[key])
                
        vals['value']['line_dr_ids'] = False
        vals['value']['line_cr_ids'] = False
        if journal_id:
            journal_data = self.pool.get('account.journal').browse(cr, uid,journal_id)
            vals['value']['account_id'] = journal_data.default_debit_account_id.id or journal_data.default_credit_account_id.id or False
        return vals
    
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
        
    def voucher_move_line_create(self, cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        tot_line = line_total
        rec_lst_ids = []

        date = self.read(cr, uid, voucher_id, ['date'], context=context)['date']
        ctx = context.copy()
        ctx.update({'date': date})
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=ctx)
        voucher_currency = voucher.journal_id.currency or voucher.company_id.currency_id
        ctx.update({
            'voucher_special_currency_rate': voucher_currency.rate * voucher.payment_rate ,
            'voucher_special_currency': voucher.payment_rate_currency_id and voucher.payment_rate_currency_id.id or False,})
        prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        for line in voucher.line_ids:
            #create one move line per voucher line where amount is not 0.0
            # AND (second part of the clause) only if the original move line was not having debit = credit = 0 (which is a legal value)
            if not line.amount and not (line.move_line_id and not float_compare(line.move_line_id.debit, line.move_line_id.credit, precision_digits=prec) and not float_compare(line.move_line_id.debit, 0.0, precision_digits=prec)):
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context, so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(cr, uid, line.untax_amount or line.amount, voucher.id, context=ctx)
            # if the amount encoded in voucher is equal to the amount unreconciled, we need to compute the
            # currency rate difference
            if line.amount == line.amount_unreconciled:
                if not line.move_line_id:
                    raise osv.except_osv(_('Wrong voucher line'),_("The invoice you are willing to pay is not valid anymore."))
                sign = line.type =='dr' and -1 or 1
                currency_rate_difference = sign * (line.move_line_id.amount_residual - amount)
            else:
                currency_rate_difference = 0.0
            move_line = {
                'journal_id': voucher.journal_id.id,
                'period_id': voucher.period_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': voucher.partner_id.id,
                'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': 0.0,
                'debit': 0.0,
                'date': voucher.date,
                'type_lctt': line.type_lctt,
            }
            if amount < 0:
                amount = -amount
                if line.type == 'dr':
                    line.type = 'cr'
                else:
                    line.type = 'dr'

            if (line.type=='dr'):
                tot_line += amount
                move_line['debit'] = amount
            else:
                tot_line -= amount
                move_line['credit'] = amount

            if voucher.tax_id and voucher.type in ('sale', 'purchase'):
                move_line.update({
                    'account_tax_id': voucher.tax_id.id,
                })

            if move_line.get('account_tax_id', False):
                tax_data = tax_obj.browse(cr, uid, [move_line['account_tax_id']], context=context)[0]
                if not (tax_data.base_code_id and tax_data.tax_code_id):
                    raise osv.except_osv(_('No Account Base Code and Account Tax Code!'),_("You have to configure account base code and account tax code on the '%s' tax!") % (tax_data.name))

            # compute the amount in foreign currency
            foreign_currency_diff = 0.0
            amount_currency = False
            if line.move_line_id:
                # We want to set it on the account move line as soon as the original line had a foreign currency
                if line.move_line_id.currency_id and line.move_line_id.currency_id.id != company_currency:
                    # we compute the amount in that foreign currency.
                    if line.move_line_id.currency_id.id == current_currency:
                        # if the voucher and the voucher line share the same currency, there is no computation to do
                        sign = (move_line['debit'] - move_line['credit']) < 0 and -1 or 1
                        amount_currency = sign * (line.amount)
                    else:
                        # if the rate is specified on the voucher, it will be used thanks to the special keys in the context
                        # otherwise we use the rates of the system
                        amount_currency = currency_obj.compute(cr, uid, company_currency, line.move_line_id.currency_id.id, move_line['debit']-move_line['credit'], context=ctx)
                if line.amount == line.amount_unreconciled:
                    foreign_currency_diff = line.move_line_id.amount_residual_currency - abs(amount_currency)

            move_line['amount_currency'] = amount_currency
            voucher_line = move_line_obj.create(cr, uid, move_line)
            rec_ids = [voucher_line, line.move_line_id.id]

            if not currency_obj.is_zero(cr, uid, voucher.company_id.currency_id, currency_rate_difference):
                # Change difference entry in company currency
                exch_lines = self._get_exchange_lines(cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                new_id = move_line_obj.create(cr, uid, exch_lines[0],context)
                move_line_obj.create(cr, uid, exch_lines[1], context)
                rec_ids.append(new_id)

            if line.move_line_id and line.move_line_id.currency_id and not currency_obj.is_zero(cr, uid, line.move_line_id.currency_id, foreign_currency_diff):
                # Change difference entry in voucher currency
                move_line_foreign_currency = {
                    'journal_id': line.voucher_id.journal_id.id,
                    'period_id': line.voucher_id.period_id.id,
                    'name': _('change')+': '+(line.name or '/'),
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': line.voucher_id.partner_id.id,
                    'currency_id': line.move_line_id.currency_id.id,
                    'amount_currency': -1 * foreign_currency_diff,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': line.voucher_id.date,
                    'type_lctt': line.type_lctt,
                }
                new_id = move_line_obj.create(cr, uid, move_line_foreign_currency, context=context)
                rec_ids.append(new_id)
            if line.move_line_id.id:
                rec_lst_ids.append(rec_ids)
        return (tot_line, rec_lst_ids)

account_voucher()

class account_voucher_line(osv.osv):
    _inherit = 'account.voucher.line'
    _columns = {
        'type_lctt': fields.selection([('hdkd','Hoạt động kinh doanh'),
                                       ('hddt','Hoạt động đầu tư'),
                                       ('hdtc','Hoạt động tài chính')], 'Loại LCTT'),
    }
    
    _defaults = {
        'type_lctt': 'hdkd',
    }
    
account_voucher_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
