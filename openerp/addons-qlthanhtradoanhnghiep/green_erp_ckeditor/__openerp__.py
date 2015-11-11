# -*- coding: utf-8 -*-

{
    "name" : 'GreenERP web_ckeditor',
    "version" : "0.1",
    "depends" : [ 'web'],
    'category': 'GreenERP',
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    'sequence': 1,
    "installable" : True,
    "active" : False,
    "js": ["static/src/js/base.js",
           "static/lib/js/ckeditor/ckeditor.js" ],
    "css": [],
    "qweb": ["static/src/xml/*.xml", ]
}
