{
    "name" : "Human resource",
    "author" : "Trần Hưng<tranhung07081989@gmail.com>",
    'category': 'General 70',
    "depends" : ['hr','hr_contract','hr_payroll','hr_expense'],
    "init_xml" : [],
    "demo_xml" : [],
    "description": """
    """,
    'update_xml': [
                   'security/ir.model.access.csv',
                   'hr_view.xml',
                   'hr_contract_view.xml',
                   'hr_payroll_view.xml',
                   'hr_expense_workflow.xml',
                   'report/report_view.xml',
                   'wizard/hr_wizard.xml',
                   
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'certificate': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
