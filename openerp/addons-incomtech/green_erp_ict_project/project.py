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

_TASK_STATE = [('draft', 'New'),('open', 'In Progress'),('pending', 'Pending'), ('done', 'Done'), ('cancelled', 'Cancelled')]

class project_phase_type(osv.osv):
    _name = 'project.phase.type'
    _description = 'Phase Stage'
    _order = 'sequence'
    _columns = {
        'name': fields.char('Stage Name', required=True, size=64, translate=True),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence'),
        'phase_ids': fields.many2many('project.phase', 'project_phase_type_rel', 'type_id', 'phase_id', 'Phases'),
        'state': fields.selection(_TASK_STATE, 'Related Status', required=True,
                        help="The status of your document is automatically changed regarding the selected stage. " \
                            "For example, if a stage is related to the status 'Close', when your document reaches this stage, it is automatically closed."),
        'fold': fields.boolean('Folded by Default',
                        help="This stage is not visible, for example in status bar or kanban view, when there are no records in that stage to display."),
    }
    _defaults = {
        'sequence': 1,
        'state': 'open',
        'fold': False,
    }
    _order = 'sequence'
    
project_phase_type()

class project_phase(osv.osv):
    _name = 'project.phase'
    _inherit = ['project.phase','mail.thread']
    _columns = {
        'type_ids': fields.many2many('project.phase.type', 'project_phase_type_rel', 'phase_id', 'type_id', 'Phase Stages'),
        'stage_id': fields.many2one('project.phase.type', 'Stage', select=True,
                        domain="['&', ('fold', '=', False), ('phase_ids', '=', id)]"),
        'state': fields.related('stage_id', 'state', type="selection", store=True,
                selection=_TASK_STATE, string="Status", readonly=True, select=True),
        'phase_type_id': fields.many2one('phase.type', 'Phase Type'),
        'user_id': fields.many2one('res.users', 'Assigned to'),
        'is_task_generated': fields.boolean('Task Generated'),
                
        'date_start': fields.date('Start Date', select=True, help="It's computed by the scheduler according the project date or the end date of the previous phase."),
        'date_end': fields.date('End Date', help=" It's computed by the scheduler according to the start date and the duration."),
        'constraint_date_start': fields.datetime('Minimum Start Date', help='force the phase to start after this date'),
        'constraint_date_end': fields.datetime('Deadline', help='force the phase to finish before this date'),
        'next_phase_ids': fields.many2many('project.phase', 'project_phase_rel', 'prv_phase_id', 'next_phase_id', 'Next Phases'),
        'previous_phase_ids': fields.many2many('project.phase', 'project_phase_rel', 'next_phase_id', 'prv_phase_id', 'Previous Phases'),
        'duration': fields.float('Duration', required=False, help="By default in days"),
        'product_uom': fields.many2one('product.uom', 'Duration Unit of Measure', required=False, help="Unit of Measure (Unit of Measure) is the unit of measurement for Duration"),
        'task_ids': fields.one2many('project.task', 'phase_id', "Project Tasks"),
        'user_ids': fields.one2many('project.user.allocation', 'phase_id', "Assigned Users",
            help="The resources on the project can be computed automatically by the scheduler."),
    }
    
    _defaults = {
        'user_id': lambda obj, cr, uid, ctx=None: uid,
    }
    
    def generate_task(self, cr, uid, ids, context=None):
        phase_type_obj = self.pool.get('phase.type')
        task_obj = self.pool.get('project.task')
        for phase in self.browse(cr, uid, ids):
            if phase.phase_type_id:
                for seq, phase_line in enumerate(phase.phase_type_id.task_of_phase):
                    task_values = {
                        'name': phase_line.name,
                        'project_id': phase.project_id and phase.project_id.id or False,
                        'phase_id': phase.id,
                        'user_id': uid,
                        'sequence': seq,
                        'implementers': phase_line.implementers,
                    }
                    task_obj.create(cr, uid, task_values, context)
        return self.write(cr, uid, ids, {'is_task_generated': True})
    
    def create(self, cr, uid, vals, context=None):
        if 'type_ids' in vals and len(vals['type_ids'])>0 and len(vals['type_ids'][0][2])>0:
            type_ids = vals['type_ids']
            vals['stage_id']=type_ids[0][2][0]
        phase_id = super(project_phase, self).create(cr, uid, vals, context)
        return phase_id
    
    def onchange_phase_type(self, cr, uid, ids, phase_type_id=False, context=None):
        vals = {}
        if phase_type_id:
            phase_type_obj = self.pool.get('phase.type')
            phase_type = phase_type_obj.browse(cr, uid, phase_type_id)
            stage_ids = [p.id for p in phase_type.stage_ids]
            vals['type_ids'] = [(6,0,stage_ids)]
        return {'value': vals}
    
project_phase()

class project_project(osv.osv):
    _inherit = 'project.project'
    _defaults = {
        'use_phases': True,
    }
    
project_project()

class project_task(osv.osv):
    _inherit = 'project.task'

    def default_get(self, cr, uid, fields, context=None):
        result = super(project_task, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        if context.get('default_phase_id', False):
            phase = self.pool.get('project.phase').browse(cr, uid, context['default_phase_id'])
            result['project_id'] = phase.project_id and phase.project_id.id or False
        return result
    
    _columns = {
        'soft_file_id': fields.many2one('ir.attachment', 'Soft File'),
        'hard_copy_file_id': fields.many2one('ir.attachment', 'Hard Copy File'),
        'file_state_id': fields.many2one('file.state', 'File Status'),
        'date_start': fields.date('Starting Date',select=True),
        'date_end': fields.date('Ending Date',select=True),
        'implementers': fields.char('Implementers', size=1024),
    }
    
project_task()

class file_state(osv.osv):
    _name = 'file.state'
    _columns = {
        'name': fields.char('Name', required=True, size=1024),
    }
    
file_state()

class phase_type(osv.osv):
    _name = 'phase.type'
    _description = 'Phase Type'
    _columns = {
        'name': fields.char('Name', required=True, size=1024),
        'stage_ids': fields.many2many('project.phase.type', 'phase_type_rel', 'type_id', 'stage_id', 'Stages'),
        'task_of_phase': fields.one2many('phase.type.line', 'phase_type_id','Task of Phase'),
    }
    
phase_type()

class phase_type_line(osv.osv):
    _name = 'phase.type.line'
    _order = 'sequence'
    _columns = {
        'name': fields.char('Name', required=True, size=1024),
        'phase_type_id': fields.many2one('phase.type', 'Phase Type', ondelete='cascade'),
        'implementers': fields.char('Implementers', size=1024),
        'sequence': fields.integer('Sequence', required=True),
    }
    
    _defaults = {
        'sequence': 1,
    }
    
phase_type_line()

class ir_attachment(osv.osv):
    _inherit = "ir.attachment"
    
    def onchange_datas_fname(self, cr, uid, ids, datas_fname=False, context=None):
        vals = {}
        if datas_fname:
            vals['name'] = datas_fname
        return {'value': vals}
    
ir_attachment()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
