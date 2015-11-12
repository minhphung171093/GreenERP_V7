# -*- coding: utf-8 -*-
{
    'name': 'GreenERP Web Serialized Field',
    'version': '1.0',
    'category': 'GreenERP',
    'description': """
Add support for fields.serialized in from view with a new widget: "serialized"
    """,
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    'sequence': 1,
    'depends': [
        'green_erp_web_unleashed'
    ],
    
    'data': [
    ],
    
    'qweb' : [
        'static/src/templates/*'
    ],
    
    
    'css' : [
        'static/lib/jsoneditor/jsoneditor.css',
    
        'static/src/css/field_serialized.css',
    ],
       
    'js': [
        # lib
        'static/lib/jsoneditor/lib/jsonlint/jsonlint.js',
        'static/lib/jsoneditor/jsoneditor.js',
        
        'static/src/js/field_serialized.js'
    ],
    
    'test': [
    ]
}