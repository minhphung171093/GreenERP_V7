# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class trathuong_theongay(osv.osv_memory):
    _name = "trathuong.theongay"
    
    _columns = {
        'date_from': fields.date('Ngày mở thưởng', required=True),
    }
    
    _defaults = {
        'date_from': time.strftime('%Y-%m-01'),
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'trathuong.theongay'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'trathuong_theongay_report', 'datas': datas}
        
trathuong_theongay()

