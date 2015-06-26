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
    
    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit, line.product_qty, line.product_id, line.hopdong_id.partner_id)['taxes']:
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
            for line in order.hopdong_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('hopdong.line').browse(cr, uid, ids, context=context):
            result[line.hopdong_id.id] = True
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
    
    _columns = {
        'name':fields.char('Số', size = 1024,required = True),
        'type':fields.selection([('hd_noi','Hợp đồng nội'),('hd_ngoai','Hợp đồng ngoại'),('hd_mua','Hợp đồng mua')],'Loại hợp đồng' ,required=True,readonly=True, states={'moi_tao': [('readonly', False)]}),
        'tu_ngay':fields.date('Từ ngày',required = True,readonly=True, states={'moi_tao': [('readonly', False)]}),
        'den_ngay':fields.date('Đến ngày'),
        'ngay_nhanhang':fields.date('Ngày nhận hàng'),
        'diadiem_nhanhang':fields.char('Địa điểm nhận hàng'),
        'port_of_loading':fields.char('Port of loading'),
        'port_of_charge':fields.char('Port of charge'),
        'partial_shipment':fields.boolean('Partial shipment'),
        'transshipment':fields.char('Transshipment'),
        'thongbao_nhanhang':fields.char('Thông báo nhận hàng'),
        'destinaltion':fields.char('Destinaltion'),
        'arbitration_id': fields.many2one('sale.arbitration','Arbitration',readonly=True, states={'moi_tao': [('readonly', False)]}),
        'phucluc_hd':fields.text('Phụ lục Hợp đồng'),
        'phuongthuc_thanhtoan':fields.text('Phương thức thanh toán'),
        'company_id': fields.many2one('res.company','Công ty',required = True,readonly=True, states={'moi_tao': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner','Khách hàng',required = True,domain="[('customer','=',True)]",readonly=True, states={'moi_tao': [('readonly', False)]}),
        'hopdong_line': fields.one2many('hopdong.line','hopdong_id','Line',readonly=True, states={'moi_tao': [('readonly', False)]}),
        
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
        'state': fields.selection([
            ('moi_tao', 'Mới tạo'),
            ('da_duyet', 'Đã duyệt'),
            ('het_han', 'Hết hạn'),
            ('huy_bo', 'Hủy bỏ'),
            ], 'Trạng thái',readonly=True, states={'moi_tao': [('readonly', False)]}),
    }
    
    def _get_phuongthuc_thanhtoan(self,cr, uid, context=None):
        property = self.pool.get('admin.property')._get_project_property_by_name(cr, uid, 'properties_phuongthucthanhtoan')
        return property and property.value or False
    
    _defaults = {
        'type': 'hd_noi',
        'tu_ngay': time.strftime('%Y-%m-%d'),
        'state': 'moi_tao',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hop.dong', context=c),
        'phuongthuc_thanhtoan': _get_phuongthuc_thanhtoan,
    }
    
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
                'datas': datas,
                'nodestroy' : True
                }
        else:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'hop_dong_ngoai_report',
                'datas': datas,
                'nodestroy' : True
            }
    
    def duyet(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'da_duyet'})
    
    def het_han(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'het_han'})
    
    def huy_bo(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'huy_bo'})
    
    def set_to_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'moi_tao'})
    
hop_dong()

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
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res
    _columns = {
        'hopdong_id': fields.many2one('hop.dong', 'Hợp đồng', required=True, ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True,),
        'name':fields.char('Name',size=1024,required=True),
        'product_uom': fields.many2one('product.uom', 'Đơn vị tính'),
        'product_qty': fields.float('Số lượng', digits_compute= dp.get_precision('Product UoS')),
        'price_unit': fields.float('Đơn giá', digits_compute= dp.get_precision('Product Price')),
        'tax_id': fields.many2many('account.tax', 'hopdong_order_tax', 'hopdong_id', 'tax_id', 'Taxes'),
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
hopdong_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
