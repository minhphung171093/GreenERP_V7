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
# from openerp.tools import amount_to_text_en
from green_erp_viruco_sale.report import amount_to_text_en

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'convert_date': self.convert_date,
            'get_lines':self.get_lines,
            'get_freight': self.get_freight,
            'get_month': self.get_month,
            'get_bl_type_viruco': self.get_bl_type_viruco,
            'get_bl_type_uythac': self.get_bl_type_uythac,
            'get_bl_type_benthuba': self.get_bl_type_benthuba,
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
    def get_month(self, date):
        if date:
            date = date[3:5]
            return date
        
    def get_freight(self, freight):
        tam = ''
        if freight == 'prepaid':
            tam = 'Prepaid'
        if freight == 'collect':
            tam = 'Collect'
        return tam
    
    
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        hop_dong = []
        sql = '''
            select hd.tu_ngay as date, rp.name as buyer, qc_dg.name_eng as packing, cl_sp.name as quality, sm.product_qty as qty,
            hdl.price_unit as price, hd_hh_l.price_unit as comission, rc.name as country, d_bl.freight as freight, sl.name as shipping_line,
            fl.name as forwarder_line, dbl_l.container_no_seal as con_no_seal_1, dbl_l.seal_no as seal_no_1,
            dl.container_no_seal as con_no_seal_2, dl.seal_no as seal_no_2,
            dbl_l.bl_no as bl_no, d_bl.dhl_no as dhl_no, pp.default_code as descrip,
            dbh.thoigian_giaohang as etd, brokerrp.name as broker, dg.name as term, dg.discharge as discharge, dk_tt.name as payment, 
            hdm.name as ten_hdm, hdm_cus.name as ncc, dbl_l.option as option,d_bl.type as type
                from hopdong_line hdl
                    left join hop_dong hd on hdl.hopdong_id=hd.id
                    left join res_partner rp on hd.partner_id=rp.id
                    left join res_users ru on rp.user_id = ru.id
                    left join res_partner rurp on ru.partner_id=rurp.id
                    left join hopdong_hoahong_line hd_hh_l on hd.id=hd_hh_l.hopdong_hh_id
                    left join draft_bl d_bl on hd.id=d_bl.hopdong_id
                    left join draft_bl_line dbl_l on d_bl.id=dbl_l.draft_bl_id
                    left join res_country rc on d_bl.country_id=rc.id
                    left join shipping_line sl on d_bl.shipping_line_id=sl.id
                    left join forwarder_line fl on d_bl.forwarder_line_id=fl.id
                    left join chatluong_sanpham cl_sp on hdl.chatluong_id=cl_sp.id
                    left join quycach_donggoi qc_dg on hdl.quycach_donggoi_id=qc_dg.id
                    left join product_product pp on hdl.product_id=pp.id
                    left join product_template pt on pp.product_tmpl_id=pt.id
                    left join don_ban_hang dbh on hd.donbanhang_id=dbh.id
                    left join res_partner brokerrp on dbh.nguoi_gioithieu_id=brokerrp.id
                    left join dieukien_giaohang dg on dbh.dieukien_giaohang_id=dg.id
                    left join noi_giaohang ng on dbh.noi_giaohang_id=ng.id
                    left join dk_thanhtoan dk_tt on hd.dk_thanhtoan_id=dk_tt.id
                    left join stock_move sm on sm.hop_dong_ban_id=hd.id
                    left join hop_dong hdm on sm.hop_dong_mua_id=hdm.id
                    left join res_partner hdm_cus on hdm.partner_id=hdm_cus.id
                    left join description_line dl on dl.seal_line_id=dbl_l.id
                where hd.tu_ngay between '%s' and '%s' and hd.type in ('hd_ngoai') and hd.state not in ('moi_tao','huy_bo')
                order by hd.tu_ngay
        '''%(date_from,date_to)
        self.cr.execute(sql)
        for line in self.cr.dictfetchall():
            hop_dong.append({'date': line['date'],
                            'etd': line['etd'],
                            'broker': line['broker'],
                            'buyer':line['buyer'],
                            'descrip': line['descrip'],
                            'packing':line['packing'],
                            'quality':line['quality'],
                            'source': line['ten_hdm'] and (line['ten_hdm']+' - '+line['ncc']) or '',
                            'qty':line['qty'],
                            'price':line['price'],
                            'comission':line['comission'],
                            'term': line['term'],
                            'discharge': line['discharge'],
                            'country':line['country'],
                            'payment': line['payment'],
                            'freight':line['freight'],
                            'shipping_line':line['shipping_line'],
                            'forwarder_line':line['forwarder_line'],
                            'con_seal_no':line['option']=='seal_no' and ((line['con_no_seal_1'] or '')+'/'+(line['seal_no_1'] or '')) or line['option']=='product' and ((line['con_no_seal_2'] or '')+'/'+(line['seal_no_2'] or '')) or '',
                            'bl_no':line['bl_no'],
                            'dhl_no':line['dhl_no'],
                            })
        return hop_dong
    
    def get_bl_type_viruco(self, type):
        if type=='viruco':
            return 'X'
        return ''
    
    def get_bl_type_uythac(self, type):
        if type=='uy_thac':
            return 'X'
        return ''
    
    def get_bl_type_benthuba(self, type):
        if type=='ben_thu_ba':
            return 'X'
        return ''
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
