# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class thtt_theo_tgian_all_dly(osv.osv_memory):
    _name = "thtt.theo.tgian.all.dly"
    
    _columns = {
        'date': fields.date('Ngày', required=True),
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
        datas['model'] = 'thtt.theo.tgian.all.dly'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'thtt_theo_tgian_all_dly_report', 'datas': datas}
        
thtt_theo_tgian_all_dly()

