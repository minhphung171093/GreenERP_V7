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

class draft_bl(osv.osv):
    _name = "draft.bl"
    
    def onchange_hopdong_id(self, cr, uid, ids, hopdong_id=False, context=None):
        vals = {}
        draft_bl_line = []
        if hopdong_id:
            hd_obj = self.pool.get('hop.dong')
            hd = hd_obj.browse(cr, uid, hopdong_id)
            if ids:
                cr.execute('''update draft_bl_line set hopdong_id=%s where draft_bl_id=%s; commit; ''',(hopdong_id,ids[0],))
#             val_line={
#                 'hopdong_id': hopdong_id,
#             }   
#             draft_bl_line.append((0,0,val_line))
            vals = {
                'port_of_loading': hd.port_of_loading and hd.port_of_loading.id or False,
                'port_of_charge': hd.port_of_charge and hd.port_of_charge.id or False,
                'diadiem_nhanhang': hd.diadiem_nhanhang and hd.diadiem_nhanhang.id or False,
                'notify_party_id':hd.partner_id and hd.partner_id.id or False,
#                 'draft_bl_line': draft_bl_line,
            }
        return {'value': vals}
    
    _columns = {
        'name':fields.char('Booking No', size = 1024,required = True),
        'hopdong_id':fields.many2one('hop.dong','Contract',required = True),
        'date':fields.date('Date',required=True),
        'company_id': fields.many2one('res.company','Company',required = True),
        'notify_party_id': fields.many2one('res.partner','Notify Party',required=True),
        'notify_party_text':fields.char('2nd Notify Party'),
        'consignee_id': fields.many2one('res.partner','Consignee'),
        'consignee_text':fields.char('Other Consignee'),
        
        'diadiem_nhanhang':fields.many2one('place.of.delivery', 'Địa điểm nhận hàng'),
        'port_of_loading':fields.many2one('port.of.loading', 'Port of loading'),
        'port_of_charge':fields.many2one('port.of.discharge', 'Port of discharge'),
        
        'quantity_kind_of_packages': fields.char('Quantity and Kind of Packages'),
        'note':fields.text('Note'),
        'meansurement':fields.char('Meansurement'),  
        'freight':fields.selection([('prepaid', 'Prepaid'),('collect', 'Collect')], 'Freight'),
        'bl_no':fields.char('B/L No'),  
        'draft_bl_line': fields.one2many('draft.bl.line','draft_bl_id','Line'),
        'country_id': fields.many2one('res.country','The Country Of Origin'),
        'customs_declaration': fields.char('Customs Declaration', size=1024),
        'shipping_line_id': fields.many2one('shipping.line','Shipping line'),
        'forwarder_line_id': fields.many2one('forwarder.line','Forwarder line'),
        'stock_picking_id': fields.many2one('stock.picking','Phiếu xuất'),
        'mean_transport': fields.char('Means of Transport', size=1024),
        'stock_ids':fields.many2many('stock.picking','kho_chungtu_ref','chung_tu_id','stock_id','Kho' ),
        'state': fields.selection([
            ('moi_tao', 'Mới tạo'),
            ('da_duyet', 'Xác nhận'),
            ('hoan_tat', 'Hoàn tất'),
            ('huy_bo', 'Hủy bỏ'),
            ], 'Trạng thái',readonly=True, states={'moi_tao': [('readonly', False)]}),
    }
    
    _defaults = {
        'state':'moi_tao',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'draft.bl', context=c),
    }
    
    def create(self, cr, uid, vals, context=None):
#         new_id = super(draft_bl, self).create(cr, uid, vals, context)
        hopdong_obj = self.pool.get('hop.dong')
        if 'hopdong_id' in vals:
            hop_dong = hopdong_obj.browse(cr,uid,vals['hopdong_id'])
            sql = '''
                select id from stock_picking where state != 'done' and id in(select picking_id from stock_move where hop_dong_ban_id = %s)
            '''%(vals['hopdong_id'])
            cr.execute(sql)
            picking_ids = [row[0] for row in cr.fetchall()]
            vals.update({
                         'stock_ids': [(6,0,picking_ids)]
                         })
        return super(draft_bl, self).create(cr, uid, vals, context)    

    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(draft_bl, self).write(cr, uid,ids, vals, context)  
        for line in self.browse(cr,uid,ids):
#             if 'stock_ids' in vals and vals['stock_ids']:
            if 'state' in vals and vals['state']:
                if vals['state'] == 'da_duyet':
                    if line.stock_ids:
                        hopdong_ban = self.pool.get('hop.dong').browse(cr,uid,line.hopdong_id.id)
                        self.pool.get('hop.dong').write(cr,uid,[hopdong_ban.id],{'state': 'thuc_hien_xongchungtu'})
        return new_write
    
    def bt_wizard(self, cr, uid, ids, context=None):
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_viruco_base', 'draft_bl_print_report_form')
        bl_id = self.browse(cr,uid,ids[0])
        return {
                    'name': 'In Báo Cáo',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': res[1],
                    'res_model': 'draft.bl.print.report',
                    'domain': [],
                    'context': {
                                'default_draft_bl_id':bl_id.id or False,
                                },
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }

    def xac_nhan(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'state': 'da_duyet'})
    
    def hoan_tat(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'hoan_tat'})
    
    def huy_bo(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'huy_bo'})   
    
#     def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
#         if context is None:
#             context = {}
#         if context.get('search_chung_tu'):
#             picking = self.pool.get('stock.picking').browse(cr,uid,context.get('picking_id'))
#             hopdong_ids=[]
#             for move in picking.move_lines:
#                 sql = '''
#                 select id from draft_bl
#                 where state in ('hoan_tat') and hopdong_id = %s 
#                 and id not in (select chung_tu_id from stock_picking where chung_tu_id is not null)
#                 '''%(move.hop_dong_ban_id.id)
#                 cr.execute(sql)
#                 hopdong_ids = [row[0] for row in cr.fetchall()]
#             args += [('id','in',hopdong_ids)]
#         return super(draft_bl, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
#     
#     def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
#         ids = self.search(cr, user, args, context=context, limit=limit)
#         return self.name_get(cr, user, ids, context=context)     
draft_bl()

class draft_bl_line(osv.osv):
    _name = 'draft.bl.line'
    
    _columns = {
        'draft_bl_id': fields.many2one('draft.bl', 'Draft bl', ondelete='cascade', select=True),
        'ocean_vessel':fields.char('Ocean Vessel/Vov No',required=True),
#         'picking_id': fields.many2one('stock.picking', 'Delivery Order'),
        'etd_date':fields.date('ETD'),
        'eta_date':fields.date('ETA'),
        'cuoc_tau': fields.float('Freight Cost'),
        'description_line': fields.one2many('description.line','draft_bl_line_id','Line'),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)]),
        'hopdong_line_id': fields.many2one('hopdong.line', 'Product', ondelete='cascade', select=True),
        'container_no_seal':fields.char('Container No/Seal No'),
        'option':fields.selection([('product', 'Product'),('seal_no', 'Container No/Seal No')], 'Option'),
        'seal_descript_line': fields.one2many('description.line','seal_line_id','Line'),
        'hopdong_id':fields.many2one('hop.dong','Contract'),
        'line_number': fields.integer('Line Number'),
    }
    
    def onchange_option(self, cr, uid, ids, option=False, line_number=False):
        vals = {}
        mang = []
        if option and line_number:
            if option=='product':
                qc_donggoi_ids = self.pool.get('quycach.donggoi').search(cr,uid,[('name','like','HÀNG RỜI')])
                for i in range(0,line_number):
                    mang.append({
                                 'packages_qty':600,
                                 'packages_id':qc_donggoi_ids and qc_donggoi_ids[0] or False,
                                 'packages_weight':'33.33',
                                 'net_weight':20,
                                 'gross_weight':20,
                                 })
                vals = {'seal_descript_line':mang,
                    }
        return {'value': vals} 
    
    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['ocean_vessel','product_id'], context=context)
        res = []
        for record in reads:
            name = (record['ocean_vessel'] and record['ocean_vessel'] +' - ' or '')\
                        + (record['product_id'] and record['product_id'][1] or '')
            res.append((record['id'], name))
        return res

    def onchange_container_no(self, cr, uid, ids,container_no_seal=False,context=None):
        vals = {}
        warning = {}
        if container_no_seal:
            a = container_no_seal.split('/')
            if len(a)==2 and len(a[0])!=11:
                vals.update({'container_no_seal': ''})
                warning = {
                    'title': _('Cảnh báo!'),
                    'message' : _('Container No hiện đang chưa đúng (cần có đủ 7 ký tự số) !')
                }
                        
        return {'warning': warning,'value':vals}
    
draft_bl_line()


class description_line(osv.osv):
    _name = 'description.line'
    
    _columns = {
        'draft_bl_line_id': fields.many2one('draft.bl.line', 'Draft bl line', ondelete='cascade', select=True), 
        'seal_line_id': fields.many2one('draft.bl.line', 'Seal Draft bl line', ondelete='cascade', select=True),
        'container_no_seal':fields.char('Container No/Seal No'),
        'packages_qty': fields.float('Packages Qty'),
        'packages_id':fields.many2one('quycach.donggoi','Packages'),
        'product_uom': fields.many2one('product.uom', ''),
        'packages_weight':fields.selection([('33.33', '33.33 Kgs/Bale'),('35', '35 Kgs/Bale'),
                                            ('1.20', '1.20 Mts/Pallet'),('1.26', '1.26 Mts/Pallet')], 'Packages Weight'),
        'net_weight':fields.float('Net Weight'),
        'gross_weight':fields.float('Gross Weight'),
        'hopdong_line_id': fields.many2one('hopdong.line', 'Product', ondelete='cascade', select=True),
    }

#     def create(self, cr, uid, vals, context=None):
# #         new_id = super(draft_bl, self).create(cr, uid, vals, context)
#         hopdong_obj = self.pool.get('hop.dong')
#         if 'container_no_seal' in vals:
#             a = vals['container_no_seal'].split('/')
#             if len(a)==2 and len(a[0])==11:
#                 raise osv.except_osv(_('Cảnh báo!'), _('Số Container hiện chưa đúng!'))
#         return super(description_line, self).create(cr, uid, vals, context)    

    def onchange_container(self, cr, uid, ids,container_no_seal=False,context=None):
        vals = {}
        warning = {}
        if container_no_seal:
            a = container_no_seal.split('/')
            if len(a)==2 and len(a[0])!=11:
                warning = {
                    'title': _('Cảnh báo!'),
                    'message' : _('Container No hiện đang chưa đúng (cần có đủ 7 ký tự, số) !')
                }
                        
        return {'warning': warning}
    
description_line()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
