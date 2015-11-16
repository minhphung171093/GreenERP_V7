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
    
    def get_master_data(self):
        wizard_data = self.localcontext['data']['form']
        draft_bl_ids = wizard_data['draft_bl_id']
        res = {'name': '',
               'contract_no': '',
                'buyer': '',
                'address': '',
                'mean_tran': '',
                'bl_no': '',
                'date_ship': '',
                'from': '',
                'to': '',}
        if draft_bl_ids:
            draft_bl_id = self.pool.get('draft.bl').browse(self.cr,self.uid,draft_bl_ids[0])
            res.update({'name': draft_bl_id.name,
                        'contract_no': draft_bl_id.hopdong_id and draft_bl_id.hopdong_id.name or '',
                        'buyer': draft_bl_id.hopdong_id and draft_bl_id.hopdong_id.partner_id and draft_bl_id.hopdong_id.partner_id.name or '',
                        'address': draft_bl_ido.hopdong_id and draft_bl_id.hopdong_id.partner_id and display_address(draft_bl_id.hopdong_id.partner_id) or '',
                        'mean_tran': draft_bl_id.mean_transport or '',
                        'bl_no': draft_bl_id.bl_no,
                        'date_ship': convert_date(draft_bl_id.date),
                        'from': draft_bl_id.port_of_loading and draft_bl_id.port_of_loading.name or '',
                        'to': draft_bl_id.diadiem_nhanhang and draft_bl_id.diadiem_nhanhang.name or '',
                        })
        return res
    
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
    
    def sum_net_weight(self):
        wizard_data = self.localcontext['data']['form']
        draft_bl_ids = wizard_data['draft_bl_line_id']
        sum = 0
        draft_bl_line_id = self.pool.get('draft.bl').browse(self.cr,self.uid,draft_bl_ids[0])
        for line in draft_bl_line_id.description_line:
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
            sum += line.hopdong_line_id.price_subtotal and line.hopdong_line_id.price_subtotal or 0.0 
        return sum
    
    def sum_packages(self,o):
        sum = 0
        for line in o.draft_bl_line:
            sum += line.packages_qty
        return sum
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
