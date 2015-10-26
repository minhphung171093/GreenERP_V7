# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class xuly_hangtra_cuakhachhang(osv.osv_memory):
    _name = "xuly.hangtra.cuakhachhang"
    _columns = {
        'name':fields.selection([('trahang_ncc','Trả hàng cho nhà cung cấp'),('huy_hang','Hủy hàng')],'Loại xử lý', required=True),
        'picking_in_id': fields.many2one('stock.picking.in', 'Phiếu nhập'),
        
    }
    _defaults = {
        'name': 'trahang_ncc',
    }
    
    def mo_phieu_nhap(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids[0])
        return_cus_id = context.get('active_id', False)
        if return_cus_id:
            self.pool.get('stock.picking.out').write(cr, uid, [return_cus_id], {'loai_xuly':line.name,'xuly_thncc_id': line.picking_in_id.id})
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'stock', 'view_picking_form')
        return {
                    'name': 'Phiếu nhập hàng mua',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.picking.in',
                    'domain': [],
                    'res_id': line.picking_in_id.id,
                    'type': 'ir.actions.act_window',
                    'view_id': res[1],
                    'target': 'current',
                }
        
    def taophieu_chuyenkhohuy(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids[0])
        return_cus_id = context.get('active_id', False)
        stock_journal_ids = self.pool.get('stock.journal').search(cr, uid, [('name','=','Xử lý hàng hư hỏng')])
        vals = {
            'stock_journal_id': stock_journal_ids and stock_journal_ids[0] or False,
            'type': 'internal',
            'return': 'none',
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