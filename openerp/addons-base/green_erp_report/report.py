# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP SA (<http://openerp.com>).
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

import base64
import re
import threading
from openerp.tools.safe_eval import safe_eval as eval
from openerp import tools
import openerp.modules
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from datetime import timedelta
import datetime
class greenerp_report(osv.osv):
    _name = 'greenerp.report'
    
    _columns = {
        'name': fields.char('Table', size=1024, required=True),
        'delete_after': fields.integer('Delete After', required=True),
    }

    def delete_greenerp_report(self, cr, uid, context=None):
        sql = '''
            select id from greenerp_report
        '''
        cr.execute(sql)
        gr_ids = [r[0] for r in cr.fetchall()]
        for line in self.browse(cr, SUPERUSER_ID, gr_ids):
            delete_after = line.delete_after or 1
            date_now = datetime.datetime.now() + timedelta(days=-delete_after)
            date = date_now.strftime('%Y-%m-%d')
            sql = '''
                delete from %s where create_date <= '%s'
            '''%(line.table,date)
            cr.execute(sql)
        return True

greenerp_report()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: