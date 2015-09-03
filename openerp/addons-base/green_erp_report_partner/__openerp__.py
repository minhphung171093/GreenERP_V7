# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

{
    "name" : "GreenERP Partner Reports",
    "version" : "7.0",
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    'complexity': "normal",
    "description": """
    """,
    "category": 'GreenERP',
    "sequence": 14,
    "images" : [],
    "depends" : ["base","account_accountant","report_aeroo",'green_erp_base'],
    "init_xml" : [],

    "demo_xml" : [],

    "update_xml" : [
        "report/report_view.xml",
        "wizard/print_report.xml",
        
        "menu.xml",
    ],
    "test" : [
    ],
    'certificate': False,
    "auto_install": False,
    "application": True,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
