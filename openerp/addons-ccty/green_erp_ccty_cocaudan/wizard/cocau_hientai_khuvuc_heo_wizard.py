# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class cocau_hientai_khuvuc_heo_form(osv.osv_memory):
    _name = "cocau.hientai.khuvuc.heo.form"
    _columns = {    
                'ten_ho_id': fields.many2one( 'chan.nuoi','Chọn hộ'),
                'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)'),
                'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)'),
                'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)', ),
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
        datas['model'] = 'cocau.hientai.khuvuc.heo.form'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'cocau_hientai_khuvuc_heo_report', 'datas': datas}
        
cocau_hientai_khuvuc_heo_form()