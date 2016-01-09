# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class xuly_hangtra_line(osv.osv_memory):
    _name = 'xuly.hangtra.line'
    _columns = {
        'xuly_id': fields.many2one('xuly.hangtra.cuakhachhang','Xu ly'),
        'product_code': fields.char('Mã sản phẩm', size = 1024),
        'product_id': fields.many2one('product.product', 'Sản phẩm'),
        'product_qty': fields.float('Số lượng'),
        'product_uom': fields.many2one('product.uom', 'Đơn vị quy đổi'),
        'prodlot_id': fields.many2one('stock.production.lot', 'Lô hàng'),
        'tracking_id': fields.many2one('stock.tracking', 'Kệ'),
        'location_id': fields.many2one('stock.location', 'Vị trí kho'),
        'location_dest_id': fields.many2one('stock.location', 'Vị trí đích'),
        'move_id': fields.many2one('stock.move','Hang Tra KH'),
        }
xuly_hangtra_line()  

class xuly_hangtra_cuakhachhang(osv.osv_memory):
    _name = "xuly.hangtra.cuakhachhang"
    
    def _get_move_lines(self, cr, uid, ids, context=None):
        xuly_hangtra_lines = []
        return_cus_id = ids['active_id']
        picking = self.pool.get('stock.picking').browse(cr,uid,return_cus_id)
        for line in picking.move_lines:
            xuly_hangtra_lines.append((0,0,{
                                            'product_code': line.product_code,
                                           'product_id': line.product_id.id,
                                           'product_qty': line.qty_hangtra_conlai,
                                           'product_uom': line.product_uom and line.product_uom.id or False,
                                           'prodlot_id': line.prodlot_id and line.prodlot_id.id or False,
                                           'tracking_id': line.tracking_id and line.tracking_id.id or False,
                                           'location_id': line.location_id and line.location_id.id or False,
                                           'location_dest_id': line.location_dest_id and line.location_dest_id.id or False,
                                           'move_id': line.id,
                                            }))
        return xuly_hangtra_lines
    
    _columns = {
        'name':fields.selection([('trahang_ncc','Trả hàng cho nhà cung cấp'),('huy_hang','Hủy hàng')],'Loại xử lý', required=True),
        'picking_in_id': fields.many2one('stock.picking.in', 'Phiếu nhập'),
        'xuly_hangtra_line': fields.one2many('xuly.hangtra.line','xuly_id','Tra Hang'),
    }
    _defaults = {
        'name': 'trahang_ncc',
        'xuly_hangtra_line': _get_move_lines,
    }
    
    def mo_phieu_nhap(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        xuly = self.browse(cr, uid, ids[0])
        xuly_trahang_ncc = []
        return_cus_id = context.get('active_id', False)
        if return_cus_id:
            self.pool.get('stock.picking.out').write(cr, uid, [return_cus_id], {'loai_xuly':xuly.name,'xuly_thncc_id': xuly.picking_in_id.id})
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'stock', 'view_stock_return_picking_form')
        for line in xuly.xuly_hangtra_line:
            xuly_trahang_ncc.append({
                                            'xuly_id': line.xuly_id and line.xuly_id.id or False,
                                            'product_code': line.product_code,
                                            'product_id': line.product_id and line.product_id.id or False,
                                            'product_qty': line.product_qty,
                                            'product_uom': line.product_uom and line.product_uom.id or False,
                                            'prodlot_id': line.prodlot_id and line.prodlot_id.id or False,
                                            'tracking_id': line.tracking_id and line.tracking_id.id or False,
                                            'location_id': line.location_id and line.location_id.id or False,
                                            'location_dest_id': line.location_dest_id and line.location_dest_id.id or False,
                                            'move_id': line.move_id and line.move_id.id or False,
                                          })
#             sql = '''
#                 update stock_move set hang_tra_kh_move_id = %s where picking_id = %s and product_id = %s and hang_tra_kh_move_id is null
#             '''%(line.move_id.id, xuly.picking_in_id.id, line.product_id.id)
#             cr.execute(sql)
        ctx = context
        ctx.update({
            'active_id': xuly.picking_in_id.id,
            'active_ids': [xuly.picking_in_id.id],
            'active_model': 'stock.picking.in',
            'xuly_trahang_ncc': xuly_trahang_ncc,
        })
        return {
                    'name': 'Phiếu nhập hàng mua',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.return.picking',
                    'domain': [],
#                     'res_id': xuly.picking_in_id.id,
                    'type': 'ir.actions.act_window',
                    'view_id': res[1],
                    'context':ctx,
                    'target': 'new',
                    
                }
        
    def taophieu_chuyenkhohuy(self, cr, uid, ids, context=None):
        move_lines = []
        line = self.browse(cr, uid, ids[0])
        return_cus_id = context.get('active_id', False)
        picking = self.pool.get('stock.picking').browse(cr,uid,return_cus_id)
        stock_journal_ids = self.pool.get('stock.journal').search(cr, uid, [('name','=','Xử lý hàng hư hỏng')])
        location_parent_ids = self.pool.get('stock.location').search(cr,uid,[('usage', '=', 'view'),('name', '=', 'Virtual Locations')])
        location_huy_id = self.pool.get('stock.location').search(cr,uid,[('usage', '=', 'inventory'),('location_id', '=', location_parent_ids[0]),('name', '=', 'Scrapped')])
        for xuly in line.xuly_hangtra_line:
            move_lines.append((0,0,{
                                    'product_code': xuly.product_code,
                                   'product_id': xuly.product_id.id,
                                   'product_qty': xuly.product_qty,
                                   'product_uom': xuly.product_uom and xuly.product_uom.id or False,
                                   'prodlot_id': xuly.prodlot_id and xuly.prodlot_id.id or False,
                                   'tracking_id': xuly.tracking_id and xuly.tracking_id.id or False,
                                    'location_id': xuly.location_dest_id and xuly.location_dest_id.id or False,
                                    'location_dest_id': location_huy_id[0],
                                   'name': xuly.product_id.name,
                                   'hang_tra_kh_move_id': xuly.move_id.id,
                                    }))
        vals = {
            'stock_journal_id': stock_journal_ids and stock_journal_ids[0] or False,
            'type': 'internal',
            'return': 'none',
            'move_lines': move_lines,
            'partner_id': picking.partner_id and picking.partner_id.id or False,
            'origin': picking.name + ':' + picking.origin,
        }
        vals.update(
            self.pool.get('stock.picking').onchange_journal(cr, uid, [], stock_journal_ids and stock_journal_ids[0] or False)['value']
        )
        xuly_huyhang_id = self.pool.get('stock.picking').create(cr, uid, vals)
        if return_cus_id:
            self.pool.get('stock.picking.out').write(cr, uid, [return_cus_id], {'loai_xuly':line.name,'xuly_huyhang_id': xuly_huyhang_id})
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'general_stock', 'view_picking_subinventory_form')
        return {
                    'name': 'Xử lý mất mát, hư hỏng',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.picking',
                    'domain': [],
                    'res_id': xuly_huyhang_id,
                    'view_id': res[1],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                }
    
xuly_hangtra_cuakhachhang()