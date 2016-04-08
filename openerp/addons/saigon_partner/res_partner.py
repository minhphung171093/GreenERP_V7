# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import datetime
from lxml import etree
import math
import pytz
import re

import openerp
from openerp import SUPERUSER_ID
from openerp import pooler, tools
from openerp.osv import osv, fields
# from openerp.osv.expression import get_unaccent_wrapper
from openerp.tools.translate import _
from openerp.tools.yaml_import import is_comment


class res_partner(osv.osv):
    _description = 'Partner'
    _inherit = "res.partner"
    def _get_sale_history(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        partner_id = ids[0]
        result[partner_id] = self.pool.get('sale.order').search(cr, uid, [('partner_id','=',partner_id)])
        return result
    def onchange_address(self, cr, uid, ids, use_parent_address, parent_id, context=None):
        def value_or_id(val):
            """ return val or val.id if val is a browse record """
            return val if isinstance(val, (bool, int, long, float, basestring)) else val.id
        result = {}
        if parent_id:
            if ids:
                partner = self.browse(cr, uid, ids[0], context=context)
                if partner.parent_id and partner.parent_id.id != parent_id:
                    result['warning'] = {'title': _('Warning'),
                                         'message': _('Changing the company of a contact should only be done if it '
                                                      'was never correctly set. If an existing contact starts working for a new '
                                                      'company then a new contact should be created under that new '
                                                      'company. You can use the "Discard" button to abandon this change.')}
            parent = self.browse(cr, uid, parent_id, context=context)
            address_fields = self._address_fields(cr, uid, context=context)
            result['value'] = dict((key, value_or_id(parent[key])) for key in address_fields)
            result['value'] = {
                    'street': parent.street,
                    'street2': parent.street2,
                    'city': parent.city,
                    'state_id': parent.state_id.id,
                    'zip': parent.zip,
                    'country_id': parent.country_id.id,
                    'website': parent.website,
                    'ref': parent.ref,
                    'phone': parent.phone,
                    'email': parent.email,           
                    }
        else:
            result['value'] = {'use_parent_address': False}
        return result
    _columns = {
         'sale_history': fields.function(_get_sale_history, method=True, type='one2many', relation='sale.order', string='Sales History'),       
    }
res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
