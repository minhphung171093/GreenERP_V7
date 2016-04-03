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
        'tu_ngay': lambda *a: time.strftime('%Y-%m-01'),
        'den_ngay': lambda *a: time.strftime('%Y-%m-%d'),
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
            if self.uid != 1:
                if self.uid != 24:
                    sql ='''
                        select sp.name as so_phieuxuat,sp.ngay_gui, rp.name as ten_kh, rpu.name as tdv, rcs.name as tinh,   
                            sum(spp.sl_nhietke_conlai) as sl_nhietke_conlai,
                            case when sp.ngay_nhan is not null then 'Da nhan' else 'Chua nhan' end as bb_giaonhan
                        from stock_picking_packaging spp
                        left join stock_picking sp on sp.id = spp.picking_id
                        left join res_partner rp ON sp.partner_id = rp.id
                        left join res_users ru ON rp.user_id = ru.id
                        left join res_partner rpu ON ru.partner_id = rpu.id
                        left join res_country_state rcs ON rp.state_id = rcs.id
                        where sp.ngay_gui >= '%s' and (sp.ngay_nhan is null or sp.ngay_nhan <= '%s') and rp.user_id = %s
                    ''' %(tu_ngay, den_ngay, self.uid)
                    if partner_id:
                        sql+='''
                            and rp.id = %s 
                        '''%(partner_id[0])
                    if da_nhan:
                        sql+='''
                            and sp.ngay_nhan is not null
                        '''
                    if chua_nhan:
                        sql+='''
                            and sp.ngay_nhan is null
                        '''    
                    sql+='''
                         group by sp.name,sp.ngay_gui, rp.name,rpu.name,rcs.name,case when sp.ngay_nhan is not null then 'Da nhan' else 'Chua nhan' end
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
                                    'tdv':line['tdv'], 
                                    'tinh':line['tinh'], 
                                })
                else:
                    sql = '''
                        select id from res_partner where 
                            customer = 't' and 
                            street LIKE '%Q.Gò Vấp%' or street LIKE '%Q. Gò Vấp%' or street LIKE '%Quận Gò Vấp%' or
                            street LIKE '%Q.Tân Bình%' or street LIKE '%Q. Tân Bình%' or street LIKE '%Quận Tân Bình%' or
                            street LIKE '%Q1%' or street LIKE '%Q.1%' or street LIKE '%Quận 1%' or
                            street LIKE '%Q.Tân Phú%' or street LIKE '%Q. Tân Phú%' or street LIKE '%Quận Tân Phú%' or
                            street LIKE '%Q3%' or street LIKE '%Q.3%' or street LIKE '%Quận 3%' or
                            street LIKE '%Q10%' or street LIKE '%Q.10%' or street LIKE '%Quận 10%' or
                            street LIKE '%Q11%' or street LIKE '%Q.11%' or street LIKE '%Quận 11%' or
                            street LIKE '%Q4%' or street LIKE '%Q.4%' or street LIKE '%Quận 4%' or
                            street LIKE '%Q5%' or street LIKE '%Q.5%' or street LIKE '%Quận 5%' or
                            street LIKE '%Q6%' or street LIKE '%Q.6%' or street LIKE '%Quận 6%' or
                            street LIKE '%Q8%' or street LIKE '%Q.8%' or street LIKE '%Quận 8%' or
                            street LIKE '%Q.Bình Tân%' or street LIKE '%Q. Bình Tân%' or street LIKE '%Quận Bình Tân%' or
                            street LIKE '%Q7%' or street LIKE '%Q.7%' or street LIKE '%Quận 7%' or
                            street LIKE '%H.Bình Chánh%' or street LIKE '%H. Bình Chánh%' or street LIKE '%Huyện Bình Chánh%' or
                            street LIKE '%H.Nhà Bè%' or street LIKE '%H. Nhà Bè%' or street LIKE '%Huyện Nhà Bè%' or
                            street LIKE '%H.Cần Giờ%' or street LIKE '%H. Cần Giờ%' or street LIKE '%Huyện Cần Giờ%' or
                            
                            street2 LIKE '%Q.Gò Vấp%' or street2 LIKE '%Q. Gò Vấp%' or street2 LIKE '%Quận Gò Vấp%' or
                            street2 LIKE '%Q.Tân Bình%' or street2 LIKE '%Q. Tân Bình%' or street2 LIKE '%Quận Tân Bình%' or
                            street2 LIKE '%Q1%' or street2 LIKE '%Q.1%' or street2 LIKE '%Quận 1%' or 
                            street2 LIKE '%Q.Tân Phú%' or street2 LIKE '%Q. Tân Phú%' or street2 LIKE '%Quận Tân Phú%' or
                            street2 LIKE '%Q3%' or street2 LIKE '%Q.3%' or street2 LIKE '%Quận 3%' or
                            street2 LIKE '%Q10%' or street2 LIKE '%Q.10%' or street2 LIKE '%Quận 10%' or
                            street2 LIKE '%Q11%' or street2 LIKE '%Q.11%' or street2 LIKE '%Quận 11%' or
                            street2 LIKE '%Q4%' or street2 LIKE '%Q.4%' or street2 LIKE '%Quận 4%' or
                            street2 LIKE '%Q5%' or street2 LIKE '%Q.5%' or street2 LIKE '%Quận 5%' or
                            street2 LIKE '%Q6%' or street2 LIKE '%Q.6%' or street2 LIKE '%Quận 6%' or
                            street2 LIKE '%Q8%' or street2 LIKE '%Q.8%' or street2 LIKE '%Quận 8%' or
                            street2 LIKE '%Q.Bình Tân%' or street2 LIKE '%Q. Bình Tân%' or street2 LIKE '%Quận Bình Tân%' or
                            street2 LIKE '%Q7%' or street2 LIKE '%Q.7%' or street2 LIKE '%Quận 7%' or
                            street2 LIKE '%H.Bình Chánh%' or street2 LIKE '%H. Bình Chánh%' or street2 LIKE '%Huyện Bình Chánh%' or
                            street2 LIKE '%H.Nhà Bè%' or street2 LIKE '%H. Nhà Bè%' or street2 LIKE '%Huyện Nhà Bè%' or
                            street2 LIKE '%H.Cần Giờ%' or street2 LIKE '%H. Cần Giờ%' or street2 LIKE '%Huyện Cần Giờ%'
                    '''
                    self.cr.execute(sql)
                    thuy_ids = [row[0] for row in self.cr.fetchall()]
                    thuy_ids = str(thuy_ids).replace('[', '(')
                    thuy_ids = str(thuy_ids).replace(']', ')')
                    sql ='''
                        select sp.name as so_phieuxuat,sp.ngay_gui, rp.name as ten_kh, rpu.name as tdv, rcs.name as tinh,   
                            sum(spp.sl_nhietke_conlai) as sl_nhietke_conlai,
                            case when sp.ngay_nhan is not null then 'Da nhan' else 'Chua nhan' end as bb_giaonhan
                        from stock_picking_packaging spp
                        left join stock_picking sp on sp.id = spp.picking_id
                        left join stock_move sm on sm.picking_id = sp.id
                        left join product_product pp on sm.product_id = pp.id
                        left join product_template pt on pp.product_tmpl_id = pt.id
                        left join product_category pc on pt.categ_id = pc.id
                        left join res_partner rp ON sp.partner_id = rp.id
                        left join res_users ru ON rp.user_id = ru.id
                        left join res_partner rpu ON ru.partner_id = rpu.id
                        left join res_country_state rcs ON rp.state_id = rcs.id
                        where sp.ngay_gui >= '%s' and (sp.ngay_nhan is null or sp.ngay_nhan <= '%s') and rp.user_id = %s
                        and rp.id in %s and pc.code='VC'
                    ''' %(tu_ngay, den_ngay, self.uid, thuy_ids)
                    if partner_id:
                        sql+='''
                            and rp.id = %s 
                        '''%(partner_id[0])
                    if da_nhan:
                        sql+='''
                            and sp.ngay_nhan is not null
                        '''
                    if chua_nhan:
                        sql+='''
                            and sp.ngay_nhan is null
                        '''    
                    sql+='''
                         group by sp.name,sp.ngay_gui, rp.name,rpu.name,rcs.name,case when sp.ngay_nhan is not null then 'Da nhan' else 'Chua nhan' end
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
                                    'tdv':line['tdv'], 
                                    'tinh':line['tinh'], 
                                })
            
            else:
                sql ='''
                    select sp.name as so_phieuxuat,sp.ngay_gui, rp.name as ten_kh, rpu.name as tdv, rcs.name as tinh,   
                        sum(spp.sl_nhietke_conlai) as sl_nhietke_conlai,
                        case when sp.ngay_nhan is not null then 'Đã nhận' else 'Chưa nhận' end as bb_giaonhan
                    from stock_picking_packaging spp
                    left join stock_picking sp on sp.id = spp.picking_id
                    left join res_partner rp ON sp.partner_id = rp.id
                    left join res_users ru ON rp.user_id = ru.id
                    left join res_partner rpu ON ru.partner_id = rpu.id
                    left join res_country_state rcs ON rp.state_id = rcs.id
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
                                'tdv':line['tdv'], 
                                'tinh':line['tinh'], 
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