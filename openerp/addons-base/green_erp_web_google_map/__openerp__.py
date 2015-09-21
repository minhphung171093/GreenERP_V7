# -*- coding: utf-8 -*-

##############################################################################
#
#    Authors: Valentin LAB for simplee.fr and Boris Timokhin, Dmitry
#    Zhuravlev-Nevsky for InfoSreda LLC
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'GreenERP Web Map',
    'version': '0.4.0',
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    'sequence': 1,
    "category": "GreenERP",
    'description': """


OpenERP Web Map
===============

Web Map module brings Google Map support right into OpenERP web-client.

Version for 6.0 was brought by Infosreda LLC.
Conversion to 6.1 needed a full rewrite from simplee.fr and was funded by CARIF/OREF.
Version 7.0 needed adaptation from 0k.io and was funded by CARIF/OREF.

Usage
=====

After installation, all "res.partner" views will be extended with neatly map.

Just type in an address and press "Get coordinates" button. Google Geocoder
will populate latitude and longitude fields. Map marker will be set
accordingly to them.

Not happy with geocoding result? Update latitude and longitude as simply as
dragging marker over Google Map widget.

Save your data and enjoy.

So, you are a module developer
==============================

Good news! In case you want to add Google Map support for your own module, all
you need to do is just put the next string to the view.

::

    <field name="map" widget="gmap" />

co cac widget la gmap, m2m_gmap, o2m_gmap
vi du
.py
'partner_ids': fields.many2many('res.partner','hdsd_partner_ref','hdsd_id','partner_id','Partners'),
.xml
<group>
    <field name="partner_ids" nolabel="1"
       widget="m2m_gmap" colspan="4"/>
</group>
se hien thi nhug diem cua nhug partner da duoc chon trong partner_ids
""",
    'depends': ['base', 'web'],
    'data': ['gmap_view.xml'],
    'update_xml': [],
    'active': True,
    'web': True,
    'js': [
           'static/src/js/gmap.js',
	    ],
    'css': ['static/src/css/gmap.css', ],
    'qweb': ['static/src/xml/base.xml', ],
    'images': ['images/map.png',],
}
