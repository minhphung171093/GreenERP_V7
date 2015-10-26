# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

import time
from datetime import datetime
from osv import fields, osv
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import decimal_precision as dp
from tools.translate import _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class bang_ke_doanh_thu(osv.osv_memory):
    _name = "bang.ke.doanh.thu"    
    
    _columns = {
        'tu_ngay': fields.date('Từ ngày', required = True),
        'den_ngay': fields.date('Đến ngày', required = True),
     }
    _defaults = {
        'tu_ngay': time.strftime('%Y-%m-01'),
        'den_ngay': lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10],         
                 }
    def print_report(self, cr, uid, ids, context=None): 
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'bang.ke.doanh.thu'
        datas['form'] = self.read(cr, uid, ids)[0]        
        return {'type': 'ir.actions.report.xml', 'report_name': 'bang_ke_doanh_thu_report' , 'datas': datas}
bang_ke_doanh_thu()

class bang_ke_doanh_thu_theo_mat_hang(osv.osv_memory):
    _name = "bang.ke.doanh.thu.theo.mat.hang"    
    
    _columns = {
        'tu_ngay': fields.date('Từ ngày', required = True),
        'den_ngay': fields.date('Đến ngày', required = True),
     }
    _defaults = {
        'tu_ngay': time.strftime('%Y-%m-01'),
        'den_ngay': lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10],         
                 }
    def print_report(self, cr, uid, ids, context=None): 
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'bang.ke.doanh.thu.theo.mat.hang'
        datas['form'] = self.read(cr, uid, ids)[0]        
        return {'type': 'ir.actions.report.xml', 'report_name': 'bang_ke_doanh_thu_theo_mat_hang_report' , 'datas': datas}
bang_ke_doanh_thu_theo_mat_hang()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
