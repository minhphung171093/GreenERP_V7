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
from openerp.tools import append_content_to_html


_TASK_STATE = [('draft', 'New'),('open', 'In Progress'),('pending', 'Pending'), ('done', 'Done'), ('cancelled', 'Cancelled')]

class trangthai_duan(osv.osv):
    _name = 'trangthai.duan'
    _order = 'sequence'
    _columns = {
        'name': fields.char('Stage Name', required=True, size=64),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence'),
        'duan_ids': fields.many2many('duan.phanmem', 'duan_trangthai_duan_rel', 'trangthai_id', 'duan_id', 'Các dự án'),
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
    
trangthai_duan()

class trangthai_nhom_congviec(osv.osv):
    _name = 'trangthai.nhom.congviec'
    _order = 'sequence'
    _columns = {
        'name': fields.char('Stage Name', required=True, size=64),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence'),
        'nhom_congviec_ids': fields.many2many('nhom.congviec', 'nhom_congviec_trangthai_rel', 'trangthai_id', 'nhom_congviecs_id', 'Các nhóm công việc'),
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
    
trangthai_nhom_congviec()

class trangthai_congviec(osv.osv):
    _name = 'trangthai.congviec'
    _order = 'sequence'
    _columns = {
        'name': fields.char('Stage Name', required=True, size=64),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence'),
        'duan_ids': fields.many2many('duan.phanmem', 'duan_trangthai_congviec_rel', 'trangthai_id', 'duan_id', 'Các dự án'),
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
    
trangthai_congviec()

class duan_phanmem(osv.osv):
    _name = 'duan.phanmem'
    _inherit = "mail.thread"
    
    def _get_members(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for duan in self.browse(cr, uid, ids, context=context):
            id = duan.id
            user_ids = []
            for line in duan.team_line:
                if line.user_id and line.user_id.id not in user_ids:
                    user_ids.append(line.user_id.id)
            res[id] = user_ids
        return res
    
    def _congviec_count(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = dict.fromkeys(ids, 0)
        ctx = context.copy()
        ctx['active_test'] = False
        task_ids = self.pool.get('cong.viec').search(cr, uid, [('duan_id', 'in', ids)], context=ctx)
        for task in self.pool.get('cong.viec').browse(cr, uid, task_ids, context):
            res[task.duan_id.id] += 1
        return res
    
    def _nhom_congviec_count(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = dict.fromkeys(ids, 0)
        ctx = context.copy()
        ctx['active_test'] = False
        task_ids = self.pool.get('nhom.congviec').search(cr, uid, [('duan_id', 'in', ids)], context=ctx)
        for task in self.pool.get('nhom.congviec').browse(cr, uid, task_ids, context):
            res[task.duan_id.id] += 1
        return res
    
    def _sotien_giam(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        for duan in self.browse(cr, uid, ids, context):
            sotien_giam = 0
            if not duan.ngay_ht:
                ngay_ht = time.strftime('%Y-%m-%d')
            else:
                ngay_ht = duan.ngay_ht
            if duan.han_chot and duan.han_chot<ngay_ht:
                date_format = '%Y-%m-%d'
                a = datetime.strptime(ngay_ht, date_format)
                b = datetime.strptime(duan.han_chot, date_format)
                songay_tre = (a-b).days
                trehan_obj = self.pool.get('duan.trehan')
                trehan_ids = trehan_obj.search(cr, uid, [],order='name')
                phantram_giam = 0
                for line in trehan_obj.browse(cr, uid, trehan_ids):
                    if songay_tre >= line.name:
                        phantram_giam = line.phantram_giam
                if phantram_giam:
                    sotien_giam = duan.muc_thuong*phantram_giam/100
            res[duan.id] = sotien_giam
        return res
    
    _columns = {
        'name': fields.char('Tên dự án', required=True, size=1024, track_visibility='onchange'),
        'user_id': fields.many2one('res.users', 'Người quản lý', track_visibility='onchange',required=True),
        'description': fields.text('Description'),
        'ngay_bd': fields.date('Ngày bắt đầu', track_visibility='onchange'),
        'ngay_kt': fields.date('Ngày kết thúc', track_visibility='onchange'),
        'muc_thuong': fields.float('Số tiền thưởng', track_visibility='onchange', readonly=True),
        'han_chot': fields.date('Hạn chót', track_visibility='onchange', readonly=True),
        'color': fields.integer('Color Index'),
        'congviec_count': fields.function(_congviec_count, type='integer', string="Công việc"),
        'nhom_congviec_count': fields.function(_nhom_congviec_count, type='integer', string="Nhóm công việc"),
        'trangthai_duan_ids': fields.many2many('trangthai.duan', 'duan_trangthai_duan_rel', 'duan_id', 'trangthai_id', 'Trạng thái của dự án'),
        'trangthai_congviec_ids': fields.many2many('trangthai.congviec', 'duan_trangthai_congviec_rel', 'duan_id', 'trangthai_id', 'Trạng thái của công việc'),
        'stage_id': fields.many2one('trangthai.duan', 'Stage', select=True, track_visibility='onchange',
                        domain="['&', ('fold', '=', False), ('duan_ids', '=', id)]"),
        'state': fields.related('stage_id', 'state', type="selection", store=True,
                selection=_TASK_STATE, string="Status", readonly=True, select=True),
        'team_line': fields.one2many('duan.team','duan_id', 'Team'),
        'members':fields.function(_get_members, type='many2many', relation='res.users', string='Members'),
        'sotien_giam': fields.function(_sotien_giam, type='float', string="Số tiền giảm"),
        'ngay_ht': fields.date('Ngày hoàn thành', track_visibility='onchange', readonly=True),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('stage_id', False):
            trangthai_obj = self.pool.get('trangthai.duan')
            trangthai = trangthai_obj.browse(cr, uid, vals['stage_id'])
            if trangthai.state=='done':
                vals.update({'ngay_ht': time.strftime('%Y-%m-%d')})
        return super(duan_phanmem, self).write(cr, uid, ids, vals, context)
    
    def _get_trangthai_duan(self, cr, uid, context):
        ids = self.pool.get('trangthai.duan').search(cr, uid, [('case_default','=',1)], context=context)
        return ids
    
    def _get_trangthai_congviec(self, cr, uid, context):
        ids = self.pool.get('trangthai.congviec').search(cr, uid, [('case_default','=',1)], context=context)
        return ids
    
    def _get_default_stage_id(self, cr, uid, context=None):
        stage_ids = self.pool.get('trangthai.duan').search(cr, uid, [('state','=','draft'),('case_default','=',1)])
        return stage_ids and stage_ids[0] or False
    
    _defaults = {
        'trangthai_duan_ids': _get_trangthai_duan,
        'trangthai_congviec_ids': _get_trangthai_congviec,
        'stage_id': _get_default_stage_id,
    }
    
duan_phanmem()

class duan_team(osv.osv):
    _name = 'duan.team'
    
    def _thanhtien(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        for team in self.browse(cr, uid, ids, context):
            thanhtien = 0
            sql = '''
                select case when sum(he_so)!=0 then sum(he_so) else 0 end tong_he_so from duan_team where duan_id=%s
            '''%(team.duan_id.id)
            cr.execute(sql)
            tong_he_so = cr.fetchone()[0]
            if tong_he_so:
                thanhtien = (team.duan_id.muc_thuong-team.duan_id.sotien_giam)*team.he_so/tong_he_so
            res[team.id] = thanhtien
        return res
    
    _columns = {
        'user_id': fields.many2one('res.users', 'User',required=True),
        'he_so': fields.float('Hệ số',required=True),
        'thanhtien': fields.function(_thanhtien, type='float', string="Thành tiền"),
        'duan_id': fields.many2one('duan.phanmem', 'Dự án', ondelete='cascade'),
    }
    
duan_team()

class duan_trehan(osv.osv):
    _name = 'duan.trehan'
    _order = 'name'
    _columns = {
        'name': fields.integer('Số ngày trễ',required=True),
        'phantram_giam': fields.integer('Giảm (%)',required=True),
    }
    
duan_trehan()

class nhom_congviec(osv.osv):
    _name = 'nhom.congviec'
    _inherit = "mail.thread"
    
    _columns = {
        'name': fields.char('Tên dự án', required=True, size=1024, track_visibility='onchange'),
        'duan_id': fields.many2one('duan.phanmem', 'Dự án', track_visibility='onchange',required=True),
        'user_id': fields.many2one('res.users', 'Người phụ trách', track_visibility='onchange',required=True),
        'description': fields.text('Description'),
        'ngay_bd': fields.date('Ngày bắt đầu', track_visibility='onchange'),
        'ngay_kt': fields.date('Ngày kết thúc', track_visibility='onchange'),
        'han_chot': fields.date('Hạn chót', track_visibility='onchange'),
        'color': fields.integer('Color Index'),
        'trangthai_nhom_congviec_ids': fields.many2many('trangthai.nhom.congviec', 'nhom_congviec_trangthai_rel', 'nhom_congviecs_id', 'trangthai_id', 'Trạng thái của công việc'),
        'stage_id': fields.many2one('trangthai.nhom.congviec', 'Stage', select=True, track_visibility='onchange',
                        domain="['&', ('fold', '=', False), ('nhom_congviec_ids', '=', id)]"),
        'state': fields.related('stage_id', 'state', type="selection", store=True,
                selection=_TASK_STATE, string="Status", readonly=True, select=True),
    }
    
    def _get_trangthai_nhom_congviec(self, cr, uid, context):
        ids = self.pool.get('trangthai.nhom.congviec').search(cr, uid, [('case_default','=',1)], context=context)
        return ids
    
    def _get_default_stage_id(self, cr, uid, context=None):
        stage_ids = self.pool.get('trangthai.nhom.congviec').search(cr, uid, [('state','=','draft'),('case_default','=',1)])
        return stage_ids and stage_ids[0] or False
    
    _defaults = {
        'trangthai_nhom_congviec_ids': _get_trangthai_nhom_congviec,
        'stage_id': _get_default_stage_id,
    }
    
nhom_congviec()

class cong_viec(osv.osv):
    _name = 'cong.viec'
    _inherit = "mail.thread"
    
    def default_get(self, cr, uid, fields, context=None):
        result = super(cong_viec, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        if context.get('default_nhom_congviec_id', False):
            phase = self.pool.get('nhom.congviec').browse(cr, uid, context['default_nhom_congviec_id'])
            result['duan_id'] = phase.duan_id and phase.duan_id.id or False
        return result
    
    _columns = {
        'name': fields.char('Tên dự án', required=True, size=1024, track_visibility='onchange'),
        'duan_id': fields.many2one('duan.phanmem', 'Dự án', track_visibility='onchange',required=True),
        'nhom_congviec_id': fields.many2one('nhom.congviec', 'Nhóm công việc', track_visibility='onchange'),
        'user_id': fields.many2one('res.users', 'Người thực hiện', track_visibility='onchange'),
        'description': fields.text('Description'),
        'ngay_bd': fields.datetime('Ngày bắt đầu', track_visibility='onchange'),
        'ngay_kt': fields.datetime('Ngày kết thúc', track_visibility='onchange'),
        'ngay_ht': fields.date('Ngày hoàn thành', track_visibility='onchange', readonly=True),
        'han_chot': fields.date('Hạn chót', track_visibility='onchange'),
        'color': fields.integer('Color Index'),
        'priority': fields.selection([('4','Very Low'), ('3','Low'), ('2','Medium'), ('1','Important'), ('0','Very important')], 'Priority', select=True),
        'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list of tasks."),
        'stage_id': fields.many2one('trangthai.congviec', 'Stage', select=True, track_visibility='onchange',
                        domain="['&', ('fold', '=', False), ('duan_ids', '=', duan_id)]"),
        'state': fields.related('stage_id', 'state', type="selection", store=True,
                selection=_TASK_STATE, string="Status", readonly=True, select=True),
    }
    
    def _resolve_project_id_from_context(self, cr, uid, context=None):
        if context is None:
            context = {}
        if type(context.get('default_duan_id')) in (int, long):
            return context['default_duan_id']
        if isinstance(context.get('default_duan_id'), basestring):
            project_name = context['default_duan_id']
            project_ids = self.pool.get('duan.phanmem').name_search(cr, uid, name=project_name, context=context)
            if len(project_ids) == 1:
                return project_ids[0][0]
        return None
    
    def _get_default_project_id(self, cr, uid, context=None):
        return (self._resolve_project_id_from_context(cr, uid, context=context) or False)
    
    def stage_find(self, cr, uid, cases, section_id, domain=[], order='sequence', context=None):
        if isinstance(cases, (int, long)):
            cases = self.browse(cr, uid, cases, context=context)
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        for task in cases:
            if task.duan_id:
                section_ids.append(task.duan_id.id)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids)-1)
            for section_id in section_ids:
                search_domain.append(('duan_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        stage_ids = self.pool.get('trangthai.congviec').search(cr, uid, search_domain, order=order, context=context)
        if stage_ids:
            return stage_ids[0]
        return False
    
    def _get_default_stage_id(self, cr, uid, context=None):
        project_id = self._get_default_project_id(cr, uid, context=context)
        return self.stage_find(cr, uid, [], project_id, [('state', '=', 'draft')], context=context)
    
    _defaults = {
        'stage_id': _get_default_stage_id,
        'priority': '2',
    }
    
    def set_high_priority(self, cr, uid, ids, *args):
        """Set task priority to high
        """
        return self.write(cr, uid, ids, {'priority' : '0'})

    def set_normal_priority(self, cr, uid, ids, *args):
        """Set task priority to normal
        """
        return self.write(cr, uid, ids, {'priority' : '2'})

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('stage_id', False):
            trangthai_obj = self.pool.get('trangthai.congviec')
            trangthai = trangthai_obj.browse(cr, uid, vals['stage_id'])
            if trangthai.state=='done':
                vals.update({'ngay_ht': time.strftime('%Y-%m-%d')})
        return super(cong_viec, self).write(cr, uid, ids, vals, context)
    
cong_viec()

class res_users(osv.osv):
    _inherit = 'res.users'
    
    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_user_with_project', False):
            duan_id = context['search_user_with_project']
            cr.execute(''' select user_id from duan_team where duan_id=%s ''',(duan_id,))
            user_ids = [r[0] for r in cr.fetchall()]
            args += [('id','in',user_ids)]
        if context.get('search_user_for_project', False):
            sql ='''
                select uid from res_groups_users_rel 
                    where gid in (select res_id from ir_model_data where name in ('group_software_project_leader','group_software_project_manager') and module='green_erp_ict_software_project' and model='res.groups' )
            '''
            cr.execute(sql)
            user_ids = [r[0] for r in cr.fetchall()]
            args += [('id','in',user_ids)]
        return super(res_users, self).search(cr, user, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
res_users()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
