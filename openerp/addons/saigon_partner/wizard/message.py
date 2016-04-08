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
class message_send(osv.osv_memory):
    _name = "message.send"
    
    _columns = {
        'name': fields.html('Message'),
    }

    _defaults = {
    }
    
    def save(self, cr, uid, ids, context=None):
        categ_ids = []
        teams = []
        temp = 0
        sale_order_id = context.get('active_ids')[0]
        project_obj = self.pool.get('project.project')
        project_type_obj = self.pool.get('project.type')
        user_obj = self.pool.get('res.users')
        project_category_obj = self.pool.get('project.category')
        task_obj = self.pool.get('project.task')
        sale_order_obj = self.pool.get('sale.order')
        sale_order = sale_order_obj.browse(cr, uid, sale_order_id)
        project_name = sale_order.name[2:]
        task_description = sale_order.client_order_ref
        if sale_order.order_line:
            for line in sale_order.order_line:
                if temp==0:
                    project_type_id = line.product_id.project_type_id.id
                    user_id = line.product_id.project_type_id.project_manager_id.id
                    temp = 1
                project_category_id = project_category_obj.search(cr, uid, [('name','=',line.product_id.name)])
                if not project_category_id:
                    project_category_obj.create(cr, uid, {'name':line.product_id.name})
                    categ_id = max(project_category_obj.search(cr, uid, [('name','=',line.product_id.name)]))
                else: 
                    categ_id = project_category_id[0]
                categ_ids.append(categ_id)
        project_id = project_obj.create(cr, uid, {'name':project_name,'privacy_visibility':'public','user_id':user_id,'project_type_id':project_type_id})
#         project_id = max(project_obj.search(cr, uid, [('name','=',project_name)]))
        project_task_type_ids = self.pool.get('project.task.type').search(cr, uid, [('name','=','Estimation')])
        if project_task_type_ids:
            project_task_type_id = project_task_type_ids[0]
        else:
            project_task_type_id = False
        task_name = 'Estimation'
        task_id = task_obj.create(cr, uid, {'name':task_name,'project_id':project_id,'categ_ids':[(6, 0, categ_ids)],'description':task_description,'stage_id':project_task_type_id})
        sale_order_obj.write(cr, uid, sale_order_id, {'create_task':True})
        project_type = project_type_obj.browse(cr, uid, project_type_id)
        teams += [x.id for x in project_type.members if x.id not in teams]
        if teams:
            for user in user_obj.browse(cr, uid, teams):
                message = self.browse(cr, uid, ids)[0]
                partner = user.partner_id
                action = 'project.action_view_task'
                partner.signup_prepare()
                url = partner._get_signup_url_for_action(action=action,view_type='form', res_id=task_id)[partner.id]
                text = _("""<p>Access this document <a href="%s">directly in OpenERP</a></p>""") % url
                body = '<p>Project %s created!</p><br/><p>%s</p>' % (project_name,message.name)
                body = append_content_to_html(body, ("<div><p>%s</p></div>" % text), plaintext=False)
                post_values = {
                'subject': project_name+'/Estimation',
                'body': body,
                'partner_ids': [],
                }
                
                lead_email = user.email
                msg_id = user_obj.message_post(cr, uid, [user.id], type='comment', subtype=False, context=context, **post_values)
                self.pool.get('account.voucher').send_mail(cr, uid, ids, lead_email, msg_id, context)
            post_values1 = {
                'subject': project_name+'/Estimation',
                'body': body,
                'partner_ids': [],
                }
            msg_id = task_obj.message_post(cr, uid, [task_id], type='comment', subtype=False, context=context, **post_values1)
        return True
message_send()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
