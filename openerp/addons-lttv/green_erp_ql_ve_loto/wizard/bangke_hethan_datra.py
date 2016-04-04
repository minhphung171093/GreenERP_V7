# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class bangke_hethan_datra(osv.osv_memory):
    _name = "bangke.hethan.datra"
    
    _columns = {
        'product_id': fields.many2one('product.product','Mệnh giá',domain="[('menh_gia','=',True)]",required=True),
        'date': fields.date('Ngày mở thưởng', required=True),
    }
    
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        trungthuong = self.browse(cr, uid, ids[0])
        ketqua_ids = self.pool.get('ketqua.xoso').search(cr ,uid, [('name','=',trungthuong.date),('state','=','validate')])
        if not ketqua_ids:
            raise osv.except_osv(_('Cảnh báo!'),_('Chưa có kết quả xổ số ngày %s!')%(trungthuong.date))
            
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'bangke.hethan.datra'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'bangke_hethan_datra_report', 'datas': datas}
        
bangke_hethan_datra()

