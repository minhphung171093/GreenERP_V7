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


class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'thoigian_giaohang':fields.datetime('Thời gian giao hàng'),
        'nguoi_gioithieu_id':fields.many2one('res.partner','Người giới thiệu',readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'dieukien_giaohang_id':fields.many2one('dieukien.giaohang','Điều kiện giao hàng'),
        'hop_dong_id':fields.many2one('hop.dong','Hợp đồng',readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'hinhthuc_giaohang_id':fields.many2one('hinhthuc.giaohang','Hình thức giao hàng'),
        'so_chuyenphatnhanh':fields.char('Số chuyển phát nhanh',size=1024),
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
    }
    
    def action_button_confirm(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        sale_line_obj = self.pool.get('sale.order.line')
        hop_dong_obj = self.pool.get('hop.dong')
        hop_dong_line_obj = self.pool.get('hop.dong.line')
        for sale in self.browse(cr, uid, ids):
            if sale.hop_dong_id:
                for hd_line in sale.hop_dong_t_id.hopdong_line:
                    sql = '''
                        select product_id, sum(product_uom_qty) as total_qty
                        from sale_order_line l
                        inner join sale_order s on l.order_id = s.id
                        where s.hop_dong_t_id = %s and s.partner_id = %s and l.product_id = %s and s.state in ('done','progress')
                        group by product_id
                    '''%(sale.hop_dong_t_id.id,sale.partner_id.id,hd_line.product_id.id)
                    cr.execute(sql)
                    lines_qty = cr.dictfetchall()
                    product_uom_qty = 0
                    sale_order_lines = sale_line_obj.search(cr,uid,[('order_id','=',sale.id),('product_id','=',hd_line.product_id.id)])
                    if sale_order_lines:
                        product_uom_qty = sale_line_obj.browse(cr,uid,sale_order_lines[0]).product_uom_qty
                        price_unit = sale_line_obj.browse(cr,uid,sale_order_lines[0]).price_unit
                        if hd_line.tax_id != sale_line_obj.browse(cr,uid,sale_order_lines[0]).tax_id:
                            raise osv.except_osv(_('Warning!'),_('Không thể duyệt sản phẩm thuế khác thuế trong hợp đồng: %s!')%(hd_line.tax_id))
                        if hd_line.price_unit != price_unit:
                            raise osv.except_osv(_('Warning!'),_('Không thể duyệt sản phẩm với đơn giá khác đơn giá trong hợp đồng: %s!')%(hd_line.price_unit))
                        for line_qty in lines_qty:
                            if line_qty['total_qty'] + product_uom_qty > hd_line.product_qty:
                                raise osv.except_osv(_('Warning!'),_('Không thể duyệt sản phẩm với số lượng lớn hơn số lượng trong hợp đồng thầu: %s!')%(hd_line.product_qty))
        raise osv.except_osv(_('Cảnh báo!'),_('Dung lai de kien tra!'))
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'sale.order', ids[0], 'order_confirm', cr)
        return True
    
    def _prepare_order_picking(self, cr, uid, order, context=None):
        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        return {
            'name': pick_name,
            'origin': order.name,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'type': 'out',
            'state': 'auto',
            'move_type': order.picking_policy,
            'sale_id': order.id,
            'partner_id': order.partner_shipping_id.id,
            'note': order.note,
            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
            'company_id': order.company_id.id,
            'nguoi_denghi_id': order.user_id and order.user_id.id or False,
        }
#Them hop dong tren stock move khj confirm sale    
    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):
        location_id = order.shop_id.warehouse_id.lot_stock_id.id
        output_id = order.shop_id.warehouse_id.lot_output_id.id
        return {
            'name': line.name,
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id)\
                    or line.product_uom.id,
            'product_packaging': line.product_packaging.id,
            'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
            'location_id': location_id,
            'location_dest_id': output_id,
            'sale_line_id': line.id,
            'tracking_id': False,
            'state': 'draft',
            #'state': 'waiting',
            'company_id': order.company_id.id,
            'price_unit': line.product_id.standard_price or 0.0,
            'hop_dong_ban_id': order.hop_dong_id and order.hop_dong_id.id or False,
            'chatluong_id': line.product_id.chatluong_id and line.product_id.chatluong_id.id or False,
            'quycach_donggoi_id': line.product_id.quycach_donggoi_id and line.product_id.quycach_donggoi_id.id or False,
            'quycach_baobi_id': line.product_id.quycach_baobi_id and line.product_id.quycach_baobi_id.id or False,
        }
    
sale_order()
class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns = {
                'chatluong_id':fields.many2one('chatluong.sanpham','Chất lượng'),
                'quycach_donggoi_id':fields.many2one('quycach.donggoi','Quy cách đóng gói'),
                }
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        lang = lang or context.get('lang',False)
        if not  partner_id:
            raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
        warning = {}
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        context = {'lang': lang, 'partner_id': partner_id}
        if partner_id:
            lang = partner_obj.browse(cr, uid, partner_id).lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)

        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False
        fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
        if update_tax: #The quantity only have changed
            result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)

        if not flag:
            result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
            if product_obj.description_sale:
                result['name'] += '\n'+product_obj.description_sale
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}
        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
        # get unit price

        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                    'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        })[pricelist]
            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                result.update({'price_unit': price})
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        result.update({'chatluong_id': product_obj.chatluong_id.id,'quycach_donggoi_id': product_obj.quycach_donggoi_id.id})
        return {'value': result, 'domain': domain, 'warning': warning}
sale_order_line()  
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
