# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class thu_thamgia_tuvan_dauthau(osv.osv_memory):
    _name = "thu.thamgia.tuvan.dauthau"
    _columns = {    
        'date_from': fields.date('Date From', required=True),
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'thu.thamgia.tuvan.dauthau'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_ids':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'thu_thamgia_tuvan_dauthau_report', 'datas': datas}
        
thu_thamgia_tuvan_dauthau()
