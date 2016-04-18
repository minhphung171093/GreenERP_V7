# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tonghop_chi_uyquyen_all(osv.osv_memory):
    _name = "tonghop.chi.uyquyen.all"
    
    _columns = {
        'date_from': fields.date('Ngày bắt đầu', required=True),
        'date_to': fields.date('Ngày kết thúc', required=True),
    }
    
    _defaults = {
        'date_from': time.strftime('%Y-%m-01'),
        'date_to': lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10]
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tonghop.chi.uyquyen.all'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tonghop_chi_uyquyen_all_report', 'datas': datas}
        
tonghop_chi_uyquyen_all()
