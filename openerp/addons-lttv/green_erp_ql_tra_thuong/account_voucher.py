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

class account_voucher(osv.osv):
    _inherit = "account.voucher"
    
    _columns = {
        'date_document': fields.date('Document Date', readonly=True, states={'draft':[('readonly',False)]},),
        'reference_number': fields.char('Number', size=32, readonly=True, states={'draft':[('readonly',False)]}),
        'batch_id': fields.many2one('account.voucher.batch', 'Related Batch', ondelete='cascade'),
        'partner_bank_id':fields.many2one('res.partner.bank', 'Partner Bank', required=False, readonly=True, states={'draft':[('readonly',False)]}),
        'company_bank_id':fields.many2one('res.partner.bank', 'Company Bank', required=False, readonly=True, states={'draft':[('readonly',False)]}),
        'unshow_financial_report':fields.boolean('Không khai báo thuế'),
    }

account_voucher()

