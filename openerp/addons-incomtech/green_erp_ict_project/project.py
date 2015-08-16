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
        'name': fields.char('Stage Name', required=True, size=64),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence'),
        'phase_ids': fields.many2many('project.phase', 'project_phase_type_rel', 'type_id', 'phase_id', 'Phases'),
        'case_default': fields.boolean('Default for New Projects'),
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
        'case_default': True,
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
#         'phase_type_id': fields.many2one('phase.type', 'Phase Type'),
#         'phase_category_id': fields.many2one('phase.category', 'Phase Category'),
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
    
    def _get_type_common(self, cr, uid, context):
        ids = self.pool.get('project.phase.type').search(cr, uid, [('case_default','=',1)], context=context)
        return ids
    
    _defaults = {
#         'user_id': lambda obj, cr, uid, ctx=None: uid,
        'type_ids': _get_type_common,
    }
    
#     def generate_task(self, cr, uid, ids, context=None):
#         phase_type_obj = self.pool.get('phase.type')
#         task_obj = self.pool.get('project.task')
#         for phase in self.browse(cr, uid, ids):
#             if phase.phase_type_id:
#                 for seq, phase_line in enumerate(phase.phase_type_id.task_of_phase):
#                     task_values = {
#                         'name': phase_line.name,
#                         'project_id': phase.project_id and phase.project_id.id or False,
#                         'phase_id': phase.id,
#                         'user_id': False,
#                         'sequence': seq,
#                         'implementers': phase_line.implementers,
#                         'template_id': phase_line.template_id and phase_line.template_id.id or False,
#                     }
#                     task_obj.create(cr, uid, task_values, context)
#         return self.write(cr, uid, ids, {'is_task_generated': True})
     
    def create(self, cr, uid, vals, context=None):
        if 'type_ids' in vals and len(vals['type_ids'])>0 and len(vals['type_ids'][0][2])>0:
            type_ids = vals['type_ids']
            vals['stage_id']=type_ids[0][2][0]
        phase_id = super(project_phase, self).create(cr, uid, vals, context)
        gd_obj = self.pool.get('giai.doan')
        for type in self.browse(cr, uid, phase_id).type_ids:
            gd_obj.create(cr, uid, {
                'name': type.name,
                'phase_id': phase_id,
            })
        return phase_id
    
#     def onchange_phase_category(self, cr, uid, ids, phase_category_id=False, context=None):
#         vals = {}
#         if phase_category_id:
#             phase_category_obj = self.pool.get('phase.category')
#             phase_category = phase_category_obj.browse(cr, uid, phase_category_id)
#             stage_ids = [p.id for p in phase_category.stage_ids]
#             vals['type_ids'] = [(6,0,stage_ids)]
#         return {'value': vals}
    
project_phase()

class giai_doan(osv.osv):
    _name = 'giai.doan'
    _inherit = "mail.thread"
    
    def default_get(self, cr, uid, fields, context=None):
        result = super(giai_doan, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        if context.get('default_phase_id', False):
            phase = self.pool.get('project.phase').browse(cr, uid, context['default_phase_id'])
            result['project_id'] = phase.project_id and phase.project_id.id or False
        return result
    
    _columns = {
        'name': fields.char('Tên', required=True, size=1024),
        'user_id': fields.many2one('res.users', 'Người thực hiện'),
        'phase_id': fields.many2one('project.phase', 'Gói thầu', required=True),
        'project_id': fields.related('phase_id','project_id', type="many2one", relation="project.project", string='Dự án', store=True, readonly=True),
        'is_goithau_con': fields.boolean('Có gói thầu con?'),
        'phase_type_id': fields.many2one('phase.type', 'Hình thức lựa chọn nhà thầu'),
        'description': fields.text('Description'),
        'type_ids': fields.many2many('giai.doan.type', 'giai_doan_type_rel', 'giai_doan_id', 'type_id', 'Trạng thái của giai đoạn'),
        'is_task_generated': fields.boolean('Task Generated'),
        'stage_id': fields.many2one('giai.doan.type', 'Stage', select=True,
                        domain="['&', ('fold', '=', False), ('giai_doan_ids', '=', id)]"),
        'state': fields.related('stage_id', 'state', type="selection", store=True,
                selection=_TASK_STATE, string="Status", readonly=True, select=True),
    }
    
    _defaults = {
        'is_goithau_con': False,
    }
    
    def generate_task(self, cr, uid, ids, context=None):
        phase_type_obj = self.pool.get('phase.type')
        task_obj = self.pool.get('project.task')
        for gd in self.browse(cr, uid, ids):
            if gd.phase_type_id:
                for seq, gd_line in enumerate(gd.phase_type_id.task_of_phase):
                    task_values = {
                        'name': gd_line.name,
                        'project_id': gd.project_id and gd.project_id.id or False,
                        'phase_id': gd.phase_id and gd.phase_id.id or False,
                        'giai_doan_id': gd.id,
                        'user_id': False,
                        'sequence': seq,
                        'implementers': gd_line.implementers,
                        'template_id': gd_line.template_id and gd_line.template_id.id or False,
                    }
                    task_obj.create(cr, uid, task_values, context)
        return self.write(cr, uid, ids, {'is_task_generated': True})
    
    def onchange_phase_type(self, cr, uid, ids, phase_type_id=False, context=None):
        vals = {}
        if phase_type_id:
            phase_type_obj = self.pool.get('phase.type')
            phase_type = phase_type_obj.browse(cr, uid, phase_type_id)
            stage_ids = [p.id for p in phase_type.stage_ids]
            vals['type_ids'] = [(6,0,stage_ids)]
        return {'value': vals}
    
giai_doan()

class giai_doan_type(osv.osv):
    _name = 'giai.doan.type'
    _order = 'sequence'
    _columns = {
        'name': fields.char('Stage Name', required=True, size=64),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence'),
        'giai_doan_ids': fields.many2many('giai.doan', 'giai_doan_type_rel', 'type_id', 'giai_doan_id', 'Giai đoạn'),
        'case_default': fields.boolean('Default for New Projects'),
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
        'case_default': True,
    }
    _order = 'sequence'
    
giai_doan_type()

class goi_thau_con(osv.osv):
    _name = 'goi.thau.con'
    _inherit = "mail.thread"
    
    def default_get(self, cr, uid, fields, context=None):
        result = super(goi_thau_con, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        if context.get('default_giai_doan_id', False):
            giaidoan = self.pool.get('giai.doan').browse(cr, uid, context['default_giai_doan_id'])
            result['phase_id'] = giaidoan.phase_id and giaidoan.phase_id.id or False
            result['project_id'] = giaidoan.project_id and giaidoan.project_id.id or False
        return result
    
    _columns = {
        'name': fields.char('Tên', required=True, size=1024),
        'user_id': fields.many2one('res.users', 'Người thực hiện'),
        'giai_doan_id': fields.many2one('giai.doan', 'Giai đoạn', required=True),
        'phase_id': fields.related('giai_doan_id','phase_id', type="many2one", relation="project.phase", string='Gói thầu', store=True, readonly=True),
        'project_id': fields.related('phase_id','project_id', type="many2one", relation="project.project", string='Dự án', store=True, readonly=True),
        'phase_category_id': fields.many2one('phase.category', 'Loại gói thầu'),
        'description': fields.text('Description'),
        'type_ids': fields.many2many('goi.thau.con.type', 'goithau_con_type_rel', 'goithau_con_id', 'type_id', 'Trạng thái'),
        'is_task_generated': fields.boolean('Task Generated'),
        'stage_id': fields.many2one('goi.thau.con.type', 'Stage', select=True,
                        domain="['&', ('fold', '=', False), ('goithaucon_ids', '=', id)]"),
        'state': fields.related('stage_id', 'state', type="selection", store=True,
                selection=_TASK_STATE, string="Status", readonly=True, select=True),
    }
    
    _defaults = {
    }
    
    def generate_task(self, cr, uid, ids, context=None):
        phase_category_obj = self.pool.get('phase.category')
        task_obj = self.pool.get('project.task')
        for gtc in self.browse(cr, uid, ids):
            if gtc.phase_category_id:
                for seq, gtc_line in enumerate(gtc.phase_category_id.task_of_phase):
                    task_values = {
                        'name': gtc_line.name,
                        'project_id': gtc.project_id and gtc.project_id.id or False,
                        'phase_id': gtc.phase_id and gtc.phase_id.id or False,
                        'giai_doan_id': gtc.giai_doan_id and gtc.giai_doan_id.id or False,
                        'gtc_id': gtc.id,
                        'user_id': False,
                        'sequence': seq,
                        'implementers': gtc_line.implementers,
                        'template_id': gtc_line.template_id and gtc_line.template_id.id or False,
                    }
                    task_obj.create(cr, uid, task_values, context)
        return self.write(cr, uid, ids, {'is_task_generated': True})
    
    def onchange_phase_category(self, cr, uid, ids, phase_category_id=False, context=None):
        vals = {}
        if phase_category_id:
            phase_category_obj = self.pool.get('phase.category')
            phase_category = phase_category_obj.browse(cr, uid, phase_category_id)
            stage_ids = [p.id for p in phase_category.stage_ids]
            vals['type_ids'] = [(6,0,stage_ids)]
        return {'value': vals}
    
goi_thau_con()

class goi_thau_con_type(osv.osv):
    _name = 'goi.thau.con.type'
    _order = 'sequence'
    _columns = {
        'name': fields.char('Stage Name', required=True, size=64),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence'),
        'goithaucon_ids': fields.many2many('goi.thau.con', 'goithau_con_type_rel', 'type_id', 'goithau_con_id', 'Gói thầu con'),
        'case_default': fields.boolean('Default for New Projects'),
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
        'case_default': True,
    }
    _order = 'sequence'
    
goi_thau_con_type()

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
        if context.get('default_gtc_id', False):
            gtc = self.pool.get('goi.thau.con').browse(cr, uid, context['default_gtc_id'])
            result['giai_doan_id'] = gtc.giai_doan_id and gtc.giai_doan_id.id or False
            context.update({'default_giai_doan_id': gtc.giai_doan_id and gtc.giai_doan_id.id or False})    
        if context.get('default_giai_doan_id', False):
            gd = self.pool.get('giai.doan').browse(cr, uid, context['default_giai_doan_id'])
            result['phase_id'] = gd.phase_id and gd.phase_id.id or False
            context.update({'default_phase_id': gd.phase_id and gd.phase_id.id or False})
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
        'ngay_ky': fields.date('Ngày ký',select=True),
        'sohieu_hoso': fields.char('Số hiệu hồ sơ', size=1024),
        'template_id': fields.many2one('ict.template', 'Template'),
        'giai_doan_id': fields.many2one('giai.doan', 'Giai đoạn'),
        'gtc_id': fields.many2one('goi.thau.con', 'Gói thầu con'),
    }
    
    def bt_print(self, cr, uid, ids, context=None):
        task = self.browse(cr, uid, ids[0])
        if task.template_id:
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                                'green_erp_ict_project', task.template_id.form_view_id)
            return {
                        'name': task.template_id.name,
                        'view_type': 'form',
                        'view_mode': 'form',
                        'view_id': res[1],
                        'res_model': task.template_id.object,
                        'domain': [],
                        'context': {},
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                    }
        return True
    
project_task()

class file_state(osv.osv):
    _name = 'file.state'
    _order = 'sequence'
    _columns = {
        'name': fields.char('Name', required=True, size=1024),
        'sequence': fields.integer('Sequence', required=True),
    }
    
file_state()

class phase_type(osv.osv):
    _name = 'phase.type'
    _description = 'Phase Type'
    _columns = {
        'name': fields.char('Name', required=True, size=1024),
        'stage_ids': fields.many2many('giai.doan.type', 'ict_phase_giaidoan_rel', 'phase_id', 'giaidoan_id', 'Stages'),
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
        'template_id': fields.many2one('ict.template', 'Template'),
        'sequence': fields.integer('Sequence', required=True),
    }
    
    _defaults = {
        'sequence': 1,
    }
    
phase_type_line()

class phase_category(osv.osv):
    _name = 'phase.category'
    _description = 'Phase Category'
    _columns = {
        'name': fields.char('Name', required=True, size=1024),
        'stage_ids': fields.many2many('goi.thau.con.type', 'phase_category__goithaucontype_rel', 'phase_category_id', 'stage_id', 'Stages'),
        'task_of_phase': fields.one2many('phase.category.line', 'phase_category_id','Task of Phase Category'),
    }
    
phase_category()

class phase_category_line(osv.osv):
    _name = 'phase.category.line'
    _order = 'sequence'
    _columns = {
        'name': fields.char('Name', required=True, size=1024),
        'phase_category_id': fields.many2one('phase.category', 'Phase Category', ondelete='cascade'),
        'implementers': fields.char('Implementers', size=1024),
        'template_id': fields.many2one('ict.template', 'Template'),
        'sequence': fields.integer('Sequence', required=True),
    }
    
    _defaults = {
        'sequence': 1,
    }
    
phase_category_line()

class ict_template(osv.osv):
    _name = 'ict.template'
    _columns = {
        'name': fields.char('Name', readonly=True, size=1024),
        'object': fields.char('Object', readonly=True, size=1024),
        'form_view_id': fields.char('Form View ID', readonly=True, size=1024),
    }
    
ict_template()

class ir_attachment(osv.osv):
    _inherit = "ir.attachment"
    
    def onchange_datas_fname(self, cr, uid, ids, datas_fname=False, context=None):
        vals = {}
        if datas_fname:
            vals['name'] = datas_fname
        return {'value': vals}
    
ir_attachment()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
