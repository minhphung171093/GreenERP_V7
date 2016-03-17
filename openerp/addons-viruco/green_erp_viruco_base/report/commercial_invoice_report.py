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
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

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
        self.pack = ''
        self.pack_weight = ''
        self.localcontext.update({
            'convert_date':self.convert_date,
            'display_address':self.display_address,
            'get_packages': self.get_packages,
            'sum_net_weight': self.sum_net_weight,
            'sum_gross_weight': self.sum_gross_weight,
#             'sum_price_subtotal': self.sum_price_subtotal, 
            'sum_packages': self.sum_packages,
            'convert': self.convert,
            'get_packages_packing_list': self.get_packages_packing_list,
            'get_consignee': self.get_consignee,
#             'get_product': self.get_product,
#             'get_master_data': self.get_master_data,
            'get_ocean': self.get_ocean,
            'get_packages_weight': self.get_packages_weight, 
#             'get_bl_line': self.get_bl_line,
            'get_sum_all': self.get_sum_all,
            'get_product_line': self.get_product_line,
            'get_date_name': self.get_date_name,
            'get_prepaid': self.get_prepaid,
            'get_packing_list': self.get_packing_list,
            'get_etd_date': self.get_etd_date,
            'get_cong': self.get_cong,
            'get_freight':self.get_freight,
            'get_bl_no':self.get_bl_no,
            'get_the_tich':self.get_the_tich,
        })
    
#     def get_master_data(self):
#         wizard_data = self.localcontext['data']['form']
#         draft_bl_ids = wizard_data['draft_bl_id']
#         res = {'name': '',
#                'contract_no': '',
#                 'buyer': '',
#                 'address': '',
#                 'mean_tran': '',
#                 'bl_no': '',
#                 'date_ship': '',
#                 'from': '',
#                 'to': '',
#                 'discharge': '',
#                 'consignee': '',
# #                 'consignee_add': '',
#                 'notify_party': '',
#                 'notify_party_add': '',
#                 'date_eng': '',
#                 }
#         if draft_bl_ids:
#             draft_bl_id = self.pool.get('draft.bl').browse(self.cr,self.uid,draft_bl_ids[0])
#             res.update({'name': draft_bl_id.name,
#                         'contract_no': draft_bl_id.hopdong_id and draft_bl_id.hopdong_id.name or '',
#                         'buyer': draft_bl_id.hopdong_id and draft_bl_id.hopdong_id.partner_id and draft_bl_id.hopdong_id.partner_id.name or '',
#                         'address': draft_bl_id.hopdong_id and draft_bl_id.hopdong_id.partner_id and self.display_address(draft_bl_id.hopdong_id.partner_id) or '',
#                         'mean_tran': draft_bl_id.mean_transport or '',
#                         'bl_no': draft_bl_id.bl_no,
#                         'date_ship': self.convert_date(draft_bl_id.date),
#                         'from': draft_bl_id.port_of_loading and draft_bl_id.port_of_loading.name or '',
#                         'to': draft_bl_id.diadiem_nhanhang and draft_bl_id.diadiem_nhanhang.name or '',
#                         'discharge': draft_bl_id.port_of_charge and draft_bl_id.port_of_charge.name or '',
#                         'consignee': self.get_consignee(draft_bl_id),
# #                         'consignee': draft_bl_id.consignee_id and draft_bl_id.consignee_id.name or '',
# #                         'consignee_add': draft_bl_id.consignee_id and self.display_address(draft_bl_id.consignee_id) or '' ,
#                         'notify_party': draft_bl_id.notify_party_id and draft_bl_id.notify_party_id.name or '',
#                         'notify_party_add': draft_bl_id.notify_party_id and self.display_address(draft_bl_id.notify_party_id) or '' ,
#                         'date_eng': draft_bl_id.date[8:10] + ' ' + self.get_month_name(int(draft_bl_id.date[5:7])) +'. '+ draft_bl_id.date[:4],
#                         })
#         return res
    
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
            consignee = draft_bl.consignee_id.name +'\n'+ self.display_address(draft_bl.consignee_id) +'\n' + (draft_bl.consignee_id.phone and ('TEL: ' + draft_bl.consignee_id.phone) or '') or ''
        elif draft_bl.consignee_text:
            consignee =  draft_bl.consignee_text or ''
        else:
            consignee = 'To Order'
        return consignee
    
    def sum_net_weight(self,line):
        sum = 0
        for product in line.seal_descript_line:
            sum += product.net_weight
        return sum
    
    def sum_gross_weight(self,line): 
        sum = 0
        for product in line.seal_descript_line:
            sum += product.gross_weight
        return sum
    
#     def sum_price_subtotal(self):
#         wizard_data = self.localcontext['data']['form']
#         draft_bl_ids = wizard_data['draft_bl_line_id']
#         res = {'total': 0,
#                'unit':0,}
#         draft_bl_line_id = self.pool.get('draft.bl.line').browse(self.cr,self.uid,draft_bl_ids[0])
#         total = draft_bl_line_id.hopdong_line_id and draft_bl_line_id.hopdong_line_id.price_subtotal or 0.0 
#         unit = draft_bl_line_id.hopdong_line_id and draft_bl_line_id.hopdong_line_id.price_unit or 0.0 
#         res.update({'total': total,
#                     'unit':unit,
#                     })
#         return res
    
    def sum_packages(self,line): 
        sum = 0
        line1 = ''
        res = {'sum': 0,
               'strline': '',
               'name': ''}
        for product in line.seal_descript_line:
            sum += product.packages_qty
            line1 = str(round(sum,0)) + ' '+ (product.packages_id and product.packages_id.name_eng or '')
            res.update({'sum' : round(sum,0),
                       'strline': line1,
                       'name': product.packages_id.name_eng,})
        return res
    
#     def get_product(self): 
#         wizard_data = self.localcontext['data']['form']
#         draft_bl_ids = wizard_data['draft_bl_line_id']
#         draft_bl_line_id = self.pool.get('draft.bl.line').browse(self.cr,self.uid,draft_bl_ids[0])
#         product = draft_bl_line_id.hopdong_line_id and draft_bl_line_id.hopdong_line_id.product_id and draft_bl_line_id.hopdong_line_id.product_id.eng_name or ''
#         return product
    
    def get_ocean(self,o): 
        ocean = ''
        for line in o.draft_bl_line:
            ocean += line.ocean_vessel + ', 'or ''
        ocean = ocean and ocean[:-2] or ''
        return ocean

    def get_bl_no(self,o): 
        bl_no = ''
        for line in o.draft_bl_line:
            bl_no = line.bl_no or ''
        return bl_no
    
    def get_the_tich(self,o): 
        tt = 0
        for line in o.draft_bl_line:
            if line.line_number:
                tt = line.line_number * 25
        return tt
    
    def get_packages_weight(self,line1): 
        line2 = ''
        if line1 == '33.33':
            line2 = '33.33 Kgs/Bale'
        elif line1 == '35':
            line2 = '35 Kgs/Bale'
        elif line1 == '1.20':
            line2 = '1.20 Mts/Pallet'
        elif line1 == '1.26':
            line2 = '1.26 Mts/Pallet'
        return line2

    def get_freight(self, freight):
        tam = ''
        if freight == 'prepaid':
            tam = 'Prepaid'
        if freight == 'collect':
            tam = 'Collect'
        return tam
    
#     def get_bl_line(self): 
#         wizard_data = self.localcontext['data']['form']
#         draft_bl_ids = wizard_data['draft_bl_line_id']
#         draft_bl_line_id = self.pool.get('draft.bl.line').browse(self.cr,self.uid,draft_bl_ids[0])
#         return draft_bl_line_id
    
    def get_product_line(self,o):
        res = []
        for line in o.draft_bl_line:
            if line.option and line.option == 'product':
                net_weight = self.sum_net_weight(line)
                gross_weight = self.sum_gross_weight(line)
                package = self.sum_packages(line)
                total = net_weight * (line.hopdong_line_id and line.hopdong_line_id.price_unit or 0)
                self.gross_weight += gross_weight
                self.net_weight += net_weight
                self.package += package['sum']
                self.amount += total
                seal_no = ''
                product = ''
                pack_weight = ''
                for seal in line.seal_descript_line:
#                     seal_no += seal.container_no_seal and (seal.container_no_seal + '/') 
#                     seal_no += '/' + seal.seal_no and (seal.seal_no + '\n') or ''
                    pack_weight = seal.packages_weight or ''
                    product = line.hopdong_line_id and line.hopdong_line_id.product_id and line.hopdong_line_id.product_id.eng_name + ' ' + line.hopdong_line_id.product_id.default_code or '' 
                res.append({ 'product': product,
                            'package': package['sum'],
                            'net_weight': round(net_weight,2),
                            'gross_weight': round(gross_weight,2),
                            'price': line.hopdong_line_id and line.hopdong_line_id.price_unit or 0,
                            'amount': total,
                            'strpack': package['strline'],
                            'seal_no': seal_no,
                            'packages_name': package['name'],
                            'pack_weight': self.get_packages_weight(pack_weight),
                            'draft_bl': 'draft_bl',
                            'invoice_thue': 'invoice_thue',
                            })
            elif line.option and line.option == 'seal_no':
                product_total = ''
                for seal in line.description_line:
                    total = (seal.net_weight or 0) * (seal.hopdong_line_id and seal.hopdong_line_id.price_unit or 0)
                    self.gross_weight += seal.gross_weight or 0
                    self.net_weight += seal.net_weight or 0
                    self.package += seal.packages_qty or 0
                    self.amount += total
                    product = seal.hopdong_line_id.product_id.default_code or ''
                    product_total += seal.hopdong_line_id.product_id.default_code and (seal.hopdong_line_id.product_id.default_code + '\n') or ''
                    res.append({ 'product': product,
                                'package': seal.packages_qty or 0,
                                'strpack': str(seal.packages_qty and round(seal.packages_qty) or 0) +' '+ (seal.packages_id and seal.packages_id.name or ''),
                                'net_weight': seal.net_weight and round(seal.net_weight,2) or 0,
                                'gross_weight': seal.gross_weight and round(seal.gross_weight,2) or 0,
                                'price': seal.hopdong_line_id and seal.hopdong_line_id.price_unit or 0,
                                'amount': total,
                                'seal_no': line.container_no_seal + '/' + line.seal_no or '',
                                'packages_name': seal.packages_id.name or '',
                                'pack_weight': self.get_packages_weight(seal.packages_weight),
                                'draft_bl': '',
                                'invoice_thue': 'invoice_thue',
                                })
                res.append({ 'product': product_total,
                                'package': self.package or 0,
                                'strpack': self.package or 0,
                                'net_weight': self.net_weight or 0,
                                'gross_weight': self.gross_weight or 0,
                                'price': seal.hopdong_line_id and seal.hopdong_line_id.price_unit or 0,
                                'amount': self.amount,
                                'seal_no': line.container_no_seal + '/' + line.seal_no or '',
                                'packages_name': seal.packages_id.name or '',
                                'pack_weight': self.get_packages_weight(seal.packages_weight),
                                'draft_bl': 'draft_bl',
                                'invoice_thue': '',
                                })
        return res
    
    def get_sum_all(self):
        return {'package': round(self.package), 
                'net_weight': round(self.net_weight,2),
                'gross_weight': round(self.gross_weight,2),
                'amount': round(self.amount,2),
                'pack': self.pack,
                'pack_weight': self.pack_weight,
                }
        
    def get_date_name(self,date):
        if date:
            date_name = date and (date[8:10] + ' ' + self.get_month_name(int(date[5:7])) +'. '+ date[:4]) or ''
            return date_name
        else:
            return ''
    
    def get_etd_date(self,o):
        if o.draft_bl_line:
            line = o.draft_bl_line[0]
            return line.etd_date
        else:
            return ''
        
    def get_cong(self,o):
        if o.draft_bl_line:
            line = o.draft_bl_line[0]
            if line.option == 'product':
                return line.line_number
            else:
                return 1
        else:
            return 0
        
    
    def get_prepaid(self,hd_id):
        amount = 0.0
        if hd_id:
            if hd_id.dk_thanhtoan_id:
                amount = (hd_id.dk_thanhtoan_id.dat_coc * self.amount)/200
        return amount
    
    def get_packing_list(self,o):
        res = []
        for line in o.draft_bl_line:
            if line.option and line.option == 'product':
                res.append({ 'product': line.hopdong_line_id and line.hopdong_line_id.product_id and line.hopdong_line_id.product_id.eng_name + ' ' + line.hopdong_line_id.product_id.default_code or '',
                            'package': '',
                            'form': '',
                            'net_weight': '',
                            'gross_weight': '',
                            })
                res.append({ 'product': 'CONTAINER NO. / SEAL NO.',
                            'package': '',
                            'form': '',
                            'net_weight': '',
                            'gross_weight': '',
                            })
                for detail in line.seal_descript_line:
                    res.append({ 'product': detail.container_no_seal + '/' + detail.seal_no or '',
                            'package': detail.packages_qty and round(detail.packages_qty) or 0,
                            'form': detail.packages_weight,
                            'net_weight': detail.net_weight and round(detail.net_weight,2) or 0,
                            'gross_weight': detail.gross_weight and round(detail.gross_weight,2) or 0,
                            })
                    self.pack = detail.packages_id.name or ''
                    self.pack_weight = self.get_packages_weight(detail.packages_weight)
            if line.option and line.option == 'seal_no':
                res.append({ 'product': line.container_no_seal + '/' + line.seal_no or '',
                            'package': '',
                            'form': '',
                            'net_weight': '',
                            'gross_weight': '',
                            })
                res.append({ 'product': 'Product',
                            'package': '',
                            'form': '',
                            'net_weight': '',
                            'gross_weight': '',
                            })
                for detail in line.description_line:
                    res.append({ 'product': detail.hopdong_line_id and detail.hopdong_line_id.product_id and detail.hopdong_line_id.product_id.eng_name + ' '+ detail.hopdong_line_id.product_id.default_code or '',
                            'package': detail.packages_qty and round(detail.packages_qty) or 0,
                            'form': detail.packages_weight,
                            'net_weight': detail.net_weight and round(detail.net_weight,2) or 0,
                            'gross_weight': detail.gross_weight and round(detail.gross_weight,2) or 0,
                            })
                    self.pack = detail.packages_id.name or ''
                    self.pack_weight = self.get_packages_weight(detail.packages_weight)
            
        return res
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
