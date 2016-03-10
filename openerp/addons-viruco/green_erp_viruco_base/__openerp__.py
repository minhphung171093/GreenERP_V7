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
    'name': 'Viruco BASE',
    'version': '1.0',
    'category': 'GreenERP',
    'sequence': 1,
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    'depends': ['green_erp_viruco_menu','web','base','purchase','sale','sale_stock','product','properties','report_aeroo','report_aeroo_ooo','stock','account','green_erp_readonly_bypass'],
    'data': [
            'security/viruco_base_security.xml',
            'security/ir.model.access.csv',
            'wizard/print_report.xml',
            'wizard/tach_phieu.xml',
            'wizard/chat_luong_wizard_view.xml',
            'report/don_ban_hang_view.xml',
            'report/don_mua_hang_view.xml',
            'report/draft_bl_report_view.xml',
            'report/theo_doi_hop_dong_view.xml',
            'report/phu_luc_hd_xuat_khau_view.xml',
            'config_view.xml',
            'hop_dong_view.xml',
            'draft_bl_view.xml',
            'phuluc_hop_dong_view.xml',
            'product_view.xml',
            'res_users_view.xml',
            'nhat_ky_tai_san_sequence.xml',
            'hopdong_sequence.xml',
            'menu.xml',
    ],
    'css' : [
        "static/src/css/base.css",
    ],
    'js' : [
    ],
    'qweb': ['static/src/xml/base.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
