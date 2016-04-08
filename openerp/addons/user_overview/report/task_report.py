# -*- coding: utf-8 -*-
##############################################################################
#
#    HLVSolution, Open Source Management Solution
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        
        self.localcontext.update({
             'get_task_line':self.get_task_line,
        })

    def get_task_line(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        task_obj = self.pool.get('project.task')
        sql = '''
           select id from project_task where date_start::timestamp::date between '%s' and '%s'
        '''%(date_from,date_to)
        self.cr.execute(sql)
        task_ids = [row[0] for row in self.cr.fetchall()]
        return task_obj.browse(self.cr,self.uid, task_ids)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
