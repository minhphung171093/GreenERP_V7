# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class chitiet_trathuong_ngay(osv.osv_memory):
    _name = "chitiet.trathuong.ngay"
    
    _columns = {
        'product_id': fields.many2one('product.product','Mệnh giá',domain="[('menh_gia','=',True)]",required=True),
        'date': fields.date('Ngày trả thưởng', required=True),
    }
    
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'chitiet.trathuong.ngay'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'chitiet_trathuong_ngay_report', 'datas': datas}
        
chitiet_trathuong_ngay()

