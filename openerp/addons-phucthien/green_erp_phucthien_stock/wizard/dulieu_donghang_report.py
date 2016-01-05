# -*- coding: utf-8 -*-
import time
from datetime import datetime
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv,fields
from openerp.tools.translate import _
import random
# from datetime import date
from dateutil.rrule import rrule, DAILY

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
class dulieu_donghang_report(osv.osv_memory):
    _name = "dulieu.donghang.report"
    _columns = {
        'partner_id': fields.many2one('res.partner', string='Khách hàng',domain="[('customer','=',True)]"),
        'da_nhan':fields.boolean('Đã nhận'),
        'chua_nhan':fields.boolean('Chưa nhận'),
        'tu_ngay':fields.date('Từ ngày', required=True),
        'den_ngay':fields.date('Đến ngày',required=True),
        
    }
    _defaults = {
        'tu_ngay': time.strftime('%Y-%m-%d'),
        'den_ngay': time.strftime('%Y-%m-%d'),
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
             
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'dulieu.donghang.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'dulieu_donghang_report', 'datas': datas}

    def review_report_in(self, cr, uid, ids, context=None): 
        report_obj = self.pool.get('dulieu.donghang.review')
        report = self.browse(cr, uid, ids[0])   
        self.tu_ngay = False
        self.den_ngay = False
        self.cr = cr
        self.uid = uid
        def convert_date(o, date):
            if date:
                date = datetime.strptime(date, DATE_FORMAT)
                return date.strftime('%d/%m/%Y')      
        def get_data(o):
            res = []
            partner_id = report.partner_id.id
            da_nhan = report.da_nhan
            chua_nhan = report.chua_nhan
            tu_ngay = report.tu_ngay
            den_ngay = report.den_ngay
            sql ='''
                select sp.name as so_phieuxuat,sp.ngay_gui, rp.name as ten_kh,    
                    sum(spp.sl_nhietke_conlai) as sl_nhietke_conlai,
                    case when sp.ngay_nhan is not null then 'Đã nhận' else 'Chưa nhận' end as bb_giaonhan
                from stock_picking_packaging spp
                left join stock_picking sp on sp.id = spp.picking_id
                left join res_partner rp ON sp.partner_id = rp.id
                where sp.ngay_gui >= '%s' and (sp.ngay_nhan is null or sp.ngay_nhan <= '%s')
            ''' %(tu_ngay, den_ngay)
            if partner_id:
                sql+='''
                    and rp.id = %s 
                '''%(partner_id)
            if da_nhan:
                sql+='''
                    and sp.ngay_nhan is not null
                '''
            if chua_nhan:
                sql+='''
                    and sp.ngay_nhan is null
                '''    
            sql+='''
                 group by sp.name,sp.ngay_gui, rp.name,case when sp.ngay_nhan is not null then 'Đã nhận' else 'Chưa nhận' end
                order by sp.name
                '''
            self.cr.execute(sql)
            for line in self.cr.dictfetchall():
                res.append({
                            'so_phieuxuat': line['so_phieuxuat'],
                            'ten_kh':line['ten_kh'],
                            'ngay_gui':convert_date(o,line['ngay_gui']),
                            'sl_nhietke_conlai':line['sl_nhietke_conlai'],
                            'bb_giaonhan':line['bb_giaonhan'],
                        })
            return res
        def get_info(o):
            mang=[]
            dem = 0
            for line in get_data(o):
                dem = dem + 1
                mang.append((0,0,{
                        'stt':dem,
                        'so_phieuxuat': line['so_phieuxuat'] or '',
                        'ngay': line['ngay_gui'] or '',
                        'khach_hang':line['ten_kh'] or '',
                        'sl_nhietke':line['sl_nhietke_conlai'] or '',
                        'bb_giaonhan':line['bb_giaonhan'] or '',
                                 }))
            return mang 
        
        vals = {
            'date_from_title': 'Từ ngày',
            'date_to_title': 'Đến ngày',
            'tu_ngay':report.tu_ngay,
            'den_ngay':report.den_ngay,
            'dulieu_donghang_review_line':get_info(report),
        }        
        report_id = report_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_phucthien_stock', 'dulieu_donghang_review')
        return {
                    'name': 'Dữ Liệu Đóng Hàng',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'dulieu.donghang.review',
                    'domain': [],
                    'view_id': res and res[1] or False,
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': report_id,
                }        
        
dulieu_donghang_report()