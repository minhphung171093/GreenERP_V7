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


class theodoi_hopdong(osv.osv_memory):
    _name = "theodoi.hopdong"    
     
    _columns = {
        'date_from':fields.date('Date From', required = True),
        'date_to':fields.date('Date To', required = True),
     }
        
    _defaults = {
        'date_from': time.strftime('%Y-%m-01'),
        'date_to': time.strftime('%Y-%m-%d'),        
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'theodoi.hopdong'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'theo_doi_hop_dong_report', 'datas': datas}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
