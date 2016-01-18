# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

import time
from datetime import datetime
from osv import fields, osv
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import decimal_precision as dp
from tools.translate import _


class tach_phieu(osv.osv):
    _name = "tach.phieu"    
     
    _columns = {
        'name_lines':fields.one2many('sp.tach.phieu','tach_phieu_id','Sản phẩm'),
        'picking_id':fields.many2one('stock.picking','Picking'),
     }
        
    _defaults = {
                 
        }
    
    def bt_tach(self, cr, uid, ids, context=None):
        picking_out_obj = self.pool.get('stock.picking.out')
        stock_move_obj = self.pool.get('stock.move')
        move_lines = []
        for line in self.browse(cr,uid,ids):
            
            move_ids = []
            for move in line.name_lines:
                sl_giao = move.sl
                sl_conlai = move.move_lines_id.product_qty - move.sl
                if move.move_lines_id.product_qty - sl_giao:
                    defaut_move = {'product_qty':sl_conlai}
                    new_move_id = stock_move_obj.copy(cr, uid, move.move_lines_id.id, defaut_move)
                    stock_move_obj.write(cr, uid, [move.move_lines_id.id], {'product_qty':sl_giao})
                    move_ids.append(new_move_id)
            default = {'backorder_id':line.picking_id.id,'move_lines':[(6,0,move_ids)],'chung_tu_ids':False,'name':self.pool.get('ir.sequence').get(cr, uid, 'stock.journal') or '/'}
            new_picking_id = picking_out_obj.copy(cr, uid, line.picking_id.id, default)
            picking_out_obj.draft_force_assign(cr, uid, [new_picking_id])
        return True
        
tach_phieu()
    
class sp_tach_phieu(osv.osv):
    _name = "sp.tach.phieu"    
     
    _columns = {
        'tach_phieu_id':fields.many2one('tach.phieu','Tách sp'),
        'name':fields.char('Sản phẩm', readonly = True),
        'sl':fields.float('Số lượng', required = True),
        'move_lines_id':fields.many2one('stock.move','stock move'),
     }
sp_tach_phieu()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
