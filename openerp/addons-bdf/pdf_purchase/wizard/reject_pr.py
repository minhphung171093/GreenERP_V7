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
WARNING_TYPES = [('warning','Warning'),('info','Information'),('error','Error')]
import datetime

class reject_pr(osv.osv_memory):
    _name = "reject.pr"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(reject_pr, self).default_get(cr, uid, fields, context=context)
        res.update({'request_id':context.get('active_id',False)})
        return res
    
    _columns = {    
        'request_id': fields.many2one('bdf.purchase', 'Request'),
        'message': fields.text("Message", required=False),
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
    
    def mail_for_reject_pr(self, cr, uid, bdf_purchase, action, user, context=None):
        partner = user.partner_id
        partner.signup_prepare()
        url = partner._get_signup_url_for_action(action=action,view_type='form', res_id=bdf_purchase.id)[partner.id]
        text = _("""<p>Access this document <a href="%s">directly in OpenERP</a></p>""") % url
        amount=self.pool.get('bdf.purchase').get_amount(bdf_purchase)
#         body = '<p>PR number: %s</p><p>PR Descriptions: %s</p><p>PR value: %s</p><p>PR creator: %s</p><p>PR status: %s</p><p>Comment history:</p>' \
#             %(bdf_purchase.name,bdf_purchase.description and bdf_purchase.description or '',format(amount, ','),bdf_purchase.create_uid.name,'Purchase Request')
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
        body = append_content_to_html(body, ("<div><p>%s</p></div>" % text), plaintext=False)
        
        post_values = {
        'subject': 'Reject for PR %s %s'''%(bdf_purchase.name,bdf_purchase.description and bdf_purchase.description or ''),
        'body': body,
        'partner_ids': [],
        }
        lead_email = user.email
        msg_id = self.pool.get('bdf.purchase').message_post(cr, uid, [bdf_purchase.id], type='comment', subtype=False, context=context, **post_values)
        self.send_mail(cr, uid, lead_email, msg_id, context)
    
    def bt_reject(self, cr, uid, ids, context=None):
        bdf_purchase_obj = self.pool.get('bdf.purchase')
        bdf_purchase_id = context.get('active_id')
        user = self.pool.get('res.users').browse(cr, uid, uid)
        bdf_purchase = bdf_purchase_obj.browse(cr, uid, bdf_purchase_id)
        for line in self.browse(cr, uid, ids):
            cr.execute('select user_comment from bdf_purchase where id = %s',(bdf_purchase_id,))
            user_comment = cr.fetchone()
            now = time.strftime('%d-%m-%Y %H:%M:%S')
            date_now = datetime.datetime.strptime(now, '%d-%m-%Y %H:%M:%S') + timedelta(hours=7)
            if user_comment and user_comment[0]:
                comment = user_comment[0]+'\n'+user.name+' Reject At %s: '%(date_now)+(line.message or '')
            else:
                comment = user.name+': '+(line.message or '')
            cr.execute('update bdf_purchase set user_comment=%s where id = %s',(comment,bdf_purchase_id,))
            
            user_ids = []
            if bdf_purchase.request_by_id:
                user_ids.append(bdf_purchase.request_by_id.id)
            if bdf_purchase.category_manager_approve_id:
                user_ids.append(bdf_purchase.category_manager_approve_id.id)
            if bdf_purchase.channel_manager_approve_id:
                user_ids.append(bdf_purchase.channel_manager_approve_id.id)
            if bdf_purchase.product_manager_approve_id:
                user_ids.append(bdf_purchase.product_manager_approve_id.id)
            if bdf_purchase.group_pm_approve_id:
                user_ids.append(bdf_purchase.group_pm_approve_id.id)
            if bdf_purchase.bu_manager_approve_id:
                user_ids.append(bdf_purchase.bu_manager_approve_id.id)
            if bdf_purchase.function_head_approve_id:
                user_ids.append(bdf_purchase.function_head_approve_id.id)
            if bdf_purchase.budget_control_approve_id:
                user_ids.append(bdf_purchase.budget_control_approve_id.id)
            if bdf_purchase.control_manager_approve_id:
                user_ids.append(bdf_purchase.control_manager_approve_id.id)
            if bdf_purchase.fi_function_head_approve_id:
                user_ids.append(bdf_purchase.fi_function_head_approve_id.id)
            if bdf_purchase.country_manager_approve_id:
                user_ids.append(bdf_purchase.country_manager_approve_id.id)
            for l in bdf_purchase.notify_ids:
                if l.id not in user_ids:
                    user_ids.append(l.id)
            for u in self.pool.get('res.users').browse(cr, uid, user_ids):
                self.mail_for_reject_pr(cr, uid, bdf_purchase, 'pdf_purchase.action_view_bdf_purchase_for_all',u)
            bdf_purchase_obj.write(cr, uid, [bdf_purchase_id],{'state':'reject','bdf_state': 'reject'})
            cr.execute('''
                update bdf_purchase set category_manager_id = null, channel_manager_id = null,product_manager_id = null, group_pm_id = null,bu_manager_id = null,
                 function_head_id = null,budget_control_id = null,control_manager_id = null,fi_function_head_id = null,country_manager_id = null,request_by_id = null,
                 category_manager_approve_id = null,channel_manager_approve_id = null,product_manager_approve_id = null, group_pm_approve_id = null, bu_manager_approve_id = null,
                 function_head_approve_id = null, budget_control_approve_id = null, control_manager_approve_id = null, fi_function_head_approve_id = null, country_manager_approve_id = null, user_request_id = null, user_id=bdf_purchase.create_uid  
                 where id=%s
            ''',(bdf_purchase_id,))
            cr.execute('delete from bdf_purchase_user_ref where bdf_purchase_id=%s',(bdf_purchase_id,))
            cr.execute('''update bdf_purchase_process_line set is_done='f',is_pass='f' where request_id=%s 
                and id not in (select id from bdf_purchase_process_line where request_id=%s order by name limit 1) ''',(bdf_purchase_id,bdf_purchase_id,))
        return {'type': 'ir.actions.act_window_close'}
    
reject_pr()