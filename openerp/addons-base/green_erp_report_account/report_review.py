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
from openerp import SUPERUSER_ID

class report_account_in_out_tax_review(osv.osv):
    _name = "report.account.in.out.tax.review"

    _columns = {
        'name': fields.char('Name', size=1024),
        'nguoi_nop_thue': fields.char('Người nộp thuế', size=1024),
        'ms_thue': fields.char('Mã số thuế', size=1024),
    }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'report.account.in.out.tax.review'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tax_vat_input_review_xls', 'datas': datas}
    
report_account_in_out_tax_review()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
