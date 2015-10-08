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


class bang_ke_doanh_thu(osv.osv_memory):
    _name = "bang.ke.doanh.thu"    
    
    _columns = {
        'tu_ngay': fields.date('Từ ngày', required = True),
        'den_ngay': fields.date('Đến ngày', required = True),
     }
    def print_report(self, cr, uid, ids, context=None): 
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'bang.ke.doanh.thu'
        datas['form'] = self.read(cr, uid, ids)[0]        
        return {'type': 'ir.actions.report.xml', 'report_name': 'bang_ke_doanh_thu_report' , 'datas': datas}
bang_ke_doanh_thu()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
