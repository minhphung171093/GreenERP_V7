# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tonghop_trungthuong(osv.osv_memory):
    _name = "tonghop.trungthuong"
    
    _columns = {
        'date': fields.date('Ngày', required=True),
        'ddphongve_1': fields.char('Ông/Bà',SIZE=256),
        'ddphongve_2': fields.char('Ông/Bà',SIZE=256),
        'ddphong_trathuong_1': fields.char('Ông/Bà',SIZE=256),
        'ddphong_trathuong_2': fields.char('Ông/Bà',SIZE=256),
        'cv_ddphongve_1': fields.char('Chức vụ',SIZE=256),
        'cv_ddphongve_2': fields.char('Chức vụ',SIZE=256),
        'cv_ddphong_trathuong_1': fields.char('Chức vụ',SIZE=256),
        'cv_ddphong_trathuong_2': fields.char('Chức vụ',SIZE=256),

    }
    
    _defaults = {
        'date': time.strftime('%Y-%m-%d'),
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        trungthuong = self.browse(cr, uid, ids[0])
        ketqua_ids = self.pool.get('ketqua.xoso').search(cr ,uid, [('name','=',trungthuong.date),('state','=','validate')])
        if not ketqua_ids:
            raise osv.except_osv(_('Cảnh báo!'),_('Chưa có kết quả xổ số ngày %s!')%(trungthuong.date))
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tonghop.trungthuong'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tonghop_trungthuong_report', 'datas': datas}
        
tonghop_trungthuong()

