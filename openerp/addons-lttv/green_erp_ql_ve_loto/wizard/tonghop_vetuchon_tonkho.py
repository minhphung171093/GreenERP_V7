# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tonghop_vetuchon_tonkho(osv.osv_memory):
    _name = "tonghop.vetuchon.tonkho"
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(tonghop_vetuchon_tonkho, self).default_get(cr, uid, fields, context=context)
        menh_gia_ids = self.pool.get('product.product').search(cr, uid, [('menh_gia','=',True)])
        res.update({
                    'menh_gia_ids': menh_gia_ids,
                    })
        return res
    
    _columns = {
        'menh_gia_ids': fields.many2many('product.product','vetonkho_product_ref','vetonkho_id','product_id','Mệnh giá',domain="[('menh_gia','=',True)]", required=True),
        'date': fields.date('Ngày'),
        'date_from': fields.date('Ngày Bắt đầu', required=True),
        'date_to': fields.date('Ngày kết thúc', required=True),
        'ky_ve_id': fields.many2one('ky.ve','Kỳ vé'),
    }
    
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'date_from': lambda *a: time.strftime('%Y-%m-01'),
        'date_to': lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10]
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tonghop.vetuchon.tonkho'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tonghop_vetuchon_tonkho_report', 'datas': datas}
        
tonghop_vetuchon_tonkho()

