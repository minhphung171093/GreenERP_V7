# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP SA (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import base64
import re
import threading
from openerp.tools.safe_eval import safe_eval as eval
from openerp import tools
import openerp.modules
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp import netsvc

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'state' or 'date' in vals: 
            new_write = super(stock_picking, self).write(cr, uid,ids, vals, context)
#             sql = '''
#                 update stock_move set date = (select date(timezone('UTC',date)) from stock_picking where id =%s) where picking_id=%s
#             '''%(new_write,new_write)
            for id in ids:
                sql = '''
                    update stock_move set date = (select date from stock_picking where id = %s) where picking_id = %s
                '''%(id,id)
                cr.execute(sql)
        else:
            new_write = super(stock_picking, self).write(cr, uid,ids, vals, context)
        return new_write
    
    def action_revert_done(self, cr, uid, ids, context=None):
        move_ids = []
        invoice_ids = []
        if not len(ids):
            return False        
        for picking in self.browse(cr, uid, ids, context):
            for line in picking.move_lines:
                line.write({'state': 'draft'})
            self.write(cr, uid, [picking.id], {'state': 'draft'})
            if picking.invoice_state == 'invoiced':
                self.write(cr, uid, [picking.id],
                           {'invoice_state': '2binvoiced'})
            wf_service = netsvc.LocalService("workflow")
            # Deleting the existing instance of workflow
            wf_service.trg_delete(uid, 'stock.picking', picking.id, cr)
            wf_service.trg_create(uid, 'stock.picking', picking.id, cr)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _(
                "The stock picking '%s' has been set in draft state."
                ) % (name,)
            self.log(cr, uid, id, message)
        return True
stock_picking()

class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    def write(self, cr, uid, ids, vals, context=None):
        if 'state' or 'date' in vals: 
            new_write = super(stock_picking_in, self).write(cr, uid,ids, vals, context)
#             sql = '''
#                 update stock_move set date = (select date(timezone('UTC',date)) from stock_picking where id =%s) where picking_id=%s
#             '''%(new_write,new_write)
            for id in ids:
                sql = '''
                    update stock_move set date = (select date from stock_picking where id = %s) where picking_id = %s
                '''%(id,id)
                cr.execute(sql)
        else:
            new_write = super(stock_picking_in, self).write(cr, uid,ids, vals, context)
        return new_write
    
    def action_revert_done(self, cr, uid, ids, context=None):
        move_ids = []
        invoice_ids = []
        if not len(ids):
            return False        
        for picking in self.browse(cr, uid, ids, context):
            for line in picking.move_lines:
                line.write({'state': 'draft'})
            self.write(cr, uid, [picking.id], {'state': 'draft'})
            if picking.invoice_state == 'invoiced':
                self.write(cr, uid, [picking.id],
                           {'invoice_state': '2binvoiced'})
            wf_service = netsvc.LocalService("workflow")
            # Deleting the existing instance of workflow
            wf_service.trg_delete(uid, 'stock.picking', picking.id, cr)
            wf_service.trg_create(uid, 'stock.picking', picking.id, cr)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _(
                "The stock picking '%s' has been set in draft state."
                ) % (name,)
            self.log(cr, uid, id, message)
        return True
stock_picking_in()

class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    def write(self, cr, uid, ids, vals, context=None):
        if 'state' or 'date' in vals: 
            new_write = super(stock_picking_out, self).write(cr, uid,ids, vals, context)
#             sql = '''
#                 update stock_move set date = (select date(timezone('UTC',date)) from stock_picking where id =%s) where picking_id=%s
#             '''%(new_write,new_write)
            for id in ids:
                sql = '''
                    update stock_move set date = (select date from stock_picking where id = %s) where picking_id = %s
                '''%(id,id)
                cr.execute(sql)
        else:
            new_write = super(stock_picking_out, self).write(cr, uid,ids, vals, context)
        return new_write
    
    def action_revert_done(self, cr, uid, ids, context=None):
        move_ids = []
        invoice_ids = []
        if not len(ids):
            return False        
        for picking in self.browse(cr, uid, ids, context):
            for line in picking.move_lines:
                line.write({'state': 'draft'})
            self.write(cr, uid, [picking.id], {'state': 'draft'})
            if picking.invoice_state == 'invoiced':
                self.write(cr, uid, [picking.id],
                           {'invoice_state': '2binvoiced'})
            wf_service = netsvc.LocalService("workflow")
            # Deleting the existing instance of workflow
            wf_service.trg_delete(uid, 'stock.picking', picking.id, cr)
            wf_service.trg_create(uid, 'stock.picking', picking.id, cr)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _(
                "The stock picking '%s' has been set in draft state."
                ) % (name,)
            self.log(cr, uid, id, message)
        return True
stock_picking_out()

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'daily_id': fields.many2one('res.partner','Đại lý',states={'done': [('readonly', True)]}),
        }
    
stock_move()

class ve_e(osv.osv):
    _name = "ve.e"
    _columns = {
        'name': fields.many2one('res.partner','Đại lý',domain="[('dai_ly','=',True)]",states={'done':[('readonly',True)]}),
        'state': fields.selection([('new','Mới tạo'),('done','Đã nhận')],'Trạng thái'),
        'ngay': fields.date('Ngày trả',states={'done':[('readonly',True)]}),
        've_e_line': fields.one2many('ve.e.line','ve_e_id','Line',states={'done':[('readonly',True)]}),
    }
    
    def bt_datra(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'done'})
ve_e()

class ve_e_line(osv.osv):
    _name = "ve.e.line"
    _columns = {
        'product_id': fields.many2one('product.product','Mệnh giá',domain="[('menh_gia','=',True)]",required=True),
        'sl': fields.integer('Số lượng'),
        've_e_id': fields.many2one('ve.e','Vé é',ondelete='cascade'),
    }
ve_e_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: