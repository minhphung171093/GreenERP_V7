# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class tinhhinh_xuat_giasuc_form(osv.osv_memory):
    _name = "tinhhinh.xuat.giasuc.form"
    _columns = {    
                'ten_ho_id': fields.many2one( 'chan.nuoi','Chọn hộ', required = True),
                'tu_ngay': fields.date('Từ ngày'),
                'den_ngay': fields.date('Đến ngày'),
                }
    _defaults = {
        'tu_ngay': time.strftime('%Y-%m-01'),
        'den_ngay': lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10]
        }
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tinhhinh.xuat.giasuc.form'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tinhhinh_xuat_giasuc_report', 'datas': datas}
        
tinhhinh_xuat_giasuc_form()