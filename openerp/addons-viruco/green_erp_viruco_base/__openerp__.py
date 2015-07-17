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
    'sequence': 14,
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    'depends': ['web','base','purchase','sale','sale_stock','product','properties','report_aeroo','report_aeroo_ooo','stock','account'],
    'data': [
            'report/don_ban_hang_view.xml',
            'report/don_mua_hang_view.xml',
            'config_view.xml',
            'hop_dong_view.xml',
            'phuluc_hop_dong_view.xml',
    ],
    'css' : [
        "static/src/css/base.css",
    ],
    'qweb': ['static/src/xml/base.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
