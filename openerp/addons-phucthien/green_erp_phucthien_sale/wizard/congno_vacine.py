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

class congno_vacine(osv.osv_memory):
    _name = 'congno.vacine'
     
    _columns = {
        'date_from': fields.date('Từ ngày',required=True),
        'date_to': fields.date('Đến ngày',required=True),
#         'user_id': fields.many2many('res.users', string='Users', readonly=True),
        'user_id': fields.many2many('res.users', 'congno_user_ref', 'congno_id', 'user_id', 'Nhân Viên Bán Hàng'),  
    }
     
    _defaults = {
        'date_from': lambda *a: time.strftime('%Y-%m-01'),
        'date_to': lambda *a: time.strftime('%Y-%m-%d'),
        'user_id': lambda self,cr, uid, ctx: [(6,0,[uid])],
        
    }
     
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'congno.vacine' 
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'congno_vacine_report', 'datas': datas}
    def review_report_in(self, cr, uid, ids, context=None): 
        report_obj = self.pool.get('congno.vacine.review')
        report = self.browse(cr, uid, ids[0])   
        self.date_from = False
        self.date_to = False
        self.cr = cr
        self.uid = uid
        self.tong_tien = 0
        self.tong_exim = 0
        self.tong_acb = 0
        self.tong_agr = 0
        self.tong_ck = 0
        def convert_date(o, date):
            if date:
                date = datetime.strptime(date, DATE_FORMAT)
                if date:
                    return date.strftime('%d/%m/%Y')    
                else:
                    date = datetime.strptime(date, DATE_FORMAT)  
        def display_address(o, partner_id):
            partner = self.pool.get('res.partner').browse(self.cr, self.uid, partner_id)
            address = partner.street and partner.street + ' , ' or ''
            address += partner.street2 and partner.street2 + ' , ' or ''
            address += partner.city and partner.city.name + ' , ' or ''
            if address:
                address = address[:-3]
            return address       
        def get_lines(o):
            user_ids = [r.id for r in o.user_id]
            invoice_obj = self.pool.get('account.invoice') 
            period_obj = self.pool.get('account.period')
            date_from = o.date_from   
            date_to =  o.date_to
            vc_cate_ids = self.pool.get('product.category').search(self.cr,self.uid,[('code','=','VC')])
            vc_cate_ids = self.pool.get('product.category').search(self.cr, self.uid, [('parent_id','child_of',vc_cate_ids)])
            vc_cate_ids = str(vc_cate_ids).replace('[', '(')
            vc_cate_ids = str(vc_cate_ids).replace(']', ')')
            account_ids = self.pool.get('account.account').search(self.cr,self.uid,[('code', '=', '64189')])
            account_ids = str(account_ids).replace('[', '(')
            account_ids = str(account_ids).replace(']', ')')
    #         period_start = period_obj.browse(self.cr,self.uid,period_id[0]).date_start
    #         period_stop = period_obj.browse(self.cr,self.uid,period_id[0]).date_stop
            cus_ids = []
            res = []
            inv_ids = []
            if not user_ids:
                sql ='''
                 select id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                            from product_product,product_template 
                            where product_template.categ_id in %s
                            and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                (select id from account_invoice where date_invoice < '%s' and type ='out_invoice' and account_id not in %s and state in ('open','paid')))
                            order by date_invoice
                '''%(vc_cate_ids,date_from,account_ids)
                self.cr.execute(sql)   
                inv_truoc_ids = [r[0] for r in self.cr.fetchall()]
                
                sql ='''
                 select id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                                from product_product,product_template 
                                where product_template.categ_id in %s
                                and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                    (select id from account_invoice where date_invoice between '%s' and '%s' and type ='out_invoice' and account_id not in %s and state in ('open','paid')))
                                order by date_invoice
                '''%(vc_cate_ids,date_from, date_to,account_ids)
                self.cr.execute(sql)   
                inv_ids = [r[0] for r in self.cr.fetchall()]
            else:
                user_ids = str(user_ids).replace("[","(")
                user_ids = str(user_ids).replace("]",")")
                sql = '''
                    select id from res_partner where user_id in %s and customer is True
                '''%(user_ids)
                self.cr.execute(sql)
                cus_ids = [r[0] for r in self.cr.fetchall()]  
                if cus_ids:
                    cus_ids = str(cus_ids).replace("[","(")
                    cus_ids = str(cus_ids).replace("]",")")
                    sql ='''
                     select id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                                    from product_product,product_template 
                                    where product_template.categ_id in %s
                                    and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                        (select id from account_invoice where date_invoice < '%s' and type ='out_invoice' and account_id not in %s and state in ('open','paid')))
                                    and partner_id in %s
                                    order by date_invoice
                    '''%(vc_cate_ids,date_from,account_ids,cus_ids)
                    self.cr.execute(sql)   
                    inv_truoc_ids = [r[0] for r in self.cr.fetchall()] 
                    
                    sql ='''
                     select id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                                    from product_product,product_template 
                                    where product_template.categ_id in %s
                                    and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                        (select id from account_invoice where date_invoice between '%s' and '%s' and type ='out_invoice' and account_id not in %s and state in ('open','paid')))
                                    and partner_id in %s
                                    order by date_invoice
                    '''%(vc_cate_ids,date_from,date_to,account_ids,cus_ids)
                    self.cr.execute(sql)   
                    inv_ids = [r[0] for r in self.cr.fetchall()] 
                    
            if inv_truoc_ids:
                for inv in inv_truoc_ids:
                    tien_mat = 0
                    exim = 0
                    acb = 0 
                    agr = 0
                    ngay_tt = ''
                    so_ngay_no = 0
                    thuc_thu = 0
                    da_tra = 0
                    nodk = 0
                    sql = ''' 
                        select ai.amount_total as amount_total, date_invoice, reference_number, rp.name as cus, rp.id as cus_id, rp.internal_code as code from account_invoice ai, res_partner rp 
                            where ai.partner_id = rp.id and ai.id = %s 
                            
                    '''%(inv)
                    self.cr.execute(sql) 
                    inv_id = self.cr.dictfetchone()
                    amount_total = inv_id and inv_id['amount_total'] or 0
                    tdv_name = self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).user_id and self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).user_id.name or ''
                    kv = self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).state_id and self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).state_id.name or ''
                    sql='''
                        select ma.name from account_invoice_line acc, product_product pr , manufacturer_product ma
                        where invoice_id = %s and acc.product_id = pr.id and ma.id = pr.manufacturer_product_id
                    '''%(inv)
                    self.cr.execute(sql) 
                    hang_sx = self.cr.fetchone() or False
                    invoice_id = self.pool.get('account.invoice').browse(self.cr,self.uid,inv)
                    for pay in invoice_id.payment_ids:
                        if pay.date < date_from:
                            da_tra += pay.credit
                        if pay.date >= date_from and pay.date <= date_to:
                            if pay.journal_id.code == '11':
                                tien_mat += pay.credit
                            if pay.journal_id.code == '12':
                                acb += pay.credit
                            if pay.journal_id.code == '13':
                                exim += pay.credit
                            if pay.journal_id.code == '16':
                                agr += pay.credit 
                            if pay.date:
                                ngay_tt +=  convert_date(o,pay.date) + ', '
                    thuc_thu = tien_mat+acb+exim+agr
                    nodk = amount_total - da_tra    
                    tong_ck = nodk-thuc_thu
                    if nodk > 0:
                        res.append({'cus_name': inv_id['cus'],
                                    'dia_chi': inv_id['cus_id'] and display_address(o,inv_id['cus_id']) or '',
                                    'ngay_xuat': convert_date(o,inv_id['date_invoice']) or False,
                                    'date_invoice':convert_date(o,inv_id['date_invoice']) or False,
                                    'reference_number':inv_id['reference_number'],
                                    'internal_code':inv_id['code'],
                                    'nodk': nodk,
                                    'phatsinh':0,
                                    'tienmat': tien_mat,
                                    'acb': acb,
                                    'exim': exim,
                                    'agr': agr,
                                    'nock': tong_ck,
                                    'ngay_tt': ngay_tt and ngay_tt[:-2] or '',
                                    'tdv_name': tdv_name,
                                    'kv': kv,
                                    'hang_sx': hang_sx and hang_sx[0] or '',
                                    'so_ngay_no':so_ngay_no,
                                    })
            if inv_ids:
                for inv in inv_ids:
                    tien_mat = 0
                    exim = 0
                    acb = 0 
                    agr = 0
                    ngay_tt = ''
                    so_ngay_no = 0
                    thuc_thu = 0
                    tong_ck = 0
                    sql = ''' 
                        select ai.residual as residual, date_invoice, reference_number, amount_total, rp.name as cus, rp.id as cus_id, rp.internal_code as code from account_invoice ai, res_partner rp 
                        where ai.partner_id = rp.id and ai.id = %s 
                    '''%(inv)
                    self.cr.execute(sql) 
                    inv_id = self.cr.dictfetchone()
                    
                    invoice_id = invoice_obj.browse(self.cr,self.uid,inv)
#                     nock = nodk + (invoice_id.residual and invoice_id.residual or 0)
                    tdv_name = self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).user_id and self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).user_id.name or ''
                    kv = self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).state_id and self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).state_id.name or ''
                    for pay in invoice_id.payment_ids:
                        if pay.date >= date_from and pay.date <= date_to:
                            if pay.journal_id.code == '11':
                                tien_mat += pay.credit
                                self.tong_tien += tien_mat
                            if pay.journal_id.code == '12':
                                acb += pay.credit
                                self.tong_acb += acb
                            if pay.journal_id.code == '13':
                                exim += pay.credit
                                self.tong_exim += exim
                            if pay.journal_id.code == '16':
                                agr += pay.credit 
                                self.tong_agr += agr
                            if pay.date:
                                ngay_tt +=  convert_date(o,pay.date) + ', '
                    thuc_thu = tien_mat+acb+exim+agr
                    sql='''
                        select ma.name from account_invoice_line acc, product_product pr , manufacturer_product ma
                        where invoice_id = %s and acc.product_id = pr.id and ma.id = pr.manufacturer_product_id
                    '''%(inv)
                    cr.execute(sql) 
                    hang_sx = self.cr.fetchone() or False
                    if invoice_id.state != 'paid':
                        sql='''
                            select case when ('%s'::date - date_invoice)!=0 then ('%s'::date - date_invoice) else 0 end ngayno from account_invoice where id = %s
                        '''%(date_to,date_to,inv)
                        self.cr.execute(sql) 
                        so_ngay_no = self.cr.fetchone()[0]
                    tong_ck = float(inv_id['amount_total'])-thuc_thu
                    self.tong_ck += tong_ck
                    res.append({'cus_name': inv_id['cus'],
                                'dia_chi': inv_id['cus_id'] and display_address(o,inv_id['cus_id']) or False,
                                'ngay_xuat': convert_date(o,inv_id['date_invoice']) or False,
                                'date_invoice':convert_date(o,inv_id['date_invoice']) or False,
                                'reference_number':inv_id['reference_number'],
                                'internal_code':inv_id['code'],
                                'nodk': 0,
                                'phatsinh':float(inv_id['amount_total']),
                                'tienmat': tien_mat,
                                'acb': acb,
                                'exim': exim,
                                'agr': agr,
                                'nock': tong_ck,
                                'ngay_tt': ngay_tt and ngay_tt[:-2] or '',
                                'tdv_name': tdv_name,
                                'kv': kv,
                                'hang_sx': hang_sx and hang_sx[0] or '',
                                'so_ngay_no':so_ngay_no,
                                })
                    
            return res     
        def get_info(o):
            mang=[]
            dem = 0
            for line in get_lines(o):
                dem = dem + 1
                mang.append((0,0,{
                        'stt':dem,
                        'ngay_xuat': line['ngay_xuat'] or False,
                        'ma_kh': line['internal_code'] or '',
                        'so_hd':line['reference_number'] or '',
                        'khach_hang':line['cus_name'] or '',
                        'dia_chi':line['dia_chi'] or '',
                        'no_dk':line['nodk'] or '',
                        'phat_sinh':line['phatsinh'] or '',
                        'tt_tien_mat':line['tienmat'] or '',
                        'tt_ck_exim': line['exim'] or '',
                        'tt_ck_acb': line['acb'] or '',
                        'tt_ck_agr':line['agr'] or '',
                        'no_ck':line['nock'] or '',
                        'ngay_thanh_toan':line['ngay_tt'] or '',
                        'so_ngay_no':line['so_ngay_no'] or '',
                        'tdv':line['tdv_name'] or '',
                        'tinh_tp':line['kv'] or '',
                        'hang':line['hang_sx'] or '',
                                 }))
            return mang 
        vals = {
            'date_from':report.date_from,
            'date_to':report.date_to,
#             'date_from_title':'Từ ngày: ',
#             'date_to_title':'đến ngày: ',
#             'tong_begin_dr':get_info(report)[self.sum_amount],
#             'tong_period_dr':get_info(report)[self.sum_amount_2],
            'congno_vacine_review_line':get_info(report),
        }        
        report_id = report_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_phucthien_sale', 'congno_vacine_review')
        return {
                    'name': 'Công Nợ Vaccine',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'congno.vacine.review',
                    'domain': [],
                    'view_id': res and res[1] or False,
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': report_id,
                }        
congno_vacine()

class congno_mypham(osv.osv_memory):
    _name = 'congno.mypham'
     
    _columns = {
        'period_id': fields.many2one('account.period','Tháng:'),
        'date_from': fields.date('Từ ngày',required=True),
        'date_to': fields.date('Đến ngày',required=True),
#         'user_id': fields.many2many('res.users', string='Users', readonly=True),
        'user_ids': fields.many2many('res.users', 'mypham_user_ref', 'mypham_id', 'user_id', 'Nhân Viên Bán Hàng'),  
    }
     
    _defaults = {
        'date_from': lambda *a: time.strftime('%Y-%m-01'),
        'date_to': lambda *a: time.strftime('%Y-%m-%d'),
        'user_ids': lambda self,cr, uid, ctx: [(6,0,[uid])],
    }
     
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'congno.mypham' 
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'congno_mypham_report', 'datas': datas}

    def review_report_in(self, cr, uid, ids, context=None): 
        report_obj = self.pool.get('congno.mypham.review')
        report = self.browse(cr, uid, ids[0])   
        self.date_from = False
        self.date_to = False
        self.cr = cr
        self.uid = uid
        self.tong_tien = 0
        self.tong_exim = 0
        self.tong_acb = 0
        self.tong_agr = 0
        self.tong_ck = 0
        def convert_date(o, date):
            if date:
                date = datetime.strptime(date, DATE_FORMAT)
                return date.strftime('%d/%m/%Y')        
        def display_address(o, partner_id):
            partner = self.pool.get('res.partner').browse(self.cr, self.uid, partner_id)
            address = partner.street and partner.street + ' , ' or ''
            address += partner.street2 and partner.street2 + ' , ' or ''
            address += partner.city and partner.city.name + ' , ' or ''
            if address:
                address = address[:-3]
            return address       
        def get_lines(o):
            user_ids = [r.id for r in o.user_ids]
            invoice_obj = self.pool.get('account.invoice') 
            period_obj = self.pool.get('account.period')
            date_from = o.date_from   
            date_to =  o.date_to
            mp_cate_ids = self.pool.get('product.category').search(self.cr,self.uid,[('code','=','MP')])
            mp_cate_ids = self.pool.get('product.category').search(self.cr, self.uid, [('parent_id','child_of',mp_cate_ids)])
            mp_cate_ids = str(mp_cate_ids).replace('[', '(')
            mp_cate_ids = str(mp_cate_ids).replace(']', ')')
            account_ids = self.pool.get('account.account').search(self.cr,self.uid,[('code', '=', '64189')])
            account_ids = str(account_ids).replace('[', '(')
            account_ids = str(account_ids).replace(']', ')')
    #         period_start = period_obj.browse(self.cr,self.uid,period_id[0]).date_start
    #         period_stop = period_obj.browse(self.cr,self.uid,period_id[0]).date_stop
            cus_ids = []
            res = []
            inv_ids = []
            if not user_ids:
                sql ='''
                 select id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                            from product_product,product_template 
                            where product_template.categ_id in %s 
                            and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                (select id from account_invoice where date_invoice < '%s' and type ='out_invoice' and account_id not in %s and state in ('open','paid')))
                            order by date_invoice
                '''%(mp_cate_ids,date_from,account_ids)
                self.cr.execute(sql)   
                inv_truoc_ids = [r[0] for r in self.cr.fetchall()]
                
                sql ='''
                 select id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                                from product_product,product_template 
                                where product_template.categ_id in %s 
                                and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                    (select id from account_invoice where date_invoice between '%s' and '%s' and type ='out_invoice' and account_id not in %s and state in ('open','paid')))
                                order by date_invoice
                '''%(mp_cate_ids,date_from, date_to,account_ids)
                self.cr.execute(sql)   
                inv_ids = [r[0] for r in self.cr.fetchall()]
            else:
                user_ids = str(user_ids).replace("[","(")
                user_ids = str(user_ids).replace("]",")")
                sql = '''
                    select id from res_partner where user_id in %s and customer is True
                '''%(user_ids)
                self.cr.execute(sql)
                cus_ids = [r[0] for r in self.cr.fetchall()]  
                if cus_ids:
                    cus_ids = str(cus_ids).replace("[","(")
                    cus_ids = str(cus_ids).replace("]",")")
                    sql ='''
                     select id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                                    from product_product,product_template 
                                    where product_template.categ_id in %s 
                                    and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                        (select id from account_invoice where date_invoice < '%s' and type ='out_invoice' and account_id not in %s and state in ('open','paid')))
                                    and partner_id in %s
                                    order by date_invoice
                    '''%(mp_cate_ids,date_from,account_ids,cus_ids)
                    self.cr.execute(sql)   
                    inv_truoc_ids = [r[0] for r in self.cr.fetchall()] 
                    
                    sql ='''
                     select id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                                    from product_product,product_template 
                                    where product_template.categ_id in %s
                                    and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                        (select id from account_invoice where date_invoice between '%s' and '%s' and type ='out_invoice' and account_id not in %s and state in ('open','paid')))
                                    and partner_id in %s
                                    order by date_invoice
                    '''%(mp_cate_ids,date_from,date_to,account_ids,cus_ids)
                    self.cr.execute(sql)   
                    inv_ids = [r[0] for r in self.cr.fetchall()] 
                    
            if inv_truoc_ids:
                for inv in inv_truoc_ids:
                    tien_mat = 0
                    exim = 0
                    acb = 0 
                    agr = 0
                    ngay_tt = ''
                    so_ngay_no = 0
                    thuc_thu = 0
                    da_tra = 0
                    nodk = 0
                    sql = ''' 
                        select ai.amount_total as amount_total, date_invoice, reference_number, rp.name as cus, rp.id as cus_id, rp.internal_code as code from account_invoice ai, res_partner rp 
                            where ai.partner_id = rp.id and ai.id = %s 
                            
                    '''%(inv)
                    self.cr.execute(sql) 
                    inv_id = self.cr.dictfetchone()
                    amount_total = inv_id and inv_id['amount_total'] or 0
                    tdv_name = self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).user_id and self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).user_id.name or ''
                    kv = self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).state_id and self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).state_id.name or ''
                    sql='''
                        select ma.name from account_invoice_line acc, product_product pr , manufacturer_product ma
                        where invoice_id = %s and acc.product_id = pr.id and ma.id = pr.manufacturer_product_id
                    '''%(inv)
                    self.cr.execute(sql) 
                    hang_sx = self.cr.fetchone() or False
                    invoice_id = self.pool.get('account.invoice').browse(self.cr,self.uid,inv)
                    for pay in invoice_id.payment_ids:
                        if pay.date < date_from:
                            da_tra += pay.credit
                        if pay.date >= date_from and pay.date <= date_to:
                            if pay.journal_id.code == '11':
                                tien_mat += pay.credit
                            if pay.journal_id.code == '12':
                                acb += pay.credit
                            if pay.journal_id.code == '13':
                                exim += pay.credit
                            if pay.journal_id.code == '16':
                                agr += pay.credit 
                            if pay.date:
                                ngay_tt +=  convert_date(o,pay.date) + ', '
                    thuc_thu = tien_mat+acb+exim+agr
                    nodk = amount_total - da_tra      
                    tong_ck = nodk-thuc_thu
                    if nodk > 0:
                        res.append({'cus_name': inv_id['cus'],
                                    'dia_chi': inv_id['cus_id'] and display_address(o,inv_id['cus_id']) or '',
                                    'ngay_xuat': convert_date(o,inv_id['date_invoice']) or False,
                                    'date_invoice':convert_date(o,inv_id['date_invoice']) or False,
                                    'reference_number':inv_id['reference_number'],
                                    'internal_code':inv_id['code'],
                                    'nodk': nodk,
                                    'phatsinh':0,
                                    'tienmat': tien_mat,
                                    'acb': acb,
                                    'exim': exim,
                                    'agr': agr,
                                    'nock': tong_ck,
                                    'ngay_tt': ngay_tt and ngay_tt[:-2] or '',
                                    'tdv_name': tdv_name,
                                    'kv': kv,
                                    'hang_sx': hang_sx and hang_sx[0] or '',
                                    'so_ngay_no':so_ngay_no,
                                    })
            if inv_ids:
                for inv in inv_ids:
                    tien_mat = 0
                    exim = 0
                    acb = 0 
                    agr = 0
                    ngay_tt = ''
                    so_ngay_no = 0
                    thuc_thu = 0
                    tong_ck = 0
                    sql = ''' 
                        select ai.residual as residual, date_invoice, reference_number, amount_total, rp.name as cus, rp.id as cus_id, rp.internal_code as code from account_invoice ai, res_partner rp 
                        where ai.partner_id = rp.id and ai.id = %s 
                    '''%(inv)
                    self.cr.execute(sql) 
                    inv_id = self.cr.dictfetchone()
                    
                    invoice_id = invoice_obj.browse(self.cr,self.uid,inv)
#                     nock = nodk + (invoice_id.residual and invoice_id.residual or 0)
                    tdv_name = self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).user_id and self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).user_id.name or ''
                    kv = self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).state_id and self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).state_id.name or ''
                    for pay in invoice_id.payment_ids:
                        if pay.date >= date_from and pay.date <= date_to:
                            if pay.journal_id.code == '11':
                                tien_mat += pay.credit
                                self.tong_tien += tien_mat
                            if pay.journal_id.code == '12':
                                acb += pay.credit
                                self.tong_acb += acb
                            if pay.journal_id.code == '13':
                                exim += pay.credit
                                self.tong_exim += exim
                            if pay.journal_id.code == '16':
                                agr += pay.credit 
                                self.tong_agr += agr
                            if pay.date:
                                ngay_tt +=  convert_date(o,pay.date) + ', '
                    thuc_thu = tien_mat+acb+exim+agr
                    sql='''
                        select ma.name from account_invoice_line acc, product_product pr , manufacturer_product ma
                        where invoice_id = %s and acc.product_id = pr.id and ma.id = pr.manufacturer_product_id
                    '''%(inv)
                    cr.execute(sql) 
                    hang_sx = self.cr.fetchone() or False
                    if invoice_id.state != 'paid':
                        sql='''
                            select case when ('%s'::date - date_invoice)!=0 then ('%s'::date - date_invoice) else 0 end ngayno from account_invoice where id = %s
                        '''%(date_to,date_to,inv)
                        self.cr.execute(sql) 
                        so_ngay_no = self.cr.fetchone()[0]
                    tong_ck = float(inv_id['amount_total'])-thuc_thu
                    self.tong_ck += tong_ck
                    res.append({'cus_name': inv_id['cus'],
                                'dia_chi': inv_id['cus_id'] and display_address(o,inv_id['cus_id']) or False,
                                'ngay_xuat': convert_date(o,inv_id['date_invoice']) or False,
                                'date_invoice':convert_date(o,inv_id['date_invoice']) or False,
                                'reference_number':inv_id['reference_number'],
                                'internal_code':inv_id['code'],
                                'nodk': 0,
                                'phatsinh':float(inv_id['amount_total']),
                                'tienmat': tien_mat,
                                'acb': acb,
                                'exim': exim,
                                'agr': agr,
                                'nock': tong_ck,
                                'ngay_tt': ngay_tt and ngay_tt[:-2] or '',
                                'tdv_name': tdv_name,
                                'kv': kv,
                                'hang_sx': hang_sx and hang_sx[0] or '',
                                'so_ngay_no':so_ngay_no,
                                })
                    
            return res      
        def get_info(o):
            mang=[]
            dem = 0
            for line in get_lines(o):
                dem = dem + 1
                mang.append((0,0,{
                        'stt':dem,
                        'ngay_xuat': line['ngay_xuat'] or '',
                        'ma_kh': line['internal_code'] or '',
                        'so_hd':line['reference_number'] or '',
                        'khach_hang':line['cus_name'] or '',
                        'dia_chi':line['dia_chi'] or '',
                        'no_dk':line['nodk'] or '',
                        'phat_sinh':line['phatsinh'] or '',
                        'tt_tien_mat':line['tienmat'] or '',
                        'tt_ck_exim': line['exim'] or '',
                        'tt_ck_acb': line['acb'] or '',
                        'tt_ck_agr':line['agr'] or '',
                        'no_ck':line['nock'] or '',
                        'ngay_thanh_toan':line['ngay_tt'] or '',
                        'so_ngay_no':line['so_ngay_no'] or '',
                        'tdv':line['tdv_name'] or '',
                        'tinh_tp':line['kv'] or '',
                        'hang':line['hang_sx'] or '',
                                 }))
            return mang 
        vals = {
            'date_from':report.date_from,
            'date_to':report.date_to,
            'congno_mypham_review_line':get_info(report),
        }        
        report_id = report_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_phucthien_sale', 'congno_mypham_review')
        return {
                    'name': 'Công Nợ Mỹ Phẩm',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'congno.mypham.review',
                    'domain': [],
                    'view_id': res and res[1] or False,
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': report_id,
                }    
     
congno_mypham()

class congno_duocpham(osv.osv_memory):
    _name = 'congno.duocpham'
     
    _columns = {
        'date_from': fields.date('Từ ngày',required=True),
        'date_to': fields.date('Đến ngày',required=True),
        'period_id': fields.many2one('account.period','Tháng:'),
        'user_ids': fields.many2many('res.users', 'duocpham_user_ref', 'duocpham_id', 'user_id', 'Nhân Viên Bán Hàng'),  
    }
     
    _defaults = {
        'date_from': lambda *a: time.strftime('%Y-%m-01'),
        'date_to': lambda *a: time.strftime('%Y-%m-%d'),
        'user_ids': lambda self,cr, uid, ctx: [(6,0,[uid])],
    }
     
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'congno.duocpham' 
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'congno_duocpham_report', 'datas': datas}

    def review_report_in(self, cr, uid, ids, context=None): 
        report_obj = self.pool.get('congno.duocpham.review')
        report = self.browse(cr, uid, ids[0])   
        self.date_from = False
        self.date_to = False
        self.cr = cr
        self.uid = uid
        self.tong_tien = 0
        self.tong_exim = 0
        self.tong_acb = 0
        self.tong_agr = 0
        self.tong_ck = 0
        def convert_date(o, date):
            if date:
                date = datetime.strptime(date, DATE_FORMAT)
                return date.strftime('%d/%m/%Y')       
        def display_address(o, partner_id):
            partner = self.pool.get('res.partner').browse(self.cr, self.uid, partner_id)
            address = partner.street and partner.street + ' , ' or ''
            address += partner.street2 and partner.street2 + ' , ' or ''
            address += partner.city and partner.city.name + ' , ' or ''
            if address:
                address = address[:-3]
            return address       
        def get_lines(o):
            user_ids = [r.id for r in o.user_ids]
            invoice_obj = self.pool.get('account.invoice') 
            period_obj = self.pool.get('account.period')
            date_from = o.date_from   
            date_to =  o.date_to
            dp_cate_ids = self.pool.get('product.category').search(self.cr,self.uid,[('code','=','DP')])
            dp_cate_ids = self.pool.get('product.category').search(self.cr, self.uid, [('parent_id','child_of',dp_cate_ids)])
            dp_cate_ids = str(dp_cate_ids).replace('[', '(')
            dp_cate_ids = str(dp_cate_ids).replace(']', ')')
            account_ids = self.pool.get('account.account').search(self.cr,self.uid,[('code', '=', '64189')])
            account_ids = str(account_ids).replace('[', '(')
            account_ids = str(account_ids).replace(']', ')')
    #         period_start = period_obj.browse(self.cr,self.uid,period_id[0]).date_start
    #         period_stop = period_obj.browse(self.cr,self.uid,period_id[0]).date_stop
            cus_ids = []
            res = []
            inv_ids = []
            if not user_ids:
                sql ='''
                 select id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                            from product_product,product_template 
                            where product_template.categ_id in %s
                            and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                (select id from account_invoice where date_invoice < '%s' and type ='out_invoice' and account_id not in %s and state in ('open','paid')))
                            order by date_invoice
                '''%(dp_cate_ids,date_from,account_ids)
                self.cr.execute(sql)   
                inv_truoc_ids = [r[0] for r in self.cr.fetchall()]
                
                sql ='''
                 select id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                                from product_product,product_template 
                                where product_template.categ_id in %s
                                and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                    (select id from account_invoice where date_invoice between '%s' and '%s' and type ='out_invoice' and account_id not in %s and state in ('open','paid')))
                                order by date_invoice
                '''%(dp_cate_ids,date_from, date_to,account_ids)
                self.cr.execute(sql)   
                inv_ids = [r[0] for r in self.cr.fetchall()]
            else:
                user_ids = str(user_ids).replace("[","(")
                user_ids = str(user_ids).replace("]",")")
                sql = '''
                    select id from res_partner where user_id in %s and customer is True
                '''%(user_ids)
                self.cr.execute(sql)
                cus_ids = [r[0] for r in self.cr.fetchall()]  
                if cus_ids:
                    cus_ids = str(cus_ids).replace("[","(")
                    cus_ids = str(cus_ids).replace("]",")")
                    sql ='''
                     select id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                                    from product_product,product_template 
                                    where product_template.categ_id in %s
                                    and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                        (select id from account_invoice where date_invoice < '%s' and type ='out_invoice' and account_id not in %s and state in ('open','paid')))
                                    and partner_id in %s
                                    order by date_invoice
                    '''%(dp_cate_ids,date_from,account_ids,cus_ids)
                    self.cr.execute(sql)   
                    inv_truoc_ids = [r[0] for r in self.cr.fetchall()] 
                    
                    sql ='''
                     select id from account_invoice where id in (select distinct invoice_id from account_invoice_line where product_id in (select product_product.id
                                    from product_product,product_template 
                                    where product_template.categ_id in %s
                                    and product_product.product_tmpl_id = product_template.id) and invoice_id in 
                                        (select id from account_invoice where date_invoice between '%s' and '%s' and type ='out_invoice' and account_id not in %s and state in ('open','paid')))
                                    and partner_id in %s
                                    order by date_invoice
                    '''%(dp_cate_ids,date_from,date_to,account_ids,cus_ids)
                    self.cr.execute(sql)   
                    inv_ids = [r[0] for r in self.cr.fetchall()] 
                    
            if inv_truoc_ids:
                for inv in inv_truoc_ids:
                    tien_mat = 0
                    exim = 0
                    acb = 0 
                    agr = 0
                    ngay_tt = ''
                    so_ngay_no = 0
                    thuc_thu = 0
                    da_tra = 0
                    nodk = 0
                    sql = ''' 
                        select ai.amount_total as amount_total, date_invoice, reference_number, rp.name as cus, rp.id as cus_id, rp.internal_code as code from account_invoice ai, res_partner rp 
                            where ai.partner_id = rp.id and ai.id = %s 
                            
                    '''%(inv)
                    self.cr.execute(sql) 
                    inv_id = self.cr.dictfetchone()
                    amount_total = inv_id and inv_id['amount_total'] or 0
                    tdv_name = self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).user_id and self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).user_id.name or ''
                    kv = self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).state_id and self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).state_id.name or ''
                    sql='''
                        select ma.name from account_invoice_line acc, product_product pr , manufacturer_product ma
                        where invoice_id = %s and acc.product_id = pr.id and ma.id = pr.manufacturer_product_id
                    '''%(inv)
                    self.cr.execute(sql) 
                    hang_sx = self.cr.fetchone() or False
                    invoice_id = self.pool.get('account.invoice').browse(self.cr,self.uid,inv)
                    for pay in invoice_id.payment_ids:
                        if pay.date < date_from:
                            da_tra += pay.credit
                        if pay.date >= date_from and pay.date <= date_to:
                            if pay.journal_id.code == '11':
                                tien_mat += pay.credit
                            if pay.journal_id.code == '12':
                                acb += pay.credit
                            if pay.journal_id.code == '13':
                                exim += pay.credit
                            if pay.journal_id.code == '16':
                                agr += pay.credit 
                            if pay.date:
                                ngay_tt +=  convert_date(o,pay.date) + ', '
                    thuc_thu = tien_mat+acb+exim+agr
                    nodk = amount_total - da_tra        
                    tong_ck = nodk-thuc_thu
                    if nodk > 0:
                        res.append({'cus_name': inv_id['cus'],
                                    'dia_chi': inv_id['cus_id'] and display_address(o,inv_id['cus_id']) or '',
                                    'ngay_xuat': convert_date(o,inv_id['date_invoice']) or False,
                                    'date_invoice':convert_date(o,inv_id['date_invoice']) or False,
                                    'reference_number':inv_id['reference_number'],
                                    'internal_code':inv_id['code'],
                                    'nodk': nodk,
                                    'phatsinh':0,
                                    'tienmat': tien_mat,
                                    'acb': acb,
                                    'exim': exim,
                                    'agr': agr,
                                    'nock': tong_ck,
                                    'ngay_tt': ngay_tt and ngay_tt[:-2] or '',
                                    'tdv_name': tdv_name,
                                    'kv': kv,
                                    'hang_sx': hang_sx and hang_sx[0] or '',
                                    'so_ngay_no':so_ngay_no,
                                    })
            if inv_ids:
                for inv in inv_ids:
                    tien_mat = 0
                    exim = 0
                    acb = 0 
                    agr = 0
                    ngay_tt = ''
                    so_ngay_no = 0
                    thuc_thu = 0
                    tong_ck = 0
                    sql = ''' 
                        select ai.residual as residual, date_invoice, reference_number, amount_total, rp.name as cus, rp.id as cus_id, rp.internal_code as code from account_invoice ai, res_partner rp 
                        where ai.partner_id = rp.id and ai.id = %s 
                    '''%(inv)
                    self.cr.execute(sql) 
                    inv_id = self.cr.dictfetchone()
                    
                    invoice_id = invoice_obj.browse(self.cr,self.uid,inv)
#                     nock = nodk + (invoice_id.residual and invoice_id.residual or 0)
                    tdv_name = self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).user_id and self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).user_id.name or ''
                    kv = self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).state_id and self.pool.get('res.partner').browse(self.cr,self.uid,inv_id['cus_id']).state_id.name or ''
                    for pay in invoice_id.payment_ids:
                        if pay.date >= date_from and pay.date <= date_to:
                            if pay.journal_id.code == '11':
                                tien_mat += pay.credit
                                self.tong_tien += tien_mat
                            if pay.journal_id.code == '12':
                                acb += pay.credit
                                self.tong_acb += acb
                            if pay.journal_id.code == '13':
                                exim += pay.credit
                                self.tong_exim += exim
                            if pay.journal_id.code == '16':
                                agr += pay.credit 
                                self.tong_agr += agr
                            if pay.date:
                                ngay_tt +=  convert_date(o,pay.date) + ', '
                    thuc_thu = tien_mat+acb+exim+agr
                    sql='''
                        select ma.name from account_invoice_line acc, product_product pr , manufacturer_product ma
                        where invoice_id = %s and acc.product_id = pr.id and ma.id = pr.manufacturer_product_id
                    '''%(inv)
                    cr.execute(sql) 
                    hang_sx = self.cr.fetchone() or False
                    if invoice_id.state != 'paid':
                        sql='''
                            select case when ('%s'::date - date_invoice)!=0 then ('%s'::date - date_invoice) else 0 end ngayno from account_invoice where id = %s
                        '''%(date_to,date_to,inv)
                        self.cr.execute(sql) 
                        so_ngay_no = self.cr.fetchone()[0]
                    tong_ck = float(inv_id['amount_total'])-thuc_thu
                    self.tong_ck += tong_ck
                    res.append({'cus_name': inv_id['cus'],
                                'dia_chi': inv_id['cus_id'] and display_address(o,inv_id['cus_id']) or False,
                                'ngay_xuat': convert_date(o,inv_id['date_invoice']) or False,
                                'date_invoice':convert_date(o,inv_id['date_invoice']) or False,
                                'reference_number':inv_id['reference_number'],
                                'internal_code':inv_id['code'],
                                'nodk': 0,
                                'phatsinh':float(inv_id['amount_total']),
                                'tienmat': tien_mat,
                                'acb': acb,
                                'exim': exim,
                                'agr': agr,
                                'nock': tong_ck,
                                'ngay_tt': ngay_tt and ngay_tt[:-2] or '',
                                'tdv_name': tdv_name,
                                'kv': kv,
                                'hang_sx': hang_sx and hang_sx[0] or '',
                                'so_ngay_no':so_ngay_no,
                                })
                    
            return res      
        def get_info(o):
            mang=[]
            dem = 0
            for line in get_lines(o):
                dem = dem + 1
                mang.append((0,0,{
                        'stt':dem,
                        'ngay_xuat': line['ngay_xuat'] or '',
                        'ma_kh': line['internal_code'] or '',
                        'so_hd':line['reference_number'] or '',
                        'khach_hang':line['cus_name'] or '',
                        'dia_chi':line['dia_chi'] or '',
                        'no_dk':line['nodk'] or '',
                        'phat_sinh':line['phatsinh'] or '',
                        'tt_tien_mat':line['tienmat'] or '',
                        'tt_ck_exim': line['exim'] or '',
                        'tt_ck_acb': line['acb'] or '',
                        'tt_ck_agr':line['agr'] or '',
                        'no_ck':line['nock'] or '',
                        'ngay_thanh_toan':line['ngay_tt'] or '',
                        'so_ngay_no':line['so_ngay_no'] or '',
                        'tdv':line['tdv_name'] or '',
                        'tinh_tp':line['kv'] or '',
                        'hang':line['hang_sx'] or '',
                                 }))
            return mang 
        vals = {
            'date_from':report.date_from,
            'date_to':report.date_to,
#             'date_from_title':'Từ ngày: ',
#             'date_to_title':'đến ngày: ',
#             'tong_begin_dr':get_info(report)[self.sum_amount],
#             'tong_period_dr':get_info(report)[self.sum_amount_2],
            'congno_duocpham_review_line':get_info(report),
        }        
        report_id = report_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_phucthien_sale', 'congno_duocpham_review')
        return {
                    'name': 'Công Nợ Dược Phẩm',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'congno.duocpham.review',
                    'domain': [],
                    'view_id': res and res[1] or False,
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': report_id,
                }  
     
congno_duocpham()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

