# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class cocau_hientai_form(osv.osv_memory):
    _name = "cocau.hientai.form"
    _columns = {    
                'ten_ho_id': fields.many2one( 'chan.nuoi','Chọn hộ', required = True),
                'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)'),
                'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)'),
                'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)', ),
                'tu_ngay': fields.date('Từ ngày'),
                'den_ngay': fields.date('Đến ngày'),
                }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'cocau.hientai.form'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'cocau_hientai_report', 'datas': datas}
        
cocau_hientai_form()