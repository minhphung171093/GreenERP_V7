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

class account_journal(osv.osv):
    _inherit = "account.journal"
 
    _columns = {
        'shop_ids': fields.many2many('sale.shop', 'account_journal_shop_rel', 'journal_id', 'shop_id', 'Shops'),
    }
     
account_journal()

class account_move(osv.osv):
    _inherit = "account.move"

    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop', states={'posted':[('readonly',True)]}),
        'date_document': fields.date('Document Date', states={'posted':[('readonly',True)]}),
    }
    
    def _get_shop_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.context_shop_id.id or False
    
    _defaults = {
        'shop_id': _get_shop_id,
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('date',False) and not vals.get('date_document',False):
            vals.update({'date_document': vals['date']})
        return super(account_move, self).create(cr, uid, vals, context)
    
    def _auto_init(self, cr, context=None):
        super(account_move, self)._auto_init(cr, context)
        cr.execute('''
        UPDATE account_move
        SET date_document = date
        where date_document IS NULL
        ''')
    
account_move()

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    
    _columns = {
        'shop_id': fields.related('move_id', 'shop_id', type='many2one', relation='sale.shop', string='Shop', readonly=True, store=True),
    }
    
account_move_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: