# -*- coding: utf-8 -*-

##############################################################################
#
#    Authors: Boris Timokhin, Dmitry Zhuravlev-Nevsky. Copyright InfoSreda LLC
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from osv import fields


class res_partner(osv.osv):

    _inherit = 'res.partner'

    _columns = {
        'lat': fields.float(u'Latitude', digits=(9, 6)),
        'lng': fields.float(u'Longitude', digits=(9, 6)),
        'radius': fields.float(u'Radius', digits=(9, 16)),
        'map': fields.dummy(),
        'points': fields.text('Points'),
    }
    
    def write_radius(self, cr, uid, id,active_model, vals, context=None):
        if vals.get('radius',False):
            vals.update({'points':'10.793740,106.658763,Diem 1;10.795204,106.659119,Diem 2;10.794135,106.658044,Diem 3'})#10.793740,106.658763,Diem 1;10.795204,106.659119,Diem 2;10.794135,106.658044,Diem 3
#         self.pool.get(active_model).write(cr, uid, [int(id)], vals, context)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
        
    def write_center(self, cr, uid, id,active_model, vals, context=None):
        if vals.get('center',False):
            vals.update({'lat':vals['center']['G'],'lng':vals['center']['K']})#10.793740,106.658763,Diem 1;10.795204,106.659119,Diem 2;10.794135,106.658044,Diem 3
#         self.pool.get(active_model).write(cr, uid, [int(id)], vals, context)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
res_partner()
