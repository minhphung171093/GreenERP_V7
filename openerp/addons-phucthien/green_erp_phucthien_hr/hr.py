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
from datetime import timedelta
from datetime import datetime
import datetime

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
            select con_lai,id,tu_ngay,den_ngay,amount,name from dinhmuc_congtacphi where name = %s and '%s' between tu_ngay and den_ngay
        '''%(line.expense_id.employee_id.id, line.date_value)
        cr.execute(sql)
        amount = cr.fetchone()
        dinhmuc_cl = amount and amount[0] or 0
        ma_dm = amount and amount[1] or False
        tu_ngay = amount and amount[2] or False
        den_ngay = amount and amount[3] or False
        dinhmuc_bd = amount and amount[4] or 0
        employee_id = amount and amount[5] or False
        if ma_dm:
            dm_truoc_cl = 0
            sql = '''
                select con_lai,id,den_ngay from dinhmuc_congtacphi where name = %s and den_ngay < '%s' and con_lai < 0 limit 1
            '''%(line.expense_id.employee_id.id, tu_ngay)
            cr.execute(sql)
            dm_truoc = cr.fetchone()
            dinhmuc_truoc_cl = dm_truoc and dm_truoc[0] or 0
            ma_dm_truoc = dm_truoc and dm_truoc[1] or False
            den_ngay_truoc = dm_truoc and dm_truoc[2] or False
            if ma_dm_truoc:
                dm_truoc_cl = dinhmuc_truoc_cl
                sql = '''
                    update dinhmuc_congtacphi set con_lai = %s where id = %s
                '''%(0, ma_dm_truoc)
                cr.execute(sql)
                    
            sql = '''
                select id from dm_congtacphi_line where dinhmuc_id = %s and expense_id = %s
            '''%(ma_dm, line.expense_id.id)
            cr.execute(sql)
            line_ids = [row[0] for row in cr.fetchall()]
            con_lai = dinhmuc_cl - line.total_amount + dm_truoc_cl
            if line_ids:
                dm_line = self.pool.get('dm.congtacphi.line').browse(cr,uid,line_ids[0])
                cl = dm_line.dm_conlai - line.total_amount + dm_truoc_cl
                self.pool.get('dm.congtacphi.line').write(cr,uid,line_ids,{
                                                                           'dm_conlai': cl,
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
             
        
        return new_id
     
    def write(self, cr, uid, ids, vals, context=None):
#         new_write = super(hr_expense_line, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr, uid, ids):
            sql = '''
                select con_lai,id,tu_ngay,den_ngay,amount,name from dinhmuc_congtacphi where name = %s and '%s' between tu_ngay and den_ngay
            '''%(line.expense_id.employee_id.id, line.date_value)
            cr.execute(sql)
            amount = cr.fetchone()
            dinhmuc_cl = amount and amount[0] or 0
            ma_dm = amount and amount[1] or 0
            tu_ngay = amount and amount[2] or ''
            den_ngay = amount and amount[3] or ''
            dinhmuc_bd = amount and amount[4] or 0
            employee_id = amount and amount[5] or False
            sql = '''
                select id from dm_congtacphi_line where dinhmuc_id = %s and expense_id = %s
            '''%(ma_dm, line.expense_id.id)
            cr.execute(sql)
            line_ids = [row[0] for row in cr.fetchall()]
            sql = '''
                select case when sum(unit_amount*unit_quantity)!=0 then sum(unit_amount*unit_quantity) else 0 end tong
                from hr_expense_line where date_value between '%s' and '%s' and expense_id in (select id from hr_expense_expense 
                where employee_id = %s)
            '''%(tu_ngay, den_ngay, employee_id)
            cr.execute(sql)
            tong = cr.dictfetchone()['tong']
#             con_lai = dinhmuc_bd - tong
            if line_ids:
                tam = 0
                total = 0
                dm_line = self.pool.get('dm.congtacphi.line').browse(cr,uid,line_ids[0])
                if 'unit_amount' in vals and 'unit_quantity' in vals:
                    total = vals['unit_amount']*vals['unit_quantity']
                if 'unit_amount' in vals:
                    total = vals['unit_amount']*line.unit_quantity
                if 'unit_quantity' in vals:
                    total = vals['unit_quantity']*line.unit_amount
                if line.total_amount > total:
                    tam = line.total_amount - total
                    cl = dm_line.dm_conlai + tam
                    con_lai = dinhmuc_cl + tam
                if line.total_amount < total:
                    tam = total - line.total_amount
                    cl = dm_line.dm_conlai - tam
                    con_lai = dinhmuc_cl - tam
                self.pool.get('dm.congtacphi.line').write(cr,uid,line_ids,{
                                                                           'dm_conlai': cl,
                                                                           })
                
                sql = '''
                    update dinhmuc_congtacphi set con_lai = %s where id = %s
                '''%(con_lai, ma_dm)
                cr.execute(sql)
            else:
                dm_truoc_cl = 0
                sql = '''
                    select con_lai,id from dinhmuc_congtacphi where name = %s and den_ngay < '%s' and con_lai < 0 limit 1
                '''%(line.expense_id.employee_id.id, tu_ngay)
                cr.execute(sql)
                dm_truoc = cr.fetchone()
                dinhmuc_truoc_cl = dm_truoc and dm_truoc[0] or 0
                ma_dm_truoc = dm_truoc and dm_truoc[1] or False
                if ma_dm_truoc:
                    dm_truoc_cl = dinhmuc_truoc_cl
                    sql = '''
                        update dinhmuc_congtacphi set con_lai = %s where id = %s
                    '''%(0, ma_dm_truoc)
                    cr.execute(sql)
                con_lai = dinhmuc_cl - line.total_amount + dm_truoc_cl
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
        return super(hr_expense_line, self).write(cr, uid,ids, vals, context)
    
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

class hr_holidays(osv.osv):
    _inherit = "hr.holidays"
    
    def _check_date_from(self, cr, uid, ids, context=None):
        for hr in self.browse(cr, uid, ids, context=context):
            datetime_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if hr.date_from < datetime_now:
                raise osv.except_osv(_('Warning!'),_('Thời gian bắt đầu không được nhỏ hơn thời gian hiện tại'))
                return False
        return True
    _constraints = [
        (_check_date_from, 'Identical Data', []),
    ]   

hr_holidays()  

    
