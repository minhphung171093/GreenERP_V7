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
            for hd_line in hd.hopdong_line:
                val_line={
                    'product_id': hd_line.product_id and hd_line.product_id.id or False,
                    'product_uom': hd_line.product_uom and hd_line.product_uom.id or False,
                    'product_qty': hd_line.product_qty,
                    'net_weight': hd_line.product_qty,
                    'hopdong_line_id': hd_line.id,
                }   
                draft_bl_line.append((0,0,val_line))
            vals = {
                'port_of_loading': hd.port_of_loading and hd.port_of_loading.id or False,
                'port_of_charge': hd.port_of_charge and hd.port_of_charge.id or False,
                'diadiem_nhanhang': hd.diadiem_nhanhang and hd.diadiem_nhanhang or False,
                'notify_party_id':hd.partner_id and hd.partner_id.id or False,
                'draft_bl_line': draft_bl_line,
            }
        return {'value': vals}
    
    _columns = {
        'name':fields.char('Booking No', size = 1024,required = True),
        'hopdong_id':fields.many2one('hop.dong','Contract',required = True),
        'date':fields.date('Date',required=True),
        'company_id': fields.many2one('res.company','Company',required = True),
        'notify_party_id': fields.many2one('res.partner','Notify Party',required=True),
        'consignee_id': fields.many2one('res.partner','Consignee'),
        'consignee_text':fields.char('Other Consignee'),
        
        'diadiem_nhanhang':fields.many2one('place.of.delivery', 'Địa điểm nhận hàng'),
        'port_of_loading':fields.many2one('port.of.loading', 'Port of loading'),
        'port_of_charge':fields.many2one('port.of.discharge', 'Port of discharge'),
        
        'quantity_kind_of_packages': fields.char('Quantity and Kind of Packages'),
        'note':fields.text('Note'),
        'meansurement':fields.char('Meansurement'),  
        'freight':fields.selection([('prepaid', 'Prepaid'),('collect', 'Collect')], 'Freight'),
        'bl_no':fields.char('B/L No',required=True),  
        'draft_bl_line': fields.one2many('draft.bl.line','draft_bl_id','Line'),
        'country_id': fields.many2one('res.country','The Country Of Origin'),
        'customs_declaration': fields.char('Customs Declaration', size=1024),
        'shipping_line_id': fields.many2one('shipping.line','Shipping line'),
        'forwarder_line_id': fields.many2one('forwarder.line','Forwarder line'),
    }
    
    _defaults = {
        'date': time.strftime('%Y-%m-%d'),
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'draft.bl', context=c),
    }
    
    def create(self, cr, uid, vals, context=None):
#         new_id = super(draft_bl, self).create(cr, uid, vals, context)
        hopdong_obj = self.pool.get('hop.dong')
        if 'hopdong_id' in vals:
            hop_dong = hopdong_obj.browse(cr,uid,vals['hopdong_id'])
            if hop_dong.state == 'thuc_hien':
                hopdong_obj.write(cr,uid,[vals['hopdong_id']],{
                                                               'state': 'thuc_hien_xongchungtu',
                                                               })
            if hop_dong.state == 'giaohang_chochungtu':
                hopdong_obj.write(cr,uid,[vals['hopdong_id']],{
                                                               'state': 'giaohang_xongchungtu',
                                                               })
        return super(draft_bl, self).create(cr, uid, vals, context)    
    
draft_bl()

class draft_bl_line(osv.osv):
    _name = 'draft.bl.line'
    
    _columns = {
        'draft_bl_id': fields.many2one('draft.bl', 'Draft bl', ondelete='cascade', select=True),
        'ocean_vessel':fields.char('Ocean Vessel/Vov No',required=True),
        'etd_date':fields.date('ETD'),
        'eta_date':fields.date('ETA'),
        'cuoc_tau': fields.float('Cước tàu'),
        'description_line': fields.one2many('description.line','draft_bl_line_id','Line'),
    }
    
draft_bl_line()


class description_line(osv.osv):
    _name = 'description.line'
    
    _columns = {
        'draft_bl_line_id': fields.many2one('draft.bl.line', 'Draft bl line', ondelete='cascade', select=True),
        'container_no_seal':fields.char('Container No/Seal No',required=True),
        'packages_qty': fields.float('Packages Qty'),
        'packages_id':fields.many2one('quycach.donggoi','Packages'),
        'packages_weight':fields.selection([('33.33', '33.33 Kgs/Bale'),('35', '35 Kgs/Bale'),
                                            ('1.20', '1.20 Mts/Pallet'),('1.26', '1.26 Mts/Pallet')], 'Packages Weight'),
        'net_weight':fields.float('Net Weight'),
        'gross_weight':fields.float('Gross Weight'),
    }
    
description_line()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: