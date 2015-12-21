# -*- coding: utf-8 -*-
import time
from lxml import etree
from openerp.osv import fields, osv
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class stock_partial_picking(osv.osv_memory):
    _inherit="stock.partial.picking"
    
    def do_partial(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = super(stock_partial_picking,self).do_partial(cr, uid, ids, context)
        partial = self.browse(cr, uid, ids[0])
        group_obj = self.pool.get('res.groups')
        group_manager_model, group_manager_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'group_stock_manager')
        group_manger = group_obj.browse(cr, uid, group_manager_id)
        group_user_model, group_user_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'group_stock_user')
        group_user = group_obj.browse(cr, uid, group_user_id)
        user_manager_ids = [u.id for u in group_manger.users]
        user_ids = [u.id for u in group_user.users]
        picking_id = context.get('active_id', False)
        picking = self.pool.get('stock.picking').browse(cr, uid, picking_id)
        prodlot_obj = self.pool.get('stock.production.lot')
        for line in partial.move_ids:
            if picking.type=='out' and line.prodlot_id:
                prodlot_ids = prodlot_obj.search(cr, uid, [('product_id','=',line.product_id.id)],order='life_date')
                for prodlot in prodlot_obj.browse(cr, uid, prodlot_ids):
                    sql = '''
                        select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                            (select st.product_qty
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_dest_id = %s and prodlot_id = %s
                            union all
                            select st.product_qty*-1
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_id = %s and prodlot_id = %s
                            )foo
                    '''%(prodlot.product_id.id,line.location_id.id,prodlot.id,prodlot.product_id.id,line.location_id.id,prodlot.id)
                    cr.execute(sql)
                    ton_sl = cr.dictfetchone()['ton_sl']
                    if (uid in user_ids and uid not in user_manager_ids and ton_sl>=line.quantity and prodlot.id==line.prodlot_id.id) or uid in user_manager_ids:
                        break
                    if uid in user_ids and uid not in user_manager_ids and ton_sl>=line.quantity and prodlot.id!=line.prodlot_id.id:
                        raise osv.except_osv(_('Cảnh báo!'),_('Bạn không được phép duyệt hàng có ngày hết hạn xa!'))
                    if prodlot.id==line.prodlot_id.id:
                        break
        return res
    
stock_partial_picking()


class split_in_production_lot(osv.osv_memory):
    _inherit = "stock.move.split"
    
    _defaults = {
        'use_exist': True,
    }
    
split_in_production_lot()



