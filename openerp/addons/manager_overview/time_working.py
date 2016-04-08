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

class time_working(osv.osv):
    _name = 'time.working'
    _columns = {
        'a_from': fields.float('From', required = True),
        'a_to': fields.float('To', required = True),
        'b_from': fields.float('From', required = True),
        'b_to': fields.float('To', required = True),
        }
    def _check_hour(self, cr, uid, ids,context=None):
        for shift in self.browse(cr, uid, ids, context=context):
            if shift.a_from:
                if shift.a_to < shift.a_from or shift.b_from < shift.a_from or shift.b_to < shift.a_from or shift.b_from < shift.a_to or shift.b_to < shift.a_to or shift.b_to < shift.b_from:
                    return False
                if shift.a_from < 0 or shift.a_from > 24:
                    return False
                if shift.a_to < 0 or shift.a_to > 24:
                    return False
                if shift.b_from < 0 or shift.b_from > 24:
                    return False
                if shift.b_to < 0 or shift.b_to > 24:
                    return False
        return True
    
    _constraints = [
        (_check_hour,"Time Validation Error",[]),
    ]
time_working() 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
