# -*- coding: utf-8 -*-
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

import time
from lxml import etree

from openerp import netsvc
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
from openerp.report import report_sxw
from openerp import tools
from openerp import SUPERUSER_ID
class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    def send_mail(self, cr, uid, ids, lead_email, msg_id ,context=None):
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
    def button_proforma_voucher(self, cr, uid, ids, context=None):
        res_ids = []
        message_follower_ids = []
        project_obj= self.pool.get('project.project')
        user_obj = self.pool.get('res.users')
        partner_obj = self.pool.get('res.partner')
        context = context or {}
        invoice_obj = self.pool.get('account.invoice')
        invoice_id = context['active_id']
        wf_service = netsvc.LocalService("workflow")
        for vid in ids:
            wf_service.trg_validate(uid, 'account.voucher', vid, 'proforma_voucher', cr)
        invoice = invoice_obj.browse(cr, uid, invoice_id)
        message_follower_ids += [x.id for x in invoice.message_follower_ids if x.id not in message_follower_ids]
        if invoice.origin:
            project_name = invoice.origin[2:]
            project_ids = project_obj.search(cr, uid, [('name','=',project_name)])
            if project_ids:
                project_id = project_ids[0]
                project = project_obj.browse(cr, uid, project_id)
                if project.members:
                    res_ids += [x.id for x in project.project_type_id.members if x.id not in res_ids]
                post_values = {
                        'subject': 'The invoice '+invoice.number+' is paid',
                        'body': '<p><b>Custommer: %s</b><br/>Invoice Amount: %s</p>' % (invoice.partner_id.name,invoice.amount_total),
                        'partner_ids': [],
                    }
                if res_ids:
                    for user in user_obj.browse(cr, uid, res_ids):
                        lead_email = user.email
                        msg_id = user_obj.message_post(cr, uid, [user.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, ids, lead_email, msg_id, context)
                if message_follower_ids:
                    for partner in partner_obj.browse(cr, uid, message_follower_ids):
                        lead_email_partner = partner.email
                        msg_id_partner = partner_obj.message_post(cr, uid, [partner.id], type='comment', subtype=False, context=context, **post_values)
                        self.send_mail(cr, uid, ids, lead_email_partner, msg_id_partner, context)
        return {'type': 'ir.actions.act_window_close'}
account_voucher()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
