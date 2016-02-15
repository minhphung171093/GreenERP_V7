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

{
    'name': 'User Overview',
    'version': '1.0',
    'category': 'User Overview',
    'sequence': 14,
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://www.incomtech.com.vn',
    'depends': ['hr_attendance','hr','project'],
    'data': [
                'security/project_security.xml',
            'wizard/work_summary_view.xml',
            'report/checking2_view.xml',
             'user_overview_view.xml',
             'security/ir.model.access.csv',
             'manager_overview_view.xml',
             'vsis_hr_overtime_view.xml',
             'wizard/hr_attendance_print_users_view.xml',
             'user_overview_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
