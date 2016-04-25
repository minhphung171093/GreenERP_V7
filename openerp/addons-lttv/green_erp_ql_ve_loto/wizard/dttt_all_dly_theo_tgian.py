# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class dttt_all_dly_theo_tgian(osv.osv_memory):
    _name = "dttt.all.dly.theo.tgian"
    
    _columns = {
        'date': fields.date('Từ ngày', required=True),
        'date_to': fields.date('Đến ngày', required=True),
    }
    
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-01'),
        'date_to': lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10]
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'dttt.all.dly.theo.tgian'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'dttt_all_dly_theo_tgian_report', 'datas': datas}
        
dttt_all_dly_theo_tgian()

