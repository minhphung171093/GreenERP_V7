# -*- coding: utf-8 -*-

{
    "name": 'GreenERP m2x options',
    "version": "0.1",
    'category': 'GreenERP',
    'sequence': 1,
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    "description": """
=====================================================
Add new options for many2one and many2manytags field:
=====================================================

- create: true/false -> disable "create" entry in dropdown panel
- create_edit: true/false -> disable "create and edit" entry in dropdown panel
- limit: 10 (int) -> change number of selected record return in dropdown panel
- m2o_dialog: true/false -> disable quick create M20Dialog triggered on error.

Example:
--------

``<field name="partner_id" options="{'limit': 10, 'create': false,
'create_edit': false}"/>``

Note:
-----

If one of those options are not set, many2one field uses default many2one
field options.

Thanks to:
----------

- Nicolas JEUDY <njeudy@tuxservices.com>
- Valentin LAB <valentin.lab@kalysto.org>

""",
    "depends": [
        'base',
        'web',
    ],
    "js": [
        'static/src/js/form.js',
    ],
    "installable": True,
    "active": False,
}
