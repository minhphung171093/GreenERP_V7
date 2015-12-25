# # -*- coding: utf-8 -*-
##############################################################################
#

#
##############################################################################

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import httplib
from openerp import SUPERUSER_ID
from datetime import datetime, timedelta
from datetime import date
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


class stock_picking_out(osv.osv):
    _inherit = 'stock.picking.out'
    def _set_minimum_date(self, cr, uid, ids, name, value, arg, context=None):
        """ Calculates planned date if it is less than 'value'.
        @param name: Name of field
        @param value: Value of field
        @param arg: User defined argument
        @return: True or False
        """
        if not value:
            return False
        if isinstance(ids, (int, long)):
            ids = [ids]
        for pick in self.browse(cr, uid, ids, context=context):
            sql_str = """update stock_move set
                    date_expected='%s'
                where
                    picking_id=%s """ % (value, pick.id)
            if pick.min_date:
                sql_str += " and (date_expected='" + pick.min_date + "')"
            cr.execute(sql_str)
        return True
    def get_min_max_date(self, cr, uid, ids, field_name, arg, context=None):
        """ Finds minimum and maximum dates for picking.
        @return: Dictionary of values
        """
        res = {}
        for id in ids:
            res[id] = {'min_date': False, 'max_date': False}
        if not ids:
            return res
        cr.execute("""select
                picking_id,
                min(date_expected),
                max(date_expected)
            from
                stock_move
            where
                picking_id IN %s
            group by
                picking_id""",(tuple(ids),))
        for pick, dt1, dt2 in cr.fetchall():
            res[pick]['min_date'] = dt1
            res[pick]['max_date'] = dt2
        return res
    
    def _kiemtra_trahang(self, cr, uid, ids, name, args, context=None):
        res = {}
        picking_ids =[]
        if context is None:
            context = {}
        for picking in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from trahang_chokho where picking_id = %s
            '''%(picking.id)
            cr.execute(sql)
            picking_ids = cr.fetchone()
            if picking_ids:
                res[picking.id] = True
            else:
                res[picking.id] = False
        return res
    
    def _trang_thai_hd(self, cr, uid, ids, name, args, context=None):
        res = {}
        picking_ids =[]
        if context is None:
            context = {}
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.type == 'out':
                for move in picking.move_lines:
                    sql = '''
                        select state from account_invoice where type = 'out_invoice'
                        and id in (select invoice_id from account_invoice_line where source_id = %s)
                    '''%(move.id)
                    cr.execute(sql)
                    trang_thai = cr.fetchone()
                    if not trang_thai:
                        res[picking.id] = 'Chưa có hóa đơn'
                    else:
                        if trang_thai[0] == 'draft':
                            res[picking.id] = 'Chờ duyệt hóa đơn'
                        if trang_thai[0] == 'open':
                            res[picking.id] = 'Chờ thanh toán'
                        if trang_thai[0] == 'paid':
                            res[picking.id] = 'Đã thanh toán'
        return res
    
    def _trangthai(self, cr, uid, ids, name, arg, context=None):
        res = {}
        stock_obj = self.pool.get('stock.picking')
        for tt in self.browse(cr,uid,ids):
            if tt.state == 'draft':
                res[tt.id] = 'draft'
            if tt.state == 'confirmed' and tt.flag == False:
                res[tt.id]='confirmed'
            if tt.state == 'confirmed' and tt.flag == True:
                res[tt.id]='assigned'
            if tt.state == 'cancel':
                res[tt.id]='cancel'
            if tt.state == 'assigned':
                res[tt.id]='assigned'
            if tt.state == 'done':
                res[tt.id]='done'
        return res
    
    _columns = {
        'description': fields.text('Description', track_visibility='onchange'),
        'ngay_gui':fields.date('Ngày gửi'),
        'ngay_nhan':fields.date('Ngày nhận lại'),
        'daidien_khachhang':fields.char('Đại diện khách hàng nhận'),
        'nguoi_giao_hang':fields.many2one('hr.employee','Người giao hàng'),
        'nguoi_van_chuyen':fields.many2one('hr.employee','Người vận chuyển'),
        'phuongtien_giaohang':fields.char('Phương tiện giao hàng'),
        'state_receive':fields.selection([('draft','Tạo mới'),('da_gui','Đã gửi'),('da_nhan','Đã nhận')],'Trạng thái',required=True),
        'picking_packaging_line': fields.one2many('stock.picking.packaging','picking_id','Đóng gói'),
        
        'partner_id': fields.many2one('res.partner', 'Partner', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
#         'stock_journal_id': fields.many2one('stock.journal','Stock Journal', select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'location_id': fields.many2one('stock.location', 'Location', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="Keep empty if you produce at the location where the finished products are needed." \
                "Set a location if you produce at a fixed location. This can be a partner location " \
                "if you subcontract the manufacturing operations.", select=True, track_visibility='onchange'),
        'location_dest_id': fields.many2one('stock.location', 'Dest. Location', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="Location where the system will stock the finished products.", select=True, track_visibility='onchange'),
        'date': fields.datetime('Creation Date', help="Creation date, usually the time of the order.", select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'min_date': fields.function(get_min_max_date, fnct_inv=_set_minimum_date, multi="min_max_date",
                 store=True, type='datetime', string='Scheduled Time', select=1, help="Scheduled time for the shipment to be processed", track_visibility='onchange'),
        'origin': fields.char('Source Document', size=64, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="Reference of the document", select=True, track_visibility='onchange'),
        'move_lines': fields.one2many('stock.move', 'picking_id', 'Internal Moves', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, track_visibility='onchange'),
        'company_id': fields.many2one('res.company', 'Company', required=True, select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'move_type': fields.selection([('direct', 'Partial'), ('one', 'All at once')], 'Delivery Method', required=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="It specifies goods to be deliver partially or all at once", track_visibility='onchange'),
        'date_done': fields.datetime('Date of Transfer', help="Date of Completion", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'auto_picking': fields.boolean('Auto-Picking', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'ly_do_xuat_id': fields.many2one('ly.do.xuat', 'Lý do xuất'),
        'xuly_thncc_id': fields.many2one('stock.picking.in', 'Trả hàng nhà cung cấp'),
        'xuly_huyhang_id': fields.many2one('stock.picking', 'Hủy hàng'),
        'loai_xuly':fields.selection([('trahang_ncc','Trả hàng cho nhà cung cấp'),('huy_hang','Hủy hàng')],'Loại xử lý'),
        'tinhtrang_chatluong': fields.char('Tình trạng chất lượng', size=1024),
        'yeu_cau': fields.char('Yêu cầu', size = 1024),
        'ghi_chu_xhd': fields.char('Ghi chú xuất hóa đơn', size = 1024),
        'exist': fields.function(_kiemtra_trahang, string='Đã tồn tại trong trahang.chokho',
            type='boolean'),
        'trang_thai_hd': fields.function(_trang_thai_hd, string='Trạng thái hóa đơn',
            type='char'),
        'trang_thai':fields.function(_trangthai, string='Trạng thái',
                                      type='selection', selection=[('draft','Nháp'),
                                                                   ('confirmed','Đơn hàng chờ xử lý'),('assigned','Đơn hàng chưa xử lý'),
                                                                   ('done','Đã chuyển'),
                                                                   ('cancel','Đã huỷ bỏ')],
                                     store={
                                                'stock.picking.out':(lambda self, cr, uid, ids, c={}: ids, ['state','flag'], 10),
                                            }),        
        'flag':fields.boolean('Check DH chua xu ly')
        
    }
    _defaults = {
                 'flag': False,
                 'state_receive':'draft',
                 }
    
    def tao_hoa_don(self, cr, uid,ids, context=None):
        picking = self.browse(cr, uid, ids[0])
        if context is None:
            context={}
        context.update({'active_id':ids[0],'active_ids':ids,'active_model':'stock.picking'})
        onshipping_obj = self.pool.get('stock.invoice.onshipping')
        onshipping_id = onshipping_obj.create(cr, uid, {},context)
        return onshipping_obj.open_invoice(cr, uid, [onshipping_id],context)
    
    def on_change_nguoivanchuyen(self, cr, uid, ids, nguoi_van_chuyen):
        value ={}
        if not nguoi_van_chuyen:
            value.update({'phuongtien_giaohang':False})
        else:
            employee = self.pool.get('hr.employee').browse(cr, uid, nguoi_van_chuyen)
            value.update({'phuongtien_giaohang':employee.phuongtien_giaohang})
        return {'value': value}
    
    def status_send(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'ngay_gui':datetime.now().strftime('%Y-%m-%d'),'state_receive':'da_gui'})
    
    def status_receive(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'ngay_nhan':datetime.now().strftime('%Y-%m-%d'),'state_receive':'da_nhan'})
    
    def status_refresh(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state_receive':'draft'})
     
    def print_report(self, cr, uid, ids, context=None):
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'phieu_xuat_kho_report',
            }
    
    def xem_phieu_xu_ly(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids[0])
        if line.loai_xuly=='trahang_ncc':
            picking_ids = self.pool.get('stock.picking').search(cr, uid, [('origin','=',line.xuly_thncc_id.name)])
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'stock', 'view_picking_form')
            return {
                        'name': 'Phiếu nhập hàng mua',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'stock.picking.in',
                        'domain': [],
                        'res_id': picking_ids and picking_ids[0] or False,
                        'type': 'ir.actions.act_window',
                        'view_id': res[1],
                        'target': 'current',
                    }
        if line.loai_xuly=='huy_hang':
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'general_stock', 'view_picking_subinventory_form')
            return {
                        'name': 'Xử lý mất mát, hư hỏng',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'stock.picking',
                        'domain': [],
                        'res_id': line.xuly_huyhang_id and line.xuly_huyhang_id.id or False,
                        'view_id': res[1],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                    }
        return True
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(stock_picking_out, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr,uid,ids):
            sql = '''
                update stock_move set date = '%s' where picking_id = %s
            '''%(line.date, line.id)
            cr.execute(sql)
        return new_write
    
    def bt_chua_xu_ly(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {
                                         'flag': True,
                                         })
    
    def bt_hanggui_kh(self, cr, uid, ids, context=None):
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_phucthien_stock', 'trahang_chokho_popup_form_view')
        move_line = []
        invoice_id = False
        picking = self.browse(cr, uid, ids[0], context=context)
        for line in picking.move_lines:
            move_line.append((0,0,{
                                   'product_code': line.product_code,
                                   'product_id': line.product_id.id,
                                   'product_qty': line.product_qty,
                                   'product_uom': line.product_uom and line.product_uom.id or False,
                                   'prodlot_id': line.prodlot_id and line.prodlot_id.id or False,
                                   'tracking_id': line.tracking_id and line.tracking_id.id or False,
                                   }))
            sql = '''
                select id from account_invoice where id in (select invoice_id from account_invoice_line where source_id = %s)
            '''%(line.id)
            cr.execute(sql)
            invoice_id = cr.fetchone()
        return {
                    'name': 'Khách hàng gửi kho',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': res[1],
                    'res_model': 'trahang.chokho',
                    'domain': [],
                    'context': {
                        'default_partner_id': picking.partner_id.id,
                        'default_invoice_id': invoice_id and invoice_id[0] or False,
                        'default_picking_id': ids[0],
                        'default_trahang_chokho_line': move_line,
                            },
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
        
    
stock_picking_out()

class stock_picking_in(osv.osv):
    _inherit = 'stock.picking.in'
    def _set_minimum_date(self, cr, uid, ids, name, value, arg, context=None):
        """ Calculates planned date if it is less than 'value'.
        @param name: Name of field
        @param value: Value of field
        @param arg: User defined argument
        @return: True or False
        """
        if not value:
            return False
        if isinstance(ids, (int, long)):
            ids = [ids]
        for pick in self.browse(cr, uid, ids, context=context):
            sql_str = """update stock_move set
                    date_expected='%s'
                where
                    picking_id=%s """ % (value, pick.id)
            if pick.min_date:
                sql_str += " and (date_expected='" + pick.min_date + "')"
            cr.execute(sql_str)
        return True
    def get_min_max_date(self, cr, uid, ids, field_name, arg, context=None):
        """ Finds minimum and maximum dates for picking.
        @return: Dictionary of values
        """
        res = {}
        for id in ids:
            res[id] = {'min_date': False, 'max_date': False}
        if not ids:
            return res
        cr.execute("""select
                picking_id,
                min(date_expected),
                max(date_expected)
            from
                stock_move
            where
                picking_id IN %s
            group by
                picking_id""",(tuple(ids),))
        for pick, dt1, dt2 in cr.fetchall():
            res[pick]['min_date'] = dt1
            res[pick]['max_date'] = dt2
        return res
    
    def _kiemtra_trahang(self, cr, uid, ids, name, args, context=None):
        res = {}
        picking_ids =[]
        if context is None:
            context = {}
        for picking in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from trahang_chokho where picking_id = %s
            '''%(picking.id)
            cr.execute(sql)
            picking_ids = cr.fetchone()
            if picking_ids:
                res[picking.id] = True
            else:
                res[picking.id] = False
        return res
    def _trang_thai_hd(self, cr, uid, ids, name, args, context=None):
        res = {}
        picking_ids =[]
        if context is None:
            context = {}
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.type == 'in':
                for move in picking.move_lines:
                    sql = '''
                        select state from account_invoice where type = 'in_invoice'
                        and id in (select invoice_id from account_invoice_line where source_id = %s)
                    '''%(move.id)
                    cr.execute(sql)
                    trang_thai = cr.fetchone()
                    if not trang_thai:
                        res[picking.id] = 'Chưa có hóa đơn'
                    else:
                        if trang_thai[0] == 'draft':
                            res[picking.id] = 'Chờ duyệt hóa đơn'
                        if trang_thai[0] == 'open':
                            res[picking.id] = 'Chờ thanh toán'
                        if trang_thai[0] == 'paid':
                            res[picking.id] = 'Đã thanh toán'
        return res    
    
    def _trangthai(self, cr, uid, ids, name, arg, context=None):
        res = {}
        stock_obj = self.pool.get('stock.picking')
        for tt in self.browse(cr,uid,ids):
            if tt.state == 'draft':
                res[tt.id] = 'draft'
            if tt.state == 'confirmed' and tt.flag == False:
                res[tt.id]='confirmed'
            if tt.state == 'confirmed' and tt.flag == True:
                res[tt.id]='assigned'
            if tt.state == 'cancel':
                res[tt.id]='cancel'
            if tt.state == 'assigned':
                res[tt.id]='assigned'
            if tt.state == 'done':
                res[tt.id]='done'
        return res
    
    _columns = {
        'description': fields.text('Description', track_visibility='onchange'),
        'nhiet_do':fields.char('Nhiệt độ'),
        'so_luong_thung':fields.char('Số lượng thùng'),
        'time_nhan':fields.datetime('Thời gian nhận'),
        'time_ketthuc':fields.datetime('Thời gian kết thúc'),
        'sampham_lanh':fields.boolean('Sản phẩm lạnh'),
        
        'partner_id': fields.many2one('res.partner', 'Partner', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
#         'stock_journal_id': fields.many2one('stock.journal','Stock Journal', select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'location_id': fields.many2one('stock.location', 'Location', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="Keep empty if you produce at the location where the finished products are needed." \
                "Set a location if you produce at a fixed location. This can be a partner location " \
                "if you subcontract the manufacturing operations.", select=True, track_visibility='onchange'),
        'location_dest_id': fields.many2one('stock.location', 'Dest. Location', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="Location where the system will stock the finished products.", select=True, track_visibility='onchange'),
        'date': fields.datetime('Creation Date', help="Creation date, usually the time of the order.", select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'min_date': fields.function(get_min_max_date, fnct_inv=_set_minimum_date, multi="min_max_date",
                 store=True, type='datetime', string='Scheduled Time', select=1, help="Scheduled time for the shipment to be processed", track_visibility='onchange'),
        'origin': fields.char('Source Document', size=64, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="Reference of the document", select=True, track_visibility='onchange'),
        'move_lines': fields.one2many('stock.move', 'picking_id', 'Internal Moves', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, track_visibility='onchange'),
        'company_id': fields.many2one('res.company', 'Company', required=True, select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'move_type': fields.selection([('direct', 'Partial'), ('one', 'All at once')], 'Delivery Method', required=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="It specifies goods to be deliver partially or all at once", track_visibility='onchange'),
        'date_done': fields.datetime('Date of Transfer', help="Date of Completion", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'auto_picking': fields.boolean('Auto-Picking', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'xuly_thncc_id': fields.many2one('stock.picking.in', 'Trả hàng nhà cung cấp'),
        'xuly_huyhang_id': fields.many2one('stock.picking', 'Hủy hàng'),
        'loai_xuly':fields.selection([('trahang_ncc','Trả hàng cho nhà cung cấp'),('huy_hang','Hủy hàng')],'Loại xử lý'),
        'tinhtrang_chatluong': fields.char('Tình trạng chất lượng', size=1024),
        'so_hd': fields.char('Số hóa đơn', size=1024),
        'yeu_cau': fields.char('Yêu cầu', size = 1024),
        'ghi_chu_xhd': fields.char('Ghi chú xuất hóa đơn', size = 1024),
        'exist': fields.function(_kiemtra_trahang, string='Đã tồn tại trong trahang.chokho',
            type='boolean'),
        'trang_thai_hd': fields.function(_trang_thai_hd, string='Trạng thái hóa đơn',
            type='char'),
        'trang_thai':fields.function(_trangthai, string='Trạng thái',
                                      type='selection', selection=[('draft','Nháp'),
                                                                   ('confirmed','Đơn hàng chờ xử lý'),('assigned','Đơn hàng chưa xử lý'),
                                                                   ('done','Đã chuyển'),
                                                                   ('cancel','Đã huỷ bỏ')],
                                     store={
                                            'stock.picking.in':(lambda self, cr, uid, ids, c={}: ids, ['state','flag'], 10),
                                            }),
        'flag':fields.boolean('Check DH chua xu ly')
        
    }
    _defaults = {
                 'flag': False,
                 }
    
    
    def tao_hoa_don(self, cr, uid,ids, context=None):
        picking = self.browse(cr, uid, ids[0])
        if context is None:
            context={}
        context.update({'active_id':ids[0],'active_ids':ids,'active_model':'stock.picking'})
        onshipping_obj = self.pool.get('stock.invoice.onshipping')
        onshipping_id = onshipping_obj.create(cr, uid, {},context)
        return onshipping_obj.open_invoice(cr, uid, [onshipping_id],context)
    
    def xem_phieu_xu_ly(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids[0])
        if line.loai_xuly=='trahang_ncc':
            picking_ids = self.pool.get('stock.picking').search(cr, uid, [('origin','=',line.xuly_thncc_id.name)])
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'stock', 'view_picking_form')
            return {
                        'name': 'Phiếu nhập hàng mua',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'stock.picking.in',
                        'domain': [],
                        'res_id': picking_ids and picking_ids[0] or False,
                        'type': 'ir.actions.act_window',
                        'view_id': res[1],
                        'target': 'current',
                    }
        if line.loai_xuly=='huy_hang':
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'general_stock', 'view_picking_subinventory_form')
            return {
                        'name': 'Xử lý mất mát, hư hỏng',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'stock.picking',
                        'domain': [],
                        'res_id': line.xuly_huyhang_id and line.xuly_huyhang_id.id or False,
                        'view_id': res[1],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                    }
        return True
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(stock_picking_in, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr,uid,ids):
            sql = '''
                update stock_move set date = '%s' where picking_id = %s
            '''%(line.date, line.id)
            cr.execute(sql)
        return new_write
    def bt_chua_xu_ly(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {
                                         'flag': True,
                                         })
stock_picking_in()


class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    def _set_minimum_date(self, cr, uid, ids, name, value, arg, context=None):
        """ Calculates planned date if it is less than 'value'.
        @param name: Name of field
        @param value: Value of field
        @param arg: User defined argument
        @return: True or False
        """
        if not value:
            return False
        if isinstance(ids, (int, long)):
            ids = [ids]
        for pick in self.browse(cr, uid, ids, context=context):
            sql_str = """update stock_move set
                    date_expected='%s'
                where
                    picking_id=%s """ % (value, pick.id)
            if pick.min_date:
                sql_str += " and (date_expected='" + pick.min_date + "')"
            cr.execute(sql_str)
        return True
    def get_min_max_date(self, cr, uid, ids, field_name, arg, context=None):
        """ Finds minimum and maximum dates for picking.
        @return: Dictionary of values
        """
        res = {}
        for id in ids:
            res[id] = {'min_date': False, 'max_date': False}
        if not ids:
            return res
        cr.execute("""select
                picking_id,
                min(date_expected),
                max(date_expected)
            from
                stock_move
            where
                picking_id IN %s
            group by
                picking_id""",(tuple(ids),))
        for pick, dt1, dt2 in cr.fetchall():
            res[pick]['min_date'] = dt1
            res[pick]['max_date'] = dt2
        return res
    def _kiemtra_trahang(self, cr, uid, ids, name, args, context=None):
        res = {}
        picking_ids =[]
        if context is None:
            context = {}
        for picking in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from trahang_chokho where picking_id = %s
            '''%(picking.id)
            cr.execute(sql)
            picking_ids = cr.fetchone()
            if picking_ids:
                res[picking.id] = True
            else:
                res[picking.id] = False
        return res
    
    def _trang_thai_hd(self, cr, uid, ids, name, args, context=None):
        res = {}
        picking_ids =[]
        if context is None:
            context = {}
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.type == 'out':
                for move in picking.move_lines:
                    sql = '''
                        select state from account_invoice where type = 'out_invoice'
                        and id in (select invoice_id from account_invoice_line where source_id = %s)
                    '''%(move.id)
                    cr.execute(sql)
                    trang_thai = cr.fetchone()
                    if not trang_thai:
                        res[picking.id] = 'Chưa có hóa đơn'
                    else:
                        if trang_thai[0] == 'draft':
                            res[picking.id] = 'Chờ duyệt hóa đơn'
                        if trang_thai[0] == 'open':
                            res[picking.id] = 'Chờ thanh toán'
                        if trang_thai[0] == 'paid':
                            res[picking.id] = 'Đã thanh toán'
            if picking.type == 'in':
                for move in picking.move_lines:
                    sql = '''
                        select state from account_invoice where type = 'in_invoice'
                        and id in (select invoice_id from account_invoice_line where source_id = %s)
                    '''%(move.id)
                    cr.execute(sql)
                    trang_thai = cr.fetchone()
                    if not trang_thai:
                        res[picking.id] = 'Chưa có hóa đơn'
                    else:
                        if trang_thai[0] == 'draft':
                            res[picking.id] = 'Chờ duyệt hóa đơn'
                        if trang_thai[0] == 'open':
                            res[picking.id] = 'Chờ thanh toán'
                        if trang_thai[0] == 'paid':
                            res[picking.id] = 'Đã thanh toán'
        return res
    
    def _trangthai(self, cr, uid, ids, name, arg, context=None):
        res = {}
        stock_obj = self.pool.get('stock.picking')
        for tt in self.browse(cr,uid,ids):
            if tt.state == 'draft':
                res[tt.id] = 'draft'
            if tt.state == 'confirmed' and tt.flag == False:
                res[tt.id]='confirmed'
            if tt.state == 'confirmed' and tt.flag == True:
                res[tt.id]='assigned'    
            if tt.state == 'cancel':
                res[tt.id]='cancel'
            if tt.state == 'assigned':
                res[tt.id]='assigned'
            if tt.state == 'done':
                res[tt.id]='done'
        return res
    
    _columns = {
        'picking_packaging_line': fields.one2many('stock.picking.packaging','picking_id','Đóng gói'),
        'description': fields.text('Description', track_visibility='onchange'),
        'ngay_gui':fields.date('Ngày gửi'),
        'ngay_nhan':fields.date('Ngày nhận lại'),
        'daidien_khachhang':fields.char('Đại diện khách hàng nhận'),
        'nguoi_giao_hang':fields.many2one('hr.employee','Người giao hàng'),
        'nguoi_van_chuyen':fields.many2one('hr.employee','Người vận chuyển'),
        'phuongtien_giaohang':fields.char('Phương tiện giao hàng'),
        'ly_do_xuat_id': fields.many2one('ly.do.xuat', 'Lý do xuất'),
        'state_receive':fields.selection([('draft','Tạo mới'),('da_gui','Đã gửi'),('da_nhan','Đã nhận')],'Trạng thái',required=True,),
        'nhiet_do':fields.char('Nhiệt độ'),
        'so_luong_thung':fields.char('Số lượng thùng'),
        'time_nhan':fields.datetime('Thời gian nhận'),
        'time_ketthuc':fields.datetime('Thời gian kết thúc'),
        'sampham_lanh':fields.boolean('Sản phẩm lạnh'),
        
        'partner_id': fields.many2one('res.partner', 'Partner', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
#         'stock_journal_id': fields.many2one('stock.journal','Stock Journal', select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'location_id': fields.many2one('stock.location', 'Location', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="Keep empty if you produce at the location where the finished products are needed." \
                "Set a location if you produce at a fixed location. This can be a partner location " \
                "if you subcontract the manufacturing operations.", select=True, track_visibility='onchange'),
        'location_dest_id': fields.many2one('stock.location', 'Dest. Location', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="Location where the system will stock the finished products.", select=True, track_visibility='onchange'),
        'date': fields.datetime('Creation Date', help="Creation date, usually the time of the order.", select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'min_date': fields.function(get_min_max_date, fnct_inv=_set_minimum_date, multi="min_max_date",
                 store=True, type='datetime', string='Scheduled Time', select=1, help="Scheduled time for the shipment to be processed", track_visibility='onchange'),
        'origin': fields.char('Source Document', size=64, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="Reference of the document", select=True, track_visibility='onchange'),
        'move_lines': fields.one2many('stock.move', 'picking_id', 'Internal Moves', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, track_visibility='onchange'),
        'company_id': fields.many2one('res.company', 'Company', required=True, select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'move_type': fields.selection([('direct', 'Partial'), ('one', 'All at once')], 'Delivery Method', required=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="It specifies goods to be deliver partially or all at once", track_visibility='onchange'),
        'date_done': fields.datetime('Date of Transfer', help="Date of Completion", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'auto_picking': fields.boolean('Auto-Picking', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, track_visibility='onchange'),
        'xuly_thncc_id': fields.many2one('stock.picking.in', 'Trả hàng nhà cung cấp'),
        'xuly_huyhang_id': fields.many2one('stock.picking', 'Hủy hàng'),
        'loai_xuly':fields.selection([('trahang_ncc','Trả hàng cho nhà cung cấp'),('huy_hang','Hủy hàng')],'Loại xử lý'),
        'tinhtrang_chatluong': fields.char('Tình trạng chất lượng', size=1024),
        'so_hd': fields.char('Số hóa đơn', size=1024),
        'yeu_cau': fields.char('Yêu cầu', size = 1024),
        'ghi_chu_xhd': fields.char('Ghi chú xuất hóa đơn', size = 1024),
        'exist': fields.function(_kiemtra_trahang, string='Đã tồn tại trong trahang.chokho',
            type='boolean'),
        'trang_thai_hd': fields.function(_trang_thai_hd, string='Trạng thái hóa đơn',
            type='char'),
                
        'trang_thai':fields.function(_trangthai, string='Trạng thái',
                                      type='selection', selection=[('draft','Nháp'),
                                                                   ('confirmed','Đơn hàng chờ xử lý'),('assigned','Đơn hàng chưa xử lý'),
                                                                   ('done','Đã chuyển'),
                                                                   ('cancel','Đã huỷ bỏ')],
                                     store={
                                                'stock.picking':(lambda self, cr, uid, ids, c={}: ids, ['state','flag'], 10),
                                            }),
        'flag':fields.boolean('Check DH chua xu ly')
        
    }
    _defaults = {
                 'flag': False,
                 'state_receive':'draft',
                 }
    
    def xem_phieu_xu_ly(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids[0])
        if line.loai_xuly=='trahang_ncc':
            picking_ids = self.pool.get('stock.picking').search(cr, uid, [('origin','=',line.xuly_thncc_id.name)])
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'stock', 'view_picking_form')
            return {
                        'name': 'Phiếu nhập hàng mua',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'stock.picking.in',
                        'domain': [],
                        'res_id': picking_ids and picking_ids[0] or False,
                        'type': 'ir.actions.act_window',
                        'view_id': res[1],
                        'target': 'current',
                    }
        if line.loai_xuly=='huy_hang':
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'general_stock', 'view_picking_subinventory_form')
            return {
                        'name': 'Xử lý mất mát, hư hỏng',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'stock.picking',
                        'domain': [],
                        'res_id': line.xuly_huyhang_id and line.xuly_huyhang_id.id or False,
                        'view_id': res[1],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                    }
        return True
    
    def onchange_journal(self, cr, uid, ids, stock_journal_id):
        value ={}
        domain = {}
        if not stock_journal_id:
            value.update({'location_id':False,
                           'location_dest_id':False})
            domain.update({'location_id':[('id','=',False)],
                           'location_dest_id':[('id','=',False)]})
        else:
            journal = self.pool.get('stock.journal').browse(cr, uid, stock_journal_id)
            from_location_ids = [x.id for x in journal.from_location_id]
            to_location_ids = [x.id for x in journal.to_location_id]
            domain.update({'location_id':[('id','=',from_location_ids)],
                           'location_dest_id':[('id','=',to_location_ids)]})
            location_choxuly_ids = self.pool.get('stock.location').search(cr, 1, [('name','=','Kho Chờ Xử Lý')])
            location_id = False
            for loca_id in from_location_ids:
                if loca_id not in location_choxuly_ids:
                     location_id = loca_id
                     break
            location_dest_id = False
            if to_location_ids and to_location_ids[0] != location_id:
                location_dest_id = to_location_ids[0]
            value.update({'location_id':location_id,
                          'location_dest_id': location_dest_id})
        return {'value': value,'domain':domain}
    
    def status_send(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'ngay_gui':datetime.now().strftime('%Y-%m-%d'),'state_receive':'da_gui'})
    
    def status_receive(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'ngay_nhan':datetime.now().strftime('%Y-%m-%d'),'state_receive':'da_nhan'})
    
    def status_refresh(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state_receive':'draft'})
    
    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        """ Builds the dict containing the values for the invoice
            @param picking: picking object
            @param partner: object of the partner to invoice
            @param inv_type: type of the invoice ('out_invoice', 'in_invoice', ...)
            @param journal_id: ID of the accounting journal
            @return: dict that will be used to create the invoice object
        """
        
        payment_mode_id = False
        if isinstance(partner, int):
            partner = self.pool.get('res.partner').browse(cr, uid, partner, context=context)
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = partner.property_account_receivable.id
            payment_term = partner.property_payment_term.id or False
            payment_mode_id = picking.sale_id and picking.sale_id.payment_mode_id and picking.sale_id.payment_mode_id.id or False
        else:
            account_id = partner.property_account_payable.id
            payment_term = partner.property_supplier_payment_term.id or False
        comment = self._get_comment_invoice(cr, uid, picking)
        warehouse_id = picking.location_id.warehouse_id.id or False
        if not warehouse_id:
            warehouse_id = picking.location_dest_id.warehouse_id.id or False
        shop_ids = self.pool.get('sale.shop').search(cr, uid, [('warehouse_id','=',warehouse_id)])
        invoice_vals = {
            'name': picking.name,
            'origin': (picking.name or '') + (picking.origin and (':' + picking.origin) or ''),
            'type': inv_type,
            'account_id': account_id,
            'partner_id': partner.id,
            'comment': comment,
            'payment_term': payment_term,
            'fiscal_position': partner.property_account_position.id,
            'date_invoice': context.get('date_inv', False),
            'company_id': picking.company_id.id,
            'user_id': uid,
#             'user_id': uid,
            'hop_dong_nt_id': picking.sale_id and picking.sale_id.hop_dong_nt_id and picking.sale_id.hop_dong_nt_id.id or False,
            'hop_dong_t_id': picking.sale_id and picking.sale_id.hop_dong_t_id and picking.sale_id.hop_dong_t_id.id or False,
            'payment_mode_id':payment_mode_id,
            'shop_id': shop_ids and shop_ids[0] or False,
            'address': picking.diachi_giaohang_id and picking.diachi_giaohang_id.name or False,
            'supplier_invoice_number': picking.so_hd or '',
#             'supplier_invoice_number': self.pool.get('ir.sequence').get(cr, uid, 'so.hd.dau.vao.seq') or '/',
        }
        cur_id = self.get_currency_id(cr, uid, picking)
        if cur_id:
            invoice_vals['currency_id'] = cur_id
        if journal_id:
            invoice_vals['journal_id'] = journal_id
        if inv_type in ['out_invoice']:
            invoice_vals['reference_number'] = self.pool.get('ir.sequence').get(cr, uid, 'so.hd.dau.vao.seq') or '/'
        return invoice_vals
    
    def tao_hoa_don(self, cr, uid,ids, context=None):
        picking = self.browse(cr, uid, ids[0])
        if context is None:
            context={}
        context.update({'active_id':ids[0],'active_ids':ids,'active_model':'stock.picking'})
        onshipping_obj = self.pool.get('stock.invoice.onshipping')
        onshipping_id = onshipping_obj.create(cr, uid, {},context)
        return onshipping_obj.open_invoice(cr, uid, [onshipping_id],context)
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(stock_picking, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr,uid,ids):
            sql = '''
                update stock_move set date = '%s' where picking_id = %s
            '''%(line.date, line.id)
            cr.execute(sql)
        return new_write
    
    def bt_chua_xu_ly(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {
                                         'flag': True,
                                         })
        
stock_picking()

class stock_picking_packaging(osv.osv):
    _name = 'stock.picking.packaging'
    
    def onchange_loai_thung_id(self, cr, uid, ids,loai_thung_id=False,sl_thung=0, context=None):
        res = {'value':{
                        'chi_phi_thung':False,
                        'sl_da':False,
                        'chi_phi_da':False,
                        'chi_phi_nhiet_ke': False,
                      }
               }
        if loai_thung_id:
            loai_thung = self.pool.get('loai.thung').browse(cr, uid, loai_thung_id)
            res['value'].update({
                                'chi_phi_thung':loai_thung.chi_phi_thung*sl_thung,
                                'sl_da':loai_thung.sl_da*sl_thung,
                                'chi_phi_da':loai_thung.chi_phi_da*sl_thung,
                                'chi_phi_nhiet_ke': loai_thung.chi_phi_nhiet_ke*sl_thung,
                                })
            
        return res
    
    def onchange_sl_nhietke(self, cr, uid, ids,sl_nhietke=0,sl_nhietke_conlai=0, context=None):
        
        res = {'value':{
                        'sl_nhietke_conlai':0,
                      }
               }
        if ids:
            for line in self.browse(cr, uid, ids):
                if sl_nhietke<line.sl_nhietke and sl_nhietke<=sl_nhietke_conlai:
                    res['value'].update({
                                'sl_nhietke_conlai':0,
                                })
                if sl_nhietke>line.sl_nhietke:
                    res['value'].update({
                                'sl_nhietke_conlai':sl_nhietke_conlai+sl_nhietke-line.sl_nhietke,
                                })
        else:
            res['value'].update({
                                'sl_nhietke_conlai':sl_nhietke_conlai+sl_nhietke,
                                })
        return res
    
    _columns = {
        'picking_id':fields.many2one('stock.picking', string='Đóng gói'),
        'loai_thung_id': fields.many2one('loai.thung', string='Loại thùng'),
        'sl_thung': fields.integer('SL thùng'),
        'chi_phi_thung': fields.float('CP thùng'),
        'sl_da': fields.float('SL đá'),
        'chi_phi_da': fields.float('CP đá'),
        'sl_nhietke': fields.integer('SL nhiệt kế'),
        'sl_nhietke_conlai': fields.integer('SL nhiệt kế còn lại'),
        'chi_phi_nhiet_ke': fields.float('CP nhiệt kế'),
        'chi_phi_gui_hang': fields.float('CP gửi hàng'),
        'employee_id': fields.many2one('hr.employee','NV giao hàng'),
        'nhietdo_packaging_di':fields.char('Nhiệt độ đi'),
        'nhietdo_packaging_den':fields.char('Nhiệt độ đến'),
        'chiphi_vanchuyen': fields.float('Chi phí vận chuyển'),
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('picking_id', False):
            picking = self.pool.get('stock.picking').browse(cr, uid, vals['picking_id'])
            dldh_obj = self.pool.get('dulieu.donghang')
            dldh_ids = dldh_obj.search(cr, uid, [('partner_id','=',picking.partner_id.id)])
            if not dldh_ids:
                dldh_obj.create(cr, uid, {'partner_id':picking.partner_id.id})
        return super(stock_picking_packaging, self).create(cr, uid, vals, context)
    
stock_picking_packaging()

class loai_thung(osv.osv):
    _name = 'loai.thung'
    
    _columns = {
        'name': fields.char('Tên lại thùng',required=True),
        'the_tich': fields.float('Thể tích',required=True),
        'kich_thuoc':fields.float('Kích thước thùng'),
        'sl_da':fields.float('Số lượng đá'),
        'chi_phi_da':fields.float('Chi phí đá'),
        'chi_phi_thung': fields.float('Chi phí thùng'),
        'chi_phi_nhiet_ke': fields.float('Chi phí nhiệt kế'),
    }
    
    
loai_thung()

class ly_do_xuat(osv.osv):
    _name = 'ly.do.xuat'
    
    _columns = {
        'name': fields.char('Tên',required=True),

    }
ly_do_xuat()

class so_lan_in(osv.osv):
    _name = 'so.lan.in'
    
    _columns = {
        'name': fields.integer('Số lần in hiện tại trong tháng'),
        'thang': fields.integer('Tháng'),

    }
so_lan_in()


class stock_location(osv.osv):
    _inherit = "stock.location"
     
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        ids = self.search(cr, user, [('name', operator, name)]+ args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)
     
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if not args:
            args = []
        stock_journal_pool = self.pool.get('stock.journal')
        if context.has_key('stock_journal_id') and context.get('phucthien_search_khochoxuly_formanager',False):
            if not context['stock_journal_id']:
                #args += [('id', 'in', [])] 
                return super(stock_location, self).search(cr, uid, args, offset, limit, order, context=context, count=count)
            else:
                group_obj = self.pool.get('res.groups')
                group_manager_model, group_manager_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'group_stock_manager')
                group_manger = group_obj.browse(cr, uid, group_manager_id)
                group_user_model, group_user_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'group_stock_user')
                group_user = group_obj.browse(cr, uid, group_user_id)
                location_choxuly_ids = self.search(cr, 1, [('name','=','Kho Chờ Xử Lý')])
                location_ids = []
                stock_journal_obj = stock_journal_pool.browse(cr, uid, context['stock_journal_id'])
                manger_user_ids = [user.id for user in group_manger.users]
                if context.get('location_id') and context['location_id'] =='location':
                    for location in stock_journal_obj.from_location_id:
                        if location_choxuly_ids and location_choxuly_ids[0] == location.id and uid in manger_user_ids:
                            location_ids.append(location.id)
                        if not location_choxuly_ids:
                            location_ids.append(location.id)
                        if location_choxuly_ids and location_choxuly_ids[0] != location.id:
                            location_ids.append(location.id)
                if context.get('location_dest_id') and context['location_dest_id'] =='location_dest':
                    for location in stock_journal_obj.to_location_id:
                        location_ids.append(location.id) 
                #l ocation_ids = super(stock_location, self).search(cr, uid, [('id','child_of',warehouse_obj.lot_stock_id.location_id.id),('inventory_type','=','SubInventory')])
                args += [('id', 'in', location_ids)]
        return super(stock_location, self).search(cr, uid, args, offset, limit, order, context=context, count=count)
stock_location()

class chuyenkho_noibo(osv.osv):
    _name = "chuyenkho.noibo"
    _inherit = ['mail.thread']
    _description = "Chuyển kho nội bộ"
    _order = "id desc"
    
    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  self._name
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        new_id = super(chuyenkho_noibo, self).create(cr, user, vals, context)
        if 'date' in vals:
            sql = '''
                update chuyenkho_noibo_line set date = '%s' where chuyenkho_noibo_id = %s
            '''%(vals['date'], new_id)
            cr.execute(sql)
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(chuyenkho_noibo, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr,uid,ids):
            sql = '''
                update chuyenkho_noibo_line set date = '%s' where chuyenkho_noibo_id = %s
            '''%(line.date, line.id)
            cr.execute(sql)
        return new_write
    
    
    def unlink(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        if context is None:
            context = {}
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.state in ['done','cancel']:
                raise osv.except_osv(_('Error!'), _('You cannot remove the picking which is in %s state!')%(pick.state,))
        return super(chuyenkho_noibo, self).unlink(cr, uid, ids, context=context)
        
    def action_cancel(self, cr, uid, ids, context=None):
        """ Changes picking state to cancel.
        @return: True
        """
        for pick in self.browse(cr, uid, ids, context=context):
            for line in pick.lines:
                self.pool.get('stock.move').action_cancel(cr, uid, [line.move_source_id.id], context)
                self.pool.get('stock.move').action_cancel(cr, uid, [line.move_dest_id.id], context)
                self.pool.get('chuyenkho.noibo.line').write(cr, uid, line.id, {'state': 'cancel'})
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True
    
    
    def force_assign(self, cr, uid, ids,context=None):
        """ Confirms picking directly from draft state.
        @return: True
        """
        for pick in self.browse(cr, uid, ids):
            if not pick.lines:
                raise osv.except_osv(_('Error!'),_('You cannot process picking without stock moves.'))
            self.write(cr,uid,ids,{'state':'confirmed'},context=context)
            for line in pick.lines:
                self.pool.get('chuyenkho.noibo.line').write(cr,uid,line.id,{'state':'confirmed'},context=context)
        return True

    def action_assign(self, cr, uid, ids,context=None):
        """ Changes state of picking to available if all moves are confirmed.
        @return: True
        """
        for pick in self.browse(cr, uid, ids):
            move_ids = [x.id for x in pick.lines if x.state == 'confirmed']
            if not move_ids:
                raise osv.except_osv(_('Warning!'),_('Not enough stock, unable to reserve the products.'))
            self.pool.get('chuyenkho.noibo.line').action_assign(cr, uid, move_ids)
            self.write(cr,uid,ids,{'state':'assigned'},context=context)
        return True
    
    def action_process(self, cr, uid, ids, context=None):
        for pick in self.browse(cr, uid, ids):
            if not pick.lines:
                raise osv.except_osv(_('Error!'),_('You cannot process picking without stock moves.'))
            for line in pick.lines:
                vals_source = {
                            'name':line.product_id and line.product_id.name or False,
                            'product_id':line.product_id and line.product_id.id or False,
                            'product_qty' : line.product_qty,
                            'product_uom': line.product_uom and line.product_uom.id or False,
                            'location_id': line.location_id and line.location_id.id or False,
                            'location_dest_id': line.product_id.property_stock_inventory.id or False,
                            'prodlot_id': line.prodlot_id and line.prodlot_id.id or False,
                            'tracking_id': line.source_tracking_id and line.source_tracking_id.id or False,
                            'date': line.date,
                            'date_expected': line.date,
                            'company_id':pick.company_id and pick.company_id.id or False,
                            'state': 'done',
                    }
                move_source_id = self.pool.get('stock.move').create(cr, uid, vals_source)
                vals_dest = {
                            'name':line.product_id and line.product_id.name or False,
                            'product_id':line.product_id and line.product_id.id or False,
                            'product_qty' : line.product_qty,
                            'product_uom': line.product_uom and line.product_uom.id or False,
                            'location_id': line.product_id.property_stock_inventory.id or False,
                            'location_dest_id': line.location_dest_id and line.location_dest_id.id or False,
                            'prodlot_id': line.prodlot_id and line.prodlot_id.id or False,
                            'tracking_id': line.dest_tracking_id and line.dest_tracking_id.id or False,
                            'date': line.date,
                            'date_expected': line.date,
                            'company_id':pick.company_id and pick.company_id.id or False,
                            'state': 'done',
                    }
                move_dest_id = self.pool.get('stock.move').create(cr, uid, vals_dest)
                self.pool.get('chuyenkho.noibo.line').write(cr,uid,line.id,{'state':'done','move_source_id':move_source_id,'move_dest_id':move_dest_id},context=context)
            self.write(cr,uid,ids,{'state':'done'},context=context)
        return True


    _columns = {
        'name': fields.char('Reference', size=64, select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'origin': fields.char('Source Document', size=64, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="Reference of the document", select=True),
        'note': fields.text('Notes'),
        'location_id': fields.many2one('stock.location', 'Location', required =True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, select=True),
        'location_dest_id': fields.many2one('stock.location', 'Dest. Location', required =True,states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, select=True),
        'state': fields.selection([
            ('draft', 'Nháp'),
            ('assigned', 'Sẵn sàng chuyển'),
            ('confirmed', 'Đơn hàng chờ xử lý'),
            ('cancel', 'Hủy chuyển'),
            ('done', 'Đã chuyển'),
            ], 'Status', readonly=True, select=True),
        'date': fields.datetime('Creation Date', help="Creation date, usually the time of the order.", select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'date_done': fields.datetime('Date of Transfer', help="Date of Completion", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'lines': fields.one2many('chuyenkho.noibo.line', 'chuyenkho_noibo_id', 'Internal Moves', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'partner_id': fields.many2one('res.partner', 'Partner', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'company_id': fields.many2one('res.company', 'Company', required=True, select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'nhietdo_di':fields.char('Nhiệt độ khi đi'),
        'nhietdo_den':fields.char('Nhiệt độ khi đến'),
        }
    
    _defaults = {
        'name': lambda self, cr, uid, context: '/',
        'state': 'draft',
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'chuyenkho.noibo', context=c)
    }
    
chuyenkho_noibo()    

class chuyenkho_noibo_line(osv.osv):

    _name = "chuyenkho.noibo.line"
    _description = "Dòng chuyển kho nội bộ"
    _order = 'date_expected desc, id'
    
    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False,
                            loc_dest_id=False, partner_id=False):
        """ On change of product id, if finds UoM, UoS, quantity and UoS quantity.
        @param prod_id: Changed Product id
        @param loc_id: Source location id
        @param loc_dest_id: Destination location id
        @param partner_id: Address id of partner
        @return: Dictionary of values
        """
        if not prod_id:
            return {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        lang = user and user.lang or False
        if partner_id:
            addr_rec = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if addr_rec:
                lang = addr_rec and addr_rec.lang or False
        ctx = {'lang': lang}

        product = self.pool.get('product.product').browse(cr, uid, [prod_id], context=ctx)[0]
        uos_id  = product.uos_id and product.uos_id.id or False
        result = {
            'name': product.name,
            'product_uom': product.uom_id.id,
            'product_qty': 1.00,
            'prodlot_id' : False,
        }
        if loc_id:
            result['location_id'] = loc_id
        if loc_dest_id:
            result['location_dest_id'] = loc_dest_id
        return {'value': result}
    
    def onchange_lot_id(self, cr, uid, ids, prodlot_id=False, product_qty=False,
                        loc_id=False, product_id=False, uom_id=False, context=None):
        """ On change of production lot gives a warning message.
        @param prodlot_id: Changed production lot id
        @param product_qty: Quantity of product
        @param loc_id: Location id
        @param product_id: Product id
        @return: Warning message
        """
        if not prodlot_id or not loc_id:
            return {}
        ctx = context and context.copy() or {}
        ctx['location_id'] = loc_id
        ctx.update({'raise-exception': True})
        uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        product_uom = product_obj.browse(cr, uid, product_id, context=ctx).uom_id
        prodlot = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_id, context=ctx)
        location = self.pool.get('stock.location').browse(cr, uid, loc_id, context=ctx)
        uom = uom_obj.browse(cr, uid, uom_id, context=ctx)
        amount_actual = uom_obj._compute_qty_obj(cr, uid, product_uom, prodlot.stock_available, uom, context=ctx)
        warning = {}
        if (location.usage == 'internal') and (product_qty > (amount_actual or 0.0)):
            warning = {
                'title': _('Insufficient Stock for Serial Number !'),
                'message': _('You are moving %.2f %s but only %.2f %s available for this serial number.') % (product_qty, uom.name, amount_actual, uom.name)
            }
        return {'warning': warning}
    
    def _default_destination_address(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.partner_id.id
    
    def action_assign(self, cr, uid, ids, *args):
        """ Changes state to confirmed or waiting.
        @return: List of values
        """
        todo = []
        for move in self.browse(cr, uid, ids):
            if move.state in ('confirmed', 'waiting'):
                todo.append(move.id)
        res = self.check_assign(cr, uid, todo)
        return res
    
    def check_assign(self, cr, uid, ids, context=None):
        """ Checks the product type and accordingly writes the state.
        @return: No. of moves done
        """
        done = []
        count = 0
        pickings = {}
        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.product_id.type == 'consu' or move.location_id.usage == 'supplier':
                if move.state in ('confirmed', 'waiting'):
                    done.append(move.id)
                pickings[move.chuyenkho_noibo_id.id] = 1
                continue
            if move.state in ('confirmed', 'waiting'):
                # Important: we must pass lock=True to _product_reserve() to avoid race conditions and double reservations
                if not move.prodlot_id:
                    raise osv.except_osv(_('Warning!'),_("Please input Prodlot"))
                if not move.source_tracking_id:
                    res = self._product_reserve(cr, uid,ids, [move.location_id.id],move.prodlot_id.id, move.product_id.id, move.product_qty, {'uom': move.product_uom.id}, lock=True)
                else:
                    res = self._product_reserve_tracking(cr, uid,ids, [move.location_id.id],move.prodlot_id.id,move.source_tracking_id.id, move.product_id.id, move.product_qty, {'uom': move.product_uom.id}, lock=True)
                if res:
                    self.write(cr, uid, [move.id], {'state':'assigned'})
                    done.append(move.id)
                    pickings[move.chuyenkho_noibo_id.id] = 1
                else:
                    raise osv.except_osv(_('Warning!'),_("Not enough stock for Product '%s'.\nPlease ask for an Internal Moves to Location '%s' and Prodlot '%s'")%(move.product_id.name,move.location_id.name,move.prodlot_id.name))
        return True
    
    def _product_reserve_tracking(self, cr, uid,ids, location_id,prodlot_id,tracking_id, product_id, product_qty, context=None, lock=False):
        """
        Attempt to find a quantity ``product_qty`` (in the product's default uom or the uom passed in ``context``) of product ``product_id``
        in locations with id ``ids`` and their child locations. If ``lock`` is True, the stock.move lines
        of product with id ``product_id`` in the searched location will be write-locked using Postgres's
        "FOR UPDATE NOWAIT" option until the transaction is committed or rolled back, to prevent reservin
        twice the same products.
        If ``lock`` is True and the lock cannot be obtained (because another transaction has locked some of
        the same stock.move lines), a log line will be output and False will be returned, as if there was
        not enough stock.

        :param product_id: Id of product to reserve
        :param product_qty: Quantity of product to reserve (in the product's default uom or the uom passed in ``context``)
        :param lock: if True, the stock.move lines of product with id ``product_id`` in all locations (and children locations) with ``ids`` will
                     be write-locked using postgres's "FOR UPDATE NOWAIT" option until the transaction is committed or rolled back. This is
                     to prevent reserving twice the same products.
        :param context: optional context dictionary: if a 'uom' key is present it will be used instead of the default product uom to
                        compute the ``product_qty`` and in the return value.
        :return: List of tuples in the form (qty, location_id) with the (partial) quantities that can be taken in each location to
                 reach the requested product_qty (``qty`` is expressed in the default uom of the product), of False if enough
                 products could not be found, or the lock could not be obtained (and ``lock`` was True).
        """
        result = []
        amount = 0.0
        if context is None:
            context = {}
        uom_obj = self.pool.get('product.uom')
        uom_rounding = self.pool.get('product.product').browse(cr, uid, product_id, context=context).uom_id.rounding
        if context.get('uom'):
            uom_rounding = uom_obj.browse(cr, uid, context.get('uom'), context=context).rounding

        locations_ids = self.pool.get('stock.location').search(cr, uid, [('location_id', 'child_of', location_id)])
        if locations_ids:
            # Fetch only the locations in which this product has ever been processed (in or out)
            cr.execute("""SELECT l.id FROM stock_location l WHERE l.id in %s AND
                        EXISTS (SELECT 1 FROM stock_move m WHERE m.product_id = %s AND m.prodlot_id = %s AND m.tracking_id = %s
                                AND ((state = 'done' AND m.location_dest_id = l.id)
                                    OR (state in ('done','assigned') AND m.location_id = l.id)))
                       """, (tuple(locations_ids), product_id,prodlot_id,tracking_id))
            locations_ids = [i for (i,) in cr.fetchall()]
        for id in locations_ids:
            if lock:
                try:
                    # Must lock with a separate select query because FOR UPDATE can't be used with
                    # aggregation/group by's (when individual rows aren't identifiable).
                    # We use a SAVEPOINT to be able to rollback this part of the transaction without
                    # failing the whole transaction in case the LOCK cannot be acquired.
                    cr.execute("SAVEPOINT stock_location_product_reserve")
                    cr.execute("""SELECT id FROM stock_move
                                  WHERE product_id=%s AND prodlot_id = %s AND tracking_id = %s AND
                                          (
                                            (location_dest_id=%s AND
                                             location_id<>%s AND
                                             state='done')
                                            OR
                                            (location_id=%s AND
                                             location_dest_id<>%s AND
                                             state in ('done'))
                                          )
                                  FOR UPDATE of stock_move NOWAIT""", (product_id,prodlot_id,tracking_id, id, id, id, id), log_exceptions=False)
                except Exception:
                    # Here it's likely that the FOR UPDATE NOWAIT failed to get the LOCK,
                    # so we ROLLBACK to the SAVEPOINT to restore the transaction to its earlier
                    # state, we return False as if the products were not available, and log it:
                    cr.execute("ROLLBACK TO stock_location_product_reserve")
                    _logger.warning("Failed attempt to reserve %s x product %s, likely due to another transaction already in progress. Next attempt is likely to work. Detailed error available at DEBUG level.", product_qty, product_id)
                    _logger.debug("Trace of the failed product reservation attempt: ", exc_info=True)
                    return False

            # XXX TODO: rewrite this with one single query, possibly even the quantity conversion
            cr.execute("""SELECT product_uom, sum(product_qty) AS product_qty
                          FROM stock_move
                          WHERE location_dest_id=%s AND
                                location_id<>%s AND
                                product_id=%s AND prodlot_id = %s AND tracking_id = %s AND 
                                state='done'
                          GROUP BY product_uom
                       """,
                       (id, id, product_id,prodlot_id,tracking_id))
            results = cr.dictfetchall()
            cr.execute("""SELECT product_uom,-sum(product_qty) AS product_qty
                          FROM stock_move
                          WHERE location_id=%s AND
                                location_dest_id<>%s AND
                                product_id=%s AND prodlot_id = %s AND tracking_id = %s AND
                                state in ('done')
                          GROUP BY product_uom
                       """,
                       (id, id, product_id,prodlot_id,tracking_id))
            results += cr.dictfetchall()
            total = 0.0
            results2 = 0.0
            for r in results:
                amount = uom_obj._compute_qty(cr, uid, r['product_uom'], r['product_qty'], context.get('uom', False))
                results2 += amount
                total += amount
            if total <= 0.0:
                continue

            amount = results2
            compare_qty = float_compare(amount, 0, precision_rounding=uom_rounding)
            if compare_qty == 1:
                if amount > min(total, product_qty):
                    amount = min(product_qty, total)
                result.append((amount, id))
                product_qty -= amount
                total -= amount
                if product_qty <= 0.0:
                    return result
                if total <= 0.0:
                    continue
        return False
    
    def _product_reserve(self, cr, uid, ids,location_id,prodlot_id, product_id, product_qty, context=None, lock=False):
        """
        Attempt to find a quantity ``product_qty`` (in the product's default uom or the uom passed in ``context``) of product ``product_id``
        in locations with id ``ids`` and their child locations. If ``lock`` is True, the stock.move lines
        of product with id ``product_id`` in the searched location will be write-locked using Postgres's
        "FOR UPDATE NOWAIT" option until the transaction is committed or rolled back, to prevent reservin
        twice the same products.
        If ``lock`` is True and the lock cannot be obtained (because another transaction has locked some of
        the same stock.move lines), a log line will be output and False will be returned, as if there was
        not enough stock.

        :param product_id: Id of product to reserve
        :param product_qty: Quantity of product to reserve (in the product's default uom or the uom passed in ``context``)
        :param lock: if True, the stock.move lines of product with id ``product_id`` in all locations (and children locations) with ``ids`` will
                     be write-locked using postgres's "FOR UPDATE NOWAIT" option until the transaction is committed or rolled back. This is
                     to prevent reserving twice the same products.
        :param context: optional context dictionary: if a 'uom' key is present it will be used instead of the default product uom to
                        compute the ``product_qty`` and in the return value.
        :return: List of tuples in the form (qty, location_id) with the (partial) quantities that can be taken in each location to
                 reach the requested product_qty (``qty`` is expressed in the default uom of the product), of False if enough
                 products could not be found, or the lock could not be obtained (and ``lock`` was True).
        """
        result = []
        amount = 0.0
        if context is None:
            context = {}
        uom_obj = self.pool.get('product.uom')
        uom_rounding = self.pool.get('product.product').browse(cr, uid, product_id, context=context).uom_id.rounding
        if context.get('uom'):
            uom_rounding = uom_obj.browse(cr, uid, context.get('uom'), context=context).rounding

        locations_ids = self.pool.get('stock.location').search(cr, uid, [('location_id', 'child_of', location_id)])
        if locations_ids:
            # Fetch only the locations in which this product has ever been processed (in or out)
            cr.execute("""SELECT l.id FROM stock_location l WHERE l.id in %s AND
                        EXISTS (SELECT 1 FROM stock_move m WHERE m.product_id = %s AND m.prodlot_id = %s
                                AND ((state = 'done' AND m.location_dest_id = l.id)
                                    OR (state in ('done','assigned') AND m.location_id = l.id)))
                       """, (tuple(locations_ids), product_id,prodlot_id))
            locations_ids = [i for (i,) in cr.fetchall()]
        for id in locations_ids:
            if lock:
                try:
                    # Must lock with a separate select query because FOR UPDATE can't be used with
                    # aggregation/group by's (when individual rows aren't identifiable).
                    # We use a SAVEPOINT to be able to rollback this part of the transaction without
                    # failing the whole transaction in case the LOCK cannot be acquired.
                    cr.execute("SAVEPOINT stock_location_product_reserve")
                    cr.execute("""SELECT id FROM stock_move
                                  WHERE product_id=%s AND prodlot_id = %s AND
                                          (
                                            (location_dest_id=%s AND
                                             location_id<>%s AND
                                             state='done')
                                            OR
                                            (location_id=%s AND
                                             location_dest_id<>%s AND
                                             state in ('done', 'assigned'))
                                          )
                                  FOR UPDATE of stock_move NOWAIT""", (product_id,prodlot_id, id, id, id, id), log_exceptions=False)
                except Exception:
                    # Here it's likely that the FOR UPDATE NOWAIT failed to get the LOCK,
                    # so we ROLLBACK to the SAVEPOINT to restore the transaction to its earlier
                    # state, we return False as if the products were not available, and log it:
                    cr.execute("ROLLBACK TO stock_location_product_reserve")
                    _logger.warning("Failed attempt to reserve %s x product %s, likely due to another transaction already in progress. Next attempt is likely to work. Detailed error available at DEBUG level.", product_qty, product_id)
                    _logger.debug("Trace of the failed product reservation attempt: ", exc_info=True)
                    return False

            # XXX TODO: rewrite this with one single query, possibly even the quantity conversion
            cr.execute("""SELECT product_uom, sum(product_qty) AS product_qty
                          FROM stock_move
                          WHERE location_dest_id=%s AND
                                location_id<>%s AND
                                product_id=%s AND prodlot_id = %s AND
                                state='done'
                          GROUP BY product_uom
                       """,
                       (id, id, product_id,prodlot_id))
            results = cr.dictfetchall()
            cr.execute("""SELECT product_uom,-sum(product_qty) AS product_qty
                          FROM stock_move
                          WHERE location_id=%s AND
                                location_dest_id<>%s AND
                                product_id=%s AND prodlot_id = %s AND
                                state in ('done', 'assigned')
                          GROUP BY product_uom
                       """,
                       (id, id, product_id,prodlot_id))
            results += cr.dictfetchall()
            total = 0.0
            results2 = 0.0
            for r in results:
                amount = uom_obj._compute_qty(cr, uid, r['product_uom'], r['product_qty'], context.get('uom', False))
                results2 += amount
                total += amount
            if total <= 0.0:
                continue

            amount = results2
            compare_qty = float_compare(amount, 0, precision_rounding=uom_rounding)
            if compare_qty == 1:
                if amount > min(total, product_qty):
                    amount = min(product_qty, total)
                result.append((amount, id))
                product_qty -= amount
                total -= amount
                if product_qty <= 0.0:
                    return result
                if total <= 0.0:
                    continue
        return False
    
    
    _columns = {
        'name': fields.char('Description', required=True, select=True),
        'date': fields.datetime('Date', required=True, select=True, help="Move date: scheduled date until move is done, then date of actual move processing"),
        'date_expected': fields.datetime('Scheduled Date',required=True, select=True, help="Scheduled date for the processing of this move"),
        'product_id': fields.many2one('product.product', 'Product', required=True, select=True, domain=[('type','<>','service')]),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'),
            required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', required=True),
        'location_id': fields.many2one('stock.location', 'Source Location', required=True, select=True, help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations."),
        'location_dest_id': fields.many2one('stock.location', 'Destination Location', required=True, select=True, help="Location where the system will stock the finished products."),
        'partner_id': fields.many2one('res.partner', 'Destination Address ', help="Optional address where goods are to be delivered, specifically used for allotment"),
        'prodlot_id': fields.many2one('stock.production.lot', 'Serial Number', help="Serial number is used to put a serial number on the production", select=True, ondelete='restrict'),
        'source_tracking_id': fields.many2one('stock.tracking', 'Kệ chuyển', select=True),
        'dest_tracking_id': fields.many2one('stock.tracking', 'Kệ đến', select=True),
        'chuyenkho_noibo_id': fields.many2one('chuyenkho.noibo','Reference', ondelete='cascade'),
        'move_source_id': fields.many2one('stock.move', 'Move source', select=True),
        'move_dest_id': fields.many2one('stock.move', 'Move dest', select=True),
        'state': fields.selection([('draft', 'New'),
                                   ('cancel', 'Cancelled'),
                                   ('waiting', 'Waiting Another Move'),
                                   ('confirmed', 'Waiting Availability'),
                                   ('assigned', 'Available'),
                                   ('done', 'Done'),
                                   ], 'Status', readonly=True, select=True),
        }
    
    _defaults = {
        'partner_id': _default_destination_address,
        'product_qty': 1.0,
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'date_expected': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

chuyenkho_noibo_line()

class ve_sinh_kho(osv.osv):
    _name = "ve.sinh.kho"
    
    _columns = {
        'name': fields.date('Ngày', required=True, states={'da_kiemtra': [('readonly', True)], 'huy': [('readonly', True)]}),
        'thoigian_di': fields.char('Thời gian khi di dời hàng đi', size=1024, states={'da_kiemtra': [('readonly', True)], 'huy': [('readonly', True)]}),
        'thoigian_ve': fields.char('Thời gian khi di dời hàng về', size=1024, states={'da_kiemtra': [('readonly', True)], 'huy': [('readonly', True)]}),
        'nhietdo_di': fields.char('Nhiệt độ', size=1024, states={'da_kiemtra': [('readonly', True)], 'huy': [('readonly', True)]}),
        'nhietdo_ve': fields.char('Nhiệt độ', size=1024, states={'da_kiemtra': [('readonly', True)], 'huy': [('readonly', True)]}),
        'location_id': fields.many2one('stock.location', 'Kho', required=True, states={'da_kiemtra': [('readonly', True)], 'huy': [('readonly', True)]}),
        'type': fields.selection([('kho_duoc','Kho dược'),('kho_lanh','Kho lạnh')],'Loại', states={'da_kiemtra': [('readonly', True)], 'huy': [('readonly', True)]}),
        'vesinhkho_line': fields.one2many('ve.sinh.kho.line', 'vesinh_kho_id', 'Nội dung', states={'da_kiemtra': [('readonly', True)], 'huy': [('readonly', True)]}),
        'user_id': fields.many2one('res.users', 'Người thực hiện', states={'da_kiemtra': [('readonly', True)], 'huy': [('readonly', True)]}),
        'nguoi_kiemtra_id': fields.many2one('res.users', 'Người kiểm tra', readonly=True),
        'state': fields.selection([('draft','Mới tạo'),('da_kiemtra','Đã kiểm tra'),('huy','Hủy bỏ')],'Trạng thái', readonly=True),
    }
    
    def _get_vesinhkho_line(self, cr, uid, context=None):
        vals = []
        keys = []
        if context.get('default_type',False) and context['default_type']=='kho_duoc':
            keys = ['Dọn quang','Vệ sinh cửa','Vệ sinh vách ngăn','Vệ sinh giá kệ','Vệ sinh tủ','Vệ sinh sàn']
        if context.get('default_type',False) and context['default_type']=='kho_lanh':
            keys = ['Vệ sinh kệ','Vệ sinh thảm','Vệ sinh vách pallet','Vệ sinh sàn','Vệ sinh vách ngăn','Vệ sinh cửa kho']
        for key in keys:
            vals.append((0,0,{'noi_dung': key}))
        return vals
    
    _defaults = {
        'name': time.strftime('%Y-%m-%d'),
        'user_id': lambda self, cr, uid, c:uid,
        'vesinhkho_line': _get_vesinhkho_line,
        'state': 'draft',
    }
    
    def kiem_tra(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'da_kiemtra','nguoi_kiemtra_id': uid})
    
    def bt_huy(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'huy'})
    
    def in_phieu(self, cr, uid, ids, context=None):
        vsk = self.browse(cr, uid, ids[0])
        if vsk.type=='kho_duoc':
            report_name = 've_sinh_kho_duoc_report'
        else:
            report_name = 've_sinh_kho_lanh_report'
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
        }
    
ve_sinh_kho()

class ve_sinh_kho_line(osv.osv):
    _name = "ve.sinh.kho.line"
    
    _columns = {
        'vesinh_kho_id': fields.many2one('ve.sinh.kho', 'Vệ sinh kho', ondelete='cascade'),
        'noi_dung': fields.text('Nội dung', required=True),
        'thu_hien': fields.text('Thực hiện'),
        'tinhtrang_sauvesinh': fields.text('Tình trạng sau vệ sinh'),
        'ghi_chu': fields.text('Ghi chú'),
    }
    
ve_sinh_kho_line()

class ve_sinh_thangmay(osv.osv):
    _name = "ve.sinh.thangmay"
    
    _columns = {
        'name': fields.date('Ngày', required=True, states={'da_kiemtra': [('readonly', True)], 'huy': [('readonly', True)]}),
        'hutbui': fields.boolean('Hút bụi', states={'da_kiemtra': [('readonly', True)], 'huy': [('readonly', True)]}),
        'lauxaphong': fields.boolean('Lau xà phòng', states={'da_kiemtra': [('readonly', True)], 'huy': [('readonly', True)]}),
        'launuocsach': fields.boolean('Lau nước sạch', states={'da_kiemtra': [('readonly', True)], 'huy': [('readonly', True)]}),
        'user_id': fields.many2one('res.users', 'Người thực hiện', states={'da_kiemtra': [('readonly', True)], 'huy': [('readonly', True)]}),
        'nguoi_kiemtra_id': fields.many2one('res.users', 'Người kiểm tra', readonly=True),
        'ghi_chu': fields.text('Ghi chú', states={'da_kiemtra': [('readonly', True)], 'huy': [('readonly', True)]}),
        'state': fields.selection([('draft','Mới tạo'),('da_kiemtra','Đã kiểm tra'),('huy','Hủy bỏ')],'Trạng thái', readonly=True),
    }
    
    _defaults = {
        'name': time.strftime('%Y-%m-%d'),
        'user_id': lambda self, cr, uid, c:uid,
        'state': 'draft',
    }
    
    def kiem_tra(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'da_kiemtra','nguoi_kiemtra_id': uid})
    
    def bt_huy(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'huy'})
    
ve_sinh_thangmay()

class phongchong_moi_mot(osv.osv):
    _name = "phongchong.moi.mot"
    
    _columns = {
        'name': fields.date('Ngày', required=True),
        'khuvuc_thuhien': fields.text('Khu vực thực hiện', required=True),
        'bienphap_thuchien': fields.text('Biện pháp thực hiện', required=True),
        'tinhtrang_sauxuly': fields.text('Tình trạng sau xử lý', required=True),
        'ghi_chu': fields.text('Ghi chú'),
        'user_id': fields.many2one('res.users', 'Người kiểm tra', required=True),
    }
    
    _defaults = {
        'name': time.strftime('%Y-%m-%d'),
        'user_id': lambda self, cr, uid, c:uid,
    }
    
phongchong_moi_mot()

class suachua_hanhdong(osv.osv):
    _name = "suachua.hanhdong"
    
    _columns = {
        'name': fields.char('Bộ phận', size=1024, required=True),
        'ngay_kt': fields.date('Ngày kiểm tra', required=True),
        'ngay_bc': fields.date('Ngày báo cáo', required=True),
        'sc_hd_line': fields.one2many('suachua.hanhdong.line', 'sc_hd_id', 'Nội dung'),
    }
    
    _defaults = {
    }
    
suachua_hanhdong()

class suachua_hanhdong_line(osv.osv):
    _name = "suachua.hanhdong.line"
    
    _columns = {
        'name': fields.char('Số', size=1024, required=True),
        'doan_thanhtra': fields.text('Ghi nhận đoàn thanh tra'),
        'nguyen_nhan': fields.text('Nguyên Nhân'),
        'hanh_dong': fields.text('Hành Động'),
        'thoi_gian': fields.text('Thời Gian'),
        'tinh_trang': fields.text('Tình Trạng'),
        'sc_hd_id': fields.many2one('suachua.hanhdong', 'Sửa chữa hành động', ondelete='cascade'),
    }
    
suachua_hanhdong_line()

class nhap_dulieu_donghang(osv.osv):
    _name = "nhap.dulieu.donghang"
    
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Đối tác', required = True),
        'ngay': fields.date('Ngày thu hồi', required=True),
        'sl_nhietke_thuhoi': fields.integer('Số lượng nhiệt kế thu hồi', required=True),
        'state': fields.selection([('moi_tao','Mới tạo'),('da_capnhat','Đã cập nhật')],'Trạng thái'),
    }
    
    _defaults = {
        'ngay': time.strftime('%Y-%m-%d'),
        'state': 'moi_tao',
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('partner_id', False):
            dldh_obj = self.pool.get('dulieu.donghang')
            dldh_ids = dldh_obj.search(cr, uid, [('partner_id','=',vals['partner_id'])])
            if not dldh_ids:
                dldh_obj.create(cr, uid, {'partner_id':vals['partner_id']})
        return super(nhap_dulieu_donghang, self).create(cr, uid, vals, context)
    
    def cap_nhat(self, cr, uid, ids, context=None):
        packaging_obj = self.pool.get('stock.picking.packaging')
        for line in self.browse(cr, uid, ids):
            sql = '''
                select id from stock_picking_packaging where sl_nhietke_conlai is not null and sl_nhietke_conlai>0
                    and picking_id in (select id from stock_picking where state='done' and type='out' and partner_id=%s) order by create_date
            '''%(line.partner_id.id)
            cr.execute(sql)
            packaging_ids = [r[0] for r in cr.fetchall()]
            sl_nhietke_thuhoi = line.sl_nhietke_thuhoi
            for packaging in packaging_obj.browse(cr, uid, packaging_ids):
                if packaging.sl_nhietke_conlai<=sl_nhietke_thuhoi:
                    packaging_obj.write(cr, uid, [packaging.id],{'sl_nhietke_conlai':0})
                    sl_nhietke_thuhoi -= packaging.sl_nhietke_conlai
                else:
                    packaging_obj.write(cr, uid, [packaging.id],{'sl_nhietke_conlai':packaging.sl_nhietke_conlai-sl_nhietke_thuhoi})
                    break
        return self.write(cr, uid, ids, {'state':'da_capnhat'})
    
nhap_dulieu_donghang()

class dulieu_donghang(osv.osv):
    _name = "dulieu.donghang"
    
    def _get_sum_sl_nhietke(self, cr, uid, ids, name, args, context=None):
        res = {}
        if context is None:
            context = {}
        for dulieu in self.browse(cr, uid, ids, context=context):
            amount = 0
            sql = '''
                select case when sum(sl_nhietke)!=0 then sum(sl_nhietke) else 0 end sl_nhietke from stock_picking_packaging
                where picking_id in (select id from stock_picking where partner_id = %s and type = 'out' and state = 'done')
            '''%(dulieu.partner_id.id)
            cr.execute(sql)
            sl_nhietke = cr.dictfetchone()['sl_nhietke']
            res[dulieu.id] = sl_nhietke
        return res
    
    def _get_sl_nhietke_conlai(self, cr, uid, ids, name, args, context=None):
        res = {}
        if context is None:
            context = {}
        for dulieu in self.browse(cr, uid, ids, context=context):
            amount = 0
            sql = '''
                select case when sum(sl_nhietke_conlai)!=0 then sum(sl_nhietke_conlai) else 0 end sl_nhietke from stock_picking_packaging
                where picking_id in (select id from stock_picking where partner_id = %s and type = 'out' and state = 'done')
            '''%(dulieu.partner_id.id)
            cr.execute(sql)
            sl_nhietke = cr.dictfetchone()['sl_nhietke']
            res[dulieu.id] = sl_nhietke
        return res
    
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Đối tác', required = True),
        'sl_nhietke':fields.function(_get_sum_sl_nhietke,type='float',string='Số lượng nhiệt kế'),
        'sl_nhietke_thuhoi': fields.integer('Số lượng nhiệt kế thu hồi'),
        'sl_nhietke_conlai': fields.function(_get_sl_nhietke_conlai,type='float',string='Số lượng nhiệt kế còn lại'),
    }
    
    def _check_sl_nhietke_thuhoi(self, cr, uid, ids, context=None):
        for sl in self.browse(cr, uid, ids, context=context):
            if sl.sl_nhietke_thuhoi>sl.sl_nhietke:
                raise osv.except_osv(_('Warning!'),_(' Số lượng nhiệt kế thu hồi không được lớn hơn số lượng nhiệt kế'))
                return False
        return True
        
    _constraints = [
        (_check_sl_nhietke_thuhoi, 'Identical Data', []),
    ] 
    
dulieu_donghang()

class dm_thietbi(osv.osv):
    _name = "dm.thietbi"
    
    def _get_ngay_canhbao(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            canh_bao = line.canh_bao or 0
            ngay_canhbao = datetime.strptime(line.ngay_kt,'%Y-%m-%d') + timedelta(days=-canh_bao)
            res[line.id]=ngay_canhbao.strftime('%Y-%m-%d')
        return res
    
    _columns = {
        'dia_diem': fields.selection([('van_phong', 'Văn phòng'),('kho_lanh', 'Kho lạnh')],'Địa điểm', required=True),
        'name': fields.char('Mã hiệu', size = 64, required = True),
        'ten': fields.char('Tên thiết bị', size = 64, required = True),
        'kich_thuoc':fields.char('Kích thước', size = 64, required = True),
        'ngay_mua': fields.date('Ngày mua'),
        'so_luong': fields.integer('Số lượng'),
        'chi_phi': fields.float('Chi phí'),
        'ngay_bd': fields.date('Ngày bắt đầu HC/KĐ/Bảo trì',required=True),
        'ngay_kt': fields.date('Ngày kết thúc HC/KĐ/Bảo trì',required=True),
        'ghi_chu': fields.text('Ghi chú'),
        'canh_bao': fields.integer('Cảnh báo'),
        'ngay_canhbao': fields.function(_get_ngay_canhbao, type='date', string='Ngày cảnh báo'),
    }
    
dm_thietbi()

class dutru_hanghoa(osv.osv):
    _name = "dutru.hanghoa"
    
    _columns = {
        'name': fields.date('Ngày', required = True, states={ 'duyet':[('readonly', True)]}),
        'tile_dutru': fields.float('Tỉ lệ (%)', required = True, states={ 'duyet':[('readonly', True)]}),
        'state':fields.selection([('moi_tao', 'Mới tạo'),('duyet', 'Đã duyệt')],'Trạng thái', readonly=True),
        'dutru_hanghoa_line': fields.one2many('dutru.hanghoa.line','dutru_id','Line',states={ 'duyet':[('readonly', True)]}),
    }
    
    _defaults = {
        'state': 'moi_tao',
                 }
    
    def onchange_name(self, cr, uid, ids,name = False, tile_dutru = 0):
        vals = {}
        dutru_hanghoa_line = []
        stt = 0
        if name:
            for dutru in self.browse(cr, uid, ids):
                sql = '''
                    delete from dutru_hanghoa_line where dutru_id = %s
                '''%(dutru.id)
                cr.execute(sql)
            dt = datetime.strptime(name, DATE_FORMAT)
            start = dt - timedelta(days=dt.weekday())
            sql = '''
                select product_id, sum(product_qty) as sl_ban_trongtuan from stock_move where picking_id in (select id from stock_picking where type = 'out' and state = 'done'
                and date between '%s' and '%s') and picking_id is not null
                group by product_id
            '''%(start,dt)
            cr.execute(sql)
            for move in cr.dictfetchall():
                sql = '''
                    select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                                (select st.product_qty
                                    from stock_move st 
                                    where st.state='done' and st.product_id=%s and st.location_dest_id in (select id from stock_location
                                                                                            where usage = 'internal')
                                union all
                                select st.product_qty*-1
                                    from stock_move st 
                                    where st.state='done' and st.product_id=%s and st.location_id in (select id from stock_location
                                                                                            where usage = 'internal')
                                )foo
                '''%(move['product_id'], move['product_id'])
                cr.execute(sql)
                ton_sl = cr.dictfetchone()['ton_sl']
                if ton_sl<move['sl_ban_trongtuan']:
                    stt += 1
                    product = self.pool.get('product.product').browse(cr,uid,move['product_id'])
                    rs = {
                            'stt': stt,
                            'product_id':product.id,
                            'uom_id':product.uom_id and product.uom_id.id or False,
                            'sl_trungbinh':move['sl_ban_trongtuan'],
                            'sl_tonkho':ton_sl,
                            'sl_dutru':round((move['sl_ban_trongtuan']-ton_sl) + ((move['sl_ban_trongtuan']-ton_sl)*(tile_dutru or 0)/100)),
                            'price_unit':product.standard_price,
                            'thanh_tien':round((move['sl_ban_trongtuan']-ton_sl) + ((move['sl_ban_trongtuan']-ton_sl)*(tile_dutru or 0)/100))*product.standard_price, 
                            }
                    dutru_hanghoa_line.append((0,0,rs))
        return {'value': {'dutru_hanghoa_line':dutru_hanghoa_line}   }
    
    def bt_duyet(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'duyet'})
dutru_hanghoa()

class dutru_hanghoa_line(osv.osv):
    _name = "dutru.hanghoa.line"
    
    _columns = {
        'dutru_id': fields.many2one('dutru.hanghoa', 'Du Tru Hang Hoa', ondelete = 'cascade'),
        'stt': fields.integer('STT'),
        'product_id': fields.many2one('product.product', 'TÊN SẢN PHẨM'),
        'uom_id': fields.many2one('product.uom', 'ĐƠN VỊ TÍNH'),
        'sl_trungbinh': fields.float('SỐ LƯỢNG TRUNG BÌNH BÁN RA/TUẦN'),
        'sl_tonkho': fields.float('SỐ LƯỢNG TỒN KHO'),
        'sl_dutru': fields.float('SỐ LƯỢNG DỰ TRÙ', digits=(16,0)),
        'ngay_dexuat': fields.date('ĐỀ XUẤT NGÀY NHẬP HÀNG'),
        'price_unit': fields.float('GIÁ'),
        'thanh_tien': fields.float('THÀNH TIỀN'),
        'ghi_chu': fields.char('GHI CHÚ'),
    }
    
dutru_hanghoa_line()

class trahang_chokho(osv.osv):
    _name = "trahang.chokho"
    
    def _invoice(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for trahang in self.browse(cr,uid,ids):
            picking = self.pool.get('stock.picking').browse(cr,uid,trahang.picking_id.id)
            for line in picking.move_lines:
                sql = '''
                    select invoice_id from account_invoice_line where source_id = %s
                '''%(line.id)
                cr.execute(sql)
                invoice_id = cr.fetchone()
            res[trahang.id] = invoice_id and invoice_id[0] or False
        return res
    
    def _trangthai(self, cr, uid, ids, name, arg, context=None):
        res = {}
        qty = 0
        for guihang in self.browse(cr,uid,ids):
            for line in guihang.trahang_chokho_line:
                qty += line.qty_conlai
            if qty == 0:
                res[guihang.id] = 'done'
            else:
                res[guihang.id] = 'cho_gh'
        return res
    
    _columns = {
        'invoice_id': fields.function(_invoice, string='Hóa đơn',
            type='many2one', relation='account.invoice'),
        'partner_id': fields.many2one('res.partner', 'Khách hàng', required = True),
        'picking_id': fields.many2one('stock.picking', 'Phiếu xuất kho'),
        'trahang_chokho_line': fields.one2many('trahang.chokho.line','trahang_id','Tra Hang'),
        'giaohang_line': fields.one2many('giaohang.line','trahang_id','Giao Hang'),
        'date': fields.date('Ngày gửi hàng', required = True),
        'state': fields.function(_trangthai, string='Trạng thái', type='selection', selection=[('cho_gh','Chờ giao hàng'),('done','Đã giao hàng')]),
    }
    
    def bt_save(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}
    
    def bt_print_bbgh(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'trahang.chokho'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'bien_ban_gui_hang_report', 'datas': datas}
    
    def bt_giaohang(self, cr, uid, ids, context=None):
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_phucthien_stock', 'giaohang_popup_form_view')
        ct_giaohang_line = []
        for guihang in self.browse(cr,uid,ids):
            for gh_line in guihang.trahang_chokho_line:
                ct_giaohang_line.append((0,0,{
                                       'product_code': gh_line.product_code,
                                       'product_id': gh_line.product_id.id,
                                       'product_qty': gh_line.qty_conlai,
                                       'qty_conlai': gh_line.qty_conlai,
                                       'product_uom': gh_line.product_uom and gh_line.product_uom.id or False,
                                       'prodlot_id': gh_line.prodlot_id and gh_line.prodlot_id.id or False,
                                       'tracking_id': gh_line.tracking_id and gh_line.tracking_id.id or False,
                                       'guihang_id': gh_line.id and gh_line.id or False,
                                       }))
            return {
                    'name': 'Giao Hàng',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': res[1],
                    'res_model': 'giaohang.line',
                    'domain': [],
                    'context': {
                        'default_trahang_id': guihang.id,
                        'default_ct_giaohang_line': ct_giaohang_line,
                            },
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    }
    
trahang_chokho()

class trahang_chokho_line(osv.osv):
    _name = "trahang.chokho.line"
    
    def _qty_conlai(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for guihang_line in self.browse(cr,uid,ids):
            sql = '''
                select case when sum(product_qty)!=0 then sum(product_qty) else 0 end qty_giaohang from ct_giaohang_line 
                where guihang_id = %s
            '''%(guihang_line.id)
            cr.execute(sql)
            qty_giaohang = cr.dictfetchone()['qty_giaohang']
            res[guihang_line.id] = guihang_line.product_qty-qty_giaohang
        return res
    
    _columns = {
        'trahang_id': fields.many2one('trahang.chokho', 'Tra Hang Hoa', ondelete = 'cascade'),
        'product_id': fields.many2one('product.product', 'Sản phẩm'),
        'product_code': fields.char('Mã sản phẩm', size = 1024),
        'product_qty': fields.float('Số lượng'),
        'product_uom': fields.many2one('product.uom', 'Đơn vị quy đổi'),
        'prodlot_id': fields.many2one('stock.production.lot', 'Lô hàng'),
        'tracking_id': fields.many2one('stock.tracking', 'Kệ'),
        'qty_conlai': fields.function(_qty_conlai, string='Số lượng còn lại', type='float'),
    }
    
trahang_chokho_line()

class giaohang_line(osv.osv):
    _name = "giaohang.line"
    
    _columns = {
        'trahang_id': fields.many2one('trahang.chokho', 'Tra Hang Hoa', ondelete = 'cascade'),
        'date': fields.date('Ngày lấy hàng'),
        'ngay_gui':fields.date('Ngày gửi'),
        'ngay_nhan':fields.date('Ngày nhận lại'),
        'ct_giaohang_line': fields.one2many('ct.giaohang.line','giaohang_id','Giao Hang'),
        'state_receive':fields.selection([('draft','Tạo mới'),('da_gui','Đã gửi'),('da_nhan','Đã nhận')],'Trạng thái',required=True),
    }
    _defaults = {
        'date': time.strftime('%Y-%m-%d'),
        'state_receive':'draft',
                 }
    
    def status_send(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'ngay_gui':datetime.now().strftime('%Y-%m-%d'),'state_receive':'da_gui'})
    
    def status_receive(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'ngay_nhan':datetime.now().strftime('%Y-%m-%d'),'state_receive':'da_nhan'})
    
    def bt_save(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}
    
    def bt_print_bbgn(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'giaohang.line'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'bien_ban_giao_nhan_kh_gui_hang_report', 'datas': datas}
    
    def bt_print_bbgn_hh(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'giaohang.line'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'bienbangiaonhan_khguihang_hanghoa_report', 'datas': datas}
    
giaohang_line()

class ct_giaohang_line(osv.osv):
    _name = "ct.giaohang.line"
    
    _columns = {
        'giaohang_id': fields.many2one('giaohang.line', 'Giao Hàng', ondelete = 'cascade'),
        'product_id': fields.many2one('product.product', 'Sản phẩm'),
        'product_code': fields.char('Mã sản phẩm', size = 1024),
        'product_qty': fields.float('Số lượng'),
        'product_uom': fields.many2one('product.uom', 'Đơn vị quy đổi'),
        'prodlot_id': fields.many2one('stock.production.lot', 'Lô hàng'),
        'tracking_id': fields.many2one('stock.tracking', 'Kệ'),
        'guihang_id': fields.many2one('trahang.chokho.line', 'GuiHang_id'),
        'qty_conlai': fields.float('Số lượng còn lại'),
    }
    
    def _check_qty_conlai(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if line.product_qty > line.qty_conlai:
                raise osv.except_osv(_('Cảnh báo!'),_('Số lượng giao không được nhiều hơn số lượng còn lại'))
        return True
    _constraints = [
        (_check_qty_conlai, 'Identical Data', []),
    ]
    
ct_giaohang_line()
class so_hoadon_dauvao(osv.osv):
    _name = 'so.hoadon.dauvao'
    
    _columns = {
        'name':fields.integer('Số hóa đơn', required = True),
        
    }
    def duyet(self, cr, uid, ids, context=None):
        account_model, so_hoadon = self.pool.get('ir.model.data').get_object_reference(cr,uid, 'general_account', 'sequence_hoadon_dauvao_1_item')
        self.pool.get('ir.sequence').check_access_rule(cr,uid, [so_hoadon], 'read', context = context)
        for line in self.browse(cr,uid,ids):
            self.pool.get('ir.sequence').write(cr,uid,[so_hoadon],{'number_next_actual':line.name})
        return self.write(cr, uid, ids, {'state': 'da_duyet'})
    def create(self, cr, uid, vals, context=None):
        account_model, so_hoadon = self.pool.get('ir.model.data').get_object_reference(cr,uid, 'general_account', 'sequence_hoadon_dauvao_1_item')
        self.pool.get('ir.sequence').check_access_rule(cr,uid, [so_hoadon], 'read', context = context)
        new_id = super(so_hoadon_dauvao, self).create(cr, uid, vals, context)
        line = self.browse(cr, uid, new_id)
        self.pool.get('ir.sequence').write(cr,uid,[so_hoadon],{'number_next_actual':line.name})
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        account_model, so_hoadon = self.pool.get('ir.model.data').get_object_reference(cr,uid, 'general_account', 'sequence_hoadon_dauvao_1_item')
        self.pool.get('ir.sequence').check_access_rule(cr,uid, [so_hoadon], 'read', context = context)
        new_write = super(so_hoadon_dauvao, self).write(cr, uid, ids, vals, context=context) 
        for line in self.browse(cr,uid,ids):
           self.pool.get('ir.sequence').write(cr,uid,[so_hoadon],{'number_next_actual':line.name}) 
        return new_write    
so_hoadon_dauvao()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
