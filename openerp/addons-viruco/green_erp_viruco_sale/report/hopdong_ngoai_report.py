# -*- coding: utf-8 -*-
##############################################################################
#
#    HLVSolution, Open Source Management Solution
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
import locale
from green_erp_viruco_sale.report import amount_to_text_en
from green_erp_viruco_sale.report import amount_to_text_vn
# from green_erp_arulmani_sale.report import amount_to_text_indian
# from amount_to_text_indian import Number2Words
#locale.setlocale(locale.LC_NUMERIC, "en_IN")
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from green_erp_viruco_sale.report import amount_to_text_en

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'convert':self.convert,
            'convert_f_amount':self.convert_f_amount,
            'convert_date': self.convert_date,
            'get_tong': self.get_tong,
            'get_transhipment': self.get_transhipment,
            'get_so_phuluc': self.get_so_phuluc,
            'get_price_hh': self.get_price_hh,
            'get_tax_hh': self.get_tax_hh,
            'get_ngaynhan_lc': self.get_ngaynhan_lc,
            'get_thanhtoan': self.get_thanhtoan,
            'get_journal': self.get_journal,
            'get_giaohang': self.get_giaohang,
            'get_delivery_order': self.get_delivery_order,
            'get_cang_den': self.get_cang_den,
            'convert_theodoi_date': self.convert_theodoi_date,
            'convert_dbh_date': self.convert_dbh_date,
            'get_dia_chi': self.get_dia_chi,
            'get_soluong': self.get_soluong,
            
        })
        
    def get_soluong(self,order):
        cur_obj = self.pool.get('res.currency')
        cur = order.pricelist_id.currency_id
        val = 0
        for line in order.don_ban_hang_line:
            val += line.product_qty
#         product_qty = cur_obj.round(self.cr, self.uid, cur, val)
        return {
                'product_qty': val,
                }
        
    def get_transhipment(self, transhipment):
        tam = ''
        if transhipment == 'allowed':
            tam = 'Allowed'
        if transhipment == 'not_allowed':
            tam = 'Not Allowed'
        return tam
    
    def get_dia_chi(self, street, street2, state_id, zip, country_id):
        address = ''
        if street:
            address += street + ', '
        if street2:
            address += street2 + ', '
        if state_id:
            state = self.pool.get('res.country.state').browse(self.cr,self.uid,state_id)
            address += state.name + ', ' 
        if zip:
            address += zip + ', '
        if country_id:
            country = self.pool.get('res.country').browse(self.cr,self.uid,country_id)
            address += country.name  
        return address
    
    def convert_dbh_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
    def convert_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d-%b-%y')
    
    def convert_theodoi_date(self, date):
        if not date:
            return ''
        date = datetime.strptime(date[0:10], DATE_FORMAT)
        return date.strftime('%d-%m-%Y')
        
    def convert_f_amount(self, amount):
        a = format(amount,',')
        b = a.split('.')
        if len(b)==2 and len(b[1])==1:
            a+='0'
        return a.replace(',',' ')
 
#     def convert_amount(self, amount):
#         a = format(int(amount),',')
#         a = a.replace(',','.')
#         return a    
    
    def convert(self, amount):
        amount_text = amount_to_text_en.amount_to_text(amount, 'en', 'Dollars')
        if amount_text and len(amount_text)>1:
            amount = amount_text[1:]
            head = amount_text[:1]
            amount_text = head.upper()+amount
        return amount_text
    
    def get_tong(self, o):
        qty = 0
        dongia = 0
        thanhtien = 0
        for line in o.hopdong_line:
            qty+=line.product_qty
            dongia += line.price_unit
            thanhtien += line.price_subtotal
        return {
            'qty': qty,
            'dongia': dongia,
            'thanhtien': thanhtien,    
        }
    def get_delivery_order(self, picking_id):
        if picking_id:
            nguon_hang = ''
            picking = self.pool.get('stock.picking').browse(self.cr,self.uid,picking_id)
            for line in picking.move_lines:
                if len(picking.move_lines) == 1:
                    nguon_hang = line.hop_dong_mua_id.name
                else:
                    nguon_hang = line.hop_dong_mua_id.name + ' - '
            return {
                    'pt_giaohang': picking.pt_giaohang,
                    'ngay_xuat_kho': picking.date_done,
                    'nguon_hang': nguon_hang,
                    }
        else:
            return {
                    'pt_giaohang': '',
                    'ngay_xuat_kho': '',
                    'nguon_hang': '',
                    }
            
    def get_cang_den(self,bl_id):
        bl = self.pool.get('draft.bl').browse(self.cr,self.uid,bl_id)
        return bl.port_of_charge.name or ''
        
    def get_giaohang(self, hopdong_id):
        bl_ids = []
        sql = '''
            select draft_bl_id, picking_id, etd_date, eta_date, cuoc_tau from draft_bl_line where draft_bl_id in (select id from draft_bl where hopdong_id = %s)
        '''%(hopdong_id)
        self.cr.execute(sql)
        bl_ids = self.cr.dictfetchall()
        return bl_ids
        
    def get_thanhtoan(self, hopdong_id):
        account_voucher_ids = []
        sql = '''
            select amount, date, journal_id from account_voucher where type = 'receipt' and hop_dong_id = %s and state = 'posted'
            order by id
        '''%(hopdong_id)
        self.cr.execute(sql)
        account_voucher_ids = self.cr.dictfetchall()
        return account_voucher_ids
    
    def get_journal(self, journal_id):
        if journal_id:
            journal = self.pool.get('account.journal').browse(self.cr,self.uid,journal_id)
            return journal.name
        else:
            return ''
            
        
    def get_ngaynhan_lc(self, hopdong_id):
        hop_dong = self.pool.get('hop.dong').browse(self.cr,self.uid,hopdong_id)
        if hop_dong.dk_thanhtoan_id.loai == 'lc':
            sql = '''
                select id from account_voucher where type = 'receipt' and hop_dong_id = %s and state = 'posted'
                order by id
            '''%(hopdong_id)
            self.cr.execute(sql)
            account_voucher_ids = [r[0] for r in self.cr.fetchall()]
            if account_voucher_ids:
                account = self.pool.get('account.voucher').browse(self.cr,self.uid,account_voucher_ids[0])
                return account.date
            else:
                return ''
        else:
            return ''
             
    def get_so_phuluc(self, hop_dong_id):
        so_phuluc = ''
        tu_ngay = ''
        sql = '''
            select name, tu_ngay from phuluc_hop_dong where type = 'hd_ngoai' and hop_dong_id = %s
        '''%(hop_dong_id)
        self.cr.execute(sql)
        phuluc_ids = self.cr.dictfetchall()
        if phuluc_ids:
            for phuluc in phuluc_ids:
                so_phuluc += phuluc['name'] + ' '
                tu_ngay += phuluc['tu_ngay'] + ' '
        return {
                'so_phuluc': so_phuluc,
                'tu_ngay': tu_ngay,
                }
    
    def get_price_hh(self,product_id,hop_dong_id): 
        price_unit = 0.0
        sql = '''
            select price_unit from hopdong_hoahong_line where hopdong_hh_id = %s and product_id = %s
        '''%(hop_dong_id,product_id)
        self.cr.execute(sql)
        price_unit = self.cr.dictfetchone()['price_unit']
        return price_unit
    
    def get_tax_hh(self,o):
        line = o.hopdong_hoahong_line[0]
        return line.tax_hh
        
        
        
    
    
        
        