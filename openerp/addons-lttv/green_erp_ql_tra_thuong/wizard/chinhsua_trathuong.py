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


class chinhsua_trathuong(osv.osv_memory):
    _name = 'chinhsua.trathuong'
    
    _columns = {
        'so_vanban': fields.char('Biên bản số',required=True),
        'date': fields.date('Ngày',required=True),
    }
    
    _defaults = {
        'date': time.strftime('%Y-%m-%d'),
    }
    
    def chinhsua(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids[0])
        tra_thuong_obj = self.pool.get('tra.thuong')
        tra_thuong_id = context.get('active_id')
        default = {'lichsu_line':[],'parent_id':tra_thuong_id,'state':'new'}
        new_id = tra_thuong_obj.copy(cr, uid, tra_thuong_id, default)
        tra_thuong_obj.write(cr, uid, [tra_thuong_id],{'so_vanban':line.so_vanban,'date':line.date})
        mod_obj = self.pool.get('ir.model.data')
        model_data_ids = mod_obj.search(cr, uid, [('model', '=', 'ir.ui.view'),('name', '=', 'chinhsua_tra_thuong_form')], context=context)
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
        return {
            'name': _('Trả Thưởng'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'tra.thuong',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': tra_thuong_id,
        }
chinhsua_trathuong()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

