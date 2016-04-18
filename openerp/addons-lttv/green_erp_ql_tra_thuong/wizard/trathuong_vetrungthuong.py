# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class trathuong_vetrungthuong(osv.osv_memory):
    _name = "trathuong.vetrungthuong"
    
    _columns = {
        'date_from': fields.date('Từ Ngày', required=True),
        'date_to': fields.date('Đến Ngày', required=True),
        'menhgia_id': fields.many2one('product.product', 'Mệnh giá', required=True),
    }
    
    _defaults = {
        'date_from': time.strftime('%Y-%m-01'),
        'date_to': lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10]
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'trathuong.vetrungthuong'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'trathuong_vetrungthuong_report', 'datas': datas}
        
trathuong_vetrungthuong()
