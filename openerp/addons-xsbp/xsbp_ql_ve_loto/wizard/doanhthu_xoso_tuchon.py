# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class doanhthu_xoso_tuchon(osv.osv_memory):
    _name = "doanhthu.xoso.tuchon"
    
    _columns = {
        'date': fields.date('Ngày', required=True),
        'giamsat_1': fields.char('Ông/Bà',SIZE=256),
        'giamsat_2': fields.char('Ông/Bà',SIZE=256),
        'giamsat_3': fields.char('Ông/Bà',SIZE=256),
        'ctyxs_1': fields.char('Ông/Bà',SIZE=256),
        'ctyxs_2': fields.char('Ông/Bà',SIZE=256),
        'ctyxs_3': fields.char('Ông/Bà',SIZE=256),
        'cv_giamsat_1': fields.char('Chức vụ',SIZE=256),
        'cv_giamsat_2': fields.char('Chức vụ',SIZE=256),
        'cv_giamsat_3': fields.char('Chức vụ',SIZE=256),
        'cv_ctyxs_1': fields.char('Chức vụ',SIZE=256),
        'cv_ctyxs_2': fields.char('Chức vụ',SIZE=256),
        'cv_ctyxs_3': fields.char('Chức vụ',SIZE=256),
    }
    
    _defaults = {
        'date': time.strftime('%Y-%m-%d'),
        'cv_giamsat_1': 'TUN HĐ GIÁM SÁT',
        'cv_giamsat_2': 'TUN HĐ GIÁM SÁT',
        'ctyxs_1': 'Nguyễn Đăng Khoa',
        'cv_ctyxs_1': 'Phó Giám Đốc Công ty',
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'doanhthu.xoso.tuchon'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'doanhthu_xoso_tuchon_report', 'datas': datas}
        
doanhthu_xoso_tuchon()

