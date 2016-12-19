# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class pr_pending_report(osv.osv_memory):
    _name = "pr.pending.report"
    
    _columns = {
        'tu_ngay':fields.date('From Date'),
        'den_ngay':fields.date('To Date'),
    }
    
    _defaults = {
        'tu_ngay': lambda *a: time.strftime('%Y-%m-01'),
        'den_ngay': lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10]
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        
        if this.den_ngay<this.tu_ngay:
            raise osv.except_osv(_('Warning!'), _('"To Date" must be greater than or equal "From Date"!'))
        
        sql = '''
            select id
                from bdf_purchase
                where state not in ('reject','cancel','procurement')
                    and COALESCE(date_from, date(timezone('UTC',create_date))) between '%s' and '%s'
        '''%(this.tu_ngay,this.den_ngay)
        cr.execute(sql)
        pr_ids = [r[0] for r in cr.fetchall()]
        
        datas = {'ids': pr_ids}
        datas['model'] = 'bdf.purchase'
        datas['form'] = pr_ids and self.pool.get('bdf.purchase').read(cr, uid, pr_ids)[0] or {}
        datas['form'].update({'active_id':pr_ids and pr_ids[0] or False,'active_ids':pr_ids})
        datas['context'] = {'active_id':pr_ids and pr_ids[0] or False,'active_ids':pr_ids}
        return {'type': 'ir.actions.report.xml', 'report_name': 'list_purchase_request_report', 'datas': datas, 'context': {'active_id':pr_ids and pr_ids[0] or False,'active_ids':pr_ids}}
        
pr_pending_report()

