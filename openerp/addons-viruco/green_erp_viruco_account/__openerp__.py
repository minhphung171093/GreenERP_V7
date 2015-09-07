# -*- encoding: utf-8 -*-
##############################################################################
#
#    Acespritech Solutions Pvt. Ltd.
#    Copyright (C) 2013-2014
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
    'name': 'Viruco Account',
    'version': '1.0',
    'category': 'GreenERP',
    'description': """Account""",
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    'depends': ['green_erp_viruco_base','account_voucher','account','green_erp_account_regularization'],
    'data': [
        'security/viruco_account_security.xml',
        'security/ir.model.access.csv',
        'report/report_view.xml',
        'wizard/print_report.xml',
        'account_invoice_view.xml',
        'account_voucher_view.xml',
        'account_voucher_batch_view.xml',
        'menu.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: