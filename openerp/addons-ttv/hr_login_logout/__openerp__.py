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
    'name': 'HR Signin/Signout based on Login Logout',
    'version': '1.0',
    'category': 'General',
    'description': """
This module is used for customization in webclient, .
""",
    'author': "Acespritech Solutions Pvt. Ltd.",
    'website': "www.acespritech.com",
    'depends': ['web', 'base', 'hr_attendance'],
    'data': [],
    'demo': [],
    'test': [],
    'qweb': ['static/src/xml/web.xml'],
    'js': ['static/src/js/base.js'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: