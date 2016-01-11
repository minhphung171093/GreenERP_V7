# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2013 OpenERP s.a. (<http://openerp.com>).
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
from functools import partial
import logging
from lxml import etree
from lxml.builder import E
from datetime import datetime, timedelta
import openerp
import time
from openerp import SUPERUSER_ID
from openerp import pooler, tools
import openerp.exceptions
from openerp.osv import fields,osv
from openerp.osv.orm import browse_record
from openerp.tools.translate import _
import datetime
from openerp.tools import append_content_to_html
_logger = logging.getLogger(__name__)

class vsis_hr_overtime(osv.osv):
    _name = "vsis.hr.overtime"
    _description = 'Overtime'
    _inherit = 'mail.thread'
    
#     def create(self, cr, uid, values, context=None):
#         if context is None:
#             context = {}
#         context = dict(context, mail_create_nolog=True)
#         overtime_id = super(vsis_hr_overtime, self).create(cr, uid, values, context=context)
#         group_obj = self.pool.get('res.groups')
#         category_ids = self.pool.get('ir.module.category').search(cr, uid, [('name','=','Human Resources')])
#         group_ids = group_obj.search(cr, uid, [('category_id','in',category_ids),('name','=','Manager')])
#         for group in group_obj.browse(cr, uid, group_ids):
#             user_ids = [x.id for x in group.users]
#             for user in self.pool.get('res.users').browse(cr, uid,user_ids):
#                 partner = user.partner_id
#                 action = 'user_overview.open_view_vsis_hr_overtime'
#                 partner.signup_prepare()
#                 url = partner._get_signup_url_for_action(action=action,view_type='form', res_id=overtime_id)[partner.id]
#                 text = _("""<p>Access this document <a href="%s">directly in OpenERP</a></p>""") % url
#                 body = '<p>new Overtime Requests created, please check and approve.</p>'
#                 body = append_content_to_html(body, ("<div><p>%s</p></div>" % text), plaintext=False)
#                 post_values = {
#                 'subject': 'Overtime Requests',
#                 'body': body,
#                 'partner_ids': [],
#                 }
#                 lead_email = user.email
#                 msg_id = self.pool.get('res.users').message_post(cr, uid, [user.id], type='comment', subtype=False, context=context, **post_values)
#                 mail_message_pool = self.pool.get('mail.message')
#                 mail_mail = self.pool.get('mail.mail')
#                 msg = mail_message_pool.browse(cr, SUPERUSER_ID, msg_id, context=context)
#                 body_html = msg.body
#                 if msg.author_id and msg.author_id.user_ids and msg.author_id.user_ids[0].alias_domain and msg.author_id.user_ids[0].alias_name:
#                     email_from = '%s <%s@%s>' % (msg.author_id.name, msg.author_id.user_ids[0].alias_name, msg.author_id.user_ids[0].alias_domain)
#                 elif msg.author_id:
#                     email_from = '%s <%s>' % (msg.author_id.name, msg.author_id.email)
#                 else:
#                     email_from = msg.email_from
#                 references = False
#                 if msg.parent_id:
#                     references = msg.parent_id.message_id
#                 mail_values = {
#                     'mail_message_id': msg.id,
#                     'auto_delete': True,
#                     'body_html': body_html,
#                     'email_from': email_from,
#                     'email_to' : lead_email,
#                     'references': references,
#                 }
#                 email_notif_id = mail_mail.create(cr, uid, mail_values, context=context)
#                 try:
#                     mail_mail.send(cr, uid, [email_notif_id], context=context)
#                 except Exception:
#                     a = 1
#         return overtime_id
    
    def _employee_get(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False
    def _get_number_of_hours(self, hour_start, hour_end):
        timedelta = hour_end - hour_start
        diff_day = timedelta > 4 and timedelta - 1 or timedelta 
        return diff_day
    
    def onchange_hour_start(self, cr, uid, ids, hour_start, hour_end):
        if (hour_start and hour_end) and (hour_start > hour_end):
            raise osv.except_osv(_('Warning!'),_('The starting hour must be anterior to the ending hour.'))
        result = {'value': {}}

        # Compute and update the number of days
        if (hour_start and hour_end) and (hour_start <= hour_end):
            diff_day = self._get_number_of_hours(hour_start, hour_end)
            result['value']['durations'] = diff_day
        else:
            result['value']['durations'] = 0

        return result
    
    def _month_compute(self, cr, uid, ids, fieldnames, args, context=None):
        res = dict.fromkeys(ids, '')
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = time.strftime('%Y-%m', time.strptime(obj.name, '%Y-%m-%d'))
        return res
    
    def _compute_durations(self, cr, uid, ids, name, args, context=None):
        result = {}
        for over in self.browse(cr, uid, ids, context=context):
            if (over.hour_start and over.hour_end) and (over.hour_start <= over.hour_end):
                diff_day = self._get_number_of_hours(over.hour_start, over.hour_end)
                result[over.id] = diff_day
            else:
                result[over.id] = 0
        return result
    
    _columns = {
                'name': fields.date('Date', required=True),
                'hour_start':fields.float('Starting Hour', required=True),
                'hour_end':fields.float('Ending Hour', required=True),
                'project_id':fields.many2one('project.project', 'Project Name', select =True),
                'employee_id': fields.many2one('hr.employee', "Employee", select=True),
                'durations': fields.function(_compute_durations,string='Durations', type='float',store=True),
                'state': fields.selection([('to_approve', 'To Approved'), ('refuse', 'Refused'),('confirm', 'Approve'), ('cancel', 'Cancelled')],'Status'),
                'month': fields.function(_month_compute, type='char', string='Month', store=True, select=1, size=32),
                }
    _defaults = {
        'name': lambda *a: time.strftime('%Y-%m-%d'),
        'employee_id': _employee_get,
        'state': 'to_approve',
    }
    
    _sql_constraints = [
        ('date_check', "CHECK (hour_start <= hour_end)", "The starting hour must be anterior to the ending hour."),
        ('employee_id_uniq', 'unique (name,employee_id)', 'The employee must be unique !'),
    ]
    
    def to_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'to_approve'})
    def confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'confirm'})
    def refuse(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'refuse'})
    def cancelled(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'})

vsis_hr_overtime()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
