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
    'name': 'Viruco Stock',
    'version': '1.0',
    'category': 'GreenERP',
    'description': """Stock""",
    'author': "tranhung07081989@gmail.com",
    'website': "www.acespritech.com",
    'depends': ['green_erp_viruco_base','stock','report_aeroo','report_aeroo_ooo'],
    'data': [
         'security/viruco_stock_security.xml',
         'security/ir.model.access.csv',
        'report/denghi_xuathang_view.xml',
        'report/denghi_nhapkho_view.xml',
        'report/denghi_xuatkho_view.xml',
        'wizard/stock_move_view.xml',
        'wizard/stock_partial_picking_view.xml',
        'wizard/stock_invoice_onshipping_view.xml',
        'stock_view.xml', 
        'stock_inventory.xml', 
        'stock_sequence.xml',
        'wizard_stock_view.xml',
     ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: