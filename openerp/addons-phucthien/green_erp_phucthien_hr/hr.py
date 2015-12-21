# # -*- coding: utf-8 -*-

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

class tinhtrang_suckhoe(osv.osv):
    _name= 'tinhtrang.suckhoe'
    _columns={
              'name':fields.char('Tình trạng sức khỏe'),
              'date':fields.date('Ngày'),
              'employee_id':fields.many2one('hr.employee','Nhân viên')
              }
    _defaults = {
        'date': fields.datetime.now,
        
        }
tinhtrang_suckhoe()

class hr_family(osv.osv):
    _name = "hr.family"
    _description = "Family"
    _order = "employee_id,name"
    _columns = {
        'name' : fields.char("Tên", size=128, required=True),
        'id_no' : fields.char("ID", size=128),
        'birthday' : fields.date('Ngày sinh'),
        'email' : fields.char('Email', size=64),
        'phone' : fields.char('Số điện thoại', size=32),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'relation': fields.char('Mối quan hệ'),
        'note' : fields.text('Ghi chú'),
        'depend': fields.boolean('Phụ thuộc'),
    } 
hr_family()

class hr_employee(osv.osv):
    _inherit= 'hr.employee'
    
    def _get_depend(self, cr, uid, ids, context):
        result = {}
        for line in self.pool.get('hr.family').browse(cr, uid, ids):
            result[line.employee_id.id] = True
        return result.keys()
    
    def _get_depend_qty(self, cr, uid, ids, field_names, arg, context):
        res = {}
        if not ids:
            return
        family_pool = self.pool.get('hr.family')         
        for line in self.browse(cr, uid, ids):
            depend_ids = family_pool.search(cr, uid, [('employee_id','=',line.id),('depend','=',True)])
            depend_qty = len(depend_ids) 
            res[line.id] = depend_qty
        return res

    _columns={
              'tinhtrang_suckhoe_ids':fields.one2many('tinhtrang.suckhoe','employee_id','Tình trạng sức khỏe'),
              'family_ids': fields.one2many('hr.family', 'employee_id','Người phụ thuộc'),
              'depend_qty': fields.function(_get_depend_qty,
                                      store={'hr.family': (_get_depend, ['depend'], 20),}, 
                                      method=True, type='integer', string='Số người phụ thuộc', readonly=True),    
              'phuongtien_giaohang':fields.char('Phương tiện đi lại'),
              }
hr_employee()

class dinhmuc_congtacphi(osv.osv):
    _name= 'dinhmuc.congtacphi'
    def _get_con_lai(self, cr, uid, ids, field_names, arg, context):
        res = {}
        if not ids:
            return
        for line in self.browse(cr, uid, ids):
            res[line.id] = 0
        return res
    
    _columns={
              'name':fields.many2one('hr.employee','Nhân viên',required=True),
              'tu_ngay':fields.date('Từ ngày',required=True),
              'den_ngay':fields.date('Đến ngày',required=True),
              'amount':fields.float('Giá trị',required=True),
              'con_lai': fields.float('Còn lại',required=True),
              }
    
    def onchange_amount(self, cr, uid, ids,amount=0, context=None):
        vals = {}
        if amount:
            return {'value': {'con_lai': amount}}
    
    def _check_ngay(self, cr, uid, ids, context=None):
        for dm in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from dinhmuc_congtacphi where '%s' between tu_ngay and den_ngay and name = %s and id != %s
            '''%(dm.tu_ngay, dm.name.id, dm.id)
            cr.execute(sql)
            ngay_ids = [r[0] for r in cr.fetchall()]
            sql = '''
                select id from dinhmuc_congtacphi where '%s' between tu_ngay and den_ngay and name = %s and id != %s
            '''%(dm.den_ngay, dm.name.id, dm.id)
            cr.execute(sql)
            ngay_ids += [r[0] for r in cr.fetchall()]
            if ngay_ids:
                raise osv.except_osv(_('Cảnh báo!'),_('Bạn đã chọn trùng ngày định mức của nhân viên %s!')%(dm.name.name))           
                return False
            return True
        
    _constraints = [
        (_check_ngay, 'Identical Data', []),
    ]  
dinhmuc_congtacphi()

class hr_expense_line(osv.osv):
    _inherit = "hr.expense.line"
    
#     def _get_dm_con_lai(self, cr, uid, ids, field_names, arg, context):
#         res = {}
#         con_lai = 0
#         if not ids:
#             return
#         for line in self.browse(cr, uid, ids):
#             sql = '''
#                 select amount,id,tu_ngay,den_ngay from dinhmuc_congtacphi where name = %s and '%s' between tu_ngay and den_ngay
#             '''%(line.expense_id.employee_id.id, line.date_value)
#             cr.execute(sql)
#             amount = cr.fetchone()
#             dinh_muc = amount and amount[0] or 0
#             ma_dm = amount and amount[1] or 0
#             tu_ngay = amount and amount[2] or ''
#             den_ngay = amount and amount[3] or ''
#             sql = '''
#                 select case when sum(unit_amount*unit_quantity)!=0 then sum(unit_amount*unit_quantity) else 0 end tong
#                 from hr_expense_line where '%s' between '%s' and '%s' and expense_id in (select id from hr_expense_expense where employee_id = %s)
#                 and id != %s
#             '''%(line.date_value, tu_ngay, den_ngay, line.expense_id.employee_id.id, line.id)
#             cr.execute(sql)
#             tong = cr.dictfetchone()['tong']
#             
#             con_lai = dinh_muc - line.total_amount - tong
#             sql = '''
#                 update dinhmuc_congtacphi set con_lai = %s where id = %s
#             '''%(con_lai, ma_dm)
#             cr.execute(sql)
             
#             res[line.id] = con_lai
#         return res

    _columns = {
#         'dm_con_lai': fields.function(_get_dm_con_lai, type='float', string='Định mức còn lại'),  
        'dm_con_lai': fields.float('Định mức còn lại'),  
        }
    
    def create(self, cr, uid, vals, context=None):
        result = False
        new_id = super(hr_expense_line, self).create(cr, uid, vals, context)
        line = self.browse(cr, uid, new_id)
        sql = '''
            select con_lai,id,tu_ngay,den_ngay,amount from dinhmuc_congtacphi where name = %s and '%s' between tu_ngay and den_ngay
        '''%(line.expense_id.employee_id.id, line.date_value)
        cr.execute(sql)
        amount = cr.fetchone()
        dinhmuc_cl = amount and amount[0] or 0
        ma_dm = amount and amount[1] or 0
        tu_ngay = amount and amount[2] or ''
        den_ngay = amount and amount[3] or ''
        dinhmuc_bd = amount and amount[4] or 0
        sql = '''
            select id from dm_congtacphi_line where dinhmuc_id = %s and expense_id = %s
        '''%(ma_dm, line.expense_id.id)
        cr.execute(sql)
        line_ids = [row[0] for row in cr.fetchall()]
        sql = '''
            select case when sum(unit_amount*unit_quantity)!=0 then sum(unit_amount*unit_quantity) else 0 end tong
            from hr_expense_line where date_value between '%s' and '%s' and expense_id = %s
        '''%(tu_ngay, den_ngay, line.expense_id.id)
        cr.execute(sql)
        tong = cr.dictfetchone()['tong']
        con_lai = dinhmuc_bd - tong
        if line_ids:
            self.pool.get('dm.congtacphi.line').write(cr,uid,line_ids,{
                                                                       'dm_conlai': con_lai,
                                                                       })
            sql = '''
                update dinhmuc_congtacphi set con_lai = %s where id = %s
            '''%(con_lai, ma_dm)
            cr.execute(sql)
        else:
            self.pool.get('dm.congtacphi.line').create(cr,uid,{
                                                               'expense_id': line.expense_id.id,
                                                               'dinhmuc_id': ma_dm,
                                                               'tu_ngay': tu_ngay,
                                                               'den_ngay': den_ngay,
                                                               'dm_bandau': dinhmuc_bd,
                                                               'dm_conlai': con_lai,
                                                               })
            sql = '''
                update dinhmuc_congtacphi set con_lai = %s where id = %s
            '''%(con_lai, ma_dm)
            cr.execute(sql)
        
#         con_lai = dinh_muc - line.total_amount
#         sql = '''
#             update hr_expense_line set dm_con_lai = %s where id = %s
#         '''%(con_lai, new_id)
#         cr.execute(sql)
#         sql = '''
#             update dinhmuc_congtacphi set con_lai = %s where id = %s
#         '''%(con_lai, ma_dm)
#         cr.execute(sql)
        return new_id
     
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(hr_expense_line, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr, uid, ids):
            sql = '''
                select amount,id,tu_ngay,den_ngay from dinhmuc_congtacphi where name = %s and '%s' between tu_ngay and den_ngay
            '''%(line.expense_id.employee_id.id, line.date_value)
            cr.execute(sql)
            amount = cr.fetchone()
            dinh_muc = amount and amount[0] or 0
            ma_dm = amount and amount[1] or 0
            tu_ngay = amount and amount[2] or ''
            den_ngay = amount and amount[3] or ''
            sql = '''
                select case when sum(unit_amount*unit_quantity)!=0 then sum(unit_amount*unit_quantity) else 0 end tong
                from hr_expense_line where '%s' between '%s' and '%s' and expense_id in (select id from hr_expense_expense where employee_id = %s)
            '''%(line.date_value, tu_ngay, den_ngay, line.expense_id.employee_id.id)
            cr.execute(sql)
            tong = cr.dictfetchone()['tong']
            con_lai = dinh_muc - tong
            sql = '''
                update hr_expense_line set dm_con_lai = %s where id = %s
            '''%(con_lai, line.id)
            cr.execute(sql)
            sql = '''
                update dinhmuc_congtacphi set con_lai = %s where id = %s
            '''%(con_lai, ma_dm)
            cr.execute(sql)
        return new_write
    
hr_expense_line()

class hr_expense_expense(osv.osv):
    _inherit = "hr.expense.expense"

    _columns = {
        'dm_congtacphi_line': fields.one2many('dm.congtacphi.line', 'expense_id', 'Expense Lines', readonly=True, states={'draft':[('readonly',False)]} ),
        }
hr_expense_expense() 

class dm_congtacphi_line(osv.osv):
    _name = "dm.congtacphi.line"

    _columns = {
        'expense_id': fields.many2one('hr.expense.expense', 'Expense', ondelete = 'cascade'),
        'dinhmuc_id': fields.many2one('dinhmuc.congtacphi', 'Dinh Muc'),
        'tu_ngay': fields.date('Từ ngày'),
        'den_ngay': fields.date('Đến ngày'),
        'dm_bandau': fields.float('ĐM ban đầu', readonly = True),
        'dm_conlai': fields.float('ĐM còn lại', readonly = True),
        }
dm_congtacphi_line()       

    
