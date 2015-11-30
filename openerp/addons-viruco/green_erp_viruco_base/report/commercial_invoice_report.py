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
        self.gross_weight = 0
        self.net_weight = 0
        self.package = 0
        self.amount = 0
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
            'get_product': self.get_product,
            'get_master_data': self.get_master_data,
            'get_ocean': self.get_ocean,
            'get_packages_weight': self.get_packages_weight, 
            'get_bl_line': self.get_bl_line,
            'get_sum_all': self.get_sum_all,
            'get_product_line': self.get_product_line,
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
                'to': '',
                'discharge': '',
                'consignee': '',
#                 'consignee_add': '',
                'notify_party': '',
                'notify_party_add': '',
                'date_eng': '',
                }
        if draft_bl_ids:
            draft_bl_id = self.pool.get('draft.bl').browse(self.cr,self.uid,draft_bl_ids[0])
            res.update({'name': draft_bl_id.name,
                        'contract_no': draft_bl_id.hopdong_id and draft_bl_id.hopdong_id.name or '',
                        'buyer': draft_bl_id.hopdong_id and draft_bl_id.hopdong_id.partner_id and draft_bl_id.hopdong_id.partner_id.name or '',
                        'address': draft_bl_id.hopdong_id and draft_bl_id.hopdong_id.partner_id and self.display_address(draft_bl_id.hopdong_id.partner_id) or '',
                        'mean_tran': draft_bl_id.mean_transport or '',
                        'bl_no': draft_bl_id.bl_no,
                        'date_ship': self.convert_date(draft_bl_id.date),
                        'from': draft_bl_id.port_of_loading and draft_bl_id.port_of_loading.name or '',
                        'to': draft_bl_id.diadiem_nhanhang and draft_bl_id.diadiem_nhanhang.name or '',
                        'discharge': draft_bl_id.port_of_charge and draft_bl_id.port_of_charge.name or '',
                        'consignee': self.get_consignee(draft_bl_id),
#                         'consignee': draft_bl_id.consignee_id and draft_bl_id.consignee_id.name or '',
#                         'consignee_add': draft_bl_id.consignee_id and self.display_address(draft_bl_id.consignee_id) or '' ,
                        'notify_party': draft_bl_id.notify_party_id and draft_bl_id.notify_party_id.name or '',
                        'notify_party_add': draft_bl_id.notify_party_id and self.display_address(draft_bl_id.notify_party_id) or '' ,
                        'date_eng': draft_bl_id.date[8:10] + ' ' + self.get_month_name(int(draft_bl_id.date[5:7])) +'. '+ draft_bl_id.date[:4],
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
    
    def sum_net_weight(self,line):
        sum = 0
        for product in line.description_line:
            sum += product.net_weight
        return sum
    
    def sum_gross_weight(self,line): 
        sum = 0
        for product in line.description_line:
            sum += product.gross_weight
        return sum
    
    def sum_price_subtotal(self):
        wizard_data = self.localcontext['data']['form']
        draft_bl_ids = wizard_data['draft_bl_line_id']
        res = {'total': 0,
               'unit':0,}
        draft_bl_line_id = self.pool.get('draft.bl.line').browse(self.cr,self.uid,draft_bl_ids[0])
        total = draft_bl_line_id.hopdong_line_id and draft_bl_line_id.hopdong_line_id.price_subtotal or 0.0 
        unit = draft_bl_line_id.hopdong_line_id and draft_bl_line_id.hopdong_line_id.price_unit or 0.0 
        res.update({'total': total,
                    'unit':unit,
                    })
        return res
    
    def sum_packages(self,line): 
        sum = 0
        line1 = ''
        res = {'sum': 0,
               'strline': '',}
        for product in line.description_line:
            sum += product.packages_qty
            line1 = str(sum) + ' '+ (product.packages_id and product.packages_id.name or '')
            res.update({'sum' : sum,
                       'strline': line1,})
        return res
    
    def get_product(self): 
        wizard_data = self.localcontext['data']['form']
        draft_bl_ids = wizard_data['draft_bl_line_id']
        draft_bl_line_id = self.pool.get('draft.bl.line').browse(self.cr,self.uid,draft_bl_ids[0])
        product = draft_bl_line_id.hopdong_line_id and draft_bl_line_id.hopdong_line_id.product_id and draft_bl_line_id.hopdong_line_id.product_id.eng_name or ''
        return product
    
    def get_ocean(self): 
        wizard_data = self.localcontext['data']['form']
        draft_bl_ids = wizard_data['draft_bl_line_id']
        draft_bl_line_id = self.pool.get('draft.bl.line').browse(self.cr,self.uid,draft_bl_ids[0])
        product = draft_bl_line_id.ocean_vessel or ''
        return product
    
    def get_packages_weight(self): 
        wizard_data = self.localcontext['data']['form']
        draft_bl_ids = wizard_data['draft_bl_line_id']
        sum = 0
        line1 = ''
        line2 = ''
        res = {'sum': 0,
                'weight': '',}
        draft_bl_line_id = self.pool.get('draft.bl.line').browse(self.cr,self.uid,draft_bl_ids[0])
        for line in draft_bl_line_id.description_line:
            sum += line.packages_qty
            line1 = line.packages_weight
        if line1 == '33.33':
            line2 = '33.33 Kgs/Bale'
        elif line1 == '35':
            line2 = '35 Kgs/Bale'
        elif line1 == '1.20':
            line2 = '1.20 Mts/Pallet'
        elif line1 == '1.26':
            line2 = '1.26 Mts/Pallet'
        res.update({ 'sum': sum,
                    'weight': line2,})
        return res
    
    def get_bl_line(self): 
        wizard_data = self.localcontext['data']['form']
        draft_bl_ids = wizard_data['draft_bl_line_id']
        draft_bl_line_id = self.pool.get('draft.bl.line').browse(self.cr,self.uid,draft_bl_ids[0])
        return draft_bl_line_id
    
    def get_product_line(self,o):
        re = []
        self.gross_weight = 0
        self.net_weight = 0
        self.package = 0
        self.amount = 0
        for line in o.draft_bl_line:
            if line.option and line.option == 'product':
                net_weight = self.sum_net_weight(line)
                gross_weight = self.sum_gross_weight(line)
                package = self.sum_packages(line)
                self.gross_weight += gross_weight
                self.net_weight += net_weight
                self.package += package['sum']
                self.amount += line.hopdong_line_id and line.hopdong_line_id.price_subtotal or 0
                res.append({ 'product': line.hopdong_line_id and line.hopdong_line_id.eng_name or '',
                            'package': package['sum'],
                            'net_weight': net_weight,
                            'gross_weight': gross_weight,
                            'price': line.hopdong_line_id and line.hopdong_line_id.price_unit or 0,
                            'amount': line.hopdong_line_id and line.hopdong_line_id.price_subtotal or 0,
                            })
            elif line.option and line.option == 'seal_no':
                for seal in line.seal_descript_line:
                    self.gross_weight += seal.gross_weight or 0
                    self.net_weight += seal.net_weight or 0
                    self.package += seal.packages_qty or 0
                    self.amount += seal.hopdong_line_id and seal.hopdong_line_id.price_subtotal or 0
                    res.append({ 'product': seal.hopdong_line_id and seal.hopdong_line_id.eng_name or '',
                                'package': str(seal.packages_qty or 0) +' '+ (seal.packages_id and seal.packages_id.name or ''),
                                'net_weight': seal.net_weight or 0,
                                'gross_weight': seal.gross_weight or 0,
                                'price': seal.hopdong_line_id and seal.hopdong_line_id.price_unit or 0,
                                'amount': seal.hopdong_line_id and seal.hopdong_line_id.price_subtotal or 0,
                                })
        return True
    
    def get_sum_all(self):
        return {'package': self.package, 
                'net_weight': self.net_weight,
                'gross_weight': self.gross_weight,
                'amount': self.amount,
                }
        
    def get_date_name(self,date):
        date_name = date and (date[8:10] + ' ' + self.get_month_name(int(date[5:7])) +'. '+ date[:4]) or ''
        return date_name
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
