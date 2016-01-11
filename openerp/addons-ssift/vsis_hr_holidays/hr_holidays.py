# -*- coding: utf-8 -*-
##################################################################################
#
# Copyright (c) 2005-2006 Axelor SARL. (http://www.axelor.com)
# and 2004-2010 Tiny SPRL (<http://tiny.be>).
#
# $Id: hr.py 4656 2006-11-24 09:58:42Z Cyp $
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from itertools import groupby
from operator import itemgetter

import math
from openerp import netsvc
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import append_content_to_html
from datetime import datetime, timedelta
import datetime
from datetime import date

class hr_holidays(osv.osv):
    _inherit = "hr.holidays"

    def create(self, cr, uid, values, context=None):
        """ Override to avoid automatic logging of creation """
        if context is None:
            context = {}
        context = dict(context, mail_create_nolog=True)
        holiday_id = super(hr_holidays, self).create(cr, uid, values, context=context)
        number_of_days_temp = self.browse(cr, uid,holiday_id).number_of_days_temp
        type = self.browse(cr, uid,holiday_id).type
        if values['holiday_type'] == 'employee' and type =='remove':
            group_obj = self.pool.get('res.groups')
            category_ids = self.pool.get('ir.module.category').search(cr, uid, [('name','=','Human Resources')])
            group_ids = group_obj.search(cr, uid, [('category_id','in',category_ids),('name','=','Manager')])
            for group in group_obj.browse(cr, uid, group_ids):
                user_ids = [x.id for x in group.users]
                for user in self.pool.get('res.users').browse(cr, uid,user_ids):
                    
                    partner = user.partner_id
                    action = 'hr_holidays.open_ask_holidays'
                    partner.signup_prepare()
                    url = partner._get_signup_url_for_action(action=action,view_type='form', res_id=holiday_id)[partner.id]
                    text = _("""<p>Access this document <a href="%s">directly in OpenERP</a></p>""") % url
                    body = '<p>new Leave Requests created, please check and approve.</p><p>%s</p>'%(self.browse(cr, uid,holiday_id).name)
                    body = append_content_to_html(body, ("<div><p>%s</p></div>" % text), plaintext=False)
                    
                    employee = self.pool.get('hr.employee').browse(cr, uid, values['employee_id']).name
                    if 'date_from' in values:
                        date_from = datetime.datetime.strptime(values['date_from'], '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                    else:
                        date_from = ''
                    if 'date_to' in values:
                        date_to = datetime.datetime.strptime(values['date_to'], '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                    else:
                        date_to = ''
                    post_values = {
                    'subject': 'leave request submitted | %s | %s | from %s to %s'%(employee,number_of_days_temp,date_from,date_to),
                    'body': body,
                    'partner_ids': [],
                    }
                    lead_email = user.email
                    msg_id = self.pool.get('res.users').message_post(cr, uid, [user.id], type='comment', subtype=False, context=context, **post_values)
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
        return holiday_id
    
    def holidays_validate(self, cr, uid, ids, context=None):
        self.check_holidays(cr, uid, ids, context=context)
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write(cr, uid, ids, {'state':'validate'})
        data_holiday = self.browse(cr, uid, ids)
        for record in data_holiday:
            
            if record.holiday_type == 'employee' and 'type'=='remove':
                post_values = {
                'subject': 'your leave request approved | %s | %s | from %s to %s'%(record.employee_id.name,record.number_of_days_temp,datetime.datetime.strptime(record.date_from, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7),datetime.datetime.strptime(record.date_to, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)),
                'body': '',
                'partner_ids': [],
                }
                if not record.employee_id.user_id:
                    raise osv.except_osv(_('Warning!'),
                        _('Please create user for employee!'))
                lead_email = record.employee_id.user_id.email
                msg_id = self.pool.get('res.users').message_post(cr, uid, [record.employee_id.user_id.id], type='comment', subtype=False, context=context, **post_values)
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
            
            if record.double_validation:
                self.write(cr, uid, [record.id], {'manager_id2': manager})
            else:
                self.write(cr, uid, [record.id], {'manager_id': manager})
            if record.holiday_type == 'employee' and record.type == 'remove':
                meeting_obj = self.pool.get('crm.meeting')
                meeting_vals = {
                    'name': record.name or _('Leave Request'),
                    'categ_ids': record.holiday_status_id.categ_id and [(6,0,[record.holiday_status_id.categ_id.id])] or [],
                    'duration': record.number_of_days_temp * 8,
                    'description': record.notes,
                    'user_id': record.user_id.id,
                    'date': record.date_from,
                    'end_date': record.date_to,
                    'date_deadline': record.date_to,
                    'state': 'open',            # to block that meeting date in the calendar
                }
                meeting_id = meeting_obj.create(cr, uid, meeting_vals)
                self._create_resource_leave(cr, uid, [record], context=context)
                self.write(cr, uid, ids, {'meeting_id': meeting_id})
            elif record.holiday_type == 'category':
                emp_ids = obj_emp.search(cr, uid, [('category_ids', 'child_of', [record.category_id.id])])
                leave_ids = []
                for emp in obj_emp.browse(cr, uid, emp_ids):
                    vals = {
                        'name': record.name,
                        'type': record.type,
                        'holiday_type': 'employee',
                        'holiday_status_id': record.holiday_status_id.id,
                        'date_from': record.date_from,
                        'date_to': record.date_to,
                        'notes': record.notes,
                        'number_of_days_temp': record.number_of_days_temp,
                        'parent_id': record.id,
                        'employee_id': emp.id
                    }
                    leave_ids.append(self.create(cr, uid, vals, context=None))
                wf_service = netsvc.LocalService("workflow")
                for leave_id in leave_ids:
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
        return True
    
hr_holidays()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
