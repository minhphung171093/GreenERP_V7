# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import time
from datetime import date
from datetime import timedelta
from datetime import datetime
import calendar
import openerp.addons.decimal_precision as dp
import codecs

class hop_dong(osv.osv):
    _name = "hop.dong"
    _order = "tu_ngay"
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(hop_dong, self).default_get(cr, uid, fields, context=context)
        if context.get('default_type')=='hd_ngoai':
            property = self.pool.get('admin.property')._get_project_property_by_name(cr, uid, 'properties_payment_terms')
        else:
            property = self.pool.get('admin.property')._get_project_property_by_name(cr, uid, 'properties_phuongthucthanhtoan')
        res.update({'phuongthuc_thanhtoan':property and property.value or False})
        if context.get('default_type')=='hd_noi':
            property = self.pool.get('admin.property')._get_project_property_by_name(cr, uid, 'properties_quycachdonggoi_chatluong')
            res.update({'quycachdonggoi_chatluong':property and property.value or False})  
        return res
    
    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit, line.product_qty, line.product_id, line.hopdong_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val
    
    def _amount_line_tax_hh(self, cr, uid, line, context=None):
        val = 0.0
        val += line.product_qty*line.price_unit*line.tax_hh/100
#         for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit, line.product_qty, line.product_id, line.hopdong_dh_id.partner_id)['taxes']:
#             val += c.get('amount', 0.0)
        return val
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.company_id.currency_id
            for line in order.hopdong_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res
    
    def _amount_all_hh(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed_hh': 0.0,
                'amount_tax_hh': 0.0,
                'amount_total_hh': 0.0,
            }
            val = val1 = 0.0
            cur = order.company_id.currency_id
            for line in order.hopdong_hoahong_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax_hh(cr, uid, line, context=context)
            res[order.id]['amount_tax_hh'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed_hh'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total_hh'] = res[order.id]['amount_untaxed_hh'] - res[order.id]['amount_tax_hh']
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('hopdong.line').browse(cr, uid, ids, context=context):
            result[line.hopdong_id.id] = True
        return result.keys()
    
    def _get_order_hh(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('hopdong.hoahong.line').browse(cr, uid, ids, context=context):
            result[line.hopdong_hh_id.id] = True
        return result.keys()
    
    def _get_hd_gan_hh(self, cr, uid, ids, name, arg, context=None):        
        res = {}          
        for line in self.browse(cr, uid, ids):
            if line.den_ngay:
                result = False     
                b = datetime.now()
                a = line.den_ngay
                temp = datetime(int(a[0:4]),int(a[5:7]),int(a[8:10]))
                kq = temp - b
                if kq.days <= 15:
                    result = True
                res[line.id] = result
            else:
                res[line.id] = False            
        return res
    def _get_date_payment_canhbao(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            canh_bao = 1
            if line.date_payment:
                date_payment_canhbao = datetime.strptime(line.date_payment,'%Y-%m-%d') + timedelta(days=canh_bao)
                res[line.id]=date_payment_canhbao.strftime('%Y-%m-%d')
                if line.state in ('moi_tao','da_duyet','da_ky'):
                    self.write(cr,uid,[line.id],{'state':'het_han'})
            else:
                res[line.id]=False
        return res    
    def _get_ngay_canhbao(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            canh_bao = 7
            if line.den_ngay:
                ngay_canhbao = datetime.strptime(line.den_ngay,'%Y-%m-%d') + timedelta(days=-canh_bao)
                res[line.id]=ngay_canhbao.strftime('%Y-%m-%d')
            else:
                res[line.id]=False
        return res    
    
    def _get_create_theodoi_hopdong(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            sql = '''
                delete from theodoi_hopdong_line where hopdong_id = %s and hopdong_id in (select id from hop_dong where type = 'hd_ngoai')
            '''%(line.id)
            cr.execute(sql)
            if line.type == 'hd_ngoai':
                sql = '''
                    select hop_dong_mua_id from stock_move where hop_dong_ban_id = %s and hop_dong_mua_id is not null 
                    group by hop_dong_mua_id
                '''%(line.id)
                cr.execute(sql)
                mua_ids = cr.dictfetchall()
                if mua_ids:
                    for hd in mua_ids:
                        hd_mua = self.pool.get('hop.dong').browse(cr,uid,hd['hop_dong_mua_id'])
                        sql = '''
                            select id from draft_bl where hopdong_id = %s
                        '''%(line.id)
                        cr.execute(sql)
                        bl_ids = cr.dictfetchall()
                        if bl_ids:
                            for draft_bl in bl_ids:
                                bl = self.pool.get('draft.bl').browse(cr,uid,draft_bl['id'])
                                if bl.draft_bl_line:
                                    for bl_line in bl.draft_bl_line:
                                        if bl_line.description_line:
                                            for good in bl_line.description_line:
                                                self.pool.get('theodoi.hopdong.line').create(cr,uid,{
                                                                                                   'hopdong_id': line.id,
                                                                                                   'name': hd_mua.name + ' - ' + hd_mua.partner_id.name,
                                                                                                   'freight': bl.freight,
                                                                                                   'shipping_line_id': bl.shipping_line_id and bl.shipping_line_id.id or False,
                                                                                                   'forwarder_line_id': bl.forwarder_line_id and bl.forwarder_line_id.id or False,
                                                                                                   'bl_no': bl.bl_no,
                                                                                                   'seal_no': good.container_no_seal,
                                                                                                   })
                                else:
                                    self.pool.get('theodoi.hopdong.line').create(cr,uid,{
                                                                                           'hopdong_id': line.id,
                                                                                           'name': hd_mua.name + ' - ' + hd_mua.partner_id.name,
                                                                                           'freight': bl.freight,
                                                                                           'shipping_line_id': bl.shipping_line_id and bl.shipping_line_id.id or False,
                                                                                           'forwarder_line_id': bl.forwarder_line_id and bl.forwarder_line_id.id or False,
                                                                                           'bl_no': bl.bl_no,
                                                                                           })
                        else:
                            self.pool.get('theodoi.hopdong.line').create(cr,uid,{
                                                                                                   'hopdong_id': line.id,
                                                                                                   'name': hd_mua.name + ' - ' + hd_mua.partner_id.name,
                                                                                                   })
                else:
                    sql = '''
                        select id from draft_bl where hopdong_id = %s
                    '''%(line.id)
                    cr.execute(sql)
                    bl_ids = cr.dictfetchall()
                    if bl_ids:
                        for draft_bl in bl_ids:
                            bl = self.pool.get('draft.bl').browse(cr,uid,draft_bl['id'])
                            if bl.draft_bl_line:
                                for bl_line in bl.draft_bl_line:
                                    if bl_line.description_line:
                                        for good in bl_line.description_line:
                                            self.pool.get('theodoi.hopdong.line').create(cr,uid,{
                                                                                               'hopdong_id': line.id,
                                                                                               'freight': bl.freight,
                                                                                               'shipping_line_id': bl.shipping_line_id and bl.shipping_line_id.id or False,
                                                                                               'forwarder_line_id': bl.forwarder_line_id and bl.forwarder_line_id.id or False,
                                                                                               'bl_no': bl.bl_no,
                                                                                               'seal_no': good.container_no_seal,
                                                                                               })
                                    else:
                                        self.pool.get('theodoi.hopdong.line').create(cr,uid,{
                                                                                               'hopdong_id': line.id,
                                                                                               'freight': bl.freight,
                                                                                               'shipping_line_id': bl.shipping_line_id and bl.shipping_line_id.id or False,
                                                                                               'forwarder_line_id': bl.forwarder_line_id and bl.forwarder_line_id.id or False,
                                                                                               'bl_no': bl.bl_no,
                                                                                               })
                    
        return res    
    _columns = {
        'name':fields.char('Số', size = 1024,required = True,readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'user_id':fields.many2one('res.users','Người đề nghị',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'type':fields.selection([('hd_noi','Hợp đồng nội'),('hd_ngoai','Hợp đồng ngoại'),('hd_mua_trongnuoc','Hợp đồng mua trong nước'),('hd_mua_nhapkhau','Hợp đồng mua nhập khẩu')],'Loại hợp đồng' ,required=True,readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'tu_ngay':fields.date('Từ ngày',required = True,readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'den_ngay':fields.date('Đến ngày',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'ngay_nhanhang':fields.char('Ngày nhận hàng', size=1024),
        'diadiem_nhanhang':fields.many2one('place.of.delivery', 'Địa điểm nhận hàng',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'port_of_loading':fields.many2one('port.of.loading', 'Port of loading',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'port_of_charge':fields.many2one('port.of.discharge', 'Port of discharge',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'destination_port':fields.many2one('destination.port','Destination port',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'partial_shipment':fields.boolean('Partial shipment',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'transshipment':fields.selection([('allowed','Allowed'),('not_allowed','Not Allowed')],'Transshipment', states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'thongbao_nhanhang':fields.char('Thông báo nhận hàng',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'chat_luong':fields.char('Chất lượng',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'destinaltion':fields.many2one('res.country','Country',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'arbitration_id': fields.many2one('sale.arbitration','Arbitration',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
#         'phucluc_hd':fields.text('Phụ lục Hợp đồng'),
        'phuongthuc_thanhtoan':fields.text('Phương thức thanh toán',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'quycachdonggoi_chatluong': fields.text('Quy cách đóng gói và chất lượng sản phẩm',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'company_id': fields.many2one('res.company','Công ty',required = True,readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'currency_company_id': fields.many2one('res.currency', 'Currency',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner','Khách hàng',required = True,readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'hopdong_line': fields.one2many('hopdong.line','hopdong_id','Line',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'hopdong_hoahong_line': fields.one2many('hopdong.hoahong.line','hopdong_hh_id','Line',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'pricelist_id': fields.many2one('product.pricelist', 'Bảng giá', required=True,readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency", string="Tiền tệ", readonly=True, required=True),
        'donbanhang_id': fields.many2one('don.ban.hang', 'Đơn bán hàng',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'donmuahang_id': fields.many2one('don.mua.hang', 'Đơn mua hàng',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'thanhtoan':fields.boolean('Thanh toán'),
        'ngay_thanhtoan':fields.date('Ngày thanh toán'),
        'dagui_nganhang':fields.boolean('Đã gửi ngân hàng'),
        'ngaygui_nganhang':fields.date('Ngày gửi ngân hàng'),
        'dagui_hopdong':fields.boolean('Đã gửi hợp đồng'),
        'ngaygui_hopdong':fields.date('Ngày gửi hợp đồng'),
        'dagui_hoadon':fields.boolean('Đã gửi hóa đơn'),
        'ngaygui_hoadon':fields.date('Ngày gửi hóa đơn'),
        'dagui_chungtugoc':fields.boolean('Đã gửi chứng từ gốc'),
        'ngaygui_chungtugoc':fields.date('Ngày gửi chứng từ gốc'),
        'dk_giaohang_id': fields.many2one('dieukien.giaohang', 'Điều kiện giao hàng',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'dk_thanhtoan_id': fields.many2one('dk.thanhtoan', 'Điều kiện thanh toán',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Cộng',
            store={
                'hop.dong': (lambda self, cr, uid, ids, c={}: ids, ['hopdong_line'], 10),
                'hopdong.line': (_get_order, ['price_unit', 'tax_id', 'product_qty'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Thuế GTGT',
            store={
                'hop.dong': (lambda self, cr, uid, ids, c={}: ids, ['hopdong_line'], 10),
                'hopdong.line': (_get_order, ['price_unit', 'tax_id', 'product_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tổng cộng',
            store={
                'hop.dong': (lambda self, cr, uid, ids, c={}: ids, ['hopdong_line'], 10),
                'hopdong.line': (_get_order, ['price_unit', 'tax_id', 'product_qty'], 10),
            },
            multi='sums', help="The total amount."),
                
        'amount_untaxed_hh': fields.function(_amount_all_hh, digits_compute=dp.get_precision('Account'), string='Cộng',
            store={
                'hop.dong': (lambda self, cr, uid, ids, c={}: ids, ['hopdong_hoahong_line'], 10),
                'hopdong.hoahong.line': (_get_order_hh, ['price_unit', 'tax_id', 'product_qty'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax_hh': fields.function(_amount_all_hh, digits_compute=dp.get_precision('Account'), string='Thuế GTGT',
            store={
                'hop.dong': (lambda self, cr, uid, ids, c={}: ids, ['hopdong_hoahong_line'], 10),
                'hopdong.hoahong.line': (_get_order_hh, ['price_unit', 'tax_id', 'product_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total_hh': fields.function(_amount_all_hh, digits_compute=dp.get_precision('Account'), string='Tổng cộng',
            store={
                'hop.dong': (lambda self, cr, uid, ids, c={}: ids, ['hopdong_hoahong_line'], 10),
                'hopdong.hoahong.line': (_get_order_hh, ['price_unit', 'tax_id', 'product_qty'], 10),
            },
            multi='sums', help="The total amount."),
        'state': fields.selection([
            ('moi_tao', 'Mới tạo'),
            ('da_duyet', 'Đã duyệt'),
            ('da_ky', 'Đã ký hợp đồng'),
            ('het_han', 'Hết hiệu lực'),
            ('thuc_hien', 'Đang chờ giao hàng(chờ chứng từ)'),
            ('thuc_hien_xongchungtu', 'Đang chờ giao hàng(xong chứng từ)'),
            ('giaohang_chochungtu', 'Đã giao hàng(chờ chứng từ)'),
            ('giaohang_xongchungtu', 'Đã giao hàng(xong chứng từ)'),
            ('thanh_toan', 'Đã thanh toán'),
            ('huy_bo', 'Hủy bỏ'),
            ], 'Trạng thái',readonly=True, states={'moi_tao': [('readonly', False)]}),
        'ngay_canhbao': fields.function(_get_ngay_canhbao, type='date', string='Ngày cảnh báo'),
        'date_payment':fields.date('Ngày thanh toán',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'date_payment_canhbao': fields.function(_get_date_payment_canhbao, type='date', string='Ngày cảnh báo'),
        'theodoi_hopdong_line': fields.one2many('theodoi.hopdong.line','hopdong_id','Line',readonly=True,states={'moi_tao': [('readonly', False)], 'da_duyet': [('readonly', False)], 'da_ky': [('readonly', False)], 'het_han': [('readonly', False)]}),
        'create_theodoi_hopdong': fields.function(_get_create_theodoi_hopdong, type='char', string='create_theodoi_hopdong'),
    }
    
    _defaults = {
        'type': 'hd_noi',
        'tu_ngay': time.strftime('%Y-%m-%d'),
        'state': 'moi_tao',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hop.dong', context=c),
        'currency_company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id,
        'user_id': lambda self, cr, uid, context=None: uid,
    }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_hopdong_id'):
            sql = '''
                select id from hop_dong
                    where type = 'hd_ngoai' and state not in ('moi_tao','da_duyet','da_ky','het_han') and id not in (select hopdong_id from draft_bl where hopdong_id is not null)
            '''
            cr.execute(sql)
            hopdong_ids = [row[0] for row in cr.fetchall()]
            if context.get('hopdong_id'):
                hopdong_ids.append(context.get('hopdong_id'))
            args += [('id','in',hopdong_ids)]
        return super(hop_dong, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
    
    def bt_list_phieuxuat(self, cr, uid, ids, context=None):
        for hd in self.browse(cr,uid,ids):
            sql = '''
                select picking_id from stock_move where hop_dong_ban_id = %s and picking_id is not null 
                and picking_id in (select id from stock_picking where type = 'out')
            '''%(hd.id)
            cr.execute(sql)
            phieuxuat_ids = [row[0] for row in cr.fetchall()]
        if phieuxuat_ids:    
            form_view = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'view_picking_out_form')
            tree_view = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'view_picking_out_tree')
            return {
                        'name': 'Phiếu xuất hàng bán',
                        'view_type': 'form',
                        'view_mode': 'tree, form',
                        'view_id': False,
                        'res_model': 'stock.picking.out',
                        'domain':[('id', 'in', phieuxuat_ids)],
                        'target': 'current',
                        'views': [(tree_view and tree_view[1] or False, 'tree'),
                                  (form_view and form_view[1] or False, 'form')],
                        'type': 'ir.actions.act_window',
                        'res_id': phieuxuat_ids,
                    }
        else:
            raise osv.except_osv(_('Warning!'),_('Không có phiếu xuất hàng bán nào thuộc hợp đồng số  %s')%(hd.name))  
        
    def bt_list_phieunhap(self, cr, uid, ids, context=None):
        for hd in self.browse(cr,uid,ids):
            sql = '''
                select picking_id from stock_move where hop_dong_mua_id = %s and picking_id is not null 
                and picking_id in (select id from stock_picking where type = 'in')
            '''%(hd.id)
            cr.execute(sql)
            phieunhap_ids = [row[0] for row in cr.fetchall()]
        if phieunhap_ids:    
            form_view = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'view_picking_in_form')
            tree_view = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'view_picking_in_tree')
            return {
                        'name': 'Phiếu nhập hàng mua',
                        'view_type': 'form',
                        'view_mode': 'tree, form',
                        'view_id': False,
                        'res_model': 'stock.picking.in',
                        'domain':[('id', 'in', phieunhap_ids)],
                        'target': 'current',
                        'views': [(tree_view and tree_view[1] or False, 'tree'),
                                  (form_view and form_view[1] or False, 'form')],
                        'type': 'ir.actions.act_window',
                        'res_id': phieunhap_ids,
                    }
        else:
            raise osv.except_osv(_('Warning!'),_('Không có phiếu nhập hàng mua nào thuộc hợp đồng số  %s')%(hd.name))  
        
        
    def print_hopdong(self, cr, uid, ids, context=None):
        hopdong = self.browse(cr, uid, ids[0])
        datas = {
             'ids': ids,
             'model': 'hop.dong',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        if hopdong.type == 'hd_noi':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'hopdong_noi_report',
#                 'datas': datas,
#                 'nodestroy' : True
                }
        elif hopdong.type=='hd_mua_trongnuoc':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'hopdong_mua_report',
#                 'datas': datas,
#                 'nodestroy' : True
            }
        elif hopdong.type=='hd_mua_nhapkhau':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'hopdong_mua_report',
#                 'datas': datas,
#                 'nodestroy' : True
            }
        else:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'hopdong_ngoai_report',
#                 'datas': datas,
#                 'nodestroy' : True
            }
    
    def het_han(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'het_han'})
    
    def duyet(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'da_duyet'})
    
    def ky_hd(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'da_ky'})
    
    def huy_bo(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'huy_bo'})
    
    def set_to_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'moi_tao'})
    
    def onchange_pricelist_id(self, cr, uid, ids, pricelist_id, order_lines, context=None):
        context = context or {}
        if not pricelist_id:
            return {}
        value = {
            'currency_id': self.pool.get('product.pricelist').browse(cr, uid, pricelist_id, context=context).currency_id.id
        }
        if not order_lines:
            return {'value': value}
        warning = {
#             'title': _('Cảnh báo!'),
#             'message' : _('Nếu bạn thay đổi bảng giá cho hợp đồng này thì giá của những sản phẩm đã được chọn sẽ không được cập nhật!')
        }
        return {'warning': warning, 'value': value}
    
    def onchange_donbanhang_id(self, cr, uid, ids, donbanhang_id=False, context=None):
        vals = {}
        order_line = []
        hd_hoahong_line = []
        if donbanhang_id:
            dbh_obj = self.pool.get('don.ban.hang')
            dbh = dbh_obj.browse(cr, uid, donbanhang_id)
            for dbh_line in dbh.don_ban_hang_line:
                val_line={
                    'product_id': dbh_line.product_id and dbh_line.product_id.id or False,
                    'name':dbh_line.name,
                    'product_uom': dbh_line.product_uom and dbh_line.product_uom.id or False,
                    'product_qty': dbh_line.product_qty,
                    'price_unit': dbh_line.price_unit,
                    'chatluong_id': dbh_line.chatluong_id and dbh_line.chatluong_id.id or False,
                    'quycach_donggoi_id': dbh_line.quycach_donggoi_id and dbh_line.quycach_donggoi_id.id or False,
                    'tax_id': [(6,0,[t.id for t in dbh_line.tax_id])],
                }
                order_line.append((0,0,val_line))
            for hh_line in dbh.donhang_hoahong_line:
                hd_hh_value={
                    'product_id': hh_line.product_id and hh_line.product_id.id or False,
                    'product_uom': hh_line.product_uom and hh_line.product_uom.id or False,
                    'product_qty': hh_line.product_qty,
                    'price_unit': hh_line.price_unit,
#                     'tax_id': [(6,0,[t.id for t in hh_line.tax_id])],
                    'tax_hh': hh_line.tax_hh,
                }
                hd_hoahong_line.append((0,0,hd_hh_value))
            vals = {
                'partner_id': dbh.partner_id and dbh.partner_id.id or False,
                'pricelist_id': dbh.pricelist_id and dbh.pricelist_id.id or False,
                'port_of_loading': dbh.port_of_loading and dbh.port_of_loading.id or False,
                'port_of_charge': dbh.port_of_charge and dbh.port_of_charge.id or False,
                'diadiem_nhanhang': dbh.diadiem_nhanhang and dbh.diadiem_nhanhang.id or False,
                'ngay_nhanhang': dbh.ngay_nhanhang,
                'destinaltion': dbh.destinaltion and dbh.destinaltion.id or False,
                'destination_port': dbh.destination_port and dbh.destination_port.id or False,
                'partial_shipment': dbh.partial_shipment,
                'transshipment': dbh.transshipment,
                'arbitration_id': dbh.arbitration_id and dbh.arbitration_id.id or False,
                'dk_giaohang_id': dbh.dieukien_giaohang_id and dbh.dieukien_giaohang_id.id or False,
                'dk_thanhtoan_id': dbh.dk_thanhtoan_id and dbh.dk_thanhtoan_id.id or False,
                'hopdong_line': order_line,
                'hopdong_hoahong_line': hd_hoahong_line,
            }
        return {'value': vals}
    
    def onchange_donmuahang_id(self, cr, uid, ids, donmuahang_id=False, context=None):
        vals = {}
        order_line = []
        if donmuahang_id:
            dmh_obj = self.pool.get('don.mua.hang')
            dmh = dmh_obj.browse(cr, uid, donmuahang_id)
            for dmh_line in dmh.don_mua_hang_line:
                val_line={
                    'product_id': dmh_line.product_id and dmh_line.product_id.id or False,
                    'name':dmh_line.name,
                    'product_uom': dmh_line.product_uom and dmh_line.product_uom.id or False,
                    'product_qty': dmh_line.product_qty,
                    'price_unit': dmh_line.price_unit,
                    'tax_id': [(6,0,[t.id for t in dmh_line.tax_id])],
                }
                order_line.append((0,0,val_line))
            vals = {
                'partner_id': dmh.partner_id.id,
                'pricelist_id': dmh.pricelist_id.id,
                'hopdong_line': order_line,
            }
        return {'value': vals}
    
hop_dong()

class hopdong_hoahong_line(osv.osv):
    _name = 'hopdong.hoahong.line'
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_qty, line.product_id, line.hopdong_hh_id.partner_id)
            if line.hopdong_hh_id:
                cur = line.hopdong_hh_id.company_id.currency_id
            else:
                cur = line.hopdong_dh_id.company_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res
    
    _columns = {
        'hopdong_hh_id': fields.many2one('hop.dong', 'Hợp đồng', ondelete='cascade', select=True),
        'hopdong_dh_id': fields.many2one('don.ban.hang', 'Đơn bán hàng', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True,),
        'product_uom': fields.many2one('product.uom', 'Đơn vị tính'),
        'product_qty': fields.float('Số lượng', digits_compute= dp.get_precision('Product UoS')),
        'price_unit': fields.float('Đơn giá', digits_compute= dp.get_precision('Product Price')),
        'tax_id': fields.many2many('account.tax', 'hopdong_hh_order_tax', 'hopdong_hh_id', 'tax_id', 'Taxes'),
        'tax_hh': fields.float('Thuế hoa hồng (%)'),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
    }
    
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        vals = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {
                    'product_uom':product.uom_id.id or False,
                    'name':product.name,
                    }
        return {'value': vals}
hopdong_hoahong_line()

class theodoi_hopdong_line(osv.osv):
    _name = 'theodoi.hopdong.line'
    
    _columns = {
        'hopdong_id': fields.many2one('hop.dong', 'Hợp đồng', ondelete='cascade', select=True),
        'name': fields.char('Source',size=1024),
        'freight':fields.selection([('prepaid', 'Prepaid'),('collect', 'Collect')], 'Freight'),
        'shipping_line_id': fields.many2one('shipping.line','Shipping line'),
        'forwarder_line_id': fields.many2one('forwarder.line','Forwarder line'),
        'log_in_charge': fields.char('LOGS IN CHARGE',size=1024),
        'doc_in_charge': fields.char('DOCS IN CHARGE',size=1024),
        'seal_no': fields.char('CONT/SEAL NO',size=1024),
        'bl_no': fields.char('BL No',size=1024),
        'dhl_no': fields.char('DHL No',size=1024),
    }
theodoi_hopdong_line()

class hopdong_line(osv.osv):
    _name = 'hopdong.line'
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_qty, line.product_id, line.hopdong_id.partner_id)
            cur = line.hopdong_id.company_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total']) - line.sotien_giam
        return res
    _columns = {
        'hopdong_id': fields.many2one('hop.dong', 'Hợp đồng', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True,),
        'name':fields.char('Name',size=1024,required=True),
        'product_uom': fields.many2one('product.uom', 'Đơn vị tính'),
        'product_qty': fields.float('Số lượng', digits_compute= dp.get_precision('Product UoS')),
        'price_unit': fields.float('Đơn giá', digits_compute= dp.get_precision('Product Price')),
        'tax_id': fields.many2many('account.tax', 'hopdong_order_tax', 'hopdong_id', 'tax_id', 'Taxes'),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
        'chatluong_id':fields.many2one('chatluong.sanpham','Chất lượng'),
        'quycach_donggoi_id':fields.many2one('quycach.donggoi','Quy cách đóng gói'),
        'sotien_giam': fields.float('Số tiền giảm'),
        'hopdong_giam_id': fields.many2one('hop.dong', 'Hợp đồng'),
    }
    
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        vals = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {
                    'product_uom':product.uom_id.id or False,
                    'name':product.name,
                    }
        return {'value': vals}
hopdong_line()

class don_ban_hang(osv.osv):
    _name = "don.ban.hang"
    
    def button_dummy(self, cr, uid, ids, context=None):
        return True
    
    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit, line.product_qty, line.product_id, line.donbanhang_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val
    
    def _amount_line_tax_hh(self, cr, uid, line, context=None):
        val = 0.0
        val += line.product_qty*line.price_unit*line.tax_hh/100
#         for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit, line.product_qty, line.product_id, line.hopdong_dh_id.partner_id)['taxes']:
#             val += c.get('amount', 0.0)
        return val
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.company_id.currency_id
            for line in order.don_ban_hang_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res
    
    def _amount_all_hh(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed_hh': 0.0,
                'amount_tax_hh': 0.0,
                'amount_total_hh': 0.0,
            }
            val = val1 = 0.0
            cur = order.company_id.currency_id
            for line in order.donhang_hoahong_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax_hh(cr, uid, line, context=context)
            res[order.id]['amount_tax_hh'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed_hh'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total_hh'] = res[order.id]['amount_untaxed_hh'] - res[order.id]['amount_tax_hh']
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('don.ban.hang.line').browse(cr, uid, ids, context=context):
            result[line.donbanhang_id.id] = True
        return result.keys()
    
    def _get_order_dh(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('hopdong.hoahong.line').browse(cr, uid, ids, context=context):
            result[line.hopdong_dh_id.id] = True
        return result.keys()

    _columns = {
        'name':fields.char('Số', size = 1024,required = True),
        'type':fields.selection([('dbh_noi','Đơn bán hàng nội'),('dbh_ngoai','Đơn bán hàng ngoại')],'Loại đơn bán hàng'),
        'ngay':fields.date('Ngày',required = True,readonly=True, states={'moi_tao': [('readonly', False)]}),
        'company_id': fields.many2one('res.company','Công ty',required = True,readonly=True, states={'moi_tao': [('readonly', False)]}),
        'diadiem_nhanhang':fields.many2one('place.of.delivery', 'Địa điểm nhận hàng', states={'moi_tao': [('readonly', False)]}),
        'port_of_loading':fields.many2one('port.of.loading', 'Port of loading', states={'moi_tao': [('readonly', False)]}),
        'port_of_charge':fields.many2one('port.of.discharge', 'Port of discharge', states={'moi_tao': [('readonly', False)]}),
        'destinaltion':fields.many2one('res.country','Country', states={'moi_tao': [('readonly', False)]}),
        'partial_shipment':fields.boolean('Partial shipment', states={'moi_tao': [('readonly', False)]}),
        'transshipment':fields.selection([('allowed','Allowed'),('not_allowed','Not Allowed')],'Transshipment', states={'moi_tao': [('readonly', False)]}),
        'arbitration_id': fields.many2one('sale.arbitration','Arbitration',readonly=True, states={'moi_tao': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner','Khách hàng',required = True,readonly=True, states={'moi_tao': [('readonly', False)]}),
        'don_ban_hang_line': fields.one2many('don.ban.hang.line','donbanhang_id','Line',readonly=True, states={'moi_tao': [('readonly', False)]}),
        'pricelist_id': fields.many2one('product.pricelist', 'Bảng giá', required=True, readonly=True, states={'moi_tao': [('readonly', False)]}, help="Pricelist for current sales order."),
        'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency", string="Đơn vị tiền tệ", readonly=True, required=True),
        'currency_company_id': fields.many2one('res.currency', 'Currency'),
        'user_id':fields.many2one('res.users','Người đề nghị',readonly=True,states={'moi_tao': [('readonly', False)]}),
        'ngay_nhanhang':fields.char('Thời gian giao hàng',size=1024),
        'nguoi_gioithieu_id':fields.many2one('res.partner','Người giới thiệu',readonly=True,states={'moi_tao': [('readonly', False)]}),
        'noi_giaohang_id':fields.many2one('noi.giaohang','Nơi giao hàng'),
        'payment_term': fields.many2one('account.payment.term', 'Payment Term'),
        'donhang_hoahong_line': fields.one2many('hopdong.hoahong.line','hopdong_dh_id','Line',readonly=True, states={'moi_tao': [('readonly', False)]}),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Cộng',
            store={
                'don.ban.hang': (lambda self, cr, uid, ids, c={}: ids, ['don_ban_hang_line'], 10),
                'don.ban.hang.line': (_get_order, ['price_unit', 'tax_id', 'product_qty'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Thuế GTGT',
            store={
                'don.ban.hang': (lambda self, cr, uid, ids, c={}: ids, ['don_ban_hang_line'], 10),
                'don.ban.hang.line': (_get_order, ['price_unit', 'tax_id', 'product_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tổng cộng',
            store={
                'don.ban.hang': (lambda self, cr, uid, ids, c={}: ids, ['don_ban_hang_line'], 10),
                'don.ban.hang.line': (_get_order, ['price_unit', 'tax_id', 'product_qty'], 10),
            },
            multi='sums', help="The total amount."),
                
        'amount_untaxed_hh': fields.function(_amount_all_hh, digits_compute=dp.get_precision('Account'), string='Cộng',
            store={
                'don.ban.hang': (lambda self, cr, uid, ids, c={}: ids, ['donhang_hoahong_line'], 10),
                'hopdong.hoahong.line': (_get_order_dh, ['price_unit', 'tax_id', 'product_qty'], 10),
            },
            multi='sum_hh', help="The amount without tax.", track_visibility='always'),
        'amount_tax_hh': fields.function(_amount_all_hh, digits_compute=dp.get_precision('Account'), string='Thuế GTGT',
            store={
                'don.ban.hang': (lambda self, cr, uid, ids, c={}: ids, ['donhang_hoahong_line'], 10),
                'hopdong.hoahong.line': (_get_order_dh, ['price_unit', 'tax_id', 'product_qty'], 10),
            },
            multi='sum_hh', help="The tax amount."),
        'amount_total_hh': fields.function(_amount_all_hh, digits_compute=dp.get_precision('Account'), string='Tổng cộng',
            store={
                'don.ban.hang': (lambda self, cr, uid, ids, c={}: ids, ['donhang_hoahong_line'], 10),
                'hopdong.hoahong.line': (_get_order_dh, ['price_unit', 'tax_id', 'product_qty'], 10),
            },
            multi='sum_hh', help="The total amount."),    
            
        'state': fields.selection([
            ('moi_tao', 'Mới tạo'),
            ('da_duyet', 'Đã duyệt'),
            ('huy_bo', 'Hủy bỏ'),
            ], 'Trạng thái',readonly=True, states={'moi_tao': [('readonly', False)]}),
        'note': fields.text('Terms and conditions'),
        'thoigian_giaohang':fields.char('Thời gian giao hàng', size=1024),
        'nguoi_gioithieu_id':fields.many2one('res.partner','Người giới thiệu',readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'dieukien_giaohang_id':fields.many2one('dieukien.giaohang','Điều kiện giao hàng'),
        'dk_thanhtoan_id': fields.many2one('dk.thanhtoan', 'Điều kiện thanh toán'),
        'hinhthuc_giaohang_id':fields.many2one('hinhthuc.giaohang','Hình thức giao hàng'),
        'so_chuyenphatnhanh':fields.char('Số chuyển phát nhanh',size=1024),
        'destination_port':fields.many2one('destination.port','Destination port'),
        'hinh_thuc_tt':fields.selection([('chuyenkhoan','Chuyển khoản'),('tienmat','Tiền mặt')],'Hình thức thanh toán'),

    }
    
    _defaults = {
        'ngay': time.strftime('%Y-%m-%d'),
        'state': 'moi_tao',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hop.dong', context=c),
        'currency_company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id,
        'user_id': lambda self, cr, uid, context=None: uid,
    }
    
    def duyet(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'da_duyet'})
    
    def onchange_pricelist_id(self, cr, uid, ids, pricelist_id, order_lines, context=None):
        context = context or {}
        if not pricelist_id:
            return {}
        value = {
            'currency_id': self.pool.get('product.pricelist').browse(cr, uid, pricelist_id, context=context).currency_id.id
        }
        if not order_lines:
            return {'value': value}
        warning = {
            'title': _('Cảnh báo!'),
            'message' : _('Nếu bạn thay đổi bảng giá cho hợp đồng này thì giá của những sản phẩm đã được chọn sẽ không được cập nhật!')
        }
        return {'warning': warning, 'value': value}
    
    def onchange_partner_id(self, cr, uid, ids, partner_id=False, context=None):
        context = context or {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr,uid,partner_id)
            value = {
                'nguoi_gioithieu_id': partner.nha_moigioi_id and partner.nha_moigioi_id.id or False
            }
        return {'value': value}
    
    def onchange_don_ban_hang_line(self, cr, uid, ids, don_ban_hang_line,donhang_hoahong_line, context=None):
        context = context or {}
        value = {}
        for dhl in don_ban_hang_line:
            if dhl[0]==0:
                donhang_hoahong_line = []
                hhl = dhl[2]
                hhl['price_unit'] = False
                hhl['tax_id'] = False
                donhang_hoahong_line.append((0,0,hhl))
                value={'donhang_hoahong_line': donhang_hoahong_line}
            else:
                if dhl[2] and 'product_qty' in dhl[2]:
                    line = self.pool.get('don.ban.hang.line').browse(cr,uid,dhl[1])
                    sql = '''
                        select id from hopdong_hoahong_line where product_id = %s and hopdong_dh_id = %s
                    '''%(line.product_id.id, line.donbanhang_id.id)
                    cr.execute(sql)
                    hoahong_id = cr.fetchone()[0]
                    self.pool.get('hopdong.hoahong.line').write(cr,uid,[hoahong_id],{
                                                                                     'product_qty': dhl[2]['product_qty']
                                                                                     })
        return {'value': value}
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_donbanhang_noi'):
            sql = '''
                select id from don_ban_hang
                    where state = 'da_duyet' and type='dbh_noi' and id not in (select donbanhang_id from hop_dong where state != 'cancel' and type='hd_noi' and donbanhang_id is not null)
            '''
            cr.execute(sql)
            dbh_ids = [row[0] for row in cr.fetchall()]
            if context.get('donbanhang_id'):
                dbh_ids.append(context.get('donbanhang_id'))
            args += [('id','in',dbh_ids)]
        if context.get('search_donbanhang_ngoai'):
            sql = '''
                select id from don_ban_hang
                    where state = 'da_duyet' and type='dbh_ngoai' and id not in (select donbanhang_id from hop_dong where state != 'cancel' and type='hd_ngoai' and donbanhang_id is not null)
            '''
            cr.execute(sql)
            dbh_ids = [row[0] for row in cr.fetchall()]
            if context.get('donbanhang_id'):
                dbh_ids.append(context.get('donbanhang_id'))
            args += [('id','in',dbh_ids)]
        return super(don_ban_hang, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
    
    def print_donbanhang(self, cr, uid, ids, context=None):
        dbh = self.browse(cr, uid, ids[0])
        if dbh.type == 'dbh_noi':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'don_ban_hang_noi_report',
                }
        else:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'don_ban_hang_ngoai_report',
            }
    
    def huy_bo(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'huy_bo'})
    
don_ban_hang()

class don_ban_hang_line(osv.osv):
    _name = 'don.ban.hang.line'
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_qty, line.product_id, line.donbanhang_id.partner_id)
            cur = line.donbanhang_id.company_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res
    _columns = {
        'donbanhang_id': fields.many2one('don.ban.hang', 'Đơn bán hàng', required=True, ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True,),
        'name':fields.char('Name',size=1024,required=True),
        'product_uom': fields.many2one('product.uom', 'Đơn vị tính'),
        'product_qty': fields.float('Số lượng', digits_compute= dp.get_precision('Product UoS')),
        'price_unit': fields.float('Đơn giá', digits_compute= dp.get_precision('Product Price')),
        'tax_id': fields.many2many('account.tax', 'don_ban_hang_line_tax_ref', 'don_ban_hang_line_id', 'tax_id', 'Thuế'),
        'price_subtotal': fields.function(_amount_line, string='Thành tiền', digits_compute= dp.get_precision('Account')),
        'chatluong_id':fields.many2one('chatluong.sanpham','Chất lượng'),
        'quycach_donggoi_id':fields.many2one('quycach.donggoi','Quy cách đóng gói'),
    }
    
    def onchange_product_id(self, cr, uid, ids,qty=0,ngay=False,partner_id=False,pricelist_id=False,product_id=False,type=False,context=None):
        vals = {}
        if not ngay:
            ngay = time.strftime('%Y-%m-%d')
        if not partner_id:
            raise osv.except_osv(_('Cảnh báo!'), _('Vui lòng chọn khách hàng trước khi chọn sản phẩm!'))
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {
                    'product_uom':product.uom_id.id or False,
                    'name':product.name,
                    'chatluong_id':product.chatluong_id and product.chatluong_id.id or False,
                    'quycach_donggoi_id':product.quycach_donggoi_id and product.quycach_donggoi_id.id or False,
                    }
            if type == 'dbh_ngoai':
                if product.tax_hd_ngoai:
                    vals.update({'tax_id': [(6,0,[product.tax_hd_ngoai.id])]})
            else:
                vals['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, False, product.taxes_id)
            if pricelist_id:
                price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id],
                        product_id, qty or 1.0, partner_id, {
                            'uom': product.uom_id.id,
                            'date': ngay,
                            })[pricelist_id]
                vals.update({'price_unit': price})
        return {'value': vals}
don_ban_hang_line()

class don_mua_hang(osv.osv):
    _name = "don.mua.hang"
    
    def button_dummy(self, cr, uid, ids, context=None):
        return True
    
    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit, line.product_qty, line.product_id, line.donmuahang_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.company_id.currency_id
            for line in order.don_mua_hang_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('don.mua.hang.line').browse(cr, uid, ids, context=context):
            result[line.donmuahang_id.id] = True
        return result.keys()
    
    _columns = {
        'name':fields.char('Số', size = 1024,required = True),
        'type':fields.selection([('dmh_trongnuoc','Đơn mua hàng trong nước'),('dmh_nhapkhau','Đơn mua hàng nhập khẩu')],'Loại đơn bán hàng'),
        'ngay':fields.date('Ngày',required = True,readonly=True, states={'moi_tao': [('readonly', False)]}),
        'company_id': fields.many2one('res.company','Công ty',required = True,readonly=True, states={'moi_tao': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner','Khách hàng',required = True,readonly=True, states={'moi_tao': [('readonly', False)]}),
        'don_mua_hang_line': fields.one2many('don.mua.hang.line','donmuahang_id','Line',readonly=True, states={'moi_tao': [('readonly', False)]}),
        'pricelist_id': fields.many2one('product.pricelist', 'Bảng giá', required=True, readonly=True, states={'moi_tao': [('readonly', False)]}, help="Pricelist for current sales order."),
        'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency", string="Đơn vị tiền tệ", readonly=True, required=True),
        'currency_company_id': fields.many2one('res.currency', 'Currency'),
        'user_id':fields.many2one('res.users','Người đề nghị',readonly=True,states={'moi_tao': [('readonly', False)]}),
        'thoigian_giaohang':fields.datetime('Thời gian giao hàng'),
        'nguoi_gioithieu_id':fields.many2one('res.partner','Người giới thiệu',readonly=True,states={'moi_tao': [('readonly', False)]}),
        'dieukien_giaohang_id':fields.many2one('dieukien.giaohang','Điều kiện giao hàng'),
        'payment_term': fields.many2one('account.payment.term', 'Payment Term'),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Cộng',
            store={
                'don.mua.hang': (lambda self, cr, uid, ids, c={}: ids, ['don_mua_hang_line'], 10),
                'don.mua.hang.line': (_get_order, ['price_unit', 'tax_id', 'product_qty'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Thuế GTGT',
            store={
                'don.mua.hang': (lambda self, cr, uid, ids, c={}: ids, ['don_mua_hang_line'], 10),
                'don.mua.hang.line': (_get_order, ['price_unit', 'tax_id', 'product_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tổng cộng',
            store={
                'don.mua.hang': (lambda self, cr, uid, ids, c={}: ids, ['don_mua_hang_line'], 10),
                'don.mua.hang.line': (_get_order, ['price_unit', 'tax_id', 'product_qty'], 10),
            },
            multi='sums', help="The total amount."),
        'state': fields.selection([
            ('moi_tao', 'Mới tạo'),
            ('da_duyet', 'Đã duyệt'),
            ('huy_bo', 'Hủy bỏ'),
            ], 'Trạng thái',readonly=True, states={'moi_tao': [('readonly', False)]}),
        'note': fields.char('Terms and conditions'),
    }
    
    _defaults = {
        'ngay': time.strftime('%Y-%m-%d'),
        'state': 'moi_tao',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hop.dong', context=c),
        'currency_company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id,
        'user_id': lambda self, cr, uid, context=None: uid,
    }
    
    def duyet(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'da_duyet'})
    
    def onchange_pricelist_id(self, cr, uid, ids, pricelist_id, order_lines, context=None):
        context = context or {}
        if not pricelist_id:
            return {}
        value = {
            'currency_id': self.pool.get('product.pricelist').browse(cr, uid, pricelist_id, context=context).currency_id.id
        }
        if not order_lines:
            return {'value': value}
        warning = {
            'title': _('Cảnh báo!'),
            'message' : _('Nếu bạn thay đổi bảng giá cho hợp đồng này thì giá của những sản phẩm đã được chọn sẽ không được cập nhật!')
        }
        return {'warning': warning, 'value': value}
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_donmuahang'):
            sql = '''
                select id from don_mua_hang
                    where state = 'da_duyet' and id not in (select donmuahang_id from hop_dong where state != 'cancel' and type='hd_noi' and donmuahang_id is not null)
            '''
            cr.execute(sql)
            dbh_ids = [row[0] for row in cr.fetchall()]
            if context.get('donmuahang_id'):
                dbh_ids.append(context.get('donmuahang_id'))
            args += [('id','in',dbh_ids)]
        return super(don_mua_hang, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
    
    def print_donmuahang(self, cr, uid, ids, context=None):
        dbh = self.browse(cr, uid, ids[0])
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'don_mua_hang_report',
            }
    
    def huy_bo(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'huy_bo'})
    
don_mua_hang()

class don_mua_hang_line(osv.osv):
    _name = 'don.mua.hang.line'
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_qty, line.product_id, line.donmuahang_id.partner_id)
            cur = line.donmuahang_id.company_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res
    _columns = {
        'donmuahang_id': fields.many2one('don.mua.hang', 'Đơn bán hàng', required=True, ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True,),
        'name':fields.char('Name',size=1024,required=True),
        'product_uom': fields.many2one('product.uom', 'Đơn vị tính'),
        'product_qty': fields.float('Số lượng', digits_compute= dp.get_precision('Product UoS')),
        'price_unit': fields.float('Đơn giá', digits_compute= dp.get_precision('Product Price')),
        'tax_id': fields.many2many('account.tax', 'don_mua_hang_line_tax_ref', 'don_mua_hang_line_id', 'tax_id', 'Thuế'),
        'price_subtotal': fields.function(_amount_line, string='Thành tiền', digits_compute= dp.get_precision('Account')),
    }
    
    def onchange_product_id(self, cr, uid, ids,qty=0,ngay=False,partner_id=False,pricelist_id=False,product_id=False, context=None):
        vals = {}
        if not ngay:
            ngay = time.strftime('%Y-%m-%d')
        if not partner_id:
            raise osv.except_osv(_('Cảnh báo!'), _('Vui lòng chọn khách hàng trước khi chọn sản phẩm!'))
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {
                    'product_uom':product.uom_id.id or False,
                    'name':product.name,
                    }
            vals['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, False, product.supplier_taxes_id)
            if pricelist_id:
                price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id],
                        product_id, qty or 1.0, partner_id, {
                            'uom': product.uom_id.id,
                            'date': ngay,
                            })[pricelist_id]
                vals.update({'price_unit': price})
        return {'value': vals}
don_mua_hang_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
