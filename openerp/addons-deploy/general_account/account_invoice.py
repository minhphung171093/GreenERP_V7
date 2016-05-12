# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

import time
from lxml import etree
import openerp.addons.decimal_precision as dp
import openerp.exceptions

from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
from datetime import datetime

class res_currency(osv.osv):
    _inherit = "res.currency"
    
    #Thanh: Update Rouding for VND currency to 1.0
    def _auto_init(self, cr, context=None):
        super(res_currency, self)._auto_init(cr, context)
        cr.execute('''
            UPDATE res_currency
            SET rounding = 1.0
            WHERE name='VND'
        ''')
        
res_currency()

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    def copy_invoice(self,cr,uid,ids,context=None):
        default = {}
        for inv in self.browse(cr,uid,ids):
            default.update({
                'rel_invoice_id':ids[0],
            })
            if inv.type == 'out_invoice':
                default.update({
                    'invoice_dieuchinh':True,
                })
            invoice_id = self.copy(cr, uid, ids[0],default,context=context)
            header = u"HĐ Điều chỉnh"
            data_pool = self.pool.get('ir.model.data')
            #action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree")
            form_id = data_pool.get_object_reference(cr, uid, 'general_account', 'invoice_dieuchinh_form')
            form_res = form_id and form_id[1] or False
            tree_id = data_pool.get_object_reference(cr, uid, 'account', 'invoice_tree')
            tree_res = tree_id and tree_id[1] or False
            
            if tree_res and form_res:
                return {
                    'name':_(header),
                    'view_mode': 'tree, form',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'account.invoice',
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'current',
                    'domain': "[('id', 'in', %s)]" % [invoice_id],
                    'views': [(tree_res, 'tree'), (form_res, 'form')],
                    'context': {}
                }
            
            return invoice_id
    
    #Thanh: Just get the Number for Linking many2one
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        return [(r['id'], '%s' % (r['number'] or '')) for r in self.read(cr, uid, ids, ['number'], context, load='_classic_write')]
    
    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()
    
    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()
    
    def _get_invoice_from_line(self, cr, uid, ids, context=None):
        move = {}
        for line in self.pool.get('account.move.line').browse(cr, uid, ids, context=context):
            if line.reconcile_partial_id:
                for line2 in line.reconcile_partial_id.line_partial_ids:
                    move[line2.move_id.id] = True
            if line.reconcile_id:
                for line2 in line.reconcile_id.line_id:
                    move[line2.move_id.id] = True
        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids
    
    def _get_invoice_from_reconcile(self, cr, uid, ids, context=None):
        move = {}
        for r in self.pool.get('account.move.reconcile').browse(cr, uid, ids, context=context):
            for line in r.line_partial_ids:
                move[line.move_id.id] = True
            for line in r.line_id:
                move[line.move_id.id] = True

        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids
    
    #Thanh: Change the way computing Balance
    def _amount_residual(self, cr, uid, ids, name, args, context=None):
        result = super(account_invoice, self)._amount_residual(cr, uid, ids, name, args, context)
        for invoice in self.browse(cr, uid, ids, context=context):
            result[invoice.id] = 0.0
            if invoice.move_id:
                for m in invoice.move_id.line_id:
                    if m.account_id.type in ('receivable','payable'):
                        if invoice.type in ['in_invoice','out_refund'] and m.date_maturity:
                            result[invoice.id] += m.amount_residual_currency or 0.0
                        if invoice.type in ['out_invoice','in_refund'] and m.date_maturity:
                            result[invoice.id] += m.amount_residual_currency or 0.0
        return result
    
    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0
            }
            for line in invoice.invoice_line:
                res[invoice.id]['amount_untaxed'] += line.price_subtotal
            for line in invoice.tax_line:
                res[invoice.id]['amount_tax'] += line.amount
            res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']
            
            #Thanh: Compute with commission
            if invoice.commission_type == 'percentage':
                res[invoice.id]['commission_amount'] = round(invoice.commission_percentage * res[invoice.id]['amount_total'] / 100, 0)
            else:
                res[invoice.id]['commission_amount'] = 0
            if invoice.commission_account_id and invoice.commission_type:
                if invoice.type in ['out_invoice','out_refund']:
                    if invoice.commission_type == 'percentage':
                        res[invoice.id]['amount_total'] = res[invoice.id]['amount_total'] - res[invoice.id]['commission_amount']
                    else:
                        res[invoice.id]['amount_total'] = res[invoice.id]['amount_total'] - invoice.commission_fix_amount
                else:
                    if invoice.commission_type == 'percentage':
                        res[invoice.id]['amount_total'] = res[invoice.id]['amount_total'] + res[invoice.id]['commission_amount']
                    else:
                        res[invoice.id]['amount_total'] = res[invoice.id]['amount_total'] + invoice.commission_fix_amount
        return res
    
    def _get_product_showin_report(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            product = ''
            for line in invoice.invoice_line:
                product = line.name
                break
            res[invoice.id] = product
        return res
    
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d-%m-%Y')
    def _compute_date_user_tz(self, cr, uid, ids, fieldnames, args, context=None):  
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = {
                'date_user_tz': False,
                'day_user_tz': False,
            }
            
            res[obj.id]['date_user_tz'] = obj.date_invoice
            res[obj.id]['day_user_tz'] = self.get_vietname_date(obj.date_invoice)
        return res
    
    def _huy_invisible(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for tt in self.browse(cr,uid,ids):
            res[tt.id] = False
            account_ids = self.pool.get('account.account').search(cr,uid,[('code', '=', '64189')])
            if tt.account_id.id == account_ids[0]:
                res[tt.id] = True
        return res
    
    def _trangthai(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for tt in self.browse(cr,uid,ids):
            if tt.state == 'draft':
                res[tt.id] = 'draft'
            elif tt.state == 'cancel':
                res[tt.id] = 'cancel'
            else:
                res[tt.id]='paid'
        return res
    
    _columns = {
        'date_user_tz': fields.function(_compute_date_user_tz, type='date', method=True, string='Date User TZ', store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['date_order'], 10),
                }, multi='tz'),
                 
            'day_user_tz': fields.function(_compute_date_user_tz, type='char', method=True, string='Day User TZ', store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['date_order'], 10),
            }, multi='tz'),
                
        'group_invoice':fields.boolean('Group invoice'),
        'shop_id': fields.many2one('sale.shop', 'Shop', readonly=True, states={'draft':[('readonly',False)]}),
        
        'number_register': fields.char('Number Register', size=64, readonly=True, states={'draft':[('readonly',False)]}),
        'reference': fields.char('Invoice Reference', size=64, help="The partner reference of this invoice.", readonly=True, states={'draft':[('readonly',False)]}),
        'reference_number': fields.char('Reference Number', size=64, readonly=True, states={'draft':[('readonly',False)]}),
        'date_document': fields.date('Document Date', readonly=True, states={'draft':[('readonly',False)]}),
        #Thanh: add field rel_invoice_id for customer refund relating to customer invoice
        'rel_invoice_id': fields.many2one('account.invoice', 'Rel invoice'),
        'reconciliation_move_ids': fields.many2many('account.move', 'reconciliation_move_rel', 'invoice_id', 'move_id', 'Reconciliation moves'),
        #Thanh: Change the way computing Balance
        'residual': fields.function(_amount_residual, digits_compute=dp.get_precision('Account'), string='Balance',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line','move_id'], 50),
                'account.invoice.tax': (_get_invoice_tax, None, 50),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 50),
                'account.move.line': (_get_invoice_from_line, None, 50),
                'account.move.reconcile': (_get_invoice_from_reconcile, None, 50),
            },
            help="Remaining amount due."),
        
        'commission_type': fields.selection([
                ('fix','Fixed Amount'),
                ('percentage','Percentage')],'Commission Type', readonly=True, states={'draft': [('readonly', False)]}),
        'commission_account_id': fields.many2one('account.account', 'Commission Account', readonly=True, states={'draft':[('readonly',False)]}),
        'commission_fix_amount': fields.float('Commission Amount', digits=(16,2), required=False, readonly=True, states={'draft': [('readonly', False)]}),
        'commission_percentage': fields.float('Commission Percentage (%)', digits=(16,2), required=False, readonly=True, states={'draft': [('readonly', False)]}),
        'commission_account_analytic_id':  fields.many2one('account.analytic.account', 'Commission Analytic Account', readonly=True, states={'draft': [('readonly', False)]}),
        'commission_amount': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Commission Amount',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line','commission_type','commission_percentage','commission_fix_amount'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='sums'),
        
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line','commission_type','commission_percentage','commission_fix_amount'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        
        'payment_mode_id': fields.many2one('res.payment.mode', 'Payment mode'),
        # kiet them 
        'supplier_inv_date':fields.date('Supplier Date', readonly=True, states={'draft':[('readonly',False)]}),
        'invoice_book_id':fields.many2one('invoice.book', 'Invoice book',readonly=True, states={'draft':[('readonly',False)]}),
        'address':fields.char('Địa chỉ giao hàng',size=300),
        #Hung them nguoi mua hang
        'buyer':fields.char('Người mua hàng'),
        'product_showin_report': fields.function(_get_product_showin_report, type='char', store=True),
        'invoice_refund': fields.boolean('Invoice Refund'),
        'invoice_dieuchinh': fields.boolean('Invoice Refund'),
#         'flag': fields.boolean('Flag'),
         'is_chiet_khau': fields.boolean('Có chiết khấu'),
         'flag': fields.function(_huy_invisible, string='Xử lý ẩn hiện nút hủy cho account 64189',
            type='boolean'),
         'ngay_xuat': fields.date('Ngày xuất', readonly=True, states={'draft':[('readonly',False)]}),
         'ngay_nhap': fields.date('Ngày nhập', readonly=True, states={'draft':[('readonly',False)]}),
         'trang_thai':fields.function(_trangthai, string='Trạng thái',
                                      type='selection', selection=[('draft','Nháp'),
                                                                   ('paid','Đã nhập hàng về'),
                                                                   ('cancel','Hủy bỏ')],
                                     ),
#         'trang_thai_dc':fields.function(_trangthai, string='Trạng thái',
#                                       type='selection', selection=[('draft','Nháp'),
#                                                                    ('paid','Chờ thanh toán')],
#                                      store={
#                                                 'account.invoice':(lambda self, cr, uid, ids, c={}: ids, ['state'], 10),
#                                             }),
#         'supplier_invoice_number': fields.char('Supplier Invoice Number', size=64, help="The reference of this invoice as provided by the supplier.", readonly=True, states={'draft':[('readonly',False)]}),
    }
    _defaults = {
#         'flag': False,
        'invoice_refund': False,
        'invoice_dieuchinh': False,
        'is_chiet_khau': False,
#         'supplier_invoice_number': '/',
                 }
    
    def onchange_ngay_nhap(self, cr, uid, ids,ngay_nhap=False, context=None):
        res = {'value':{
                        'date_invoice':False,
                      }
               }
        if ngay_nhap:
            res['value'].update({
                                'date_invoice':ngay_nhap,
                                })
            
        return res
    
    # kiet Add sinh so number
    def create(self, cr,uid,vals,context=None):
        if vals.get('invoice_book_id',False):
            book = self.pool.get("invoice.book")
            book_obj = book.browse(cr,uid,vals['invoice_book_id'])
            number = book.create_sohoadonketiep(cr,uid,vals['invoice_book_id'],context)
            vals.update({'reference_number':number,'reference':book_obj.kyhieuhoadon})
#         if vals.get('supplier_invoice_number',False):
#             if vals.get('supplier_invoice_number','/')=='/':
#                 vals['supplier_invoice_number'] = self.pool.get('ir.sequence').get(cr, uid, 'so.hd.dau.vao.seq') or '/'
        return super(account_invoice, self).create(cr, uid, vals, context)
    
    def write(self,cr,uid,ids,vals,context=None):
        if vals.get('invoice_book_id',False):
            book = self.pool.get("invoice.book")
            book_obj = book.browse(cr,uid,vals['invoice_book_id'])
            number = book.create_sohoadonketiep(cr,uid,vals['invoice_book_id'],context)
            vals.update({'reference_number':number,'reference':book_obj.kyhieuhoadon})
        if vals.get('state',False)=='open':
            for line in self.browse(cr,uid,ids):
                account_ids = self.pool.get('account.account').search(cr,uid,[('code', '=', '64189')])
                if line.account_id.id == account_ids[0]:
                    vals.update({'state':'paid'})
                    
#         if vals.get('state',False):
#             if vals['state'] == 'open':
#                 for acc_inv in self.browse(cr,uid,ids):
#                     if acc_inv.rel_invoice_id and acc_inv.type == 'out_refund':
#                         sql = '''
#                             update account_invoice set state = 'paid' where id = %s
#                         '''%(acc_inv.id)
#                         cr.execute(sql)
        return super(account_invoice, self).write(cr, uid,ids, vals, context)
        
    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        result = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id,\
            date_invoice=date_invoice, payment_term=payment_term, partner_bank_id=partner_bank_id, company_id=company_id)
        if partner_id:
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            address = self.pool.get('res.partner')._display_address(cr, uid, p, without_company=True, context=None)
            result['value'].update({'number_register':p.number_register,'address':address})
        return result
    
    def _get_commission_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        if context.get('default_type',False) and context['default_type'] in ['out_invoice']:
            property_pool = self.pool.get('admin.property')
            property_obj = property_pool._get_project_property_by_name(cr, uid, 'commission_type') or None
            if property_obj and property_obj.value:
                return property_obj.value
            return ''
        return False
    
    def _get_commission_percentage(self, cr, uid, context=None):
        if context is None:
            context = {}
        if context.get('default_type',False) and context['default_type'] in ['out_invoice']:
            property_pool = self.pool.get('admin.property')
            property_obj = property_pool._get_project_property_by_name(cr, uid, 'commission_percentage') or None
            if property_obj and property_obj.value:
                return float(property_obj.value)
            return 0.0
        return False
    
    def _get_commission_account_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        if context.get('default_type',False) and context['default_type'] in ['out_invoice']:
            property_pool = self.pool.get('admin.property')
            property_obj = property_pool._get_project_property_by_name(cr, uid, 'commission_account_id') or None
            if property_obj and property_obj.value:
                res_ids = self.pool.get('account.account').search(cr, uid, [('code','=',property_obj.value)])
                return res_ids and res_ids[0] or False
            return False
        return False
    
    def _get_shop_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.context_shop_id.id or False
    
    _defaults = {
         'date_document': fields.date.context_today,
         'commission_type': _get_commission_type,
         'commission_percentage': _get_commission_percentage,
         'commission_account_id': _get_commission_account_id,
         'shop_id': _get_shop_id,
         'group_invoice':False,
    }
    def _refund_cleanup_lines(self, cr, uid, lines, context=None):
        """Convert records to dict of values suitable for one2many line creation

            :param list(browse_record) lines: records to convert
            :return: list of command tuple for one2many line creation [(0, 0, dict of valueis), ...]
        """
        clean_lines = []
        for line in lines:
            clean_line = {}
            for field in line._all_columns.keys():
                if line._all_columns[field].column._type == 'many2one':
                    if field == 'account_id':
                        account_ids = self.pool.get('account.account').search(cr,uid,[('code', '=', '5212')])
                        clean_line[field] = account_ids[0]
                    else:
                        clean_line[field] = line[field].id
                elif line._all_columns[field].column._type not in ['many2many','one2many']:
                    clean_line[field] = line[field]
                elif field == 'invoice_line_tax_id':
                    tax_list = []
                    for tax in line[field]:
                        tax_list.append(tax.id)
                    clean_line[field] = [(6,0, tax_list)]
            clean_lines.append(clean_line)
        return map(lambda x: (0,0,x), clean_lines)
    
    def _prepare_refund(self, cr, uid, invoice, date=None, period_id=None, description=None, journal_id=None, context=None):
        """Prepare the dict of values to create the new refund from the invoice.
            This method may be overridden to implement custom
            refund generation (making sure to call super() to establish
            a clean extension chain).

            :param integer invoice_id: id of the invoice to refund
            :param dict invoice: read of the invoice to refund
            :param string date: refund creation date from the wizard
            :param integer period_id: force account.period from the wizard
            :param string description: description of the refund from the wizard
            :param integer journal_id: account.journal from the wizard
            :return: dict of value to create() the refund
        """
        obj_journal = self.pool.get('account.journal')

        type_dict = {
            'out_invoice': 'out_refund', # Customer Invoice
            'in_invoice': 'in_refund',   # Supplier Invoice
            'out_refund': 'out_invoice', # Customer Refund
            'in_refund': 'in_invoice',   # Supplier Refund
        }
        invoice_data = {}
        for field in ['name', 'reference', 'reference_number', 'supplier_invoice_number', 'comment', 'date_due', 'partner_id', 'company_id',
                'account_id', 'currency_id', 'payment_term', 'user_id', 'fiscal_position']:
            if invoice._all_columns[field].column._type == 'many2one':
                invoice_data[field] = invoice[field].id
            else:
                invoice_data[field] = invoice[field] if invoice[field] else False

        invoice_lines = self._refund_cleanup_lines(cr, uid, invoice.invoice_line, context=context)

        tax_lines = filter(lambda l: l['manual'], invoice.tax_line)
        tax_lines = self._refund_cleanup_lines(cr, uid, tax_lines, context=context)
        if journal_id:
            refund_journal_ids = [journal_id]
        elif invoice['type'] == 'in_invoice':
            refund_journal_ids = obj_journal.search(cr, uid, [('type','=','purchase_refund')], context=context)
        else:
            refund_journal_ids = obj_journal.search(cr, uid, [('type','=','sale_refund')], context=context)

        if not date:
            date = fields.date.context_today(self, cr, uid, context=context)
        invoice_data.update({
            'type': type_dict[invoice['type']],
            'date_invoice': date,
            'ngay_nhap': date,
            'state': 'draft',
            'number': False,
            'invoice_line': invoice_lines,
            'tax_line': tax_lines,
            'journal_id': refund_journal_ids and refund_journal_ids[0] or False,
        })
        if period_id:
            invoice_data['period_id'] = period_id
        if description:
            invoice_data['name'] = description
        return invoice_data
    
    def refund(self, cr, uid, ids, date=None, period_id=None, description=None, journal_id=None, context=None):
        new_ids = []
        for invoice in self.browse(cr, uid, ids, context=context):
            invoice_id = invoice.id
            
            invoice = self._prepare_refund(cr, uid, invoice,
                                                date=date,
                                                period_id=period_id,
                                                description=description,
                                                journal_id=journal_id,
                                                context=context)
            # create the new invoice
            new_id = self.create(cr, uid, invoice, context=context)
            new_ids.append(new_id)
            
            #Thanh: Link customer invoice into refund invoice
            cr.execute('UPDATE account_invoice SET rel_invoice_id=%s WHERE id=%s'%(invoice_id, new_id))
            #Thanh: Link customer invoice into refund invoice
            
            cr.execute('UPDATE account_invoice SET invoice_refund = True WHERE id=%s'%(new_id))
            
        return new_ids
    
    def action_date_assign(self, cr, uid, ids, *args):
        for inv in self.browse(cr, uid, ids):
            #Thanh: Check Invoice Reference and Number (Ko can check vi neu la hoa don ban le)
#             if not inv.reference or not inv.reference_number:
#                 raise osv.except_osv(_('Error !'), _("Please define 'Invoice Reference' and 'Number' before Validating this invoice."))
            
            res = self.onchange_payment_term_date_invoice(cr, uid, inv.id, inv.payment_term.id, inv.date_invoice)
            if res and res['value']:
                self.write(cr, uid, [inv.id], res['value'])
        return True
    
    def action_move_create(self, cr, uid, ids, context=None):
        """Creates invoice related analytics and financial move lines"""
        ait_obj = self.pool.get('account.invoice.tax')
        cur_obj = self.pool.get('res.currency')
        period_obj = self.pool.get('account.period')
        payment_term_obj = self.pool.get('account.payment.term')
        journal_obj = self.pool.get('account.journal')
        move_obj = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids, context=context):
            if not inv.journal_id.sequence_id:
                raise osv.except_osv(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise osv.except_osv(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue
            name = ''
            ctx = context.copy()
            ctx.update({'lang': inv.partner_id.lang})
            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice': fields.date.context_today(self,cr,uid,context=context)}, context=ctx)
            company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
            # create the analytical lines
            # one move line per invoice line
            iml = self._get_analytic_lines(cr, uid, inv.id, context=ctx)
            # check if taxes are all computed
            compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)
            self.check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)

            # I disabled the check_total feature
            group_check_total_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'group_supplier_inv_check_total')[1]
            group_check_total = self.pool.get('res.groups').browse(cr, uid, group_check_total_id, context=context)
            if group_check_total and uid in [x.id for x in group_check_total.users]:
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
            
            #Thanh: Set name of partner entry to the Invoice number
            if not inv.reference:
#                 if inv.type not in ('out_refund'):
                raise osv.except_osv(_('Lỗi nhập liệu!'), _("Vui lòng nhập Ký hiệu hóa đơn!"))
                
            if inv.reference:
                if inv.type in ('in_invoice', 'in_refund'):
                    if not inv.supplier_invoice_number:
                        raise osv.except_osv(_('Lỗi nhập liệu!'), _("Vui lòng nhập Số hóa đơn!"))
                    else:
                        name = inv.reference  + '/' + inv['supplier_invoice_number'] or '/'
                else:
#                     if inv.type not in ('out_refund'):
                    if not inv.reference_number:
                        raise osv.except_osv(_('Lỗi nhập liệu!'), _("Vui lòng nhập Số hóa đơn!"))
                    else:
                        name = inv.reference  + '/' + inv.reference_number or '/'
#                 name = inv['name'] or inv['supplier_invoice_number'] or '/'
            #Thanh: Set name of partner entry to the Invoice number
            
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
#                     'name': inv.rel_invoice_id.name,
                    'price': total,
                    'account_id': acc_id,
                    'date_maturity': inv.date_due or False,
                    'amount_currency': diff_currency_p \
                            and total_currency or False,
                    'currency_id': diff_currency_p \
                            and inv.currency_id.id or False,
                    'ref': ref
            })

            date = inv.date_invoice or time.strftime('%Y-%m-%d')

            part = self.pool.get("res.partner")._find_accounting_partner(inv.partner_id)

            line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part.id, date, context=ctx)),iml)

            line = self.group_lines(cr, uid, iml, line, inv)

            journal_id = inv.journal_id.id
            journal = journal_obj.browse(cr, uid, journal_id, context=ctx)
            if journal.centralisation:
                raise osv.except_osv(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = self.finalize_invoice_move_lines(cr, uid, inv, line)
            
            #Thanh: create Move for Commission Entry
            commission_moves = []
            commission_amount = 0.0
            if inv.commission_type:
                if inv.commission_type == 'percentage':
                    commission_amount = inv.commission_amount
                else:
                    commission_amount = inv.commission_fix_amount
                    
                commission_moves += [(0,0, {
                        'name': inv.commission_account_id.name + ' [' + str(inv.date_invoice) + ']',
                        'product_id': False,
                        'quantity': False,
                        'ref': name,
                        'date': inv.date_invoice,
                        'debit': inv.type in ['out_invoice','in_refund'] and commission_amount or 0.0,
                        'credit': inv.type in ['in_invoice','out_refund'] and commission_amount or 0.0,
                        'account_id': inv.commission_account_id.id,
                        'analytic_account_id': inv.commission_account_analytic_id.id,
                        })]
                
                commission_moves += [(0,0, {
                        'name': name,
                        'product_id': False,
                        'quantity': False,
                        'ref': name,
                        'date': inv.date_invoice,
                        'debit': inv.type in ['in_invoice','out_refund'] and commission_amount or 0.0,
                        'credit': inv.type in ['out_invoice','in_refund'] and commission_amount or 0.0,
                        'account_id': inv.account_id.id,
                        })]
            #Thanh: create Move for Commission Entry
            
            #Thanh generate Extend Group Entries
            extend_move_lines = []
            for invoice_line in inv.invoice_line:
                for move_line in line:
                    total_extend_line_currency = 0.0
                    if move_line[2]['account_id'] == invoice_line.account_id.id and invoice_line.discount_type=='2':
                        if inv.currency_id.id != company_currency:
                            total_extend_line_currency = cur_obj.compute(cr, uid, company_currency, inv.currency_id.id, move_line[2]['debit'] or move_line[2]['credit'], context=ctx)
                        new_move_line_vals = (0,0,move_line[2].copy())
                        new_move_line_vals[2].update({ 'account_id': inv.account_id.id,
                                                       'debit': move_line[2]['credit'],
                                                       'credit': move_line[2]['debit'],
                                                       'analytic_lines': [],
                                                       'amount_currency': total_extend_line_currency,
                                                       'tax_code_id': False,
                                                       'tax_amount': False,
                                                       'quantity': move_line[2]['quantity'],
                                                       'product_id': False,
                                                       'product_uom_id': False,
                                                       'analytic_account_id': False})
                        extend_move_lines.append(new_move_line_vals)
            #Thanh: update Invoice Entry            
            for move_line in line:
                if inv.account_id.id == move_line[2]['account_id']:
                    if move_line[2]['debit']:
                        for extend_move_line in extend_move_lines:
                            move_line[2]['debit'] += extend_move_line[2]['credit']
                            move_line[2]['debit'] -= extend_move_line[2]['debit']
                    else:
                        for extend_move_line in extend_move_lines:
                            move_line[2]['credit'] += extend_move_line[2]['debit']
                            move_line[2]['credit'] -= extend_move_line[2]['credit']
#                     if inv.commission_type:
#                         if inv.type in ['out_invoice','in_refund']:
#                             move_line[2]['debit'] -= commission_amount
#                         else:
#                             move_line[2]['credit'] -= commission_amount
            line += extend_move_lines
            line += commission_moves
            
            
            move = {
                'name': name,
                'ref': inv.reference,
                #Thanh: Add more Reference Number to Account Move
                'ref_number': inv.reference_number,
                'date_document': inv.date_document,
                'shop_id': inv.shop_id.id or False,
                #Thanh: Add more Reference Number to Account Move
                'line_id': line,
                'journal_id': journal_id,
                'date': date,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
                
                # Kiet: Add Date Suplier from Account Invoice
                'invoice_date':inv.supplier_inv_date or False
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
            
            #Thanh: Reconciliation Extend Move Line
            cr.execute("SELECT id FROM account_move_line WHERE move_id=%s AND account_id=%s"%(move_id, inv.account_id.id))
            rec_ids = [x[0] for x in cr.fetchall()]
            if rec_ids:
                move_line_pool.reconcile_partial(cr, uid, rec_ids)
            new_move_name = move_obj.browse(cr, uid, move_id, context=ctx).name
            if inv.type == 'in_invoice':
                name_ids = self.search(cr,uid,[('id', '!=',inv.id),('move_name','=',new_move_name),('partner_id','=',inv.partner_id.id),('type','=','in_invoice')])
                if name_ids:
                    raise osv.except_osv(_('Cảnh báo!'),
                                                  _('Số hóa đơn không được trùng nhau.'))
            if inv.type == 'out_invoice':
                name_ids = self.search(cr,uid,[('id', '!=',inv.id),('move_name','=',new_move_name),('type','=','out_invoice')])
                if name_ids:
                    raise osv.except_osv(_('Cảnh báo!'),
                                                  _('Số hóa đơn không được trùng nhau.'))
            # make the invoice point to that move
            self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name}, context=ctx)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move_obj.post(cr, uid, [move_id], context=ctx)
        self._log_event(cr, uid, ids)
        return True
    
#     def test_paid(self, cr, uid, ids, *args):
#         res = self.move_line_id_payment_get(cr, uid, ids)
#         
#         if not res:
#             #Thanh: Check Residual is 0.0 then call comfirm paid (Because these re some invoices issue Cash directly
#             this = self.browse(cr, uid, ids[0])
#             if this.residual != 0.0:
#                 return False
#             #Thanh: Check Residual is 0.0 then call comfirm paid (Because these re some invoices issue Cash directly
#             
#         ok = True
#         for id in res:
#             cr.execute('select reconcile_id from account_move_line where id=%s', (id,))
#             ok = ok and  bool(cr.fetchone()[0])
#         return ok
    
    def unlink(self, cr, uid, ids, context=None):
        source_id = []
        if context is None:
            context = {}
        invoices = self.read(cr, uid, ids, ['state','number'], context=context)
        unlink_ids = []

        for t in invoices:
            if t['state'] not in ('draft', 'cancel'):
                raise openerp.exceptions.Warning(_('You cannot delete an invoice which is not draft or cancelled. You should refund it instead.'))
            #Thanh: Check number instead of internal_number of original module
            elif t['number']:#t['internal_number']
                raise openerp.exceptions.Warning(_('You cannot delete an invoice after it has been validated (and received a number).  You can set it back to "Draft" state and modify its content, then re-confirm it.'))
            else:
                unlink_ids.append(t['id'])
        
        
        # kiet Update picking tao invoice
        sql ='''
            SELECT id,source_id,source_obj 
            FROM account_invoice_line 
            WHERE invoice_id = %s and source_obj ='stock.move'
        '''%(ids[0])
        cr.execute(sql)
        for line in cr.dictfetchall():
            if line['source_id']:
                source_id.append(line['source_id'])
        if source_id:
            sql='''
                SELECT distinct sp.id 
                FROM stock_picking sp inner join stock_move sm on sp.id =sm.picking_id
                WHERE sm.id in (%s)
            '''%(','.join(map(str,source_id)))
            cr.execute(sql)
            for line in cr.dictfetchall():
                sql ='''
                     UPDATE stock_picking 
                     SET invoice_state = '2binvoiced' where id = %s
                ''' %(line['id'])
                cr.execute(sql)

        osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
        return True
    
    def bt_huy_paid(self, cr, uid,ids, context=None):
        line = self.browse(cr,uid,ids[0])
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'account.invoice', line.id, 'invoice_cancel', cr)
        
        return self.write(cr,uid,ids,{
                                      'state': 'cancel',
                                      })
    
    def bt_ghinhan_vao_chiphi(self, cr, uid,ids, context=None):
        line = self.browse(cr,uid,ids[0])
        account_ids = self.pool.get('account.account').search(cr,uid,[('code', '=', '64189')])
        return self.write(cr,uid,ids,{
                                      'account_id': account_ids[0],
                                      'flag': True,
                                      })
account_invoice()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            res[line.id] = {
                'price_subtotal': 0.0,
                'amount_tax': 0.0,
            }
            
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
            res[line.id]['price_subtotal'] = taxes['total']
            
            for tax in taxes['taxes']:
                res[line.id]['amount_tax'] += tax['amount']
                
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id]['price_subtotal'] = cur_obj.round(cr, uid, cur, res[line.id]['price_subtotal']) + line.adjust_price
                res[line.id]['amount_tax'] = cur_obj.round(cr, uid, cur, res[line.id]['amount_tax'])
                sql = '''
                    update account_invoice_line set gia_tri = %s where id = %s
                '''%(res[line.id]['price_subtotal'], line.id)
                cr.execute(sql)
        return res
    
    
    def _get_product_info(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        uom_obj = self.pool.get('product.uom')
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                            'uom_conversion': 0.0,
                            'primary_qty': 0.0,
                            }
            if line.product_id and line.uos_id:
                if line.uos_id.id != line.product_id.uom_id.id:
                    res[line.id]['primary_qty'] = uom_obj._compute_qty(cr, uid, line.uos_id.id, line.quantity, line.product_id.uom_id.id)
                else:
                    res[line.id]['primary_qty'] = line.quantity
                res[line.id]['uom_conversion'] = line.quantity and round(res[line.id]['primary_qty']/line.quantity,3) or 0.0
                
        return res
    
    _columns = {
        'discount_type': fields.selection([('1', 'Normal'), 
                                             ('2', 'Cash Discount'),], 'Discount Type', size=32, required=True),
        
        #Modify price_subtotal, add field line_tax
        'price_subtotal': fields.function(_amount_line, string='Amount', type="float",
            digits_compute= dp.get_precision('Account'), store=True, multi='sums',),
        'amount_tax': fields.function(_amount_line, string='Amount Tax', type="float",
            digits_compute=dp.get_precision('Account'), store=True, multi='sums',),
        'source_obj':fields.char('Source Obj'),
        'source_id':fields.integer('Source Id'),
        'uom_conversion': fields.function(_get_product_info, string='Factor', digits= (16,4),type='float',
            store={
                'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['product_id','uos_id','quantity'], 10),
            }, readonly=True, multi='pro_info'),
        'primary_qty': fields.function(_get_product_info, string='Primary Qty', digits_compute= dp.get_precision('Product Unit of Measure'), type='float',
            store={
                'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['product_id','uos_id','quantity'], 10),
            }, readonly=True, multi='pro_info'),
        #Hung them so lo trên line
        'prodlot_id': fields.many2one('stock.production.lot', 'Số lô', ondelete='restrict'),
        'adjust_price':fields.float('Adjust Price'),
        'price_unit': fields.float('Unit Price', required=True, digits=(16,5)),
        'gia_tri': fields.float('Giá trị', digits=(16,0)),
    }
    
    _defaults = {
        'discount_type': '1',
    }
    
    def onchange_gia_tri(self, cr, uid, ids, gia_tri=False, quantity = False, context=None):
        vals = {}
        if gia_tri and quantity:
            vals = {
                    'price_unit':float(gia_tri)/float(quantity),
                    }
        return {'value': vals}
    
    def write(self,cr,uid,ids,vals,context=None):
        renew_id =  super(account_invoice_line, self).write(cr, uid,ids, vals, context)
        for invoiceline in self.browse(cr, uid, ids):
            if vals.get('price_unit',False):
#                 picking_id = False
#                 sql ='''
#                     SELECT picking_id 
#                         FROM stock_move 
#                         WHERE invoice_id = (
#                              SELECT invoice_id FROM account_invoice_line WHERE id = %s)
#                 '''%(id)
#                 cr.execute(sql)
#                 for i in cr.dictfetchall():
#                     picking_id = i['picking_id']

# PHUOC (cau sql la co san, moi sua lai thanh ham write de write lai price_unit trong stock move)
#                 sql='''
#                     UPDATE stock_move sm SET price_unit = 
#                         (SELECT price_unit FROM account_invoice_line ail 
#                             
#                             WHERE ail.id=%s
#                              ) 
#                      WHERE sm.id = %s
#                 '''%(invoiceline.id,invoiceline.source_id)
#                 cr.execute(sql)
                move = self.pool.get('stock.move').browse(cr,uid,invoiceline.source_id)
                if move.purchase_line_id:
                    self.pool.get('stock.move').write(cr,uid,[move.id],{
                                                                        'price_unit': vals['price_unit']
                                                                        })
                    self.pool.get('purchase.order.line').write(cr,uid,[move.purchase_line_id.id],{
                                                                                           'price_unit': vals['price_unit']
                                                                                           })
        return renew_id
    
    #Thanh: Set Account is Null --> User should choose other account
    def discount_type_change(self, cr, uid, ids, discount_type=False, context=None):
        result = {}
        if discount_type and discount_type == '2':
            result = {'value': {
                    'account_id': False,
                    }
                }
        return result
    
account_invoice_line()

class account_invoice_refund(osv.osv_memory):
     _inherit = "account.invoice.refund"
     
     def compute_refund(self, cr, uid, ids, mode='refund', context=None):
        """
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: the account invoice refund’s ID or list of IDs

        """
        inv_obj = self.pool.get('account.invoice')
        reconcile_obj = self.pool.get('account.move.reconcile')
        account_m_line_obj = self.pool.get('account.move.line')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        wf_service = netsvc.LocalService('workflow')
        inv_tax_obj = self.pool.get('account.invoice.tax')
        inv_line_obj = self.pool.get('account.invoice.line')
        res_users_obj = self.pool.get('res.users')
        if context is None:
            context = {}

        for form in self.browse(cr, uid, ids, context=context):
            created_inv = []
            date = False
            period = False
            description = False
            company = res_users_obj.browse(cr, uid, uid, context=context).company_id
            journal_id = form.journal_id.id
            for inv in inv_obj.browse(cr, uid, context.get('active_ids'), context=context):
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise osv.except_osv(_('Error!'), _('Cannot %s draft/proforma/cancel invoice.') % (mode))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise osv.except_osv(_('Error!'), _('Cannot %s invoice which is already reconciled, invoice should be unreconciled first. You can only refund this invoice.') % (mode))
                if form.period.id:
                    period = form.period.id
                else:
                    period = inv.period_id and inv.period_id.id or False

                if not journal_id:
                    journal_id = inv.journal_id.id

                if form.date:
                    date = form.date
                    if not form.period.id:
                            cr.execute("select name from ir_model_fields \
                                            where model = 'account.period' \
                                            and name = 'company_id'")
                            result_query = cr.fetchone()
                            if result_query:
                                cr.execute("""select p.id from account_fiscalyear y, account_period p where y.id=p.fiscalyear_id \
                                    and date(%s) between p.date_start AND p.date_stop and y.company_id = %s limit 1""", (date, company.id,))
                            else:
                                cr.execute("""SELECT id
                                        from account_period where date(%s)
                                        between date_start AND  date_stop  \
                                        limit 1 """, (date,))
                            res = cr.fetchone()
                            if res:
                                period = res[0]
                else:
                    date = inv.date_invoice
                if form.description:
                    description = form.description
                else:
                    description = inv.name

                if not period:
                    raise osv.except_osv(_('Insufficient Data!'), \
                                            _('No period found on the invoice.'))

                refund_id = inv_obj.refund(cr, uid, [inv.id], date, period, description, journal_id, context=context)
                refund = inv_obj.browse(cr, uid, refund_id[0], context=context)
                inv_obj.write(cr, uid, [refund.id], {'date_due': date,
                                                'check_total': inv.check_total})
                inv_obj.button_compute(cr, uid, refund_id)

                created_inv.append(refund_id[0])
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_id
                    to_reconcile_ids = {}
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
                        if line.reconcile_id:
                            line.reconcile_id.unlink()
                    wf_service.trg_validate(uid, 'account.invoice', \
                                        refund.id, 'invoice_open', cr)
                    refund = inv_obj.browse(cr, uid, refund_id[0], context=context)
                    for tmpline in  refund.move_id.line_id:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_ids[tmpline.account_id.id].append(tmpline.id)
                    for account in to_reconcile_ids:
                        account_m_line_obj.reconcile(cr, uid, to_reconcile_ids[account],
                                        writeoff_period_id=period,
                                        writeoff_journal_id = inv.journal_id.id,
                                        writeoff_acc_id=inv.account_id.id
                                        )
                    if mode == 'modify':
                        invoice = inv_obj.read(cr, uid, [inv.id],
                                    ['name', 'type', 'number', 'reference',
                                    'comment', 'date_due', 'partner_id',
                                    'partner_insite', 'partner_contact',
                                    'partner_ref', 'payment_term', 'account_id',
                                    'currency_id', 'invoice_line', 'tax_line',
                                    'journal_id', 'period_id'], context=context)
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = inv_line_obj.browse(cr, uid, invoice['invoice_line'], context=context)
                        invoice_lines = inv_obj._refund_cleanup_lines(cr, uid, invoice_lines, context=context)
                        tax_lines = inv_tax_obj.browse(cr, uid, invoice['tax_line'], context=context)
                        tax_lines = inv_obj._refund_cleanup_lines(cr, uid, tax_lines, context=context)
                        invoice.update({
                            'type': inv.type,
                            'date_invoice': date,
                            'ngay_nhap': date,
                            'state': 'draft',
                            'number': False,
                            'invoice_line': invoice_lines,
                            'tax_line': tax_lines,
                            'period_id': period,
                            'name': description
                        })
                        for field in ('partner_id', 'account_id', 'currency_id',
                                         'payment_term', 'journal_id'):
                                invoice[field] = invoice[field] and invoice[field][0]
                        inv_id = inv_obj.create(cr, uid, invoice, {})
                        if inv.payment_term.id:
                            data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], inv.payment_term.id, date)
                            if 'value' in data and data['value']:
                                inv_obj.write(cr, uid, [inv_id], data['value'])
                        created_inv.append(inv_id)
            xml_id = (inv.type == 'out_refund') and 'action_invoice_tree1' or \
                     (inv.type == 'in_refund') and 'action_invoice_tree2' or \
                     (inv.type == 'out_invoice') and 'action_invoice_tree3' or \
                     (inv.type == 'in_invoice') and 'action_invoice_tree4'
            result = mod_obj.get_object_reference(cr, uid, 'account', xml_id)
            id = result and result[1] or False
            result = act_obj.read(cr, uid, id, context=context)
            invoice_domain = eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result
     
account_invoice_refund()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
