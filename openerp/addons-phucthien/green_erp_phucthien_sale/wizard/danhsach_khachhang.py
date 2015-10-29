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


class danhsach_khachhang(osv.osv_memory):
    _name = 'danhsach.khachhang'
    
    _columns = {
        'categ_ids': fields.many2many('product.category','danhsachkhachhang_categ_ref','dskh_id','categ_id', 'Nhóm sản phẩm'),
    }
    
    _defaults = {
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'danhsach.khachhang'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'danhsach_khachhang_report', 'datas': datas}
    
danhsach_khachhang()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

