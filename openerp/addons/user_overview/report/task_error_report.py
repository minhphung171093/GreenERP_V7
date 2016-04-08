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
             'get_error_col':self.get_error_col,
             'get_error_line':self.get_error_line,
             'get_error_cell':self.get_error_cell,
        })
    
    def get_error_col(self):
        res = ['STT','User','Leader','Project','File name']
        error_obj = self.pool.get('error.reporting')
        error_ids = error_obj.search(self.cr, self.uid, [])
        for error in error_obj.browse(self.cr, self.uid, error_ids):
            res.append(error.name)
        return res

    def get_error_line(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        task_obj = self.pool.get('project.task')
        sql = '''
            select id from project_task where date_end::timestamp::date between '%s' and '%s'
                and stage_id in (select id from project_task_type where state='done')
        '''%(date_from,date_to)
        self.cr.execute(sql)
        task_ids = [row[0] for row in self.cr.fetchall()]
        return task_ids
    
    def get_error_cell(self,sequence,error,line):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        task = self.pool.get('project.task').browse(self.cr, self.uid, line)
        if error=='STT':
            cell = sequence+1
        elif error=='User':
            cell = task.user_id.name
        elif error=='Leader':
            cell = task.project_id.user_id.name
        elif error=='Project':
            cell = task.project_id.name
        elif error=='File name':
            cell = task.name
        else:
            temp = 0
            for e in task.error_ids:
                if e.error_id and e.error_id.name==error and e.date>date_from and e.date<date_to:
                    temp+=1
            cell = temp
        return cell
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
