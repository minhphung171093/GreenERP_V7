# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class danhsach_vesinh_thangmay(osv.osv_memory):
    _name = "danhsach.vesinh.thangmay"
    _columns = {
        'tu_ngay':fields.date('Từ ngày', required=True),
        'den_ngay':fields.date('Đến ngày',required=True),
        
    }
    _defaults = {
        'tu_ngay': lambda *a: time.strftime('%Y-%m-01'),
        'den_ngay': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
             
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'danhsach.vesinh.thangmay'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_vesinh_thangmay', 'datas': datas}
        
danhsach_vesinh_thangmay()