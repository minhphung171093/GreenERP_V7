#-*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from openerp import SUPERUSER_ID
from openerp.tools import append_content_to_html
import random
from urllib import urlencode
from urlparse import urljoin

DATE_FORMAT = "%Y-%m-%d"

class bdf_channel(osv.osv):
    _name="bdf.channel"
    _columns={
        'name':fields.char('Name',size=128,required=True),
        'budget_id':fields.many2one("master.budget.owner",'Budget',required=False),
      }
bdf_channel()

class purchasing_group(osv.osv):
    _name="purchasing.group"
    _columns={
        'name':fields.char('Name',size=128,required=True),
        'is_default':fields.boolean('Default'),
      }
    
    def onchang_is_default(self, cr, uid, ids, is_default=False, context=None):
        if is_default:
            if ids:
                group_ids = self.search(cr, uid, [('id','<>',ids[0])])
            else:
                group_ids = self.search(cr, uid, [])
            self.write(cr, uid, group_ids, {'is_default':False})
        return {'value': {}}
    
purchasing_group()

class bdf_mail_queue(osv.osv):
    _name="bdf.mail.queue"
    _columns={
        'mail_id':fields.many2one("mail.mail",'Mail',required=False),
        'state': fields.selection([('draft','Draft'),('send','Send')],'Status',readonly=True),
    }
    
    _defaults = {
        'state': 'draft',
    }
    
    def send_mail(self, cr, uid, mail_id, context=None):
        mail_mail = self.pool.get('mail.mail')
        try:
            mail_mail.send(cr, uid, [mail_id], context=context)
        except Exception:
            a = 1
        return True
    
    def mail_queue_send(self, cr, uid, context=None):
        cr.execute('''select id,mail_id from bdf_mail_queue where state='draft' ''',)
        for mail in cr.fetchall():
            self.send_mail(cr, uid, mail[1],context)
            cr.execute('''update bdf_mail_queue set state='send' where id=%s ''',(mail[0],))
        return True
bdf_mail_queue()

class bdf_cost_center(osv.osv):
    _name="bdf.cost.center"
    _columns={
        'name':fields.char('Name',size=128,required=True),
        'cat_id':fields.many2one("product.category",'Cat',required=False),
        'sub_cat_id':fields.many2one("product.category",'Sub_CAT',required=False),
      }
    
bdf_cost_center()
class procurement_detail(osv.osv):
    _name="procurement.detail"
    
    def _compute_amount(self, cr, uid, ids, name, args, context=None):
        res={}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amt': 0.0,
            }
            res[order.id]['amt'] = order.qty * order.price_unit
        return res
    
    _columns={
        'product_id':fields.char('Item',size=1024,required=True),
        'qty':fields.float('Qty',digits=(16, 0),required=True),
        'price_unit':fields.float('Unit Price',digits=(16, 0),required=True),
        'amt':fields.function(_compute_amount, string='Amount',digits=(16, 0), type='float',  multi='all'),
        'purchase_id':fields.many2one('bdf.purchase','Purchase'),
    }
    
    _defaults = {
        'qty': 1,
    }
    
procurement_detail()

class spending_detail(osv.osv):
    _name="spending.detail"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(spending_detail, self).default_get(cr, uid, fields, context=context)
        channel_id = context.get('channel_id',False)
        if channel_id:
            vals = []
            region_obj = self.pool.get('master.regions')
            region_ids = region_obj.search(cr, uid, [('channel_id','=',channel_id)])
            for line in region_obj.browse(cr, uid, region_ids):
                vals.append({
                    'key_account_id': line.account_id.id,
                })
            res.update({'allocation_id':vals})
        return res
    
    def _compute_amount(self, cr, uid, ids, name, args, context=None):
        res={}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amt': 0.0,
                'fx_currency': 0.0,
            }
            res[order.id]['amt'] = order.qty * order.price_unit
            if order.purchase_id:
                res[order.id]['fx_currency'] = order.purchase_id.fx and order.qty * order.price_unit / order.purchase_id.fx or 0
            elif order.purchase2_id:
                res[order.id]['fx_currency'] = order.purchase2_id.fx and order.qty * order.price_unit / order.purchase2_id.fx or 0
            elif order.purchase3_id:
                res[order.id]['fx_currency'] = order.purchase3_id.fx and order.qty * order.price_unit / order.purchase3_id.fx or 0
        return res
    
    def onchange_product(self,cr,uid,ids,product_id,context=None):
        res={
#                 'cat':False,
#                 'sub_cat':False,
                'gl_code':False
             }
        if product_id:
            prod_obj = self.pool.get('product.product').browse(cr,uid,product_id)
            res={
#                     'cat':prod_obj.categ_id.id or False,
#                     'sub_cat':prod_obj.categ_id and prod_obj.categ_id.parent_id.id or False ,
                'account_id':prod_obj.account_id.id or False,
#                 'price_unit':prod_obj.list_price,
                }
        return {'value': res}
    
    _columns={
        'product_id':fields.many2one('product.product','Item',required=True),
        'cost_center_id':fields.many2one('bdf.cost.center','Cost Center',required=True),
        'cat':fields.many2one('product.category','Cat',readonly=True),
        'sub_cat':fields.many2one('product.category','Sub-Cat',readonly=True),
        'gl_code':fields.char('GL code',size=128,readonly=True),
        'account_id':fields.many2one('account.account','GL Code',readonly=True),
        'qty':fields.float('Qty',digits=(16, 0),required=True),
        'price_unit':fields.float('Unit Price',digits=(16, 0),required=True),
        'amt':fields.function(_compute_amount, string='Amt (VND)',  multi='all',digits=(16,0)),
        'fx_currency':fields.function(_compute_amount, string='Amt FX Currency',  multi='all',digits=(16,0)),
        'purchase_id':fields.many2one('bdf.purchase','Purchase',ondelete='cascade'),
        'purchase2_id':fields.many2one('bdf.purchase','Purchase',ondelete='cascade'),
        'purchase3_id':fields.many2one('bdf.purchase','Purchase',ondelete='cascade'),
        'allocation_id':fields.one2many('bdf.allocation','spending_detail_id','allocation'),
        'project_id':fields.char('Project',size=1024),
        'io_id':fields.many2one('bdf.io','IO'),
        'channel_name': fields.char('Channel Name', size=1024),
        'col_1': fields.float('Col',digits=(16,0)),
        'col_2': fields.float('Col',digits=(16,0)),
        'col_3': fields.float('Col',digits=(16,0)),
        'col_4': fields.float('Col',digits=(16,0)),
        'col_5': fields.float('Col',digits=(16,0)),
        'col_6': fields.float('Col',digits=(16,0)),
    }
    
    _defaults = {
        'qty': 1,
    }
    
    def onchange_cost(self,cr,uid,ids,cost_center_id,context=None):
        res={
                'cat':False,
                'sub_cat':False,
             }
        if cost_center_id:
            prod_obj = self.pool.get('bdf.cost.center').browse(cr,uid,cost_center_id)
            if prod_obj:
                res={
                    'cat':prod_obj.cat_id.id,
                    'sub_cat':prod_obj.sub_cat_id.id,
             }
        return {'value': res}
    
#     def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
#         if context is None:context = {}
#         res = super(spending_detail, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
#         if context.get('default_channel_name'):
#             channel = context.get('default_channel_name')
#             if channel=='MT':
#                 fields = res['fields']
#                 fields['col_1']['string'] = 'COOP'
#                 fields['col_2']['string'] = 'METRO'
#                 fields['col_3']['string'] = 'BIG C'
#                 fields['col_4']['string'] = 'HYPER'
#                 fields['col_5']['string'] = 'INDEPT'
#                 fields['col_6']['string'] = 'GUARDIAN'
#                 res['fields'] = fields
#             if channel=='GT':
#                 fields = res['fields']
#                 fields['col_1']['string'] = 'CENTRAL'
#                 fields['col_2']['string'] = 'HCM'
#                 fields['col_3']['string'] = 'MEKONG'
#                 fields['col_4']['string'] = 'NORTH 1'
#                 fields['col_5']['string'] = 'NORTH 2'
#                 fields['col_6']['string'] = 'SE'
#             if channel in ['PHARMACY','HOSPITAL']:
#                 fields = res['fields']
#                 fields['col_1']['string'] = 'HCM'
#                 fields['col_2']['string'] = 'CENTRAL'
#                 fields['col_3']['string'] = 'MEKONG'
#                 fields['col_4']['string'] = 'NORTH'
#                 fields['col_5']['string'] = 'HANOI'
#                 fields['col_6']['string'] = 'SEAST'
#         return res

    def create(self, cr, uid, vals, context=None):
        if 'cost_center_id' in vals:
            prod_obj = self.pool.get('bdf.cost.center').browse(cr,uid,vals['cost_center_id'])
            if prod_obj:
                vals.update({
                    'cat':prod_obj.cat_id.id,
                    'sub_cat':prod_obj.sub_cat_id.id,
             })
        if 'product_id' in vals:
            prod_obj = self.pool.get('product.product').browse(cr,uid,vals['product_id'])
            if prod_obj:
                vals.update({
                    'account_id':prod_obj.account_id.id or False,
             })
        return super(spending_detail,self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'cost_center_id' in vals:
            prod_obj = self.pool.get('bdf.cost.center').browse(cr,uid,vals['cost_center_id'])
            if prod_obj:
                vals.update({
                    'cat':prod_obj.cat_id.id,
                    'sub_cat':prod_obj.sub_cat_id.id,
             })
        if 'product_id' in vals:
            prod_obj = self.pool.get('product.product').browse(cr,uid,vals['product_id'])
            if prod_obj:
                vals.update({
                    'account_id':prod_obj.account_id.id or False,
             })
        return super(spending_detail,self).write(cr, uid, ids, vals, context)
spending_detail()

class  master_function_expense(osv.osv):
    _name="master.function.expense"
    
    _columns={
              'name':fields.char("Name",size=64,required=True),
              }
    
master_function_expense()

class bdf_io(osv.osv):
    _name="bdf.io"
    
    _columns={
        'name':fields.char("IO",size=64,required=True),
        'description':fields.char("Description",size=1024),
        'io_name':fields.char("Name",size=1024),
    }
    
bdf_io()

class master_key_accounts(osv.osv):
    _name="master.key.accounts"
    _columns={
              'name':fields.char("Name",size=64,required=True),
              }
    
master_key_accounts()

class master_regions(osv.osv):
    _name="master.regions"
    _columns={
              'account_id':fields.many2one('master.key.accounts','Region/KA',required=True),
              'channel_id':fields.many2one('bdf.channel','Channel Header',required=True),
              }
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if context is None:
            context = {}
        if not ids:
            return res
        if isinstance(ids, (int, long)):
            ids = [ids]
        for id in ids:
            elmt = self.browse(cr, uid, id, context=context)
            if not elmt.account_id.name:
                mess ='/'
            else:
                mess =elmt.account_id.name
            res.append((id, mess))
        return res
master_regions()


class  master_budget_owner(osv.osv):
    _name="master.budget.owner"
    _columns={
              'name':fields.char("Name",size=64,required=True),
              'function_id':fields.many2one("master.function.expense",'Function',required=False),
              }
    
master_budget_owner()

class bdf_allocation(osv.osv):
    _name="bdf.allocation"
    _columns={
        'allocation':fields.integer('% Allocation'),
        'key_account_id':fields.many2one('master.key.accounts','Regions',required=True),
        'spending_detail_id':fields.many2one('spending.detail','Spending detail',ondelete='cascade'),
    }
bdf_allocation()

class bdf_purchase(osv.osv):
    _name="bdf.purchase"
    _inherit = 'mail.thread'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(bdf_purchase, self).default_get(cr, uid, fields, context=context)
        user = self.pool.get('res.users').browse(cr, uid, uid)
        vals = []
        if not user.process_id:
            raise osv.except_osv(_('Warning!'), _('Please config Process for user %s'%(user.name)))
        for line in user.process_id.process_line:
            notify_ids = [l.id for l in line.notify_ids]
            vals.append({
                'name': line.name,
                'pr_value_filter': line.pr_value_filter,
                'amount': line.amount,
                'group_id': line.group_id.id,
                'user_id': line.user_id.id,
                'notify_ids': [(6,0,notify_ids)],
            })
        group_ids = self.pool.get('purchasing.group').search(cr, uid, [('is_default','=',True)])
        res.update({'process_line':vals,'purchasing_group_id':group_ids and group_ids[0] or False})
        return res
    
    def _compute_amount(self, cr, uid, ids, name, args, context=None):
        res={}
        for order in self.browse(cr, uid, ids, context=context):
            line_obj = self.pool.get('spending.detail')
            line_ids = line_obj.search(cr, uid, [('purchase_id','=',order.id)])
            res[order.id] = {
                'amt': 0.0,
                'fx_currency': 0.0,
            }
            amt = 0
            fx_currency = 0
            for line in line_obj.browse(cr, uid, line_ids):
                amt += line.qty * line.price_unit
                if line.purchase_id:
                    fx_currency += line.purchase_id.fx and line.qty * line.price_unit / line.purchase_id.fx or 0
                if line.purchase2_id:
                    fx_currency += line.purchase2_id.fx and line.qty * line.price_unit / line.purchase2_id.fx or 0
                if line.purchase3_id:
                    fx_currency += line.purchase3_id.fx and line.qty * line.price_unit / line.purchase3_id.fx or 0
            res[order.id]['amt'] = amt
            res[order.id]['fx_currency'] = fx_currency
        return res
    
    def _compute_cat(self, cr, uid, ids, name, args, context=None):
        res={}
        for order in self.browse(cr, uid, ids, context=context):
            line_obj = self.pool.get('spending.detail')
            line_ids = line_obj.search(cr, uid, [('purchase_id','=',order.id)])
            cat = ''
            for line in line_obj.browse(cr, uid, line_ids):
                cat+=line.cat and (line.cat.name +', ') or ''
            if cat:
                cat=cat[:-2]
            res[order.id] = cat
        return res
    
    _columns={
        'name': fields.char('Number', size=1024),
        'function':fields.many2one('master.function.expense','Function', required=False,
                        states={'purchase_request': [('readonly', False)],'budget_control': [('readonly', False)],'reject': [('readonly', False)]},readonly=True),
              
        'budget_owner':fields.many2one('master.budget.owner','Budget Holder',required=True,
                        states={'purchase_request': [('readonly', False)],'budget_control': [('readonly', False)],'reject': [('readonly', False)]},readonly=True),
              
        'channel':fields.many2one('bdf.channel','Channel',required=True,states={'purchase_request': [('readonly', False)],
                                                                                'budget_control': [('readonly', False)],'reject': [('readonly', False)]},readonly=True),
        'state': fields.selection([('purchase_request','Purchase Request'),
                                   ('category_manager','Category Manager'),
                                   ('channel_manager','Channel Manager'),
                                   ('product_manager','Product Manager (PM)'),
                                   ('group_pm','Group PM'),
                                   ('bu_manager','BU Manager'),
                                   ('function_head','Function Head'),
                                   ('budget_control','Budget Control'),
                                   ('control_manager','Control Manager'),
                                   ('fi_function_head','FI Function Head'),
                                   ('country_manager','Country Manager'),
                                   ('procurement','Procurement'),
                                   ('cancel','Canceled'),
                                   ('reject','Rejected')], 'State', required=True, track_visibility='onchange'),
        'bdf_state': fields.selection([('draft','Draft'),
                                   ('pending','Pending'),
                                   ('full_approved','Full Approved'),
                                   ('reject','Rejected')], 'Status'),
        'description':fields.char('Description',size=1024,states={'purchase_request': [('readonly', False)],'budget_control': [('readonly', False)],'reject': [('readonly', False)]},readonly=True),
        'date_from':fields.date('From',states={'purchase_request': [('readonly', False)],'budget_control': [('readonly', False)],'reject': [('readonly', False)]},readonly=True),
        'date':fields.date('Date',readonly=True),
        'date_to':fields.date('To',states={'purchase_request': [('readonly', False)],'budget_control': [('readonly', False)],'reject': [('readonly', False)]},readonly=True),
        'supplier_id':fields.char('Vendor',size=1024,required=False,
                                      states={'purchase_request': [('readonly', False)],'budget_control': [('readonly', False)],'reject': [('readonly', False)]},readonly=True),
        'budget_charged_in':fields.date('Budget',states={'purchase_request': [('readonly', False)],'budget_control': [('readonly', False)],'reject': [('readonly', False)]},readonly=True),
        'procurement_detail_line':fields.one2many('procurement.detail','purchase_id','procurement',required=True,states={'purchase_request': [('readonly', False)],'budget_control': [('readonly', False)],'reject': [('readonly', False)]},readonly=True),
        'spending_detail_line':fields.one2many('spending.detail','purchase_id','spending',required=True,states={'purchase_request': [('readonly', False)],'budget_control': [('readonly', False)],'reject': [('readonly', False)]},readonly=True),
        'spending_detail2_line':fields.one2many('spending.detail','purchase2_id','spending',required=True,states={'purchase_request': [('readonly', False)],'budget_control': [('readonly', False)],'reject': [('readonly', False)]},readonly=True),
        'spending_detail3_line':fields.one2many('spending.detail','purchase3_id','spending',required=True,states={'purchase_request': [('readonly', False)],'budget_control': [('readonly', False)],'reject': [('readonly', False)]},readonly=True),
        'process_line': fields.one2many('bdf.purchase.process.line','request_id','Process Line'),
        'user_comment': fields.text('Comment'),
        'notify_ids':fields.many2many('res.users', 'bdf_purchase_user_ref', 'bdf_purchase_id', 'user_id', 'Notify'),
        'history_ids':fields.many2many('res.users', 'bdf_purchase_user_history_ref', 'bdf_purchase_id', 'user_id', 'History'),
        'product_id': fields.related('spending_detail_line','product_id', relation='product.product',type='many2one',string="Item"),
        
        'create_uid':fields.many2one('res.users', 'Create uid'),
        'category_manager_id':fields.many2one('res.users','Category Manager'),
        'channel_manager_id':fields.many2one('res.users','Channel Manager'),
        'product_manager_id':fields.many2one('res.users','Product Manager (PM)'),
        'group_pm_id':fields.many2one('res.users','Group PM'),
        'bu_manager_id':fields.many2one('res.users','BU Manager'),
        'function_head_id':fields.many2one('res.users','Function Head'),
        'budget_control_id':fields.many2one('res.users','Budget Control'),
        'control_manager_id':fields.many2one('res.users','Control Manager'),
        'fi_function_head_id':fields.many2one('res.users','FI Function Head'),
        'country_manager_id':fields.many2one('res.users','Country Manager'),
        
        'request_by_id':fields.many2one('res.users', 'Request by'),
        'category_manager_approve_id':fields.many2one('res.users','Category Manager Approve'),
        'channel_manager_approve_id':fields.many2one('res.users','Channel Manager Approve'),
        'product_manager_approve_id':fields.many2one('res.users','Product Manager (PM) Approve'),
        'group_pm_approve_id':fields.many2one('res.users','Group PM Approve'),
        'bu_manager_approve_id':fields.many2one('res.users','BU Manager Approve'),
        'function_head_approve_id':fields.many2one('res.users','Function Head Approve'),
        'budget_control_approve_id':fields.many2one('res.users','Budget Control Approve'),
        'control_manager_approve_id':fields.many2one('res.users','Control Manager Approve'),
        'fi_function_head_approve_id':fields.many2one('res.users','FI Function Head Approve'),
        'country_manager_approve_id':fields.many2one('res.users','Country Manager Approve'),
        
        'user_id':fields.many2one('res.users','Approve Pending'),
        'user_request_id':fields.many2one('res.users','User Request'),
        'purchasing_group_id':fields.many2one('purchasing.group','Purchasing Group'),
        'fx': fields.float('FX',digits=(16,0)),
        
        'amt':fields.function(_compute_amount, string='Amt (VND)',  multi='all',digits=(16,0)),
        'fx_currency':fields.function(_compute_amount, string='Amt FX Currency',  multi='all',digits=(16,0)),
        'cat':fields.function(_compute_cat, string='CAT',type='char'),
      }
    _defaults={
        'name': '/',
        'state':'purchase_request',
        'bdf_state': 'draft',
    }
    
    def test(self,cr, uid, ids):
        print 'asds'
        return True
    
    def approve_pr_by_mail(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        request = self.browse(cr, uid, ids[0])
        line_obj = self.pool.get('bdf.purchase.process.line')
        line_ids = line_obj.search(cr, uid, [('request_id','=',request.id),('is_done','=',False)],order='name')
        group_id = False
        user_id = False
        user_approve_id = False
        if line_ids:
            
            line = line_obj.browse(cr, uid, line_ids[0])
            if line.pr_value_filter:
                amount = self.pool.get('bdf.purchase').get_amount(request)
                if amount<line.amount:
                    line_obj.write(cr, uid, [line_ids[0]], {'is_done': True,'is_pass': True})
                    line2_ids = line_obj.search(cr, uid, [('request_id','=',request.id),('is_done','=',False)],order='name')
                    for line2 in line_obj.browse(cr, uid, line2_ids):
                        if line2.pr_value_filter and amount<line2.amount: 
                            line_obj.write(cr, uid, [line2.id], {'is_done': True,'is_pass': True})
                            continue
                        break
            
            line_ids = line_obj.search(cr, uid, [('request_id','=',request.id),('is_done','=',False)],order='name')
            if line_ids:
                line = line_obj.browse(cr, uid, line_ids[0])
                line_group_ids = line_obj.search(cr, uid, [('request_id','=',request.id),('is_done','=',True),('is_pass','=',False)],order='name desc')
                if line_group_ids:
                    process = line_obj.browse(cr, uid, line_group_ids[0])
                    group_id = process.group_id.id
                    user_approve_id = process.user_id and process.user_id.id or False
                    user_id = line.user_id.id
#                 if len(line_ids)==1:
#                     context.update({'is_done':True})
#                 if line.pr_value_filter:
#                     amount = self.get_amount(line.request_id)
#                     if amount>=line.amount and len(line_ids)<2:
#                         context.update({'is_done':True})
            else:
                context.update({'is_done':True})
                line_ids = line_obj.search(cr, uid, [('request_id','=',request.id),('is_done','=',True),('is_pass','=',False)],order='name desc')
                process = line_obj.browse(cr, uid, line_ids[0])
                group_id = process.group_id.id
                user_approve_id = process.user_id and process.user_id.id or False
        else:
            user_approve_id = uid
            context.update({'is_done':True})
            line_ids = line_obj.search(cr, uid, [('request_id','=',request.id),('is_done','=',True),('is_pass','=',False)],order='name desc')
            process = line_obj.browse(cr, uid, line_ids[0])
            group_id = process.group_id.id
            
        context.update({'group_id':group_id,'user_id':user_id,'active_id':ids[0],'active_ids':ids})
        if user_approve_id and user_approve_id==uid:
            approve_obj = self.pool.get('approve.pr')
            approve_id = approve_obj.create(cr, uid, {'message':''}, context)
            approve_obj.bt_approve(cr, uid, [approve_id],context)
        return True
    
    def button_request(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        request = self.browse(cr, uid, ids[0])
        line_obj = self.pool.get('bdf.purchase.process.line')
        line_ids = line_obj.search(cr, uid, [('request_id','=',request.id),('is_done','=',False)],order='name')
        group_id = False
        user_id = False
        if line_ids:
            
            line = line_obj.browse(cr, uid, line_ids[0])
            if line.pr_value_filter:
                amount = self.pool.get('bdf.purchase').get_amount(request)
                if amount<line.amount:
                    line_obj.write(cr, uid, [line_ids[0]], {'is_done': True,'is_pass': True})
                    line2_ids = line_obj.search(cr, uid, [('request_id','=',request.id),('is_done','=',False)],order='name')
                    for line2 in line_obj.browse(cr, uid, line2_ids):
                        if line2.pr_value_filter and amount<line2.amount: 
                            line_obj.write(cr, uid, [line2.id], {'is_done': True,'is_pass': True})
                            continue
                        break
            
            line_ids = line_obj.search(cr, uid, [('request_id','=',request.id),('is_done','=',False)],order='name')
            if line_ids:
                line = line_obj.browse(cr, uid, line_ids[0])
                line_group_ids = line_obj.search(cr, uid, [('request_id','=',request.id),('is_done','=',True),('is_pass','=',False)],order='name desc')
                if line_group_ids:
                    process = line_obj.browse(cr, uid, line_group_ids[0])
                    group_id = process.group_id.id
                    
                    user_id = line.user_id.id
#                 if len(line_ids)==1:
#                     context.update({'is_done':True})
#                 if line.pr_value_filter:
#                     amount = self.get_amount(line.request_id)
#                     if amount>=line.amount and len(line_ids)<2:
#                         context.update({'is_done':True})
            else:
                context.update({'is_done':True})
                line_ids = line_obj.search(cr, uid, [('request_id','=',request.id),('is_done','=',True),('is_pass','=',False)],order='name desc')
                process = line_obj.browse(cr, uid, line_ids[0])
                group_id = process.group_id.id
        else:
            context.update({'is_done':True})
            line_ids = line_obj.search(cr, uid, [('request_id','=',request.id),('is_done','=',True),('is_pass','=',False)],order='name desc')
            process = line_obj.browse(cr, uid, line_ids[0])
            group_id = process.group_id.id
        context.update({'group_id':group_id,'user_id':user_id})
        return {
                'name':'Approve',
                'view_mode': 'form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'approve.pr',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': context,
        }
    def get_amount(self,obj):
        amount = 0.0
        for i in obj.spending_detail_line:
            amount += i.amt
        return amount
    
    def reject_pr_by_mail(self, cr, uid, ids, context=None):
        if context is None:
            context={}
        user_approve_id = False
        line_obj = self.pool.get('bdf.purchase.process.line')
        request = self.browse(cr, uid, ids[0])
        line_group_ids = line_obj.search(cr, uid, [('request_id','=',request.id),('is_done','=',True),('is_pass','=',False)],order='name desc')
        if line_group_ids:
            process = line_obj.browse(cr, uid, line_group_ids[0])
            user_approve_id = process.user_id and process.user_id.id or False
        
        if user_approve_id and user_approve_id==uid and request.state not in ['procurement','reject']:
            context.update({'active_id':ids[0],'active_ids':ids})
            reject_obj = self.pool.get('reject.pr')
            reject_id = reject_obj.create(cr, uid, {'message':''}, context)
            reject_obj.bt_reject(cr, uid, [reject_id],context)
        return True
    
    def button_reject(self, cr, uid, ids, context=None):
        return {
                'name':'Reject',
                'view_mode': 'form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'reject.pr',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': context,
            }
#     def button_reject(self, cr, uid, ids, context=None):
#         if context and context.get('states',False):
#             for i in self.browse(cr,uid,ids):
#                 if i.state in ('purchase_request','functional_manager'):
#                     self.write(cr, uid, ids, {'state':'purchase_request'})
#                 else:
#                     raise osv.except_osv(_('Error!'), _('Không được huỷ phiếu'))
#         else:
#             self.write(cr, uid, ids, {'state':'purchase_request'})
#         return {'type':'ir.actions.act_window_close'}
    
    def button_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancel'})
    
    def button_set_to_draft(self, cr, uid, ids, context=None):
        for id in ids:
            cr.execute('''
                update bdf_purchase set category_manager_id = null, channel_manager_id = null,product_manager_id = null, group_pm_id = null,bu_manager_id = null,
                 function_head_id = null,budget_control_id = null,control_manager_id = null,fi_function_head_id = null,country_manager_id = null,request_by_id = null,
                 category_manager_approve_id = null,channel_manager_approve_id = null,product_manager_approve_id = null, group_pm_approve_id = null, bu_manager_approve_id = null,
                 function_head_approve_id = null, budget_control_approve_id = null, control_manager_approve_id = null, fi_function_head_approve_id = null, country_manager_approve_id = null, user_request_id = null, user_id=bdf_purchase.create_uid  
                 where id=%s
            ''',(id,))
            cr.execute('delete from bdf_purchase_user_ref where bdf_purchase_id=%s',(id,))
            cr.execute('delete from bdf_purchase_user_history_ref where bdf_purchase_id=%s',(id,))
            cr.execute('''update bdf_purchase_process_line set is_done='f',is_pass='f' where request_id=%s 
                and id not in (select id from bdf_purchase_process_line where request_id=%s order by name limit 1) ''',(id,id,))
        return self.write(cr, uid, ids, {'state':'purchase_request'})
    
    def print_purchase(self, cr, uid, ids, context=None): 
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'pdf_report_pr_master',
            }
    
    def create(self, cr, uid, vals, context=None):
        vals.update({'history_ids':[(4,uid)]})
        new_id = super(bdf_purchase,self).create(cr, uid, vals, context)
        line_obj = self.pool.get('bdf.purchase.process.line')
        line_ids = line_obj.search(cr, uid, [('request_id','=',new_id),('is_done','=',False)],order='name')
        if line_ids:
            line_obj.write(cr, uid, [line_ids[0]],{'is_done':True})
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(bdf_purchase,self).write(cr, uid, ids, vals, context)
        for line in self.browse(cr, uid, ids):
            if 'state' in vals and vals['state'] not in ['cancel','reject'] and line.name=='/':
                cr.execute('''update bdf_purchase set name=%s,date=%s where id = %s''',(self.pool.get('ir.sequence').get(cr, uid, 'bdf.purchase.request'),time.strftime('%Y-%m-%d'),line.id,))
        return new_write
    
    def unlink(self, cr, uid, ids, context=None):
        leave_details = self.read(cr, uid, ids, ['bdf_state'], context=context)
        unlink_ids = []
        for ld in leave_details:
            if ld['bdf_state'] in ['draft', 'cancel']:
                unlink_ids.append(ld['id'])
            else:
                raise osv.except_osv(_('Warning!'), _('In PR to delete a submited PR, You can not delete it!'))
        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
    
bdf_purchase()

class product_product(osv.osv):
    _inherit='product.product'
    _columns={
        'master_function_expense_id':fields.many2one('master.function.expense','Function expense',required=False),
        'master_budget_owner_id':fields.many2one('master.budget.owner','Budget owner',required=False),
        'channel_id':fields.many2many('bdf.channel','product_channel_ref','product_id','channel_id','Channel',required=False),
        'account_id': fields.many2one('account.account','GL Code',required=False),
        }
product_product()

class product_category(osv.osv):
    _inherit='product.category'
    _columns={
        'cate':fields.char("Cate",size=1024),
        'brand':fields.char("Brand",size=1024),
        'sub_cate':fields.char("Sub Cate",size=1024),
    }
product_category()

class product_template(osv.osv):
    _inherit='product.template'
    _columns={
        'categ_id': fields.many2one('product.category','Category', required=False, change_default=True, domain="[('type','=','normal')]" ,help="Select category for the current product"),
        }
product_template()

class account_account(osv.osv):
    _inherit='account.account'
    _columns={
        'user_type': fields.many2one('account.account.type', 'Account Type', required=False,
            help="Account Type is used for information purpose, to generate "
              "country-specific legal reports, and set the rules to close a fiscal year and generate opening entries."),
        }
account_account()

class master_project(osv.osv):
    _name ='master.project'
    _columns={
        'name':fields.char('Project name',size=256,required=True),
        'categ_ids':fields.many2many('product.category', 'category_project_ref', 'categ_id', 'project_id', 'cat'),
        }
master_project()

class master_process(osv.osv):
    _name ='master.process'
    _columns={
        'name':fields.char('Process name',size=256,required=True),
        'process_line': fields.one2many('master.process.line','process_id','Process Line'),
        }
master_process()

class master_process_line(osv.osv):
    _name ='master.process.line'
    _order = 'name'
    _columns={
        'process_id':fields.many2one('master.process','Process', ondelete='cascade',required=True),
        'name': fields.integer('Sequence',required=True),
        'pr_value_filter': fields.boolean('PR value filter'),
        'amount': fields.float('>= amount'),
        'group_id': fields.many2one('res.groups','Group',required=True),
        'user_id': fields.many2one('res.users','Default Approval'),
        'notify_ids':fields.many2many('res.users', 'process_line_user_ref', 'process_line_id', 'user_id', 'Notify'),
        }
    
    def _check_name(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            process_line_ids = self.search(cr, uid, [('id','!=',line.id),('process_id','=',line.process_id.id),('name','=',line.name)])
            if process_line_ids:
                raise osv.except_osv(_('Warning!'),_('Sequence in Process should be unique!'))
                return False
        return True
    _constraints = [
        (_check_name, 'Identical Data', ['name']),
    ]
    
master_process_line()

class bdf_purchase_process_line(osv.osv):
    _name ='bdf.purchase.process.line'
    _order = 'name'
    _columns={
        'request_id':fields.many2one('bdf.purchase','Purchase request', ondelete='cascade',required=True),
        'name': fields.integer('Sequence',required=True),
        'pr_value_filter': fields.boolean('PR value filter'),
        'amount': fields.float('>= amount'),
        'group_id': fields.many2one('res.groups','Group',required=True),
        'user_id': fields.many2one('res.users','Default Approval'),
        'is_done': fields.boolean('Done'),
        'is_pass': fields.boolean('Pass'),
        'notify_ids':fields.many2many('res.users', 'bdf_process_line_user_ref', 'bdf_process_line_id', 'user_id', 'Notify'),
        }
    
bdf_purchase_process_line()

class res_users(osv.osv):
    _inherit="res.users"
    _columns={
        'process_id':fields.many2one('master.process','Process'),
      }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_bdf_user_approve') and context.get('request_id'):
            line_obj = self.pool.get('bdf.purchase.process.line')
            line_ids = line_obj.search(cr, uid, [('request_id','=',context.get('request_id')),('is_done','=',False)],order='name')
            if line_ids:
                line = line_obj.browse(cr, uid, line_ids[0])
                sql ='''
                    select uid from res_groups_users_rel 
                    where gid = %s
                '''%(line.group_id.id)
                cr.execute(sql)
                user_ids = [x[0] for x in cr.fetchall()]
                args += [('id','in',user_ids)]
        if context.get('search_user_group_assistant_pm'):
            sql ='''
                select uid from res_groups_users_rel 
                where gid in (select id from res_groups where name='Assistant PM')
            '''
            cr.execute(sql)
            user_ids = [x[0] for x in cr.fetchall()]
            args += [('id','in',user_ids)]
        if context.get('search_user_group_process') and context.get('group_id'):
            sql ='''
                select uid from res_groups_users_rel 
                where gid = %s
            '''%(context.get('group_id'))
            cr.execute(sql)
            user_ids = [x[0] for x in cr.fetchall()]
            args += [('id','in',user_ids)]
        return super(res_users, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)    

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
   
res_users()

class res_partner(osv.osv):
    _inherit="res.partner"
    
    def _get_signup_url_for_action(self, cr, uid, ids, action='login', view_type=None, menu_id=None, res_id=None, model=None, context=None):
        """ generate a signup url for the given partner ids and action, possibly overriding
            the url state components (menu_id, id, view_type) """
        res = dict.fromkeys(ids, False)
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        for partner in self.browse(cr, uid, ids, context):
            # when required, make sure the partner has a valid signup token
            if context and context.get('signup_valid') and not partner.user_ids:
                self.signup_prepare(cr, uid, [partner.id], context=context)
                partner.refresh()

            # the parameters to encode for the query and fragment part of url
            query = {'db': cr.dbname}
            fragment = {'action': action, 'type': partner.signup_type}

#             if partner.signup_token:
#                 fragment['token'] = partner.signup_token
#             elif partner.user_ids:
#                 fragment['db'] = cr.dbname
#                 fragment['login'] = partner.user_ids[0].login
#                 fragment['password'] = partner.user_ids[0].password
#             else:
#                 continue        # no signup token, no user, thus no signup url!
            
            if partner.user_ids:
                fragment['db'] = cr.dbname
                fragment['login'] = partner.user_ids[0].login
                fragment['password'] = partner.user_ids[0].password
            
            if view_type:
                fragment['view_type'] = view_type
            if menu_id:
                fragment['menu_id'] = menu_id
            if model:
                fragment['model'] = model
            if res_id:
                fragment['id'] = res_id

            res[partner.id] = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))

        return res
    
    def _get_signup_url_for_action_approve_pr_by_mail(self, cr, uid, ids, action='login', view_type=None, menu_id=None, res_id=None, model=None, context=None):
        """ generate a signup url for the given partner ids and action, possibly overriding
            the url state components (menu_id, id, view_type) """
        res = dict.fromkeys(ids, False)
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        for partner in self.browse(cr, uid, ids, context):
            # when required, make sure the partner has a valid signup token
            if context and context.get('signup_valid') and not partner.user_ids:
                self.signup_prepare(cr, uid, [partner.id], context=context)
                partner.refresh()

            # the parameters to encode for the query and fragment part of url
            query = {'db': cr.dbname}
            fragment = {'action': action, 'type': partner.signup_type}

#             if partner.signup_token:
#                 fragment['token'] = partner.signup_token
#             elif partner.user_ids:
#                 fragment['db'] = cr.dbname
#                 fragment['login'] = partner.user_ids[0].login
#                 fragment['password'] = partner.user_ids[0].password
#             else:
#                 continue        # no signup token, no user, thus no signup url!
            
            if partner.user_ids:
                fragment['db'] = cr.dbname
                fragment['login'] = partner.user_ids[0].login
                fragment['password'] = partner.user_ids[0].password
            
            if view_type:
                fragment['view_type'] = view_type
            if menu_id:
                fragment['menu_id'] = menu_id
            if model:
                fragment['model'] = model
            if res_id:
                fragment['id'] = res_id
                fragment['approve_pr_by_mail'] = res_id

            res[partner.id] = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))

        return res
    
    def _get_signup_url_for_action_reject_pr_by_mail(self, cr, uid, ids, action='login', view_type=None, menu_id=None, res_id=None, model=None, context=None):
        """ generate a signup url for the given partner ids and action, possibly overriding
            the url state components (menu_id, id, view_type) """
        res = dict.fromkeys(ids, False)
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        for partner in self.browse(cr, uid, ids, context):
            # when required, make sure the partner has a valid signup token
            if context and context.get('signup_valid') and not partner.user_ids:
                self.signup_prepare(cr, uid, [partner.id], context=context)
                partner.refresh()

            # the parameters to encode for the query and fragment part of url
            query = {'db': cr.dbname}
            fragment = {'action': action, 'type': partner.signup_type}

#             if partner.signup_token:
#                 fragment['token'] = partner.signup_token
#             elif partner.user_ids:
#                 fragment['db'] = cr.dbname
#                 fragment['login'] = partner.user_ids[0].login
#                 fragment['password'] = partner.user_ids[0].password
#             else:
#                 continue        # no signup token, no user, thus no signup url!
            
            if partner.user_ids:
                fragment['db'] = cr.dbname
                fragment['login'] = partner.user_ids[0].login
                fragment['password'] = partner.user_ids[0].password
            
            if view_type:
                fragment['view_type'] = view_type
            if menu_id:
                fragment['menu_id'] = menu_id
            if model:
                fragment['model'] = model
            if res_id:
                fragment['id'] = res_id
                fragment['reject_pr_by_mail'] = res_id

            res[partner.id] = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))

        return res

res_partner()

