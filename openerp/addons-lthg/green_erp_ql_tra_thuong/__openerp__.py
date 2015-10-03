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
    'name': 'GreenERP QL Trả thưởng',
    'version': '1.1',
    "author" : "nguyentoanit@gmail.com",
    'website': 'http://incomtech.com/',
    "category": 'GreenERP',
    'sequence': 1,
    'description': """
    """,
    'depends': ['green_erp_base','account_voucher','account_accountant','product','report_aeroo','report_aeroo_ooo'],
    'data': [
        'security/ql_tra_thuong_security.xml',
        'security/ir.model.access.csv',
        'report/trathuong_bctt_view.xml',
        'report/trathuong_theolo_view.xml',
        'report/trathuong_theongay_view.xml',
        'report/trathuong_vetrungthuong_view.xml',
        'wizard/chinhsua_trathuong_view.xml',
        'wizard/trathuong_bctt_view.xml',
        'wizard/trathuong_theolo_view.xml',
        'wizard/trathuong_theongay_view.xml',
        'wizard/trathuong_vetrungthuong_view.xml',
        'ql_tra_thuong_view.xml',
        'account_voucher_batch_view.xml',
        'menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
