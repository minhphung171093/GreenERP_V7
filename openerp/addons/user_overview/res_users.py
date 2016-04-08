# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2013 OpenERP s.a. (<http://openerp.com>).
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
from functools import partial
import logging
from lxml import etree
from lxml.builder import E
from datetime import datetime, timedelta
import openerp
from openerp import SUPERUSER_ID
from openerp import pooler, tools
import openerp.exceptions
from openerp.osv import fields,osv
from openerp.osv.orm import browse_record
from openerp.tools.translate import _
import datetime
_logger = logging.getLogger(__name__)

class res_users(osv.osv):
    _inherit = "res.users"
    _description = 'Users'

    def login(self, db, login, password):
        if not password:
            return False
        user_id = False
        cr = pooler.get_db(db).cursor()
        try:
            # autocommit: our single update request will be performed atomically.
            # (In this way, there is no opportunity to have two transactions
            # interleaving their cr.execute()..cr.commit() calls and have one
            # of them rolled back due to a concurrent access.)
            cr.autocommit(True)
            # check if user exists
            res = self.search(cr, SUPERUSER_ID, [('login','=',login)])
            if res:
                user_id = res[0]
                # check credentials
                self.check_credentials(cr, user_id, password)
                # We effectively unconditionally write the res_users line.
                # Even w/ autocommit there's a chance the user row will be locked,
                # in which case we can't delay the login just for the purpose of
                # update the last login date - hence we use FOR UPDATE NOWAIT to
                # try to get the lock - fail-fast
                # Failing to acquire the lock on the res_users row probably means
                # another request is holding it. No big deal, we don't want to
                # prevent/delay login in that case. It will also have been logged
                # as a SQL error, if anyone cares.
                try:
                    cr.execute("SELECT id FROM res_users WHERE id=%s FOR UPDATE NOWAIT", (user_id,), log_exceptions=False)
                    cr.execute("UPDATE res_users SET login_date = now() AT TIME ZONE 'UTC' WHERE id=%s", (user_id,))
                except Exception:
                    _logger.debug("Failed to update last_login for db:%s login:%s", db, login, exc_info=True)
            
            hr_attendance_obj = self.pool.get('hr.attendance')
            hr_employee_obj = self.pool.get('hr.employee')
            date_now_d = datetime.datetime.now() + timedelta(hours=7)
            date_now = str(date_now_d)[0:10]
            hr_attendance_ids = hr_attendance_obj.search(cr, user_id, [('day','=',date_now),('employee_id.user_id','=',user_id)])
            hr_employee_ids = hr_employee_obj.search(cr, user_id, [('user_id','=',user_id)])
            if hr_employee_ids:
                if len(hr_attendance_ids)%2==0:
                    hr_employee_obj.attendance_action_change(cr, user_id, [hr_employee_ids[0]], context=None)
        except openerp.exceptions.AccessDenied:
            _logger.info("Login failed for db:%s login:%s", db, login)
            user_id = False
        finally:
            cr.close()

        return user_id

res_users()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
