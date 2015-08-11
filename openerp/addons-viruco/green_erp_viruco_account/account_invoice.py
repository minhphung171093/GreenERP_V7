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
import os
from xlrd import open_workbook,xldate_as_tuple
from openerp import modules

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    _columns = {
        'hop_dong_id':fields.many2one('hop.dong','Hợp đồng'),
    }
    
account_invoice()

class group_invoice(osv.osv_memory):
    _name = "group.invoice"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(group_invoice, self).default_get(cr, uid, fields, context=context)
        invoice_ids = context.get('active_ids', [])
        partner_id = []
        for invoice in self.pool.get('account.invoice').browse(cr, uid, invoice_ids):
            if not partner_id:
                partner_id = invoice.partner_id.id
            if invoice.state != 'draft':
                raise osv.except_osv(_('Cảnh báo!'),_('Không thể gộp hóa đơn có trạng thái khác nháp!'))
            if partner_id != invoice.partner_id.id:
                if invoice.type in ['out_invoice','out_refund']:
                    raise osv.except_osv(_('Cảnh báo!'),_('Không thể gộp hóa đơn khác khách hàng!'))
                if invoice.type in ['in_invoice','in_refund']:
                    raise osv.except_osv(_('Cảnh báo!'),_('Không thể gộp hóa đơn khác nhà cung cấp!'))
        return res
    
    _columns = {
        'name':fields.text('Name'),
    }
    
    def bt_gop(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice_ids = context.get('active_ids', [])
        invoice_obj = self.pool.get('account.invoice')
        invoice_id = False
        for seq,invoice in enumerate(self.pool.get('account.invoice').browse(cr, uid, invoice_ids)):
            if seq == 0:
                invoice_id = invoice.id
                continue
            cr.execute(''' update account_invoice_line set invoice_id=%s where invoice_id=%s ''',(invoice_id,invoice.id,))
            cr.execute('delete from account_invoice where id=%s',(invoice.id,))
        if invoice_id:
            invoice_obj.button_reset_taxes(cr, uid, [invoice_id])
            invoice = invoice_obj.browse(cr, uid, invoice_id)
            model_data = self.pool.get('ir.model.data')
            if invoice.type=='out_invoice':
                tree_view = model_data.get_object_reference(cr, uid, 'account', 'invoice_tree')
                form_view = model_data.get_object_reference(cr, uid, 'account', 'invoice_form')
                return {
                        'name': 'Hóa đơn khách hàng',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'account.invoice',
                        'views': [(form_view and form_view[1] or False, 'form'), (tree_view and tree_view[1] or False, 'tree')],
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'res_id':invoice_id,
                    }
            if invoice.type=='in_invoice':
                tree_view = model_data.get_object_reference(cr, uid, 'account', 'invoice_tree')
                form_view = model_data.get_object_reference(cr, uid, 'account', 'invoice_supplier_form')
                return {
                        'name': 'Hóa đơn nhà cung cấp',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'views': [(form_view and form_view[1] or False, 'form'),(tree_view and tree_view[1] or False, 'tree')],
                        'res_model': 'account.invoice',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'res_id':invoice_id,
                    }
        return {'type': 'ir.actions.act_window_close'}
    
group_invoice()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
