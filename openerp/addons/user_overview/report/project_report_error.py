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

from openerp.osv import fields,osv
from openerp import tools

class report_project_task_error(osv.osv):
    _name = "report.project.task.error"
    _auto = False
    _columns = {
        'name': fields.char('Task Summary', size=128, readonly=True),
        'day': fields.char('Day', size=128, readonly=True),
        'year': fields.char('Year', size=64, required=False, readonly=True),
        'user_id': fields.many2one('res.users', 'Assigned To', readonly=True),
        'date': fields.date('Date',readonly=True),
        'project_id': fields.many2one('project.project', 'Project', readonly=True),
        'task_id': fields.many2one('project.task', 'Task', readonly=True),
        'nbr': fields.integer('# of tasks', readonly=True),
        'month':fields.selection([('01','January'), ('02','February'), ('03','March'), ('04','April'), ('05','May'), ('06','June'), ('07','July'), ('08','August'), ('09','September'), ('10','October'), ('11','November'), ('12','December')], 'Month', readonly=True),
        'state': fields.selection([('draft', 'Draft'), ('open', 'In Progress'), ('pending', 'Pending'), ('cancelled', 'Cancelled'), ('done', 'Done')],'Status', readonly=True),
    }
    _order = 'name desc, project_id'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'report_project_task_error')
        cr.execute("""
            CREATE view report_project_task_error as
              SELECT
                     count(*) AS nbr,
                    min(e.id) as id,
                    to_char(e.date, 'YYYY') as year,
                    to_char(e.date, 'MM') as month,
                    to_char(e.date, 'YYYY-MM-DD') as day,
                    t.user_id,
                    t.project_id,
                    e.task_id,
                    t.state,
                    r.name as name,
                    t.stage_id
              FROM error_line e join project_task t on (e.task_id=t.id)
                      left join error_reporting r on (e.error_id=r.id)
                WHERE t.active = 'true'
                GROUP BY
                    t.id,
                    year,
                    month,
                    day,
                    t.user_id,
                    e.task_id,
                    t.project_id,
                    t.state,
                    r.name,
                    t.stage_id
                    

        """)

report_project_task_error()

