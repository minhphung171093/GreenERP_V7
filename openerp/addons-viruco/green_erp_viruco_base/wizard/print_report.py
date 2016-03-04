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


class theodoi_hopdong(osv.osv):
    _name = "theodoi.hopdong"    
     
    _columns = {
        'date_from':fields.date('Date From', required = True),
        'date_to':fields.date('Date To', required = True),
     }
        
    _defaults = {
        'date_from': lambda *a: time.strftime('%Y-%m-01'),
        'date_to': lambda *a: time.strftime('%Y-%m-%d'),        
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'theodoi.hopdong'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'theo_doi_hop_dong_report', 'datas': datas}
    
class draft_bl_print_report(osv.osv_memory):
    _name = "draft.bl.print.report"
    
    _columns = {    
                'draft_bl_id': fields.many2one('draft.bl', 'Draft bl'),
                'draft_bl_line_id': fields.many2one('draft.bl.line', 'Draft BL line'),
                }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'draft.bl.print.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'commercial_invoice_report',
            'datas': datas,
        }
draft_bl_print_report()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
