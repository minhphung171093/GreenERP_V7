{
    "name" : "GreenERP Group Expand Buttons",
    "category": "GreenERP",
    "version" : '1.0',
    'sequence': 1,
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    "description":
        """
A group by list can be expanded and collapased with buttons
===============================================================
You'll see two buttons appear on top right corner of the list when you perform a group by with which you can expand and collapse grouped records by level.
        """,
    "depends" : ["web"],
    "js": ["static/src/js/web_group_expand.js"],
     'qweb' : ["static/src/xml/expand_buttons.xml"],
     'css' : ["static/src/css/expand_buttons.css"],
    'installable': True,
    'auto_install': False,
}

