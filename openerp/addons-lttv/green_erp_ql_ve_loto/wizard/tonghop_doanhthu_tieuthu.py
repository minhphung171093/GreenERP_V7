# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tonghop_doanhthu_tieuthu(osv.osv_memory):
    _name = "tonghop.doanhthu.tieuthu"
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(tonghop_doanhthu_tieuthu, self).default_get(cr, uid, fields, context=context)
        dai_ly_ids = self.pool.get('res.partner').search(cr, uid, [('dai_ly','=',True),('parent_id','=',False)])
        menh_gia_ids = self.pool.get('product.product').search(cr, uid, [('menh_gia','=',True)])
        res.update({
                    'dai_ly_ids': dai_ly_ids,
                    'menh_gia_ids': menh_gia_ids,
                    })
        return res
    
    _columns = {
        'dai_ly_ids': fields.many2many('res.partner','tonghop_doanhthu_tieuthu_partner_ref','doanhthu_tieuthu_id','partner_id','Đại lý',domain="[('dai_ly','=',True),('parent_id','=',False)]", required=True),
        'menh_gia_ids': fields.many2many('product.product','tonghop_doanhthu_tieuthu_product_ref','doanhthu_tieuthu_id','product_id','Mệnh giá',domain="[('menh_gia','=',True)]", required=True),
        'date': fields.date('Ngày', required=True),
    }
    
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tonghop.doanhthu.tieuthu'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tonghop_doanhthu_tieuthu_report', 'datas': datas}
        
tonghop_doanhthu_tieuthu()

