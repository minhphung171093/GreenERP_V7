# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from openerp import SUPERUSER_ID
from openerp.tools import append_content_to_html
import datetime
WARNING_TYPES = [('warning','Warning'),('info','Information'),('error','Error')]

class approve_pr(osv.osv_memory):
    _name = "approve.pr"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(approve_pr, self).default_get(cr, uid, fields, context=context)
        res.update({'request_id':context.get('active_id',False),
                    'group_id':context.get('group_id',False),
                    'is_done':context.get('is_done',False),
                    'user_id':context.get('user_id',False),})
        return res
    
    _columns = {    
        'user_id': fields.many2one('res.users', 'Submit to'),
        'request_id': fields.many2one('bdf.purchase', 'Request'),
        'group_id': fields.many2one('res.groups','Group'),
        'message': fields.text("Message",required=False),
        'is_done': fields.boolean('Done'), 
    }
    
    def send_mail(self, cr, uid, lead_email, msg_id,context=None):
        mail_message_pool = self.pool.get('mail.message')
        mail_mail = self.pool.get('mail.mail')
        msg = mail_message_pool.browse(cr, SUPERUSER_ID, msg_id, context=context)
        body_html = msg.body
        # email_from: partner-user alias or partner email or mail.message email_from
        if msg.author_id and msg.author_id.user_ids and msg.author_id.user_ids[0].alias_domain and msg.author_id.user_ids[0].alias_name:
            email_from = '%s <%s@%s>' % (msg.author_id.name, msg.author_id.user_ids[0].alias_name, msg.author_id.user_ids[0].alias_domain)
        elif msg.author_id:
            email_from = '%s <%s>' % (msg.author_id.name, msg.author_id.email)
        else:
            email_from = msg.email_from

        references = False
        if msg.parent_id:
            references = msg.parent_id.message_id

        mail_values = {
            'mail_message_id': msg.id,
            'auto_delete': True,
            'body_html': body_html,
            'email_from': email_from,
            'email_to' : lead_email,
            'references': references,
        }
        email_notif_id = mail_mail.create(cr, uid, mail_values, context=context)
        try:
            self.pool.get('bdf.mail.queue').create(cr, uid, {'mail_id':email_notif_id,'state': 'draft'})
#             mail_mail.send(cr, uid, [email_notif_id], context=context)
        except Exception:
            a = 1
        return True
    
    def mail_for_approve_pr(self, cr, uid, bdf_purchase, action, user, context=None):
        partner = user.partner_id
        partner.signup_prepare()
        url = partner._get_signup_url_for_action(action=action,view_type='form', res_id=bdf_purchase.id)[partner.id]
        approve_url = partner._get_signup_url_for_action_approve_pr_by_mail(action=action,view_type='form', res_id=bdf_purchase.id)[partner.id]
        reject_url = partner._get_signup_url_for_action_reject_pr_by_mail(action=action,view_type='form', res_id=bdf_purchase.id)[partner.id]
        text = _("""<p>Access this document <a href="%s">directly in OpenERP</a></p>""") % url
        approve_text = _("""<p><a href="%s">APPROVE</a> \t <a href="%s">REJECT</a></p>""")%(approve_url,reject_url)
#         if bdf_purchase.state=='purchase_request':
#             bdf_purchase_state = 'Purchase Request'
#         elif bdf_purchase.state=='category_manager':
#             bdf_purchase_state = 'Category Manager'
#         elif bdf_purchase.state=='channel_manager':
#             bdf_purchase_state = 'Channel Manager'
#         elif bdf_purchase.state=='product_manager':
#             bdf_purchase_state = 'Product Manager (PM)'
#         elif bdf_purchase.state=='group_pm':
#             bdf_purchase_state = 'Group PM'
#         elif bdf_purchase.state=='bu_manager':
#             bdf_purchase_state = 'BU Manager'
#         elif bdf_purchase.state=='function_head':
#             bdf_purchase_state = 'Function Head'
#         elif bdf_purchase.state=='budget_control':
#             bdf_purchase_state = 'Budget Control'
#         elif bdf_purchase.state=='control_manager':
#             bdf_purchase_state = 'Control Manager'
#         elif bdf_purchase.state=='fi_function_head':
#             bdf_purchase_state = 'FI Function Head'
#         elif bdf_purchase.state=='country_manager':
#             bdf_purchase_state = 'Country Manager'
#         elif bdf_purchase.state=='procurement':
#             bdf_purchase_state = 'Procurement'
#         elif bdf_purchase.state=='cancel':
#             bdf_purchase_state = 'Cancel'
#         else:
#             bdf_purchase_state = ''
        amount=self.pool.get('bdf.purchase').get_amount(bdf_purchase)
#         body = '<p>PR number: %s</p><p>PR Descriptions: %s</p><p>PR value: %s</p><p>PR creator: %s</p><p>Comment history:</p>' \
#             %(bdf_purchase.name,bdf_purchase.description and bdf_purchase.description or '',format(amount, ','),bdf_purchase.create_uid.name)
        spending_detail_line = ''
        for line in bdf_purchase.spending_detail_line:
            spending_detail_line += '''
                <tr align="left" width="100%" style="font-size: 12px">
                    <th width="15%" style="border: 2px solid black;font-size: 12px" align ="center">'''+(line.cat and line.cat.name or '')+'''</th>
                    <th width="15%" style="border: 2px solid black;font-size: 12px" align ="center">'''+(line.sub_cat and line.sub_cat.name or '')+'''</th>
                    <th width="35%" style="border: 2px solid black;font-size: 12px" align ="center">'''+(line.product_id and line.product_id.name or '')+'''</th>
                    <th width="15%" style="border: 2px solid black;font-size: 12px" align ="center">'''+(format(int(line.amt), ',') or '')+'''</th>
                    <th width="20%" style="border: 2px solid black;font-size: 12px" align ="center">'''+(format(int(line.fx_currency), ',') or '')+'''</th>
                </tr>
            '''
        body = '''
            <table >
                <tr align="left" width="100%" style= "font-size: 12px">
                    <th width="15%" align ="left">PR No.</th>
                    <th colspan="4" style="border: 2px solid black;font-size: 12px" width="85%" align ="left">'''+(bdf_purchase.name or '')+'''</th>
                </tr>
                <tr align="left" width="100%" style="font-size: 12px">
                    <th colspan="2" align ="left">Vendor</th>
                    <th colspan="3" align ="left">Description</th>
                </tr>
                <tr align="left" width="100%" style="font-size: 12px">
                    <th colspan="2" style="border: 2px solid black;font-size: 12px" width="30%" align ="left">'''+(bdf_purchase.supplier_id or '')+'''</th>
                    <th colspan="3" style="border: 2px solid black;font-size: 12px" width="70%" align ="left">'''+(bdf_purchase.description or '')+'''</th>
                </tr>
                <tr align="left" width="100%" style="font-size: 12px">
                    <th width="15%" align ="left"></th>
                    <th width="15%" align ="left"></th>
                    <th width="35%" align ="left"></th>
                    <th width="15%" align ="left"></th>
                    <th width="20%" style="font-size: 12px;background-color: rgb(0,32,96) ;color: rgb(255, 255, 255);" align ="center">FX</th>
                </tr>
                <tr align="left" width="100%" style="font-size: 12px">
                    <th width="15%" align ="left"></th>
                    <th width="15%" align ="left"></th>
                    <th width="35%" align ="left"></th>
                    <th width="15%" align ="left"></th>
                    <th width="20%" style="border: 2px solid black;font-size: 12px" align ="center">'''+(str(bdf_purchase.fx) or '')+'''</th>
                </tr>
                <tr align="left" width="100%" style="font-size: 12px;background-color: rgb(0,32,96) ;color: rgb(255, 255, 255);">
                    <th width="15%" align ="center">CAT</th>
                    <th width="15%" align ="center">Sub_CAT</th>
                    <th width="35%" align ="center">Item</th>
                    <th width="15%" align ="center">Amt (VND)</th>
                    <th width="20%" align ="center">(Other)</th>
                </tr>
                '''+spending_detail_line+'''
                <tr align="left" width="100%" style="font-size: 12px">
                    <th width="15%" align ="center"></th>
                    <th width="15%" align ="center"></th>
                    <th width="35%" align ="center"></th>
                    <th width="15%" style="border: 2px solid black;font-size: 12px;background-color: rgb(0,32,96) ;color: rgb(255, 255, 255);" align ="center">'''+(format(int(bdf_purchase.amt), ',') or '')+'''</th>
                    <th width="20%" style="border: 2px solid black;font-size: 12px;background-color: rgb(0,32,96) ;color: rgb(255, 255, 255);" align ="center">'''+(format(int(bdf_purchase.fx_currency), ',') or '')+'''</th>
                </tr>
             </table>
             <p>Requestor:'''+(bdf_purchase.create_uid and bdf_purchase.create_uid.name or '')+'''
             <p>Note:</p>
        '''
        if bdf_purchase.user_comment:
            for line in bdf_purchase.user_comment.split('\n'):
                body = append_content_to_html(body, ("<p>%s</p>" % line), plaintext=False)
        body = append_content_to_html(body, ("<div><p>%s</p></div>" % approve_text), plaintext=False)
        body = append_content_to_html(body, ("<div><p>%s</p></div>" % text), plaintext=False)
        
        post_values = {
        'subject': 'Request Approval for PR %s %s'''%(bdf_purchase.name,bdf_purchase.description and bdf_purchase.description or ''),
        'body': body,
        'partner_ids': [],
        }
        lead_email = user.email
        msg_id = self.pool.get('bdf.purchase').message_post(cr, uid, [bdf_purchase.id], type='comment', subtype=False, context=context, **post_values)
        self.send_mail(cr, uid, lead_email, msg_id, context)
        
    def mail_for_procurement_pr(self, cr, uid, bdf_purchase, action, user, context=None):
        partner = user.partner_id
        partner.signup_prepare()
        url = partner._get_signup_url_for_action(action=action,view_type='form', res_id=bdf_purchase.id)[partner.id]
        text = _("""<p>Access this document <a href="%s">directly in OpenERP</a></p>""") % url
#         if bdf_purchase.state=='purchase_request':
#             bdf_purchase_state = 'Purchase Request'
#         elif bdf_purchase.state=='category_manager':
#             bdf_purchase_state = 'Category Manager'
#         elif bdf_purchase.state=='channel_manager':
#             bdf_purchase_state = 'Channel Manager'
#         elif bdf_purchase.state=='product_manager':
#             bdf_purchase_state = 'Product Manager (PM)'
#         elif bdf_purchase.state=='group_pm':
#             bdf_purchase_state = 'Group PM'
#         elif bdf_purchase.state=='bu_manager':
#             bdf_purchase_state = 'BU Manager'
#         elif bdf_purchase.state=='function_head':
#             bdf_purchase_state = 'Function Head'
#         elif bdf_purchase.state=='budget_control':
#             bdf_purchase_state = 'Budget Control'
#         elif bdf_purchase.state=='control_manager':
#             bdf_purchase_state = 'Control Manager'
#         elif bdf_purchase.state=='fi_function_head':
#             bdf_purchase_state = 'FI Function Head'
#         elif bdf_purchase.state=='country_manager':
#             bdf_purchase_state = 'Country Manager'
#         elif bdf_purchase.state=='procurement':
#             bdf_purchase_state = 'Procurement'
#         elif bdf_purchase.state=='cancel':
#             bdf_purchase_state = 'Cancel'
#         else:
#             bdf_purchase_state = ''
        amount=self.pool.get('bdf.purchase').get_amount(bdf_purchase)
#         body = '<p>PR number: %s</p><p>PR Descriptions: %s</p><p>PR value: %s</p><p>PR creator: %s</p><p>Comment history:</p>' \
#             %(bdf_purchase.name,bdf_purchase.description and bdf_purchase.description or '',format(amount, ','),bdf_purchase.create_uid.name)
        spending_detail_line = ''
        for line in bdf_purchase.spending_detail_line:
            spending_detail_line += '''
                <tr align="left" width="100%" style="font-size: 12px">
                    <th width="15%" style="border: 2px solid black;font-size: 12px" align ="center">'''+(line.cat and line.cat.name or '')+'''</th>
                    <th width="15%" style="border: 2px solid black;font-size: 12px" align ="center">'''+(line.sub_cat and line.sub_cat.name or '')+'''</th>
                    <th width="35%" style="border: 2px solid black;font-size: 12px" align ="center">'''+(line.product_id and line.product_id.name or '')+'''</th>
                    <th width="15%" style="border: 2px solid black;font-size: 12px" align ="center">'''+(format(int(line.amt), ',') or '')+'''</th>
                    <th width="20%" style="border: 2px solid black;font-size: 12px" align ="center">'''+(format(int(line.fx_currency), ',') or '')+'''</th>
                </tr>
            '''
        body = '''
            <table >
                <tr align="left" width="100%" style= "font-size: 12px">
                    <th width="15%" style="border: 2px solid black;font-size: 12px" align ="left">PR No.</th>
                    <th colspan="4" style="border: 2px solid black;font-size: 12px" width="85%" align ="left">'''+(bdf_purchase.name or '')+'''</th>
                </tr>
                <tr align="left" width="100%" style="font-size: 12px">
                    <th colspan="2" style="border: 2px solid black;font-size: 12px" width="30%" align ="left">Vendor</th>
                    <th colspan="3" style="border: 2px solid black;font-size: 12px" width="70%" align ="left">Description</th>
                </tr>
                <tr align="left" width="100%" style="font-size: 12px">
                    <th colspan="2" style="border: 2px solid black;font-size: 12px" width="30%" align ="left">'''+(bdf_purchase.supplier_id or '')+'''</th>
                    <th colspan="3" style="border: 2px solid black;font-size: 12px" width="70%" align ="left">'''+(bdf_purchase.description or '')+'''</th>
                </tr>
                <tr align="left" width="100%" style="font-size: 12px">
                    <th width="15%" align ="left"></th>
                    <th width="15%" align ="left"></th>
                    <th width="35%" align ="left"></th>
                    <th width="15%" align ="left"></th>
                    <th width="20%" style="border: 2px solid black;font-size: 12px;background-color: rgb(0,32,96) ;color: rgb(255, 255, 255);" align ="center">FX</th>
                </tr>
                <tr align="left" width="100%" style="font-size: 12px">
                    <th width="15%" align ="left"></th>
                    <th width="15%" align ="left"></th>
                    <th width="35%" align ="left"></th>
                    <th width="15%" align ="left"></th>
                    <th width="20%" style="border: 2px solid black;font-size: 12px" align ="center">'''+(str(bdf_purchase.fx) or '')+'''</th>
                </tr>
                <tr align="left" width="100%" style="font-size: 12px;background-color: rgb(0,32,96) ;color: rgb(255, 255, 255);">
                    <th width="15%" style="border: 2px solid black;font-size: 12px" align ="center">CAT</th>
                    <th width="15%" style="border: 2px solid black;font-size: 12px" align ="center">Sub_CAT</th>
                    <th width="35%" style="border: 2px solid black;font-size: 12px" align ="center">Item</th>
                    <th width="15%" style="border: 2px solid black;font-size: 12px" align ="center">Amt (VND)</th>
                    <th width="20%" style="border: 2px solid black;font-size: 12px" align ="center">(Other)</th>
                </tr>
                '''+spending_detail_line+'''
                <tr align="left" width="100%" style="font-size: 12px;">
                    <th width="15%" align ="center"></th>
                    <th width="15%" align ="center"></th>
                    <th width="35%" align ="center"></th>
                    <th width="15%" style="border: 2px solid black;font-size: 12px;background-color: rgb(0,32,96) ;color: rgb(255, 255, 255);" align ="center">'''+(format(int(bdf_purchase.amt), ',') or '')+'''</th>
                    <th width="20%" style="border: 2px solid black;font-size: 12px;background-color: rgb(0,32,96) ;color: rgb(255, 255, 255);" align ="center">'''+(format(int(bdf_purchase.fx_currency), ',') or '')+'''</th>
                </tr>
             </table>
             <p>Requestor:'''+(bdf_purchase.create_uid and bdf_purchase.create_uid.name or '')+'''
             <p>Note:</p>
        '''
        if bdf_purchase.user_comment:
            for line in bdf_purchase.user_comment.split('\n'):
                body = append_content_to_html(body, ("<p>%s</p>" % line), plaintext=False)
        body = append_content_to_html(body, ("<div><p>%s</p></div>" % text), plaintext=False)
        
        post_values = {
        'subject': 'PR %s Successfull Approved %s'''%(bdf_purchase.name,bdf_purchase.description and bdf_purchase.description or ''),
        'body': body,
        'partner_ids': [],
        }
        lead_email = user.email
        msg_id = self.pool.get('bdf.purchase').message_post(cr, uid, [bdf_purchase.id], type='comment', subtype=False, context=context, **post_values)
        self.send_mail(cr, uid, lead_email, msg_id, context)
    
    def bt_approve(self, cr, uid, ids, context=None):
        bdf_purchase_obj = self.pool.get('bdf.purchase')
        bdf_purchase_id = context.get('active_id')
        line_obj = self.pool.get('bdf.purchase.process.line')
        user = self.pool.get('res.users').browse(cr, uid, uid)
        for line in self.browse(cr, uid, ids):
            cr.execute('select user_comment from bdf_purchase where id = %s',(bdf_purchase_id,))
            user_comment = cr.fetchone()
            now = time.strftime('%d-%m-%Y %H:%M:%S')
            date_now = datetime.datetime.strptime(now, '%d-%m-%Y %H:%M:%S') + timedelta(hours=7)
            if user_comment and user_comment[0]:
                comment = user_comment[0]+'\n'+user.name+' Approved At %s: '%(date_now)+(line.message or '')
            else:
                comment = user.name+' Submit At %s: '%(date_now)+(line.message or '')
            cr.execute('update bdf_purchase set user_comment=%s where id = %s',(comment,bdf_purchase_id,))
            bdf_purchase = bdf_purchase_obj.browse(cr, uid, bdf_purchase_id)
            line_ids = line_obj.search(cr, uid, [('request_id','=',bdf_purchase_id),('is_done','=',False)],order='name')
            if line.is_done or not line_ids:
                if line.group_id.name=='Purchase Request':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'procurement','bdf_state': 'full_approved','request_by_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
#                     self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_procurement',line.user_id)
                elif line.group_id.name=='Category Manager':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'procurement','bdf_state': 'full_approved','category_manager_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
#                     self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_procurement',line.user_id)
                elif line.group_id.name=='Channel Manager':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'procurement','bdf_state': 'full_approved','channel_manager_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
#                     self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_procurement',line.user_id)
                elif line.group_id.name=='Product Manager (PM)':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'procurement','bdf_state': 'full_approved','product_manager_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
#                     self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_procurement',line.user_id)
                elif line.group_id.name=='Group PM':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'procurement','bdf_state': 'full_approved','group_pm_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
#                     self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_procurement',line.user_id)
                elif line.group_id.name=='BU Manager':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'procurement','bdf_state': 'full_approved','bu_manager_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
#                     self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_procurement',line.user_id)
                elif line.group_id.name=='Function Head':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'procurement','bdf_state': 'full_approved','function_head_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
#                     self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_procurement',line.user_id)
                elif line.group_id.name=='Budget Control':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'procurement','bdf_state': 'full_approved','budget_control_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
#                     self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_procurement',line.user_id)
                elif line.group_id.name=='Control Manager':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'procurement','bdf_state': 'full_approved','control_manager_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
#                     self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_procurement',line.user_id)
                elif line.group_id.name=='FI Function Head':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'procurement','bdf_state': 'full_approved','fi_function_head_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
#                     self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_procurement',line.user_id)
                else:
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'procurement','bdf_state': 'full_approved','country_manager_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
#                     self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_procurement',line.user_id)
                
                user_ids = []
                if bdf_purchase.request_by_id:
                    user_ids.append(bdf_purchase.request_by_id.id)
                if bdf_purchase.budget_control_approve_id:
                    user_ids.append(bdf_purchase.budget_control_approve_id.id)
                for u in self.pool.get('res.users').browse(cr, uid, user_ids):
                    self.mail_for_procurement_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_procurement',u)
                
            else:
                if line.group_id.name=='Purchase Request':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'request_by_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
                elif line.group_id.name=='Category Manager':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'category_manager_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
                elif line.group_id.name=='Channel Manager':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'channel_manager_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
                elif line.group_id.name=='Product Manager (PM)':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'product_manager_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
                elif line.group_id.name=='Group PM':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'group_pm_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
                elif line.group_id.name=='BU Manager':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'bu_manager_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
                elif line.group_id.name=='Function Head':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'function_head_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
                elif line.group_id.name=='Budget Control':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'budget_control_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
                elif line.group_id.name=='Control Manager':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'control_manager_approve_id':uid,'user_request_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
                elif line.group_id.name=='FI Function Head':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'fi_function_head_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
                else:
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'country_manager_approve_id':uid,'user_request_id':uid,'history_ids':[(4,uid)]})
                
                process = line_obj.browse(cr, uid, line_ids[0])
                group = process.group_id
                if group.name=='Purchase Request':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'purchase_request','bdf_state': 'draft','request_by_id':line.user_id.id,'user_id':line.user_id.id,'history_ids':[(4,line.user_id.id)]})
                    self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_request',line.user_id)
                elif group.name=='Category Manager':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'category_manager','bdf_state': 'pending','category_manager_id':line.user_id.id,'user_id':line.user_id.id,'history_ids':[(4,line.user_id.id)]})
                    self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_category_manager',line.user_id)
                elif group.name=='Channel Manager':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'channel_manager','bdf_state': 'pending','channel_manager_id':line.user_id.id,'user_id':line.user_id.id,'history_ids':[(4,line.user_id.id)]})
                    self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_channel_manager',line.user_id)
                elif group.name=='Product Manager (PM)':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'product_manager','bdf_state': 'pending','product_manager_id':line.user_id.id,'user_id':line.user_id.id,'history_ids':[(4,line.user_id.id)]})
                    self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_product_manager',line.user_id)
                elif group.name=='Group PM':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'group_pm','bdf_state': 'pending','group_pm_id':line.user_id.id,'user_id':line.user_id.id,'history_ids':[(4,line.user_id.id)]})
                    self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_group_pm',line.user_id)
                elif group.name=='BU Manager':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'bu_manager','bdf_state': 'pending','bu_manager_id':line.user_id.id,'user_id':line.user_id.id,'history_ids':[(4,line.user_id.id)]})
                    self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_bu_manager',line.user_id)
                elif group.name=='Function Head':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'function_head','bdf_state': 'pending','function_head_id':line.user_id.id,'user_id':line.user_id.id,'history_ids':[(4,line.user_id.id)]})
                    self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_function_head',line.user_id)
                elif group.name=='Budget Control':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'budget_control','bdf_state': 'pending','budget_control_id':line.user_id.id,'user_id':line.user_id.id,'history_ids':[(4,line.user_id.id)]})
                    self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_budget_control',line.user_id)
                elif group.name=='Control Manager':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'control_manager','bdf_state': 'pending','control_manager_id':line.user_id.id,'user_id':line.user_id.id,'history_ids':[(4,line.user_id.id)]})
                    self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_control_manager',line.user_id)
                elif group.name=='FI Function Head':
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'fi_function_head','bdf_state': 'pending','fi_function_head_id':line.user_id.id,'user_id':line.user_id.id,'history_ids':[(4,line.user_id.id)]})
                    self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_fi_function_head',line.user_id)
                else:
                    bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'state': 'country_manager','bdf_state': 'pending','country_manager_id':line.user_id.id,'user_id':line.user_id.id,'history_ids':[(4,line.user_id.id)]})
                    self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_country_manager',line.user_id)
                
                notify_ids = []
                for l in process.notify_ids:
                    self.mail_for_approve_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_for_all',l)
                    notify_ids.append((4,l.id))
                bdf_purchase_obj.write(cr, uid, [bdf_purchase_id], {'notify_ids': notify_ids})
                    
            line_ids = line_obj.search(cr, uid, [('request_id','=',bdf_purchase_id),('is_done','=',False)],order='name')
            if line_ids:
                line_obj.write(cr, uid, [line_ids[0]],{'is_done':True})
        return {'type': 'ir.actions.act_window_close'}
    
approve_pr()