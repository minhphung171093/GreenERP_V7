# -*- coding: utf-8 -*-
{
    'name': 'GreenERP Booking Chart - Task Demo',
    'version': '1.0',
    'author': 'nguyentoanit@gmail.com',
    'website' : 'http://incomtech.com/',
    'sequence': 1,
    'category': 'GreenERP',
    'description': """
Demo of a booking chart view applied on the project module, powered by the booking chart module.

features in demo:

- data binding between tasks and resources booking
- new menu entry to access to the booking chart

notes:

- this demo depend on booking_chart and project modules
- install it on a database with demo data enabled
    """,
    
    'depends': [
        'project',
        'green_erp_booking_chart',
    ],
    
    'data': [
        # create a booking chart for the demo 
        'data/booking_chart.xml',
        
        # add the booking chart to the menu
        'menu/booking_chart.xml',
        
        # declare an init function to generate booking.resource from existing tasks
        'data/task_function.xml',
    ],
    
    'js': [],
    
    'css': [],
    
    'demo': [],
    
    'application': True,
    'installable': True,
    'active': False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
