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
    'name': 'Chi Cuc Thu Y Co cau Dan',
    'version': '1.0',
    'category': 'GreenERP',
    'sequence': 14,
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    'depends': ['report_aeroo','report_aeroo_ooo','green_erp_ccty_base','green_erp_ccty_nhapxuatquacanh','green_erp_ccty_xuly_giasuc'],
    'data': [
            'security/cocaudan_security.xml',
            'security/ir.model.access.csv', 
            'wizard/cocau_hientai_wizard_view.xml',
            'wizard/cocau_tai_thoi_diem_wizard_view.xml',
            'wizard/cocau_hientai_cac_ho_wizard_view.xml',
            'wizard/cocau_hientai_khuvuc_heo_wizard_view.xml',
            'report/cocau_hientai_report_view.xml',
            'report/cocau_tai_thoi_diem_report_view.xml',
            'report/cocau_hientai_cac_ho_report_view.xml',
            'report/cocau_hientai_khuvuc_heo_report_view.xml',
            'cocau_view.xml',
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
