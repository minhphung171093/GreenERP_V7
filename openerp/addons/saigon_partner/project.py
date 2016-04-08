# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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

from datetime import datetime, date
from lxml import etree
import time

from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

from openerp.addons.base_status.base_stage import base_stage
from openerp.addons.resource.faces import task as Task


class project(osv.osv):
    _inherit = "project.project"

    _columns = {
        'project_type_id': fields.many2one('project.type', 'Project Type', required=True),
     }
    def onchange_project_type(self, cr, uid, ids, project_type_id, context=None):
        task_obj = self.pool.get('project.task')
        if project_type_id:
            task_ids = task_obj.search(cr, uid, [('project_id','in',ids)])
            for task in task_obj.browse(cr, uid, task_ids):
                task_obj.write(cr, uid, task.id,{'project_type_id':project_type_id})
        return True
project()

class task(osv.osv):
    _inherit = "project.task"
    _columns = {
        'project_type_id': fields.many2one('project.type', 'Project Type'),
     }
#     def init(self, cr):
#         task_ids = self.search(cr, 1, [])
#         for task in self.browse(cr, 1, task_ids):
#             if task.project_id.project_type_id:
#                 self.write(cr, 1, task.id, {'project_type_id':task.project_id.project_type_id.id}, context=None)
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('project_id') and not context.get('default_project_id'):
            context['default_project_id'] = vals.get('project_id')

        # context: no_log, because subtype already handle this
        create_context = dict(context, mail_create_nolog=True)
        if 'project_id' in vals:
            project = self.pool.get('project.project').browse(cr, uid, vals['project_id'])
            vals['project_type_id'] = project.project_type_id.id
            if 'name' in vals:
                task_name = str(project.name)+'-'+str(vals['name'])
                vals['name'] = task_name
        task_id = super(task, self).create(cr, uid, vals, context=create_context)
        self._store_history(cr, uid, [task_id], context=context)
        return task_id
    
    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if vals and not 'kanban_state' in vals and 'stage_id' in vals:
            new_stage = vals.get('stage_id')
            vals_reset_kstate = dict(vals, kanban_state='normal')
            for t in self.browse(cr, uid, ids, context=context):
                #TO FIX:Kanban view doesn't raise warning
                #stages = [stage.id for stage in t.project_id.type_ids]
                #if new_stage not in stages:
                    #raise osv.except_osv(_('Warning!'), _('Stage is not defined in the project.'))
                write_vals = vals_reset_kstate if t.stage_id != new_stage else vals
                if 'project_id' in vals:
                    project = self.pool.get('project.project').browse(cr, uid, vals['project_id'])
                    write_vals['project_type_id'] = project.project_type_id.id
                super(task, self).write(cr, uid, [t.id], write_vals, context=context)
            result = True
        else:
            if 'project_id' in vals:
                project = self.pool.get('project.project').browse(cr, uid, vals['project_id'])
                vals['project_type_id'] = project.project_type_id.id
            result = super(task, self).write(cr, uid, ids, vals, context=context)
        if ('stage_id' in vals) or ('remaining_hours' in vals) or ('user_id' in vals) or ('state' in vals) or ('kanban_state' in vals):
            self._store_history(cr, uid, ids, context=context)
        return result
task()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
