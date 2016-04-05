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
from datetime import datetime
from openerp.tools.translate import _
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
# from green_erp_pharma_report.report import amount_to_text_vn
class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.context = context
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_partner_address':self.get_partner_address,
            'get_so_hd':self.get_so_hd,
            'get_ngay_hd':self.get_ngay_hd,
            'get_ngay_hethan':self.get_ngay_hethan,
            'get_date':self.get_date,
            'get_bienban_giaonhan': self.get_bienban_giaonhan,
            'get_nhanvien_donggoi': self.get_nhanvien_donggoi,
            'get_so_thung': self.get_so_thung,
            'get_line':self.get_line,
            'get_picking': self.get_picking,
            'get_stt': self.get_stt,
        })
    
    def get_stt(self,seq_1,seq):
        stt = 1
        for s,picking in enumerate(self.get_picking()):
            if s<seq_1:
                stt += len(picking.move_lines)
            if s==seq_1:
                for s2,line in enumerate(picking.move_lines):
                    if s2<seq:
                        stt += 1
        return stt
       
    def get_nhanvien_donggoi(self, picking_out_id):
        nhanvien = ''
        picking_out_obj = self.pool.get('stock.picking.out')
        picking = picking_out_obj.browse(self.cr, self.uid, picking_out_id)
        if picking.picking_packaging_line:
            for seq_2,line in enumerate(picking.picking_packaging_line):
                if line.employee_id:
                    nhanvien = line.employee_id and line.employee_id.name or ''
#                     else:
#                         nhanvien += line.employee_id and ', ' + line.employee_id.name or ''
        return nhanvien
    
    def get_so_thung(self, picking_out_id):
        loai_thung = ''
        picking_out_obj = self.pool.get('stock.picking.out')
        picking = picking_out_obj.browse(self.cr, self.uid, picking_out_id)
        if picking.picking_packaging_line:
            for seq_2,line in enumerate(picking.picking_packaging_line):
                if seq_2 == 0:
                    loai_thung += line.loai_thung_id and line.loai_thung_id.name or ''
                else:
                    loai_thung += line.loai_thung_id and ', ' + line.loai_thung_id.name or ''
        return loai_thung
    
    def get_bienban_giaonhan(self):
        return self.pool.get('ir.sequence').get(self.cr, self.uid, 'bienban.giaonhan') 

    def get_date(self, date=False):
        res={}
        if not date:
            date = time.strftime('%Y-%m-%d')
        day = date[8:10],
        month = date[5:7],
        year = date[:4],
        res={
            'day' : day,
            'month' : month,
            'year' : year,
            }
        return res
    
    def get_partner_address(self, picking):
        address = ''
        if picking.diachi_giaohang_id:
            address += picking.diachi_giaohang_id.name or ''
        else:
            if picking.partner_id:
                address += picking.partner_id.street or ''
                address += picking.partner_id.state_id and ', ' + picking.partner_id.state_id.name or ''
                address += picking.partner_id.country_id and ', ' + picking.partner_id.country_id.name or ''
        return address
    
    def get_so_hd(self, picking):
        invoice_ids = self.pool.get('account.invoice').search(self.cr,self.uid,[('name','=',picking.name)])
        if invoice_ids:
            invoice = self.pool.get('account.invoice').browse(self.cr,self.uid,invoice_ids[0])
            so_hd = invoice.reference_number
        else:
            so_hd = ''
        return so_hd
    
    def get_picking(self, picking_out_id):
        picking_out_obj = self.pool.get('stock.picking.out')
        return picking_out_obj.browse(self.cr, self.uid, picking_out_id)
    
    def get_line(self,picking):
        res = []
        sql= '''
            select ac.reference_number as shd, ac.date_invoice as nhd, pt.name as sp,pu.name as dvt, acl.quantity, 
                spl.name as slo, spl.life_date as hdung
            from account_invoice_line acl
            left join account_invoice ac on acl.invoice_id = ac.id
            left join product_template pt on acl.product_id = pt.id
            left join product_uom pu on pt.uom_id = pu.id
            left join stock_production_lot spl on acl.prodlot_id = spl.id
            where ac.name= '%s'
        '''%(picking.name)
        self.cr.execute(sql)
        for line in self.cr.dictfetchall():
            res.append({
                        'shd': line['shd'],
                        'nhd': line['nhd'],
                        'sp': line['sp'],
                        'dvt':line['dvt'],
                        'quantity':line['quantity'],
                        'slo':line['slo'],
                        'hdung':line['hdung'],
                    })
        return res
    def get_ngay_hd(self, date):
        if date:
            ngay_hd = datetime.strptime(date, DATE_FORMAT)
            ngay_hd = ngay_hd.strftime('%d-%m-%Y')
        else:
            ngay_hd = ''
        return ngay_hd
    
    def get_ngay_hethan(self, life_date):
        if life_date:
            ngay_hh = datetime.strptime(life_date, DATETIME_FORMAT) + timedelta(hours=7)
            ngay_hh = ngay_hh.strftime('%m-%Y')
        else:
            ngay_hh = ''
        return ngay_hh
    
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: