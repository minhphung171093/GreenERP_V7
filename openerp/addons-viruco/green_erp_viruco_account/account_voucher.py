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
        if vals.get('date',False) and not vals.get('date_document',False):
            vals.update({'date_document': vals['date']})
        if vals.get('hop_dong_id',False):
            voucher_ids = self.search(cr, uid, [('hop_dong_id','=',vals['hop_dong_id']),('state','=','posted')])
            vals['dot_thanhtoan_ids']=[(6,0,voucher_ids)]
        return super(account_voucher,self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('hop_dong_id',False):
            voucher_ids = self.search(cr, uid, [('hop_dong_id','=',vals['hop_dong_id']),('state','=','posted'),('id','not in',ids)])
            vals['dot_thanhtoan_ids']=[(6,0,voucher_ids)]
        return super(account_voucher,self).write(cr, uid, ids, vals, context)
    
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
    
account_voucher()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
