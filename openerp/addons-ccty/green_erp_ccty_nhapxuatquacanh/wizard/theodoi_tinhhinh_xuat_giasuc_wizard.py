# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class theodoi_tinhhinh_xuat_giasuc_form(osv.osv_memory):
    _name = "theodoi.tinhhinh.xuat.giasuc.form"
    _columns = {    
                'ten_ho_id': fields.many2one( 'chan.nuoi','Chọn hộ', required = True),
                'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)'),
                'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)'),
                'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)', ),  
                'tu_ngay': fields.date('Từ ngày'),
                'den_ngay': fields.date('Đến ngày'),
                }
    _defaults = {
        'tu_ngay': time.strftime('%Y-%m-01'),
        'den_ngay': lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10]
        }
    def onchange_quan_huyen(self, cr, uid, ids, context=None):
        vals = {}
        vals = {'phuong_xa_id':False}
        return {'value': vals}
    def onchange_phuong_xa(self, cr, uid, ids, context=None):
        vals = {}
        vals = {'khu_pho_id':False}
        return {'value': vals}
    def onchange_khu_pho(self, cr, uid, ids, context=None):
        vals = {}
        vals = {'ho_chan_nuoi_id':False}
        return {'value': vals}
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'theodoi.tinhhinh.xuat.giasuc.form'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'theodoi_tinhhinh_xuat_giasuc_report', 'datas': datas}
        
theodoi_tinhhinh_xuat_giasuc_form()