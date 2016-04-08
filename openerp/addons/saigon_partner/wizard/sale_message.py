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
from openerp.tools import append_content_to_html
class sale_message(osv.osv_memory):
    _name = "sale.message"
    
    _columns = {
        'name': fields.html('Message'),
    }

    _defaults = {
    }

    def save(self, cr, uid, ids, context=None):
        project_obj = self.pool.get('project.project')
        user_obj = self.pool.get('res.users')
        sale_order_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        teams = []
        sale_ids = context['active_ids']
        assert len(sale_ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'sale.order', sale_ids[0], 'order_confirm', cr)

        # redisplay the record as a sales order
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'view_order_form')
        view_id = view_ref and view_ref[1] or False,
        sale_order = sale_order_obj.browse(cr, uid, sale_ids[0])
        project_name = sale_order.name[2:]
        project_ids = project_obj.search(cr ,uid, [('name','=',project_name)])
        if project_ids:
            project_id = max(project_ids)
            project = project_obj.browse(cr, uid, project_id)
            teams += [x.id for x in project.project_type_id.members if x.id not in teams]
            if teams:
                for user in user_obj.browse(cr, uid, teams):
                    message = self.browse(cr, uid, ids)[0]
                    partner = user.partner_id
                    action = 'project.open_view_project_all'
                    partner.signup_prepare()
                    url = partner._get_signup_url_for_action(action=action,view_type='form', res_id=project_id)[partner.id]
                    text = _("""<p>Access this document <a href="%s">directly in OpenERP</a></p>""") % url
                    body = '<p>%s</p><br/>' % (message.name)
                    body = append_content_to_html(body, ("<div><p>%s</p></div>" % text), plaintext=False)
                    post_values = {
                        'subject': 'Project '+project_name+'/Start',
                        'body': body,
                        'partner_ids': [],
                    }
                    lead_email = user.email
                    msg_id = user_obj.message_post(cr, uid, [user.id], type='comment', subtype=False, context=context, **post_values)
                    self.pool.get('account.voucher').send_mail(cr, uid, ids, lead_email, msg_id, context)
                post_values1 = {
                        'subject': 'Project '+project_name+'/Start',
                        'body': body,
                        'partner_ids': [],
                    }
                msg_id = project_obj.message_post(cr, uid, [project_id], type='comment', subtype=False, context=context, **post_values1)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales Order'),
            'res_model': 'sale.order',
            'res_id': sale_ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }
sale_message()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
