# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################


{
    "name" : "GreenERP Stock Account",
    "version" : "7.0",
    'category': 'GreenERP',
    'sequence': 1,
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    "depends" : ["green_erp_stock"],
    "init_xml" : [],
    "demo_xml" : [],
    "description": """
    """,
    'update_xml': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'cost_history_view.xml',
        'menu.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'certificate': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
