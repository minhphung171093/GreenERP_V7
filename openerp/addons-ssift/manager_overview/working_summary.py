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

class working_summary(osv.osv):
    _name = 'working.summary'
    _order = 'day desc,date desc'
    _columns = {
        'name': fields.datetime('Date', select=1),
        'user_id': fields.many2one('res.users','User'),
        'date': fields.char('Date',size=64),
        'day': fields.date('Date'),
        'login': fields.char('Login',size=64),
        'logout': fields.char('Logout',size=64),
        'total_attendance': fields.char('Total Attendance',size=64),
        'total_timesheet': fields.char('Total Timesheet',size=64),
        'difference_time': fields.char('Difference Time',size=64),
        }
    _defaults = {
        'total_attendance': '0:00:00',
        'total_timesheet': '0:00:00',
        'difference_time': '0:00:00',
    }
working_summary() 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
