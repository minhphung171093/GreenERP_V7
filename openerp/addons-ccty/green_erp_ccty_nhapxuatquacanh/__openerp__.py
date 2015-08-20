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
    'name': 'Chi Cuc Thu Nhap-Xuat-Qua Canh',
    'version': '1.0',
    'category': 'GreenERP',
    'sequence': 14,
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    'depends': ['green_erp_ccty_base'],
    'data': [
            'security/nhap_xuat_security.xml',
            'security/ir.model.access.csv', 
            'wizard/tinhhinh_nhap_giasuc_wizard_view.xml',
            'wizard/tinhhinh_xuat_giasuc_wizard_view.xml',
            'wizard/theodoi_tinhhinh_nhap_giasuc_wizard_view.xml',
            'wizard/theodoi_tinhhinh_xuat_giasuc_wizard_view.xml',
            'report/tinhhinh_nhap_giasuc_report_view.xml',
            'report/tinhhinh_xuat_giasuc_report_view.xml',
            'report/theodoi_tinhhinh_nhap_giasuc_report_view.xml',
            'report/theodoi_tinhhinh_xuat_giasuc_report_view.xml',
            'nhap_xuat_view.xml',
            'menu.xml',
    ],
    'css' : [
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
