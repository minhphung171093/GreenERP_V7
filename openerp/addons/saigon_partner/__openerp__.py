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

{
    'name': 'Sai Gon Partner',
    'version': '1.0',
    'category': 'Sai Gon Partner',
    'sequence': 14,
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://www.incomtech.com.vn',
    'depends': ['account','account_voucher','base','sale','project'],
    'data': [
             'security/ir.model.access.csv',
             'sale_view.xml',
             'res_partner_view.xml',
             'project_type_view.xml',
             'project_view.xml',
             'product_view.xml',
             'wizard/message_view.xml',
             'wizard/sale_message_view.xml',
             'account_invoice_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
