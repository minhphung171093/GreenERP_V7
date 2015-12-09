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
    'name': 'Chi Cuc Thu Y BASE',
    'version': '1.0',
    'category': 'GreenERP',
    'sequence': 14,
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    'depends': ['report_aeroo','report_aeroo_ooo','web_m2x_options','web_widget_radio','green_erp_hdsd','green_erp_web_google_map','green_erp_ckeditor','green_erp_readonly_bypass'],
    'data': [
            'security/base_security.xml', 
            'security/ir.model.access.csv',
            'baocao_cscn_map_data.xml', 
            'danhmuc_view.xml',
            'menu.xml',
            'danhmuc_loaivat_data.xml',
            ],
    'css' : [
        'static/src/css/base.css'
    ],
    'qweb': [
        'static/src/xml/base.xml'
    ],
    'js' : [
        "static/src/js/view_form.js",
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
