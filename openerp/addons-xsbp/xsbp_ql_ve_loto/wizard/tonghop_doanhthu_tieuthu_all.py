# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tonghop_doanhthu_tieuthu_all(osv.osv_memory):
    _name = "tonghop.doanhthu.tieuthu.all"
    
    _columns = {
        'date': fields.date('Ngày', required=True),
    }
    
    _defaults = {
        'date': time.strftime('%Y-%m-%d'),
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tonghop.doanhthu.tieuthu.all'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tonghop_doanhthu_tieuthu_all_report', 'datas': datas}
        
tonghop_doanhthu_tieuthu_all()

