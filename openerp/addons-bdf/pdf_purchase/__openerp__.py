# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################


{
    "name" : "BDF Purchase",
    "version" : "7.0",
    "author" : "Pham Tuan Kiet <tykiet.208@gmail.com>",
    'category': 'VSIS 70',
    "depends" : ["base",'report_aeroo','product','account','green_erp_bdf_base','web_adblock','web_group_expand','web_m2x_options','document','ir_sequence_autoreset'],
    "init_xml" : [],
    "demo_xml" : [],
    "description": """
    """,
    'update_xml': [
                'security/security.xml',
                'security/ir.model.access.csv',
                'wizard/approve_pr_view.xml',
                'wizard/reject_pr_view.xml',
                'wizard/alert_form_view.xml',
                'wizard/pr_pending_report_view.xml',
                'report/report_view.xml',
                'report/list_purchase_request_view.xml',
                'purchase_request.xml',
                'menu.xml',
                'bdf_sequence.xml',
                'bdf_schedule.xml',
#                 'data/process_data.xml',
    ],
    'test': [
    ],
    'css' : [
        "static/src/css/base.css",
    ],
    'js': ['static/src/js/base.js'],
    'installable': True,
    'auto_install': False,
    'certificate': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
