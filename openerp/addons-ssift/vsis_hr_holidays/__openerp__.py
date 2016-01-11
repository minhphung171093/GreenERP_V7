# -*- encoding: utf-8 -*-
##############################################################################
#
#    Viet Solution Infomation System, Open Source Management Solution
#    Copyright (C) 2009 General Solutions (<http://vietsolutionis.com>). All Rights Reserved
#
##############################################################################

{
        "name" : "VSIS HR Holidays",
        "version" : "1.0",
        "author" : "Viet Solution Infomation System",
        "website" : "http://www.vietsolutionis.com",
        "category" : "VSIS Modules",
        "description" : """VSIS HR""",
        "depends" : ["hr_holidays"],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : [
                        'hr_holidays_view.xml',
                        ],
        "installable": True
}
