# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class theodoi_tinhhinh_xuly_giasuc_form(osv.osv_memory):
    _name = "theodoi.tinhhinh.xuly.giasuc.form"
    _columns = {    
                'ten_ho_id': fields.many2one('chan.nuoi','Chọn hộ', required = True),
                'tu_ngay': fields.date('Từ ngày'),
                'den_ngay': fields.date('Đến ngày'),
                }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'theodoi.tinhhinh.xuly.giasuc.form'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'theodoi_tinhhinh_xuly_giasuc_report', 'datas': datas}
        
theodoi_tinhhinh_xuly_giasuc_form()