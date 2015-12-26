# -*- coding: utf-8 -*-
##############################################################################
#
#    HLVSolution, Open Source Management Solution
#
##############################################################################

import openerp
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.addons.general_base import amount_to_text_vn
from openerp.addons.general_base import amount_to_text_en

class users(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'context_shop_id': fields.many2one('sale.shop', 'Shop', required=False, context={'user_preference': True}),
        'shop_ids':fields.many2many('sale.shop', 'sale_shop_users_rel', 'user_id', 'shop_id', 'Shops'),
    }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_nhanvien_id'):
            if context.get('uid'):
                sql = '''
                    select res_id from ir_model_data where name = 'group_sale_salesman' and module = 'base'
                '''
                cr.execute(sql)
                group_sale_salesman_id = cr.dictfetchone()['res_id']
                
                sql = '''
                    select res_id from ir_model_data where name = 'group_sale_salesman_all_leads' and module = 'base'
                '''
                cr.execute(sql)
                group_sale_salesman_all_id = cr.dictfetchone()['res_id']
                sql = '''
                    select uid from res_groups_users_rel 
                    where gid = %s and uid not in (select uid from res_groups_users_rel where gid = %s)
                '''%(group_sale_salesman_id,group_sale_salesman_all_id)
                cr.execute(sql)
                user_kinhdoanh_ids = [row[0] for row in cr.fetchall()]
                if context.get('uid') in user_kinhdoanh_ids:
                    sql = '''
                        select id from res_users 
                        where nguoi_quanly_id = %s or id = %s
                    '''%(context.get('uid'),context.get('uid'))
                    cr.execute(sql)
                    user_dc_quanly_ids = [row[0] for row in cr.fetchall()]
                    args += [('id','in',user_dc_quanly_ids)]
        return super(users, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
    
    def on_change_shop_id(self, cr, uid, ids, context_shop_id):
        return {
                'warning' : {
                    'title': _("Shop Switch Warning"),
                    'message': _("Please keep in mind that documents currently displayed may not be relevant after switching to another Shop. If you have unsaved changes, please make sure to save and close all forms before switching to a different Shop. (You can click on Cancel in the User Preferences now)"),
                }
        }
    
    def _check_shop(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            if this.context_shop_id and this.shop_ids and this.context_shop_id not in this.shop_ids:
                return False
        return True

    _constraints = [
        (_check_shop, 'The chosen Shop is not in the allowed Shops for this user', ['context_shop_id', 'shop_ids']),
    ]
    
    def amount_to_text(self, nbr, lang='vn', currency='USD'):
        if lang == 'vn':
            return amount_to_text_vn.amount_to_text(nbr, lang)
        else:
            return amount_to_text_en.amount_to_text(nbr, 'en', currency)
        
users()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
