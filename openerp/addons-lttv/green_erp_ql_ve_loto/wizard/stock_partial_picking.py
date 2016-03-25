# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP SA (<http://openerp.com>).
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
from lxml import etree
from openerp.osv import fields, osv
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"

    def _partial_move_for(self, cr, uid, move, context=None):
        partial_move = {
            'daily_id' : move.daily_id and move.daily_id.id or False,
            'product_id' : move.product_id.id,
            'quantity' : move.product_qty if move.state == 'assigned' or move.picking_id.type == 'in' else 0,
            'product_uom' : move.product_uom.id,
            'prodlot_id' : move.prodlot_id.id,
            'move_id' : move.id,
            'location_id' : move.location_id.id,
            'location_dest_id' : move.location_dest_id.id,
            'currency': move.picking_id and move.picking_id.company_id.currency_id.id or False,
        }
        if move.picking_id.type == 'in' and move.product_id.cost_method == 'average':
            partial_move.update(update_cost=True, **self._product_cost_for_average_update(cr, uid, move))
        return partial_move

stock_partial_picking()

class stock_partial_picking_line(osv.TransientModel):
    _inherit = "stock.partial.picking.line"
    _columns = {
        'daily_id': fields.many2one('res.partner','Đại lý'),
    }

stock_partial_picking_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
