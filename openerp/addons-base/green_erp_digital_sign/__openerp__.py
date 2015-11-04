# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#    Copyright (C) 2011-2015 Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
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
    "name" : "GreenERP Web Digital Signature",
    "version" : "1.0",
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    'sequence': 1,
    "category": 'GreenERP',
    'complexity': "easy",
    'depends': ['web'],
    "description": """
        This module provides the functionality to store digital signature image for a record.
        The example can be seen into the User's form view where we have added a test field under signature.
    """,
    'data': [
#         'views/we_digital_sign_view.xml',
        'users_view.xml'
    ],
    'qweb': ['static/src/xml/digital_sign.xml'],
    'js': [
        'static/lib/excanvas.js',
        'static/lib/jquery.signature.js',
        'static/src/js/digital_sign.js',
     ],
    'css': ['static/src/css/digital.css'
            'static/src/css/jquery.signature.css'
            ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
