# -*- encoding: utf-8 -*-
##############################################################################
#
#
##############################################################################

{
    "name" : "GreenERP Assets Management",
    'category': 'GreenERP',
    'sequence': 1,
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    "depends" : ["account_asset","report_aeroo_ooo",'green_erp_viruco_base','report_aeroo_ooo'],
    "description": """Financial and accounting asset management.
    This Module manages the assets owned by a company or an individual. It will keep track of depreciation's occurred on
    those assets. And it allows to create Move's of the depreciation lines.
    """,
    "init_xml" : [
    ],
    "demo_xml" : [ ],
    'test': [],
    "update_xml" : [
        'security/account_security.xml',
        'security/ir.model.access.csv',
        "wizard/account_asset_change_duration_view.xml",
        "wizard/wizard_asset_compute_view.xml",
        "wizard/print_report.xml",
        "report/report_view.xml",
        "report/account_asset_report_view.xml",
        "account_asset_view.xml",
        "menu.xml",
    ],
    "auto_install": False,
    "installable": True,
    "application": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

