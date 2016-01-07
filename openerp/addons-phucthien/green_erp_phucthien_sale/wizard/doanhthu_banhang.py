# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from openerp.osv import osv,fields
from openerp.tools.translate import _
from datetime import date
from dateutil.rrule import rrule, DAILY

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class doanhthu_banhang_review(osv.osv):
    _name = 'doanhthu.banhang.review'
    
    _columns = {
        'name': fields.char('BCDTBH', size=1024),
        'tu_ngay': fields.char('Từ ngày', size=1024),
        'den_ngay': fields.char('Đến ngày', size=1024),
        'doanhthu_banhang_review_line':fields.one2many('doanhthu.banhang.review.line','review_id','Chi tiết'),
    }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'doanhthu.banhang.review'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'doanhthu_banhang_review_xls', 'datas': datas}
    
doanhthu_banhang_review()

class doanhthu_banhang_review_line(osv.osv):
    _name = 'doanhthu.banhang.review.line'
    
    _columns = {
        'review_id': fields.many2one('doanhthu.banhang.review','Review',ondelete='cascade'),
        'ngay_hd': fields.char('Ngày hóa đơn', size=1024),
        'so_hd': fields.char('Số hóa đơn', size=1024),
        'ten_kh': fields.char('Tên khách hàng', size=1024),
        'dia_chi': fields.char('Địa chỉ', size=1024),
        'ten_sp': fields.char('Tên sản phẩm', size=1024),
        'hang_sx': fields.char('Hãng sản xuất', size=1024),
        'dvt': fields.char('Đơn vị tính', size=1024),
        'so_lo': fields.char('Số lô', size=1024),
        'hsd': fields.char('Hạn dùng',size=1024),
        'so_luong': fields.integer('Số lượng'),
        'gia_ban': fields.float('Gía bán'),
        'doanhthu_truocthue': fields.float('Doanh thu trước thuế'),
        'doanhthu_sauthue': fields.float('Doanh thu sau thuế'),
        'ti_le': fields.float('Tỉ lệ'),
    }
doanhthu_banhang_review_line()

class doanhthu_banhang(osv.osv_memory):
    _name = 'doanhthu.banhang'
    
    _columns = {
        'partner_ids': fields.many2many('res.partner','doanhthubanhang_partner_ref','dtbh_id','partner_id', 'Khách hàng'),
        'users_ids': fields.many2many('res.users','doanhthubanhang_users_ref','dtbh_id','users_id', 'Nhân viên bán hàng'),
        'product_ids': fields.many2many('product.product','doanhthubanhang_product_ref','dtbh_id','product_id', 'Sản phẩm'),
        'categ_ids': fields.many2many('product.category','doanhthubanhang_categ_ref','dtbh_id','categ_id', 'Nhóm sản phẩm'),
        'loc_ids': fields.many2many('stock.location','doanhthubanhang_location_ref','dtbh_id','loc_id', 'Kho hàng'),
        'nsx_ids': fields.many2many('manufacturer.product','doanhthubanhang_manufacturer_product_ref','dtbh_id','nsx_id', 'Hãng sản xuất'),
        'date_from': fields.date('Từ ngày',required=True),
        'date_to': fields.date('Đến ngày',required=True),
        'khu_vuc_ids': fields.many2many('kv.benh.vien','doanhthubanhang_khu_vuc_bv_ref','dtbh_id','khu_vuc_id', 'Khu vực'),
        'tinh_ids': fields.many2many('res.country.state','doanhthubanhang_country_state_ref','dtbh_id','state_id', 'Tỉnh'),
    }
    
    _defaults = {
        'date_from': time.strftime('%Y-%m-%d'),
        'date_to': time.strftime('%Y-%m-%d'),
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'doanhthu.banhang'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'doanhthu_banhang_report', 'datas': datas}
    
    def review_report(self, cr, uid, ids, context=None):
        def convert_date(o, date):
            if date:
                date = datetime.strptime(date, DATE_FORMAT)
                return date.strftime('%d/%m/%Y')

        def get_tile(o, amount):
            tong = get_tong(o,'dt_truocthue')
            if tong:
                return amount/tong
            return 0
         
        def get_tong(o, loai):
            tong = 0
            if loai=='so_luong':
                tong = get_tong_soluong(o)['tong']
            if loai=='dt_truocthue':
                tong = get_tong_dt_truocthue(o)['tong']
            if loai=='dt_sauthue':
                tong = get_tong_dt_sauthue(o)['tong']
            return tong
         
        def get_lines(o):
            mang_partner_ids = []
            mang_users_ids = []
            mang_product_ids = []
            mang_categ_ids = []
            mang_loc_ids = []
            mang_nsx_ids = []
            mang_khu_vuc_ids = []
            mang_tinh_ids = []
            
            date_from = o.date_from
            date_to = o.date_to
            
            partner_ids = o.partner_ids
            for partner_id in partner_ids:
                mang_partner_ids.append(partner_id.id)
                
            users_ids = o.users_ids
            for users_id in users_ids:
                mang_users_ids.append(users_id.id)
                
            product_ids = o.product_ids
            for product_id in product_ids:
                mang_product_ids.append(product_id.id)
                
            categ_ids = o.categ_ids
            for categ_id in categ_ids:
                mang_categ_ids.append(categ_id.id)
            
            loc_ids = o.loc_ids
            for loc_id in loc_ids:
                mang_loc_ids.append(loc_id.id)
            
            nsx_ids = o.nsx_ids
            for nsx_id in nsx_ids:
                mang_nsx_ids.append(nsx_id.id)
                
            khu_vuc_ids = o.khu_vuc_ids
            for khu_vuc_id in khu_vuc_ids:
                mang_khu_vuc_ids.append(khu_vuc_id.id)
                
            tinh_ids = o.tinh_ids
            for tinh_id in tinh_ids:
                mang_tinh_ids.append(tinh_id.id)
                
            sql = '''
                select ail.id as id,ai.partner_id as partner_id,ai.date_invoice as ngay_hd,ai.reference_number as so_hd,rp.internal_code as ma_kh,rp.name as ten_kh,pp.default_code as ma_sp,
                    pp.name_template as ten_sp,pu.name as dvt,spl.name as so_lo,spl.life_date as han_dung,ail.quantity as so_luong,ail.price_unit as gia_ban,
                    ail.price_unit*ail.quantity as dt_truocthue,at.amount_tax as tien_thue,(ail.price_unit*ail.quantity)+at.amount_tax as dt_sauthue,pt.standard_price as gia_von,
                    sl.name as loc_name,mp.name as nsx, rurp.name as nvbh
                    from account_invoice_line ail
                        left join account_invoice ai on ail.invoice_id=ai.id
                        left join res_partner rp on ail.partner_id=rp.id
                        left join res_users ru on rp.user_id = ru.id
                        left join res_partner rurp on ru.partner_id=rurp.id
                        left join product_product pp on ail.product_id=pp.id
                        left join product_template pt on pp.product_tmpl_id=pt.id
                        left join product_category pc on pt.categ_id=pc.id
                        left join product_uom pu on ail.uos_id=pu.id
                        left join stock_production_lot spl on ail.prodlot_id = spl.id
                        left join (
                                select ail.id,sum(at.amount*ail.price_unit*ail.quantity) as amount_tax
                                    from account_invoice_line ail
                                        left join account_invoice_line_tax ailt on ail.id=ailt.invoice_line_id
                                        left join account_tax at on ailt.tax_id=at.id
                                    group by ail.id
                            ) as at on ail.id=at.id
                        left join stock_move sm on sm.id=ail.source_id
                        left join stock_location sl on sl.id=sm.location_id
                        left join manufacturer_product mp on pp.manufacturer_product_id = mp.id
                        left join kv_benh_vien kv on kv.id=rp.kv_benh_vien
                        left join res_country_state rcs on rcs.id=rp.state_id
                    where ai.date_invoice between '%s' and '%s' and ai.state!='cancel' and ai.type='out_invoice' 
            '''%(date_from,date_to)
            if mang_partner_ids:
                mang_partner_ids = str(mang_partner_ids).replace('[', '(')
                mang_partner_ids = str(mang_partner_ids).replace(']', ')')
                sql+='''
                    and ai.partner_id in %s 
                '''%(mang_partner_ids)
            if mang_users_ids:
                mang_users_ids = str(mang_users_ids).replace('[', '(')
                mang_users_ids = str(mang_users_ids).replace(']', ')')
                sql+='''
                    and rp.user_id in %s 
                '''%(mang_users_ids)
            if mang_product_ids:
                mang_product_ids = str(mang_product_ids).replace('[', '(')
                mang_product_ids = str(mang_product_ids).replace(']', ')')
                sql+='''
                    and ail.product_id in %s 
                '''%(mang_product_ids)
            if mang_categ_ids:
                mang_categ_ids = str(mang_categ_ids).replace('[', '(')
                mang_categ_ids = str(mang_categ_ids).replace(']', ')')
                sql+='''
                    and pc.id in %s 
                '''%(mang_categ_ids)
            if mang_loc_ids:
                mang_loc_ids = str(mang_loc_ids).replace('[', '(')
                mang_loc_ids = str(mang_loc_ids).replace(']', ')')
                sql+='''
                    and sl.id in %s 
                '''%(mang_loc_ids)
            if mang_nsx_ids:
                mang_nsx_ids = str(mang_nsx_ids).replace('[', '(')
                mang_nsx_ids = str(mang_nsx_ids).replace(']', ')')
                sql+='''
                    and mp.id in %s 
                '''%(mang_nsx_ids)
            if mang_khu_vuc_ids:
                mang_khu_vuc_ids = str(mang_khu_vuc_ids).replace('[', '(')
                mang_khu_vuc_ids = str(mang_khu_vuc_ids).replace(']', ')')
                sql+='''
                    and kv.id in %s 
                '''%(mang_khu_vuc_ids)
            if mang_tinh_ids:
                mang_tinh_ids = str(mang_tinh_ids).replace('[', '(')
                mang_tinh_ids = str(mang_tinh_ids).replace(']', ')')
                sql+='''
                    and rcs.id in %s 
                '''%(mang_tinh_ids)
                 
            sql+='''
                 order by ai.date_invoice
            '''
            cr.execute(sql)
            return cr.dictfetchall()
         
        def get_tong_dt_truocthue(o):
            mang_partner_ids = []
            mang_users_ids = []
            mang_product_ids = []
            mang_categ_ids = []
            mang_loc_ids = []
            mang_nsx_ids = []
            mang_khu_vuc_ids = []
            mang_tinh_ids = []
            
            date_from = o.date_from
            date_to = o.date_to
            
            partner_ids = o.partner_ids
            for partner_id in partner_ids:
                mang_partner_ids.append(partner_id.id)
                
            users_ids = o.users_ids
            for users_id in users_ids:
                mang_users_ids.append(users_id.id)
                
            product_ids = o.product_ids
            for product_id in product_ids:
                mang_product_ids.append(product_id.id)
                
            categ_ids = o.categ_ids
            for categ_id in categ_ids:
                mang_categ_ids.append(categ_id.id)
            
            loc_ids = o.loc_ids
            for loc_id in loc_ids:
                mang_loc_ids.append(loc_id.id)
            
            nsx_ids = o.nsx_ids
            for nsx_id in nsx_ids:
                mang_nsx_ids.append(nsx_id.id)
                
            khu_vuc_ids = o.khu_vuc_ids
            for khu_vuc_id in khu_vuc_ids:
                mang_khu_vuc_ids.append(khu_vuc_id.id)
                
            tinh_ids = o.tinh_ids
            for tinh_id in tinh_ids:
                mang_tinh_ids.append(tinh_id.id)
                
            sql = '''
                select ail.price_unit*ail.quantity as dt_truocthue
                    from account_invoice_line ail
                        left join account_invoice ai on ail.invoice_id=ai.id
                        left join res_partner rp on ail.partner_id=rp.id
                        left join res_users ru on rp.user_id = ru.id
                        left join res_partner rurp on ru.partner_id=rurp.id
                        left join product_product pp on ail.product_id=pp.id
                        left join product_template pt on pp.product_tmpl_id=pt.id
                        left join product_category pc on pt.categ_id=pc.id
                        left join product_uom pu on ail.uos_id=pu.id
                        left join stock_production_lot spl on ail.prodlot_id = spl.id
                        left join (
                                select ail.id,sum(at.amount*ail.price_unit*ail.quantity) as amount_tax
                                    from account_invoice_line ail
                                        left join account_invoice_line_tax ailt on ail.id=ailt.invoice_line_id
                                        left join account_tax at on ailt.tax_id=at.id
                                    group by ail.id
                            ) as at on ail.id=at.id
                        left join stock_move sm on sm.id=ail.source_id
                        left join stock_location sl on sl.id=sm.location_id
                        left join manufacturer_product mp on pp.manufacturer_product_id = mp.id
                        left join kv_benh_vien kv on kv.id=rp.kv_benh_vien
                        left join res_country_state rcs on rcs.id=rp.state_id
                    where ai.date_invoice between '%s' and '%s' and ai.state!='cancel' and ai.type='out_invoice' 
            '''%(date_from,date_to)
            if mang_partner_ids:
                mang_partner_ids = str(mang_partner_ids).replace('[', '(')
                mang_partner_ids = str(mang_partner_ids).replace(']', ')')
                sql+='''
                    and ai.partner_id in %s 
                '''%(mang_partner_ids)
            if mang_users_ids:
                mang_users_ids = str(mang_users_ids).replace('[', '(')
                mang_users_ids = str(mang_users_ids).replace(']', ')')
                sql+='''
                    and rp.user_id in %s 
                '''%(mang_users_ids)
            if mang_product_ids:
                mang_product_ids = str(mang_product_ids).replace('[', '(')
                mang_product_ids = str(mang_product_ids).replace(']', ')')
                sql+='''
                    and ail.product_id in %s 
                '''%(mang_product_ids)
            if mang_categ_ids:
                mang_categ_ids = str(mang_categ_ids).replace('[', '(')
                mang_categ_ids = str(mang_categ_ids).replace(']', ')')
                sql+='''
                    and pc.id in %s 
                '''%(mang_categ_ids)
            if mang_loc_ids:
                mang_loc_ids = str(mang_loc_ids).replace('[', '(')
                mang_loc_ids = str(mang_loc_ids).replace(']', ')')
                sql+='''
                    and sl.id in %s 
                '''%(mang_loc_ids)
            if mang_nsx_ids:
                mang_nsx_ids = str(mang_nsx_ids).replace('[', '(')
                mang_nsx_ids = str(mang_nsx_ids).replace(']', ')')
                sql+='''
                    and mp.id in %s 
                '''%(mang_nsx_ids)
            if mang_khu_vuc_ids:
                mang_khu_vuc_ids = str(mang_khu_vuc_ids).replace('[', '(')
                mang_khu_vuc_ids = str(mang_khu_vuc_ids).replace(']', ')')
                sql+='''
                    and kv.id in %s 
                '''%(mang_khu_vuc_ids)
            if mang_tinh_ids:
                mang_tinh_ids = str(mang_tinh_ids).replace('[', '(')
                mang_tinh_ids = str(mang_tinh_ids).replace(']', ')')
                sql+='''
                    and rcs.id in %s 
                '''%(mang_tinh_ids)
                  
            sql+='''
                 order by ai.date_invoice
            '''
            s= 'select sum(v.dt_truocthue) as tong from ('+sql+')v'
            cr.execute(s)
            return cr.dictfetchone()
         
        def get_tong_soluong(o):
            mang_partner_ids = []
            mang_users_ids = []
            mang_product_ids = []
            mang_categ_ids = []
            mang_loc_ids = []
            mang_nsx_ids = []
            mang_khu_vuc_ids = []
            mang_tinh_ids = []
            
            date_from = o.date_from
            date_to = o.date_to
            
            partner_ids = o.partner_ids
            for partner_id in partner_ids:
                mang_partner_ids.append(partner_id.id)
                
            users_ids = o.users_ids
            for users_id in users_ids:
                mang_users_ids.append(users_id.id)
                
            product_ids = o.product_ids
            for product_id in product_ids:
                mang_product_ids.append(product_id.id)
                
            categ_ids = o.categ_ids
            for categ_id in categ_ids:
                mang_categ_ids.append(categ_id.id)
            
            loc_ids = o.loc_ids
            for loc_id in loc_ids:
                mang_loc_ids.append(loc_id.id)
            
            nsx_ids = o.nsx_ids
            for nsx_id in nsx_ids:
                mang_nsx_ids.append(nsx_id.id)
                
            khu_vuc_ids = o.khu_vuc_ids
            for khu_vuc_id in khu_vuc_ids:
                mang_khu_vuc_ids.append(khu_vuc_id.id)
                
            tinh_ids = o.tinh_ids
            for tinh_id in tinh_ids:
                mang_tinh_ids.append(tinh_id.id)
                
            sql = '''
                select ail.quantity as so_luong
                    from account_invoice_line ail
                        left join account_invoice ai on ail.invoice_id=ai.id
                        left join res_partner rp on ail.partner_id=rp.id
                        left join res_users ru on rp.user_id = ru.id
                        left join res_partner rurp on ru.partner_id=rurp.id
                        left join product_product pp on ail.product_id=pp.id
                        left join product_template pt on pp.product_tmpl_id=pt.id
                        left join product_category pc on pt.categ_id=pc.id
                        left join product_uom pu on ail.uos_id=pu.id
                        left join stock_production_lot spl on ail.prodlot_id = spl.id
                        left join (
                                select ail.id,sum(at.amount*ail.price_unit*ail.quantity) as amount_tax
                                    from account_invoice_line ail
                                        left join account_invoice_line_tax ailt on ail.id=ailt.invoice_line_id
                                        left join account_tax at on ailt.tax_id=at.id
                                    group by ail.id
                            ) as at on ail.id=at.id
                        left join stock_move sm on sm.id=ail.source_id
                        left join stock_location sl on sl.id=sm.location_id
                        left join manufacturer_product mp on pp.manufacturer_product_id = mp.id
                        left join kv_benh_vien kv on kv.id=rp.kv_benh_vien
                        left join res_country_state rcs on rcs.id=rp.state_id
                    where ai.date_invoice between '%s' and '%s' and ai.state!='cancel' and ai.type='out_invoice' 
            '''%(date_from,date_to)
            if mang_partner_ids:
                mang_partner_ids = str(mang_partner_ids).replace('[', '(')
                mang_partner_ids = str(mang_partner_ids).replace(']', ')')
                sql+='''
                    and ai.partner_id in %s 
                '''%(mang_partner_ids)
            if mang_users_ids:
                mang_users_ids = str(mang_users_ids).replace('[', '(')
                mang_users_ids = str(mang_users_ids).replace(']', ')')
                sql+='''
                    and rp.user_id in %s 
                '''%(mang_users_ids)
            if mang_product_ids:
                mang_product_ids = str(mang_product_ids).replace('[', '(')
                mang_product_ids = str(mang_product_ids).replace(']', ')')
                sql+='''
                    and ail.product_id in %s 
                '''%(mang_product_ids)
            if mang_categ_ids:
                mang_categ_ids = str(mang_categ_ids).replace('[', '(')
                mang_categ_ids = str(mang_categ_ids).replace(']', ')')
                sql+='''
                    and pc.id in %s 
                '''%(mang_categ_ids)
            if mang_loc_ids:
                mang_loc_ids = str(mang_loc_ids).replace('[', '(')
                mang_loc_ids = str(mang_loc_ids).replace(']', ')')
                sql+='''
                    and sl.id in %s 
                '''%(mang_loc_ids)
            if mang_nsx_ids:
                mang_nsx_ids = str(mang_nsx_ids).replace('[', '(')
                mang_nsx_ids = str(mang_nsx_ids).replace(']', ')')
                sql+='''
                    and mp.id in %s 
                '''%(mang_nsx_ids)
            if mang_khu_vuc_ids:
                mang_khu_vuc_ids = str(mang_khu_vuc_ids).replace('[', '(')
                mang_khu_vuc_ids = str(mang_khu_vuc_ids).replace(']', ')')
                sql+='''
                    and kv.id in %s 
                '''%(mang_khu_vuc_ids)
            if mang_tinh_ids:
                mang_tinh_ids = str(mang_tinh_ids).replace('[', '(')
                mang_tinh_ids = str(mang_tinh_ids).replace(']', ')')
                sql+='''
                    and rcs.id in %s 
                '''%(mang_tinh_ids)
                 
            sql+='''
                 order by ai.date_invoice
            '''
            s= 'select sum(v.so_luong) as tong from ('+sql+')v'
            cr.execute(s)
            return cr.dictfetchone()
         
        def get_tong_dt_sauthue(o):
            mang_partner_ids = []
            mang_users_ids = []
            mang_product_ids = []
            mang_categ_ids = []
            mang_loc_ids = []
            mang_nsx_ids = []
            mang_khu_vuc_ids = []
            mang_tinh_ids = []
            
            date_from = o.date_from
            date_to = o.date_to
            
            partner_ids = o.partner_ids
            for partner_id in partner_ids:
                mang_partner_ids.append(partner_id.id)
                
            users_ids = o.users_ids
            for users_id in users_ids:
                mang_users_ids.append(users_id.id)
                
            product_ids = o.product_ids
            for product_id in product_ids:
                mang_product_ids.append(product_id.id)
                
            categ_ids = o.categ_ids
            for categ_id in categ_ids:
                mang_categ_ids.append(categ_id.id)
            
            loc_ids = o.loc_ids
            for loc_id in loc_ids:
                mang_loc_ids.append(loc_id.id)
            
            nsx_ids = o.nsx_ids
            for nsx_id in nsx_ids:
                mang_nsx_ids.append(nsx_id.id)
                
            khu_vuc_ids = o.khu_vuc_ids
            for khu_vuc_id in khu_vuc_ids:
                mang_khu_vuc_ids.append(khu_vuc_id.id)
                
            tinh_ids = o.tinh_ids
            for tinh_id in tinh_ids:
                mang_tinh_ids.append(tinh_id.id)
                
            sql = '''
                select (ail.price_unit*ail.quantity)+at.amount_tax as dt_sauthue
                    from account_invoice_line ail
                        left join account_invoice ai on ail.invoice_id=ai.id
                        left join res_partner rp on ail.partner_id=rp.id
                        left join res_users ru on rp.user_id = ru.id
                        left join res_partner rurp on ru.partner_id=rurp.id
                        left join product_product pp on ail.product_id=pp.id
                        left join product_template pt on pp.product_tmpl_id=pt.id
                        left join product_category pc on pt.categ_id=pc.id
                        left join product_uom pu on ail.uos_id=pu.id
                        left join stock_production_lot spl on ail.prodlot_id = spl.id
                        left join (
                                select ail.id,sum(at.amount*ail.price_unit*ail.quantity) as amount_tax
                                    from account_invoice_line ail
                                        left join account_invoice_line_tax ailt on ail.id=ailt.invoice_line_id
                                        left join account_tax at on ailt.tax_id=at.id
                                    group by ail.id
                            ) as at on ail.id=at.id
                        left join stock_move sm on sm.id=ail.source_id
                        left join stock_location sl on sl.id=sm.location_id
                        left join manufacturer_product mp on pp.manufacturer_product_id = mp.id
                        left join kv_benh_vien kv on kv.id=rp.kv_benh_vien
                        left join res_country_state rcs on rcs.id=rp.state_id
                    where ai.date_invoice between '%s' and '%s' and ai.state!='cancel' and ai.type='out_invoice' 
            '''%(date_from,date_to)
            if mang_partner_ids:
                mang_partner_ids = str(mang_partner_ids).replace('[', '(')
                mang_partner_ids = str(mang_partner_ids).replace(']', ')')
                sql+='''
                    and ai.partner_id in %s 
                '''%(mang_partner_ids)
            if mang_users_ids:
                mang_users_ids = str(mang_users_ids).replace('[', '(')
                mang_users_ids = str(mang_users_ids).replace(']', ')')
                sql+='''
                    and rp.user_id in %s 
                '''%(mang_users_ids)
            if mang_product_ids:
                mang_product_ids = str(mang_product_ids).replace('[', '(')
                mang_product_ids = str(mang_product_ids).replace(']', ')')
                sql+='''
                    and ail.product_id in %s 
                '''%(mang_product_ids)
            if mang_categ_ids:
                mang_categ_ids = str(mang_categ_ids).replace('[', '(')
                mang_categ_ids = str(mang_categ_ids).replace(']', ')')
                sql+='''
                    and pc.id in %s 
                '''%(mang_categ_ids)
            if mang_loc_ids:
                mang_loc_ids = str(mang_loc_ids).replace('[', '(')
                mang_loc_ids = str(mang_loc_ids).replace(']', ')')
                sql+='''
                    and sl.id in %s 
                '''%(mang_loc_ids)
            if mang_nsx_ids:
                mang_nsx_ids = str(mang_nsx_ids).replace('[', '(')
                mang_nsx_ids = str(mang_nsx_ids).replace(']', ')')
                sql+='''
                    and mp.id in %s 
                '''%(mang_nsx_ids)
            if mang_khu_vuc_ids:
                mang_khu_vuc_ids = str(mang_khu_vuc_ids).replace('[', '(')
                mang_khu_vuc_ids = str(mang_khu_vuc_ids).replace(']', ')')
                sql+='''
                    and kv.id in %s 
                '''%(mang_khu_vuc_ids)
            if mang_tinh_ids:
                mang_tinh_ids = str(mang_tinh_ids).replace('[', '(')
                mang_tinh_ids = str(mang_tinh_ids).replace(']', ')')
                sql+='''
                    and rcs.id in %s 
                '''%(mang_tinh_ids)
                 
            sql+='''
                 order by ai.date_invoice
            '''
            s= 'select sum(v.dt_sauthue) as tong from ('+sql+')v'
            cr.execute(s)
            return cr.dictfetchone()
         
        def display_address(o, partner_id):
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            address = partner.street and partner.street + ' , ' or ''
            address += partner.street2 and partner.street2 + ' , ' or ''
            address += partner.city and partner.city.name + ' , ' or ''
            if address:
                address = address[:-3]
            return address
        
        def display_name_partner(o, partner_id):
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            name = partner.name and partner.name or ''
            return name
#         
#         def get_kho(self,invoice_line_id):
#             sql = '''
#                 select sl.name 
#                     from stock_location sl
#                         left join stock_move sm on sm.location_id = sl.id
#                         left join account_invoice_line ail on sm.id=ail.source_id
#                     where ail.id=%s
#             '''%(invoice_line_id)
#             self.cr.execute(sql)
#             name = self.cr.fetchone()
#             return name and name[0] or ''

                
        report_obj = self.pool.get('doanhthu.banhang.review')
        report = self.browse(cr, uid, ids[0])
        mang = []
        for line in get_lines(report):
            mang.append((0,0,{
                'ngay_hd': convert_date(report,line['ngay_hd']),
                'so_hd': line['so_hd'],
                'ten_kh':display_name_partner(report,line['partner_id']),
                'dia_chi': display_address(report,line['partner_id']),
                'ten_sp': line['ten_sp'],
                'hang_sx':line['nsx'],
                'dvt':line['dvt'],
                'so_lo':line['so_lo'],
                'hsd': line['han_dung'] and convert_date(report,line['han_dung'][:10]) or '',
                'so_luong':line['so_luong'],
                'gia_ban':line['gia_ban'],   
                'doanhthu_truocthue': line['dt_truocthue'], 
                'doanhthu_sauthue': line['dt_sauthue'], 
                'ti_le': get_tile(report,line['dt_truocthue']), 
                }))
            
        mang.append((0,0,{
                'hsd': 'TỔNG',
                'so_luong':get_tong(report,'so_luong'),
                'doanhthu_truocthue': get_tong(report,'dt_truocthue'), 
                'doanhthu_sauthue': get_tong(report,'dt_sauthue'), 
                }))
        
        vals = {
            'name': 'Báo cáo doanh thu bán hàng',
            'tu_ngay': convert_date(report,report.date_from),
            'den_ngay': convert_date(report,report.date_to),
            'doanhthu_banhang_review_line': mang,
        }
        report_id = report_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_phucthien_sale', 'report_doanhthu_banhang_review')
        return {
                    'name': 'Báo cáo doanh thu bán hàng',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'doanhthu.banhang.review',
                    'view_id': res and res[1] or False,
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': report_id,
                }       
    
doanhthu_banhang()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

