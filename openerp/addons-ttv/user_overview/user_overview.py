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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import datetime
from datetime import date
from openerp import tools

class user_overview(osv.osv):
    _name = 'user.overview'
    
    def _tasks(self, cr, uid, context=None):
        task_obj = self.pool.get('project.task')
        list_tasks = task_obj.search(cr,uid,[('user_id','=',uid),('stage_id.state','=','open'),('checking_task','=','none')])        
        return list_tasks
    
    def _checking_tasks1(self, cr, uid, context=None):
        task_obj = self.pool.get('project.task')
        list_task = task_obj.search(cr,uid,[('previous_assigned_to1','=',uid),('stage_id.state','=','open'),('checking_task','=','checking1')])
        return list_task
    
    def _checking_tasks2(self, cr, uid, context=None):
        task_obj = self.pool.get('project.task')
        list_tasks = task_obj.search(cr,uid,[('previous_assigned_to2','=',uid),('stage_id.state','=','open'),('checking_task','=','checking2')])        
        return list_tasks
    
    def _attendances_times(self, cr, uid, context=None):
        date_now_d = datetime.datetime.now() + timedelta(hours=7)
        date_now = str(date_now_d)[0:10]
        attendances_times_obj = self.pool.get('attendances.time')
        list_attendances_time =  attendances_times_obj.search(cr,uid,[('day','=',date_now),('user_id','=',uid)])
        return list_attendances_time
    
    def default_get(self, cr, uid, fields, context=None):
        date_now_d = datetime.datetime.now() + timedelta(hours=7)
        date_now = str(date_now_d)[0:10]
        res = super(user_overview, self).default_get(cr, uid, fields, context=context)
        total_obj = self.pool.get('total.timesheet')
        total_id = total_obj.search(cr,1,[('user_id','=',uid)])
        check_obj = self.pool.get('check.login.logout')
        check_id = check_obj.search(cr,1,[('user_id','=',uid)])
        current_status_obj = self.pool.get('current.status')
        current_status_id = current_status_obj.search(cr,1,[('user_id','=',uid)])
        difference_obj = self.pool.get('difference.time')
        difference_id = difference_obj.search(cr,1,[('user_id','=',uid)])
        total_attendance_obj = self.pool.get('total.attendance')
        total_attendance_id = total_attendance_obj.search(cr,1,[('user_id','=',uid)])
        working_summary_obj = self.pool.get('working.summary')
        working_summary_id = working_summary_obj.search(cr,1,[('user_id','=',uid),('date','=',date_now)])
        if not check_id:
            check_obj.create(cr, 1,{
                                    'check': True,
                                    'user_id': uid,  
                                    })
        if not current_status_id:
            current_status_obj.create(cr, 1,{
                                    'name': 'paused',
                                    'user_id': uid,  
                                    })
        if not difference_id:
            difference_obj.create(cr, 1,{
                                    'name': '0:00:00',
                                    'user_id': uid,  
                                    })
        else:
            sql = '''
                select write_date
                from difference_time
                where id = %s
                '''
            cr.execute(sql,difference_id)
            difference_time = cr.dictfetchall()
            difference = difference_time[0]['write_date']
            difference_date = difference[0:10]
            if difference_date != date_now:
                difference_obj.write(cr, 1, difference_id, {
                                    'name': '0:00:00',
                                    })
        if not total_attendance_id:
            total_attendance_obj.create(cr, 1,{
                                    'name': '0:00:00',
                                    'user_id': uid,  
                                    })
        else:
            sql = '''
                select write_date
                from total_attendance
                where id = %s
                '''
            cr.execute(sql,total_attendance_id)
            total_attendance = cr.dictfetchall()
            total_att = total_attendance[0]['write_date']
            total_attendance_date = total_att[0:10]
            if total_attendance_date != date_now:
                total_attendance_obj.write(cr, 1, total_attendance_id, {
                                    'name': '0:00:00',
                                    })
        if not total_id:
            total_obj.create(cr, 1,{
                                    'name': '0:00:00',
                                    'user_id': uid,  
                                    })
        else:
            sql = '''
                select write_date
                from total_timesheet
                where id = %s
                '''
            cr.execute(sql,total_id)
            total_timesheet = cr.dictfetchall()
            total = total_timesheet[0]['write_date']
            total_date = total[0:10]
            if total_date != date_now:
                total_obj.write(cr, 1, total_id, {
                                    'name': '0:00:00',
                                    })
        if not working_summary_id:
                working_summary_obj.create(cr, 1,{
                                        'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                                        'user_id': uid,
                                        'date': date_now,
                                        'day': date_now,
                                        'total_attendance': '0:00:00',
                                        'total_timesheet': '0:00:00',
                                        'difference_time': '0:00:00',
                                        })
        current_id = current_status_obj.search(cr,1,[('user_id','=',uid)])
        difference_time_id = difference_obj.search(cr,1,[('user_id','=',uid)])
        total_att_id = total_attendance_obj.search(cr,1,[('user_id','=',uid)])
        if total_id:
            res.update({'total_timesheet': total_id[0],'current_status':current_id[0],'difference':difference_time_id[0],'total_attendance':total_att_id[0]})
        return res
    
    def _sum_total(self, cr, uid, ids, sign_in, sign_out, context=None):
        total = 0
        time_working_obj = self.pool.get('time.working')
        time_working_ids = time_working_obj.search(cr, uid, [])
        time_working_id = max(time_working_ids)
        time_working = time_working_obj.browse(cr, 1, time_working_id)
        a_from_s = int(time_working.a_from*3600)
        a_to_s = int(time_working.a_to*3600)
        b_from_s = int(time_working.b_from*3600)
        b_to_s = int(time_working.b_to*3600)
        sign_in_hour = sign_in.hour
        sign_in_minute = sign_in.minute
        sign_in_second = sign_in.second
        sign_out_hour = sign_out.hour
        sign_out_minute = sign_out.minute
        sign_out_second = sign_out.second
        sign_in_time_s = sign_in_hour*3600 + sign_in_minute*60 + sign_in_second
        sign_out_time_s = sign_out_hour*3600 + sign_out_minute*60 + sign_out_second
        if sign_in_time_s < a_from_s:
            if sign_out_time_s < a_from_s:
                sign_in_time_s = sign_out_time_s = 0
            elif sign_out_time_s >= a_from_s and sign_out_time_s <= a_to_s:
                sign_in_time_s = a_from_s
            elif sign_out_time_s > a_to_s and sign_out_time_s < b_from_s:
                sign_in_time_s = a_from_s
                sign_out_time_s = a_to_s
            elif sign_out_time_s >= b_from_s and sign_out_time_s <= b_to_s:
                sign_in_time_s = a_from_s
                sign_out_time_s = sign_out_time_s - (b_from_s - a_to_s)
            elif sign_out_time_s > b_to_s:
                sign_in_time_s = a_from_s
                sign_out_time_s = b_to_s - (b_from_s - a_to_s)
        elif sign_in_time_s >= a_from_s and sign_in_time_s <= a_to_s:
            if sign_out_time_s > a_to_s and sign_out_time_s < b_from_s:
                sign_out_time_s = a_to_s
            elif sign_out_time_s >= b_from_s and sign_out_time_s <= b_to_s:
                sign_out_time_s = sign_out_time_s - (b_from_s - a_to_s)
            elif sign_out_time_s > b_to_s:
                sign_out_time_s = b_to_s - (b_from_s - a_to_s)
        elif sign_in_time_s > a_to_s and sign_in_time_s < b_from_s:
            if sign_out_time_s > a_to_s and sign_out_time_s < b_from_s:
                sign_in_time_s = sign_out_time_s = 0
            elif sign_out_time_s >= b_from_s and sign_out_time_s <= b_to_s:
                sign_in_time_s = b_from_s
            elif sign_out_time_s > b_to_s:
                sign_in_time_s = b_from_s
                sign_out_time_s = b_to_s
        elif sign_in_time_s >= b_from_s and sign_in_time_s <= b_to_s:
            if sign_out_time_s > b_to_s:
                sign_out_time_s = b_to_s
        elif sign_in_time_s > b_to_s:
            sign_in_time_s = sign_out_time_s = 0
        total += sign_out_time_s - sign_in_time_s
        return total
    
    def onchange_attendances_times(self, cr, uid, context=None):
        temp = 0
        temp_hr = 0
        sign_in = []
        sign_out = []
        hr_sign_in = []
        hr_sign_out = []
        total = 0
        total_hr = 0
        time_working_obj = self.pool.get('time.working')
        time_working_ids = time_working_obj.search(cr, 1, [])
        if not time_working_ids:
            raise osv.except_osv(_('Warning!'),
                        _('Time Working isnot Defined'))
        date_now_d = datetime.datetime.now() + timedelta(hours=7)
        date_now = str(date_now_d)[0:10]
        attendances_times_obj = self.pool.get('attendances.time')
        attendances_time_ids =  attendances_times_obj.search(cr,1,[('day','=',date_now),('user_id','=',uid)])
        if attendances_time_ids:
            attendances_time_ids.sort()
            for line in attendances_times_obj.browse(cr, 1, attendances_time_ids):
                date = datetime.datetime.strptime(line.name, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                if line.action=='sign_in':
                    sign_in.append(date)
                if line.action=='sign_out':
                    sign_out.append(date)
#             if sign_in:
#                 time_login = str(sign_in[0])[11:]
#             else:
#                 time_login = ''
#             if sign_out:
#                 time_logout = str(sign_out[-1])[11:]
#             else:
#                 time_logout = None
            if len(sign_in) > len(sign_out):
                sign_out.append(date_now_d)
            if sign_in:
                for line in sign_out:
                    total += self._sum_total(cr, uid, uid, sign_in[temp], sign_out[temp], context)
                    temp+=1
            else:
                total = 0
        else:
            total = 0
#             time_login = None
#             time_logout = None
        total_obj = self.pool.get('total.timesheet')
        total_id = total_obj.search(cr, 1, [('user_id','=',uid)])
        hr_attendance_obj = self.pool.get('hr.attendance')
        hr_attendance_ids = hr_attendance_obj.search(cr, 1, [('day','=',date_now),('employee_id.user_id','=',uid)])
        if hr_attendance_ids:
            hr_attendance_ids.sort()
            for line in hr_attendance_obj.browse(cr, 1, hr_attendance_ids):
                date_time_hr_att = datetime.datetime.strptime(line.name, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                if line.action=='sign_in':
                    hr_sign_in.append(date_time_hr_att)
                if line.action=='sign_out':
                    hr_sign_out.append(date_time_hr_att)
            if hr_sign_in:
                time_login = str(hr_sign_in[0])[11:]
            else:
                time_login = ''
            if hr_sign_out:
                time_logout = str(hr_sign_out[-1])[11:]
            else:
                time_logout = None
            if len(hr_sign_in) > len(hr_sign_out):
                hr_sign_out.append(date_now_d)
            if hr_sign_in:
                for line in hr_sign_out:
                    total_hr += self._sum_total(cr, uid, uid, hr_sign_in[temp_hr], hr_sign_out[temp_hr])
                    temp_hr+=1
            else:
                total_hr = 0
        else:
            total_hr = 0
            time_login = None
            time_logout = None
        if total_hr > total:
            difference_s = total_hr - total
        else:
            difference_s = total - total_hr
        difference = datetime.timedelta(seconds=difference_s)
        difference_str = str(difference)
        difference_obj = self.pool.get('difference.time')
        difference_id = difference_obj.search(cr,1,[('user_id','=',uid)])
        difference_obj.write(cr, 1, difference_id,{'name': difference_str})
        total_attendance_obj = self.pool.get('total.attendance')
        total_attendance = datetime.timedelta(seconds=total_hr)
        total_attendance_str = str(total_attendance)
        total_attendance_id = total_attendance_obj.search(cr,1,[('user_id','=',uid)])
        total_attendance_obj.write(cr, 1, total_attendance_id,{'name': total_attendance_str})
        b = datetime.timedelta(seconds=total)
        a = str(b)
        total_obj.write(cr, 1, total_id,{'name': a})
        working_summary_obj = self.pool.get('working.summary')
        working_summary_id = working_summary_obj.search(cr,1,[('user_id','=',uid),('date','=',date_now)])
        if total_attendance_id and total_id and difference_id:
            total_attendance_name = total_attendance_obj.browse(cr, 1, total_attendance_id)[0]
            total_timesheet_name = total_obj.browse(cr, 1, total_id)[0]
            difference_time_name = difference_obj.browse(cr, 1, difference_id)[0]
            working_summary_obj.write(cr, 1, working_summary_id,{
                                                        'login': time_login,
                                                        'logout': time_logout,
                                                        'total_attendance': total_attendance_name.name,
                                                        'total_timesheet': total_timesheet_name.name,
                                                        'difference_time': difference_time_name.name,
                                                    })
        res = {'type': 'ir.actions.client', 'tag': 'reload' }
        return res
    
    _columns = {
             'tasks': fields.one2many('project.task', 'task_id', "My Tasks", domain=[('stage_id.state','not in',['done','cancelled']),('checking_task','=','none')]),
             'checking_tasks1': fields.one2many('project.task', 'task_id', "My Checking", domain=[('stage_id.state','not in',['done','cancelled']),('checking_task','=','checking1')]),
             'checking_tasks2': fields.one2many('project.task', 'task_id', "My Checking", domain=[('stage_id.state','not in',['done','cancelled']),('checking_task','=','checking2')]),
             'attendances_times': fields.one2many('attendances.time', 'attendance_id', "Attendance"),
             'total_attendance': fields.many2one('total.attendance','Total Attendance',readonly=True),
             'total_timesheet': fields.many2one('total.timesheet', 'Total Timesheet', readonly=True),
             'difference': fields.many2one('difference.time', 'Difference', readonly=True),
             'current_status': fields.many2one('current.status','Current Status', readonly=True),
        }
    _defaults = {
        'tasks': _tasks,
        'attendances_times': _attendances_times,
        'checking_tasks1': _checking_tasks1,
        'checking_tasks2': _checking_tasks2,
    }
    
    def get_datat(self, cr, uid, ids, context=None):
        date_now_d = datetime.datetime.now() + timedelta(hours=7)
        date_now = str(date_now_d)[0:10]
        attendances_time_obj = self.pool.get('attendances.time')
        attendances_time_obj.create(cr, 1, {
                                                'name':  time.strftime('%Y-%m-%d %H:%M:%S'),
                                                'action': context['data']['action'],
                                                'task_id': context['data']['task_id'],
                                                'user_id': uid,
                                                'day': date_now,
                                            })
        
        return True      
user_overview()

class project(osv.osv):
    _inherit = "project.project"
    
    _columns = {
        'department_id': fields.many2one('hr.department', 'Department'),
        'year': fields.char('Year', size=5),
    }
    
    _defaults = {
        'year': time.strftime('%Y'),
    }
    
    def onchange_type_ids(self, cr, uid, context=None):
        if context:
            project_id = context[0]
        else:
            project_id = None
        if project_id:
            project = self.pool.get('project.project').browse(cr, uid, project_id)
            if project and project.partner_id:
                return {'value': {'partner_id': project.partner_id.id}}
        return {}
    
    def set_done(self, cr, uid, ids, context=None):
        task_obj = self.pool.get('project.task')
        
        task_working_ids = task_obj.search(cr,uid,[('stage_id.state','=','open'),('flag','=',False)])
        user_overview_obj = self.pool.get('user.overview')
        attendances_time_obj = self.pool.get('attendances.time')
        if task_working_ids:
            for line in task_obj.browse(cr, uid, task_working_ids):
                if line.checking_task == 'none':
                    user_id = line.user_id.id
                elif line.checking_task == 'checking1':
                    user_id = line.previous_assigned_to1.id
                else:
                    user_id = line.previous_assigned_to2.id
                hours = self.pool.get('work.summary.line')._get_hours(cr, user_id, context)
                self.pool.get('project.task.work').create(cr, uid, {
                    'name':'Auto Summary',
                    'task_id':line.id,
                    'hours': hours,
                    'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'user_id': user_id,
                    })
                attendances_time_obj.create(cr, uid, {
                                                    'name':  time.strftime('%Y-%m-%d %H:%M:%S'),
                                                    'action': 'sign_out',
                                                    'task_id': line.id,
                                                    'user_id': user_id,
                                                })
                check_obj = self.pool.get('check.login.logout')
                check_id = check_obj.search(cr,uid,[('user_id','=',user_id)])
                current_status_obj = self.pool.get('current.status')
                current_status_id = current_status_obj.search(cr,uid,[('user_id','=',user_id)])
                current_status_obj.write(cr,user_id,current_status_id,{'name':'paused'})
                check_obj.write(cr,user_id,check_id,{'check':True})
                task_obj.write(cr,user_id,line.id,{'flag':True,'status_task': 'paused'})
                user_overview_obj.onchange_attendances_times(cr, user_id, context=context)
        
        task_ids = task_obj.search(cr, uid, [('project_id', 'in', ids), ('state', 'not in', ('cancelled', 'done'))])
        task_obj.case_close(cr, uid, task_ids, context=context)
        return self.write(cr, uid, ids, {'state':'close'}, context=context)
    
project()
class project_task(osv.osv):
    _inherit = 'project.task'
    def _planned_hours_user_get(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = task.planned_hours
        return res
    _columns = {
             'task_id': fields.many2one('user.overview','Task'),
             'error_ids': fields.one2many('error.line', 'task_id', "Error Reporting"),
             'flag':fields.boolean('Flag'),
             'status_task': fields.selection([('working', 'Working'), ('paused', 'Paused')], 'Status', readonly=True),
             'checking_task': fields.selection([('checking1','checking1'),('checking2','checking2'),('none','None')], 'Status', readonly=True),
             'planned_hours_user': fields.function(_planned_hours_user_get, string='Planned Hours', type='float', help="Estimated time to do the task, usually set by the project manager when the task is in draft state.",
            store = {
            }),
             'previous_assigned_to1': fields.many2one('res.users','Previous Assigned to 1'),
             'previous_assigned_to2': fields.many2one('res.users','Previous Assigned to 2'),
            'priority': fields.selection([('0','01'),('1','02'),('2','03'),('3','04'),('4','05'),('5','06'), ('6','07'), ('7','08'), ('8','09'), ('9','10')], 'Priority', select=True),
        }
    _defaults = {
              'flag':True,
              'status_task': 'paused',
              'checking_task': 'none',
        }
    
    def task_login(self, cr, uid, ids, context=None):
        date_now_d = datetime.datetime.now() + timedelta(hours=7)
        date_now = str(date_now_d)[0:10]
        time_working_obj = self.pool.get('time.working')
        time_working_ids = time_working_obj.search(cr, 1, [])
        if not time_working_ids:
            raise osv.except_osv(_('Warning!'),
                        _('Time Working isnot Defined'))
        attendances_time_obj = self.pool.get('attendances.time')
        check_obj = self.pool.get('check.login.logout')
        check_id = check_obj.search(cr,1,[('user_id','=',uid)])
        line = check_obj.browse(cr,1,check_id)[0]
        if line.check==False:
            raise osv.except_osv(_('Warning!'),
                        _('You cannnot login this task before ending your current task!'))
        for task_id in self.browse(cr,1,ids):
#             if task_id.checking_task=='checking1' and task_id.checking_task=='checking2':
#                 raise osv.except_osv(_('Warning!'),
#                         _('Please wait for Project Manager checking this task!'))
            attendances_time_obj.create(cr, 1,  {
                                                   'name': time.strftime('%Y-%m-%d %H:%M:%S'),
#                                                    'attendance_id' : context['active_id'],
                                                   'task_id': task_id.id,
                                                   'action': 'sign_in',
                                                    'user_id': uid,
                                                    'day': date_now,
                                                         })
        self.write(cr,1,ids,{'flag':False,'status_task': 'working'})
        current_status_obj = self.pool.get('current.status')
        current_status_id = current_status_obj.search(cr,1,[('user_id','=',uid)])
        current_status_obj.write(cr,1,current_status_id,{'name':'working'})
        check_obj.write(cr,1,check_id,{'check':False})
        user_overview_obj = self.pool.get('user.overview')
        user_overview_obj.onchange_attendances_times(cr, uid, context)
        res = {
               'type': 'ir.actions.client',
               'tag': 'reload',
               'context' : context,
               }
        return res     
    def task_logout(self, cr, uid, ids, context=None):
        time_working_obj = self.pool.get('time.working')
        time_working_ids = time_working_obj.search(cr, uid, [])
        if not time_working_ids:
            raise osv.except_osv(_('Warning!'),
                        _('Time Working isnot Defined'))
        obj_model = self.pool.get('ir.model.data')
        model_data_ids = obj_model.search(cr,1,[('model','=','ir.ui.view'),('name','=','work_summary_view_form')])
        resource_id = obj_model.read(cr, 1, model_data_ids, fields=['res_id'])[0]['res_id']
        check_obj = self.pool.get('check.login.logout')
        check_id = check_obj.search(cr,1,[('user_id','=',uid)])
        current_status_obj = self.pool.get('current.status')
        current_status_id = current_status_obj.search(cr,1,[('user_id','=',uid)])
        current_status_obj.write(cr,1,current_status_id,{'name':'paused'})
        check_obj.write(cr,1,check_id,{'check':True})
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'work.summary',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
        
    def open_task(self, cr, uid, ids, context=None):
        obj_model = self.pool.get('ir.model.data')
        model_data_ids = obj_model.search(cr,1,[('model','=','ir.ui.view'),('name','=','view_task_form2')])
        resource_id = obj_model.read(cr, 1, model_data_ids, fields=['res_id'])[0]['res_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': ids and ids[0] or False,
            'context': context,
        }
    
    def back_to_drawing(self, cr, uid, ids, context=None):
        task_type_obj = self.pool.get('project.task.type')
        task_type_id = task_type_obj.search(cr, 1, [('name','=','Drawing')])
        self.write(cr, uid, ids, {'status_task': 'paused','previous_assigned_to':[],'stage_id':task_type_id[0]})
        res = {
               'type': 'ir.actions.client',
               'tag': 'reload',
               'context' : context,
               }
        return res
    
    def logout_all_task(self, cr, uid, context=None):
        task_ids = self.search(cr,1,[('stage_id.state','=','open'),('flag','=',False)])
        user_overview_obj = self.pool.get('user.overview')
        attendances_time_obj = self.pool.get('attendances.time')
        if task_ids:
            for line in self.browse(cr, uid, task_ids):
                if line.checking_task == 'none':
                    user_id = line.user_id.id
                elif line.checking_task == 'checking1':
                    user_id = line.previous_assigned_to1.id
                else:
                    user_id = line.previous_assigned_to2.id
                hours = self.pool.get('work.summary.line')._get_hours(cr, user_id, context)
                self.pool.get('project.task.work').create(cr, 1, {
                    'name':'Auto Summary',
                    'task_id':line.id,
                    'hours': hours,
                    'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'user_id': user_id,
                    })
                attendances_time_obj.create(cr, 1, {
                                                    'name':  time.strftime('%Y-%m-%d %H:%M:%S'),
                                                    'action': 'sign_out',
                                                    'task_id': line.id,
                                                    'user_id': user_id,
                                                })
                check_obj = self.pool.get('check.login.logout')
                check_id = check_obj.search(cr,1,[('user_id','=',user_id)])
                current_status_obj = self.pool.get('current.status')
                current_status_id = current_status_obj.search(cr,1,[('user_id','=',user_id)])
                current_status_obj.write(cr,user_id,current_status_id,{'name':'paused'})
                check_obj.write(cr,user_id,check_id,{'check':True})
                self.write(cr,user_id,line.id,{'flag':True,'status_task': 'paused'})
                user_overview_obj.onchange_attendances_times(cr, user_id, context=context)
#         date_now_d = datetime.datetime.now() + timedelta(hours=7)
#         date_now = str(date_now_d)[0:10]
#         user_obj = self.pool.get('res.users')
#         user_ids = user_obj.search(cr, uid, [])
#         hr_attendance_obj = self.pool.get('hr.attendance')
#         hr_employee_obj = self.pool.get('hr.employee')
#         employee_ids = hr_employee_obj.search(cr, uid, [('user_id','!=',False)])
#         for employee in hr_employee_obj.browse(cr, uid, employee_ids):
#             hr_sign_in = []
#             hr_sign_out = []
#             hr_attendance_ids = hr_attendance_obj.search(cr, uid, [('day','=',date_now),('employee_id','=',employee.id)])
#             if hr_attendance_ids:
#                 for line in hr_attendance_obj.browse(cr, uid, hr_attendance_ids):
#                     if line.action=='sign_in':
#                         hr_sign_in.append(line.employee_id.id)
#                     if line.action=='sign_out':
#                         hr_sign_out.append(line.employee_id.id)
#                 if len(hr_sign_in) > len(hr_sign_out):
#                     hr_employee_obj.attendance_action_change(cr, uid, [hr_sign_in[0]], context)
#             user_overview_obj.onchange_attendances_times(cr, employee.user_id.id, context=context)
        return True
    
    def logout_all_attendance(self, cr, uid, context=None):
        date_now_d = datetime.datetime.now() + timedelta(hours=7)
        date_now = str(date_now_d)[0:10]
        user_obj = self.pool.get('res.users')
        user_ids = user_obj.search(cr, 1, [])
        hr_attendance_obj = self.pool.get('hr.attendance')
        hr_employee_obj = self.pool.get('hr.employee')
        employee_ids = hr_employee_obj.search(cr, 1, [('user_id','!=',False)])
        user_overview_obj = self.pool.get('user.overview')
        for employee in hr_employee_obj.browse(cr, 1, employee_ids):
            hr_sign_in = []
            hr_sign_out = []
            hr_attendance_ids = hr_attendance_obj.search(cr, 1, [('day','=',date_now),('employee_id','=',employee.id)],order='id desc')
            if hr_attendance_ids:
                line = hr_attendance_obj.browse(cr, uid, hr_attendance_ids[0])
                if line.action=='sign_in':
                    hr_employee_obj.attendance_action_change(cr, uid, [line.employee_id.id], context)
                    user_overview_obj.onchange_attendances_times(cr, employee.user_id.id, context=context)
        return True
    
    def refresh_all_user(self, cr, uid, context=None):
        sql='''
            update project_task set flag='t',status_task='paused'
        '''
        cr.execute(sql)
        sql='''
            update check_login_logout set "check"='t'
        '''
        cr.execute(sql)
        sql='''
            update current_status set name='paused'
        '''
        cr.execute(sql)
        return True
    
    def attendance_update(self, cr, uid, context=None):
        date_now_d = datetime.datetime.now() + timedelta(hours=7)
        date_now = str(date_now_d)[0:10]
        user_overview_obj = self.pool.get('user.overview')
        working_summary_obj = self.pool.get('working.summary')
        working_summary_id = working_summary_obj.search(cr,1,[('date','=',date_now)])
        for working_summary in working_summary_obj.browse(cr, 1, working_summary_id):
            user_overview_obj.onchange_attendances_times(cr, working_summary.user_id.id, context=context)
        res = {
               'type': 'ir.actions.client',
               'tag': 'reload',
               'context' : context,
               }
        return res
project_task()

class hr_attendance(osv.osv):
    _inherit = "hr.attendance"

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if 'sheet_id' in context:
            ts = self.pool.get('hr_timesheet_sheet.sheet').browse(cr, uid, context['sheet_id'], context=context)
            if ts.state not in ('draft', 'new'):
                raise osv.except_osv(_('Error!'), _('You cannot modify an entry in a confirmed timesheet.'))
        res = super(hr_attendance,self).create(cr, uid, vals, context=context)
        if 'sheet_id' in context:
            if context['sheet_id'] != self.browse(cr, uid, res, context=context).sheet_id.id:
                raise osv.except_osv(_('User Error!'), _('You cannot enter an attendance ' \
                        'date outside the current timesheet dates.'))
        user_overview_obj = self.pool.get('user.overview')
        user_overview_obj.onchange_attendances_times(cr, uid, context=context)
        return res
hr_attendance()

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
            'department_id': fields.many2one('hr.department','Department'),
        }
sale_order()

class attendances_time(osv.osv):
    _name = "attendances.time"
    _order = 'name desc'
    _columns = {
                'name': fields.datetime('Date', select=1, readonly=True), 
                'attendance_id': fields.many2one('user.overview','Task'),
                'task_id': fields.many2one('project.task','Task', readonly=True),
                'action': fields.selection([('sign_in', 'Sign In'), ('sign_out', 'Sign Out'), ('action','Action')], 'Action', required=True, readonly=True),
                'action_desc': fields.many2one("hr.action.reason", "Action Reason", domain="[('action_type', '=', action)]", help='Specifies the reason for Signing In/Signing Out in case of extra hours.'),
                'user_id': fields.many2one('res.users','User'),
                'day': fields.char('Day', size=64),
        }
attendances_time()

class total_attendance(osv.osv):
    _name = "total.attendance"
    _columns = {
                'name': fields.char('Total Attendance', size=64, readonly=True),
                'user_id': fields.many2one('res.users', 'User', readonly=True),
        }
total_attendance()

class total_timesheet(osv.osv):
    _name = "total.timesheet"
    _columns = {
                'name': fields.char('Total Timesheet', size=64, readonly=True),
                'user_id': fields.many2one('res.users', 'User', readonly=True),
        }
total_timesheet()

class check_login_logout(osv.osv):
    _name = "check.login.logout"
    _columns = {
                'check':fields.boolean('Check'),
                'user_id': fields.many2one('res.users', 'User', readonly=True),
        }
check_login_logout()

class difference_time(osv.osv):
    _name = "difference.time"
    _columns = {
                'name': fields.char('Difference', size=64, readonly=True),
                'user_id': fields.many2one('res.users', 'User', readonly=True),
        }
difference_time()

class current_status(osv.osv):
    _name = "current.status"
    _columns = {
                'name': fields.selection([('working', 'Working'), ('paused', 'Paused')],'Current Status', readonly=True),
                'user_id': fields.many2one('res.users', 'User', readonly=True),
        }
current_status()

class error_reporting(osv.osv):
    _name = "error.reporting"
    _columns = {
                'name': fields.char('Name', size=64, required=True),
                'task_id': fields.many2one('project.task','Task'),
        }
error_reporting()

class error_line(osv.osv):
    _name = "error.line"
    _columns = {
                'error_id': fields.many2one('error.reporting','Error summary'),
                'date': fields.date('Date'),
                'task_id': fields.many2one('project.task','Task'),
        }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d')
    }
error_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
