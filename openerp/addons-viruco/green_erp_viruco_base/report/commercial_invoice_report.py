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
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from green_erp_viruco_base.report import amount_to_text_en
class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'convert_date':self.convert_date,
            'display_address':self.display_address,
            'get_packages': self.get_packages,
            'sum_net_weight': self.sum_net_weight,
            'sum_gross_weight': self.sum_gross_weight,
            'sum_price_subtotal': self.sum_price_subtotal, 
            'sum_packages': self.sum_packages,
            'convert': self.convert,
            'get_packages_packing_list': self.get_packages_packing_list,
            'get_consignee': self.get_consignee,
        })
    
    def convert(self, amount):
        amount_text = amount_to_text_en.amount_to_text(amount, 'en', 'Dollars')
        if amount_text and len(amount_text)>1:
            amount = amount_text[1:]
            head = amount_text[:1]
            amount_text = head.upper()+amount
        return amount_text
    
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def display_address(self, partner):
        address = partner.street and partner.street + ' , ' or ''
        address += partner.street2 and partner.street2 + ' , ' or ''
        address += partner.city and partner.city + ' , ' or ''
        if address:
            address = address[:-3]
        return address
    
    def get_packages(self,line):
        packages = 'PACKING IN' +' '+ str(line.packages_qty or '')
        if line.packages_id:
            packages +=' ' + (line.packages_id.name or '')
        packages +=' '+(line.packages_weight or '')
        return packages
    
    def get_packages_packing_list(self,line):
        packages = 'PACKING IN' +' '+ str(line.packages_qty or '')
#         if line.packages_id:
#             packages +=' ' + (line.packages_id.name or '')
#         packages +=' '+(line.packages_weight or '')
        return packages
    
    def get_month_name(self, month):
        _months = {1:_("JAN"), 2:_("FEB"), 3:_("MAR"), 4:_("APR"), 5:_("MAY"), 6:_("JUN"), 7:_("JUL"), 8:_("AUG"), 9:_("SEP"), 10:_("OCT"), 11:_("NOV"), 12:_("DEC")}
        d = _months[month]
        return d
        
    def get_consignee(self,draft_bl):
        consignee = ''
        if draft_bl.consignee_id:
            consignee = draft_bl.consignee_id.name or ''
        elif draft_bl.consignee_text:
            consignee =  draft_bl.consignee_text or ''
        else:
            consignee = 'To Order'
        return consignee
    
    def sum_net_weight(self,o):
        sum = 0
        for line in o.draft_bl_line:
            sum += line.net_weight
        return sum
    
    def sum_gross_weight(self,o):
        sum = 0
        for line in o.draft_bl_line:
            sum += line.gross_weight
        return sum
    
    def sum_price_subtotal(self,o):
        sum = 0
        for line in o.draft_bl_line:
            sum += line.hopdong_line_id.price_subtotal
        return sum
    
    def sum_packages(self,o):
        sum = 0
        for line in o.draft_bl_line:
            sum += line.packages_qty
        return sum
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
