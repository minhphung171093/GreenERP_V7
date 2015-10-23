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
import time
from openerp.osv import osv,fields
from openerp.tools.translate import _


class congno_vacine(osv.osv_memory):
    _name = 'congno.vacine'
     
    _columns = {
        'date_from': fields.date('Tính đến ngày',required=True),
#         'user_id': fields.many2many('res.users', string='Users', readonly=True),
        'user_id': fields.many2many('res.users', 'congno_user_ref', 'congno_id', 'user_id', 'Users'),  
    }
     
    _defaults = {
        'date_from': time.strftime('%Y-%m-%d'),
        'user_id': lambda self,cr, uid, ctx: [(6,0,[uid])],
        
    }
     
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'congno.vacine' 
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'congno_vacine_report', 'datas': datas}
     
congno_vacine()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

