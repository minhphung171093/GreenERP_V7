##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from openerp import netsvc
import datetime
from openerp import SUPERUSER_ID
from openerp.tools import append_content_to_html
class work_summary(osv.osv_memory):
    _name = "work.summary"
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(work_summary, self).default_get(cr, uid, fields, context=context)
        task_id = context['active_ids'][0]
        task = self.pool.get('project.task').browse(cr, uid, task_id)
        res.update({'previous_assigned_to': task.project_id.user_id.id,'checking_task': task.checking_task})
        
        hours = 0
        if not context.get('quick_check',False):
            attendances_times_obj = self.pool.get('attendances.time')
            list_attendances_id =  max(attendances_times_obj.search(cr,1,[('user_id','=',uid)]))
            date_now_d = datetime.datetime.now() + timedelta(hours=7)
            line = attendances_times_obj.browse(cr, 1, list_attendances_id)
            date = datetime.datetime.strptime(line.name, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
            total = self.pool.get('user.overview')._sum_total(cr, uid, uid, date, date_now_d, context)
            hours = float(total)/3600
        res.update({
                'work_ids':[(0,0,{
                              'name': 'Summary ...',
                              'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                              'user_id': uid,
                              'hours': hours,
                              })],
                'task_id': task_id,
                    })
        
        return res
    
    
    _columns = {
        'task_id': fields.many2one('project.task','Task',readonly=True),
        'work_ids': fields.one2many('work.summary.line', 'task_id', 'Work done'),
        'error_ids': fields.one2many('error.reporting.line', 'task_id', 'Error Reporting'),
        'is_done': fields.boolean('Submit for checking'),
        'back_for_repair': fields.boolean('Back for repair'),
        'ready_for_delivery': fields.boolean('Ready for delivery'),
        'previous_assigned_to': fields.many2one('res.users','Previous Assigned to'),
        'send_message': fields.text('Send a message'),
        'checking_task': fields.selection([('checking1','checking1'),('checking2','checking2'),('none','None')], 'Status', readonly=True),
        'attachment_ids': fields.many2many('ir.attachment',
            'worksummary_ir_attachments_rel',
            'worksummary_id', 'attachment_id', 'Attachments'),
    }

    _defaults = {
        'is_done':False,
        'back_for_repair':False,
        'ready_for_delivery':False,
    }
    
    def onchange_back_for_repair(self, cr, uid, ids, back_for_repair, ready_for_delivery, context=None):
        vals={}
        if back_for_repair==True and ready_for_delivery==True:
            vals['value'] = {'back_for_repair':True,'ready_for_delivery':False}
        return vals
    
    def onchange_ready_for_delivery(self, cr, uid, ids, back_for_repair, ready_for_delivery, context=None):
        vals={}
        if back_for_repair==True and ready_for_delivery==True:
            vals['value'] = {'back_for_repair':False,'ready_for_delivery':True}
        return vals
    
    def send_mail(self, cr, uid, ids, lead_email, msg_id,context=None):
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
            mail_mail.send(cr, uid, [email_notif_id], context=context)
        except Exception:
            a = 1
        return True
    
    def save(self, cr, uid, ids, context=None):
        user_overview_obj = self.pool.get('user.overview')
        task_type_obj = self.pool.get('project.task.type')
        task_obj = self.pool.get('project.task')
        user_obj = self.pool.get('res.users')
        task_id = context.get('active_ids')[0]
        project_task = task_obj.browse(cr, uid, task_id)
        line = self.browse(cr,uid,ids)[0]
        
        quick_check = context.get('quick_check')
        
        if line.work_ids or quick_check:
            for task in line.work_ids:
                self.pool.get('project.task.work').create(cr, uid, {
                    'name':task.name,
                    'task_id':task_id,
                    'hours': task.hours,
                    'date': task.date,
                    'user_id': task.user_id.id,
            }, context=context)
        else:
            raise osv.except_osv(_('Warning!'),
                        _('Please add working summary!'))
        if line.is_done == True:
            if line.previous_assigned_to:
                
                partner = line.previous_assigned_to.partner_id
                action = 'project.action_view_task'
                partner.signup_prepare()
                url = partner._get_signup_url_for_action(action=action,view_type='form', res_id=task_id)[partner.id]
                text = _("""<p>Access this document <a href="%s">directly in OpenERP</a></p>""") % url
                body = '<p>%s</p>' % (line.send_message)
                body = append_content_to_html(body, ("<div><p>%s</p></div>" % text), plaintext=False)
                
                post_values = {
                'subject': 'Submit for checking Task %s'%(project_task.name),
                'body': body,
                'partner_ids': [],
                'attachment_ids': [attach.id for attach in line.attachment_ids],
                }
                lead_email = line.previous_assigned_to.email
                msg_id = task_obj.message_post(cr, uid, [task_id], type='comment', subtype=False, context=context, **post_values)
                self.send_mail(cr, uid, ids, lead_email, msg_id, context)
            task_type_id = task_type_obj.search(cr, uid, [('name','=','Checking')])
            task_obj.write(cr, uid, task_id, {'flag':True,'status_task': 'paused','checking_task': 'checking1','previous_assigned_to1':line.previous_assigned_to.id,'stage_id':task_type_id[0]})
        elif line.back_for_repair == True and line.checking_task=='checking1':
            if project_task.previous_assigned_to1:
                
                partner = project_task.user_id.partner_id
                action = 'project.action_view_task'
                partner.signup_prepare()
                url = partner._get_signup_url_for_action(action=action,view_type='form', res_id=task_id)[partner.id]
                text = _("""<p>Access this document <a href="%s">directly in OpenERP</a></p>""") % url
                body = '<p>%s</p>' % (line.send_message)
                body = append_content_to_html(body, ("<div><p>%s</p></div>" % text), plaintext=False)
                
                post_values = {
                'subject': 'Error Task %s' %(project_task.name),
                'body': body,
                'partner_ids': [],
                'attachment_ids': [attach.id for attach in line.attachment_ids],
                }
                lead_email = project_task.user_id.email
                msg_id = task_obj.message_post(cr, uid, [task_id], type='comment', subtype=False, context=context, **post_values)
                self.send_mail(cr, uid, ids, lead_email, msg_id, context)
            if line.error_ids:
                for task in line.error_ids:
                    self.pool.get('error.line').create(cr, uid, {
                        'error_id':task.error_id.id,
                        'task_id':task_id,
                        'date': task.date,
                }, context=context)
            task_type_id = task_type_obj.search(cr, uid, [('name','=','Drawing')])
            task_obj.write(cr, uid, task_id, {'flag':True,'status_task': 'paused','checking_task': 'none','previous_assigned_to1':[],'stage_id':task_type_id[0]})
        elif line.back_for_repair == True and line.checking_task=='checking2':
            if project_task.previous_assigned_to2:
                
                partner = project_task.previous_assigned_to1.partner_id
                action = 'project.action_view_task'
                partner.signup_prepare()
                url = partner._get_signup_url_for_action(action=action,view_type='form', res_id=task_id)[partner.id]
                text = _("""<p>Access this document <a href="%s">directly in OpenERP</a></p>""") % url
                body = '<p>%s</p>' % (line.send_message)
                body = append_content_to_html(body, ("<div><p>%s</p></div>" % text), plaintext=False)
                
                post_values = {
                'subject': 'Error Task  %s' %(project_task.name),
                'body': body,
                'partner_ids': [],
                'attachment_ids': [attach.id for attach in line.attachment_ids],
                }
                lead_email = project_task.previous_assigned_to1.email
                msg_id = task_obj.message_post(cr, uid, [task_id], type='comment', subtype=False, context=context, **post_values)
                self.send_mail(cr, uid, ids, lead_email, msg_id, context)
            if line.error_ids:
                for task in line.error_ids:
                    self.pool.get('error.line').create(cr, uid, {
                        'error_id':task.error_id.id,
                        'task_id':task_id,
                        'date': task.date,
                }, context=context)
            task_type_id = task_type_obj.search(cr, uid, [('name','=','Checking')])
            task_obj.write(cr, uid, task_id, {'flag':True,'status_task': 'paused','checking_task': 'checking1','previous_assigned_to2':[],'stage_id':task_type_id[0]})
        elif line.ready_for_delivery == True and line.checking_task=='checking1':
            if line.previous_assigned_to:
                
                partner = line.previous_assigned_to.partner_id
                action = 'project.action_view_task'
                partner.signup_prepare()
                url = partner._get_signup_url_for_action(action=action,view_type='form', res_id=task_id)[partner.id]
                text = _("""<p>Access this document <a href="%s">directly in OpenERP</a></p>""") % url
                body = '<p>%s</p>' % (line.send_message)
                body = append_content_to_html(body, ("<div><p>%s</p></div>" % text), plaintext=False)
                
                post_values = {
                'subject': 'Checking Task %s' %(project_task.name),
                'body': body,
                'partner_ids': [],
                'attachment_ids': [attach.id for attach in line.attachment_ids],
                }
                lead_email = line.previous_assigned_to.email
                msg_id = task_obj.message_post(cr, uid, [task_id], type='comment', subtype=False, context=context, **post_values)
                self.send_mail(cr, uid, ids, lead_email, msg_id, context)
            task_type_id = task_type_obj.search(cr, uid, [('name','=','Checking')])
            task_obj.write(cr, uid, task_id, {'flag':True,'status_task': 'paused','checking_task': 'checking2','previous_assigned_to2':line.previous_assigned_to.id,'stage_id':task_type_id[0]})
        elif line.ready_for_delivery == True and line.checking_task=='checking2':
            task_type_id = task_type_obj.search(cr, uid, [('name','=','Ready for delivery')])
            task_obj.write(cr, uid, task_id, {'flag':True,'status_task': 'paused','checking_task': 'none','stage_id':task_type_id[0]})
        else:
            task_obj.write(cr, uid, task_id, {'flag':True,'status_task': 'paused'})
        val= {
                    'name':datetime.datetime.now(),
                    'task_id':task_id,
                    'action': 'sign_out',
            }
        context.update({'data': val})
        if not quick_check:
            user_overview_obj.get_datat(cr,uid,ids,context)
            user_overview_obj.onchange_attendances_times(cr, uid, context)
        res = {'type': 'ir.actions.client', 'tag': 'reload' }
        return res
work_summary()

class work_summary_line(osv.osv_memory):
    _name = "work.summary.line"
    
    def _get_hours(self, cr, uid, context=None):
#         quick_check = context.get('quick_check',False)
        hours = 0
#         if not quick_check:
        attendances_times_obj = self.pool.get('attendances.time')
        list_attendances_id =  max(attendances_times_obj.search(cr,uid,[('user_id','=',uid)]))
        date_now_d = datetime.datetime.now() + timedelta(hours=7)
        line = attendances_times_obj.browse(cr, uid, list_attendances_id)
        date = datetime.datetime.strptime(line.name, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
        total = self.pool.get('user.overview')._sum_total(cr, uid, uid, date, date_now_d, context)
        hours = float(total)
        return hours/3600
    
    _columns = {
        'name': fields.char('Work summary', size=128),
        'date': fields.datetime('Date', select="1", readonly=True),
        'task_id': fields.many2one('work.summary', 'Task', ondelete='cascade', required=True, select="1"),
        'hours': fields.float('Time Spent', readonly=True),
        'user_id': fields.many2one('res.users', 'Done by', required=True, select="1", readonly=True),
    }

    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
#         'hours': _get_hours,
        'name': 'Summary ...',
    }
work_summary_line()

class error_reporting_line(osv.osv_memory):
    _name = "error.reporting.line"
    _columns = {
                'error_id': fields.many2one('error.reporting','Error summary'),
                'date': fields.date('Date'),
                'task_id': fields.many2one('work.summary', 'Task', ondelete='cascade', required=True, select="1"),
        }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d')
    }

error_reporting_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
