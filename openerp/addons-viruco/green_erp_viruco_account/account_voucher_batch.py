# -*- coding: utf-8 -*-
import time
from lxml import etree
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools import float_compare
import netsvc
from openerp import tools
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

class account_voucher_batch(osv.osv):
    _name = 'account.voucher.batch'
    _order = 'name desc'
    
    def _get_total(self, cr, uid, ids, name, args, context=None):
        if not ids: return {}
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            amount = 0.0
            for voucher in record.voucher_lines:
                amount += voucher.amount
            res[record.id] =  amount
        return res
    
    _columns = {
            'name': fields.char('Number', size=128, required=False, readonly=False),
            'shop_id': fields.many2one('sale.shop', 'Shop', required=True, states={'draft':[('readonly',False)]}),
            'description': fields.text('Description', required=True),
            'date': fields.date('Date', required=True, readonly=True, states={'draft':[('readonly',False)]}),
            'assign_user': fields.char('Assign User', size = 128, required = True, readonly=True, states={'draft':[('readonly',False)]},),
            'journal_id':fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft':[('readonly',False)]}),
            'voucher_lines': fields.one2many('account.voucher', 'batch_id', 'Voucher lines', required=True, readonly=True, states={'draft':[('readonly',False)]}),
            'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True, states={'draft':[('readonly',False)]}),
            'account_id':fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft':[('readonly',False)]}),
            'type':fields.selection(
                [('receive','Receive'),
                 ('payment','Payment'),
                ], 'Type', size=32),
                
            'write_date':  fields.datetime('Last Modification', readonly=True),
            'create_date': fields.datetime('Creation Date', readonly=True),
            'write_uid':  fields.many2one('res.users', 'Updated by', readonly=True),
            'create_uid': fields.many2one('res.users', 'Created by', readonly=True),
            
            'amount': fields.function(_get_total, string='Amount', type='float', digits_compute=dp.get_precision('Account'), readonly=True), 
                                               
            'state':fields.selection(
                [('draft','Draft'),
                 ('cancel','Cancelled'),
                 ('posted','Posted')
                ], 'Status', readonly=True, size=32),
            'partner_bank_id':fields.many2one('res.partner.bank', 'Partner Bank', required=False, readonly=True, states={'draft':[('readonly',False)]}),
            'company_bank_id':fields.many2one('res.partner.bank', 'Company Bank', required=False, readonly=True, states={'draft':[('readonly',False)]}),
            'type_journal_rel': fields.related('journal_id', 'type', type='selection',selection=[('sale', 'Sale'),
                                                                                                 ('sale_refund','Sale Refund'), 
                                                                                                 ('purchase', 'Purchase'), 
                                                                                                 ('purchase_refund','Purchase Refund'), 
                                                                                                 ('cash', 'Cash'), 
                                                                                                 ('bank', 'Bank and Checks'), 
                                                                                                 ('general', 'General'), 
                                                                                                 ('situation', 'Opening/Closing Situation')], string='Type Rel'),
        
        }
    
    def print_eximbank_report(self, cr, uid, ids, context=None): 
        datas = {'ids': ids}
        datas['model'] = 'account.voucher.batch'
        datas['form'] = self.read(cr, uid, ids)[0]        
        return {'type': 'ir.actions.report.xml', 'report_name': 'eximbank_report' , 'datas': datas}
    
    def _get_assign_user(self, cr, uid, context=None):
        res = self.pool.get('res.users').read(cr, uid, uid, ['name'])['name']
        return res
    
    def _get_journal(self, cr, uid, context=None):
        ttype = ['cash','bank']
        journal_pool = self.pool.get('account.journal')
        res = journal_pool.search(cr, uid, [('type', 'in', ttype)], limit=1)
        return res and res[0] or False
    
    def _get_shop_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.context_shop_id.id or False
    
    _defaults = {
        'state': 'draft',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'assign_user':_get_assign_user,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.voucher.batch',context=c),
        #get Bank and Cash Journal firstly
        'journal_id':_get_journal,
        'shop_id': _get_shop_id,
        'type': 'payment',
    }
    
    def onchange_journal(self, cr, uid, ids, journal_id, context=None):
        if not journal_id:
            return False
        res = {'value': {}}
        if journal_id:
            journal_data = self.pool.get('account.journal').browse(cr, uid,journal_id)
            res['value']['account_id'] = journal_data.default_debit_account_id.id or journal_data.default_credit_account_id.id or False
        return res
    
    def validate(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for record in self.browse(cr, uid, ids, context=context):
            for voucher in record.voucher_lines:
                if record.state == 'draft':
                    wf_service.trg_validate(uid, 'account.voucher', voucher.id, 'proforma_voucher', cr)
            number = record.name
            if not record.name:
                number = self.pool.get('ir.sequence').get(cr, uid, 'account.voucher.batch')
            self.write(cr, uid, [record.id], {'state':'posted','name':number})
        return True
    
    def cancel(self, cr, uid, ids, context=None):
#         wf_service = netsvc.LocalService("workflow")
#         for record in self.browse(cr, uid, ids, context=context):
#             for voucher in record.voucher_lines:
#                 if record.state in ['draft','posted']:
#                     wf_service.trg_validate(uid, 'account.voucher', voucher.id, 'cancel_voucher', cr)
        
        voucher_pool = self.pool.get('account.voucher')
        for record in self.browse(cr, uid, ids, context=context):
            for voucher in record.voucher_lines:
                if record.state in ['draft','posted']:
                    voucher_pool.cancel_voucher(cr, uid, [voucher.id])
                      
        self.write(cr, uid, ids, {'state':'cancel'})
        return True
    
    def action_cancel_draft(self, cr, uid, ids, context=None):
        voucher_pool = self.pool.get('account.voucher')
        for record in self.browse(cr, uid, ids, context=context):
            for voucher in record.voucher_lines:
                if record.state in ['cancel']:
                    voucher_pool.action_cancel_draft(cr, uid, [voucher.id])
        self.write(cr, uid, ids, {'state':'draft'})
        return True
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        journal_obj = self.pool.get('account.journal')
        partner_banks_pool = self.pool.get('res.partner.bank')
        if context is None:
            context = {}
        res = super(account_voucher_batch,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        type = context.get('voucher_journal_type', False)
                
        doc = etree.XML(res['arch'])
        if type and type[0] == 'cash':
            for node in doc.xpath("//field[@name='company_bank_id']"):
                node.set('invisible', '1')
            for node in doc.xpath("//field[@name='partner_bank_id']"):
                node.set('invisible', '1')
            
            xarch, xfields = self._view_look_dom_arch(cr, uid, doc, view_id, context=context)
            res['arch'] = xarch
            res['fields'] = xfields
        
        for field in res['fields']:
            if field == 'journal_id' and type:
                journal_select = journal_obj._name_search(cr, uid, '', [('type', 'in', type)], context=context, limit=None, name_get_uid=1)
                res['fields'][field]['selection'] = journal_select
                
            if field == 'company_bank_id':
                company = self.pool.get('res.users').browse(cr, uid, uid).company_id
                banks_ids = partner_banks_pool.search(cr, uid, [('partner_id','=', company.partner_id.id)])
                partner_banks_ids = [(line.id, line.bank_name) for line in partner_banks_pool.browse(cr, uid, banks_ids)] 
                res['fields'][field]['selection'] = partner_banks_ids
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        for t in self.read(cr, uid, ids, ['state'], context=context):
            if t['state'] not in ('draft', 'cancel'):
                raise osv.except_osv(_('Invalid Action!'), _('Cannot delete Voucher Batch which are already posted.'))
        return super(account_voucher_batch, self).unlink(cr, uid, ids, context=context)
    
    def print_phieuchi(self, cr, uid, ids, context=None): 
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'general_phieu_chi',
            }
account_voucher_batch()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
