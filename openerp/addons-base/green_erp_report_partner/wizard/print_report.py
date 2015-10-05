# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from osv import fields, osv
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import decimal_precision as dp
from tools.translate import _
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
from datetime import datetime
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


class general_aged_partner_balance(osv.osv_memory):
    
    def get_account_combo (self,cr,uid,context=None):  
        result = []
        sql ='''
            select id ,code || '-' || name from account_account where code in (
            select distinct code from fn_get_account_liability()) 
            order by code
        '''
        cr.execute(sql)
        vouchers = cr.fetchall()
        for line in vouchers:
            result.append((line[0], line[1]))   
        return result
    
    def _get_fiscalyear(self, cr, uid, context=None):
        
        now = time.strftime('%Y-%m-%d')
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return fiscalyears and fiscalyears[0] or False
    
    _name = "general.aged.partner.balance"
    _columns = {
        'times': fields.selection([
            ('periods', 'Periods'),
            ('dates','Dates'),
            ('years','Years')], 'Time', required=True ),
        'partner_id': fields.many2one('res.partner','Partner'),
        'date_start':fields.date('Start Date'),
        'date_end' :fields.date('End date'),
        'check':fields.boolean('Clearing'),
#         'warehouse_id':fields.many2one('stock.warehouse','Warehouse'),
        'period_id_start': fields.many2one('account.period', 'Start Period',  domain=[('state','=','draft')],),
        'period_id_end': fields.many2one('account.period', 'End Perirod',  domain=[('state','=','draft')],),
        'fiscalyear_start': fields.many2one('account.fiscalyear', 'Start Fiscalyear', domain=[('state','=','draft')],),
        'fiscalyear_stop': fields.many2one('account.fiscalyear', 'Stop Fiscalyear',  domain=[('state','=','draft')],),
        'type': fields.selection([
            ('open', 'Open'),
            ('paid','Paid')], 'Type'),
        'account_id': fields.selection(get_account_combo, 'Account',required=True),
        
        'period_length':fields.integer('Period Length (days)', required=True),
        'direction_selection': fields.selection([('Past','Past'),
                                                 ('Future','Future')],
                                                 'Direction', required=True),
                
        'company_id': fields.many2one('res.company', 'Company', required=True),
     }
    
    def _get_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id and user.company_id.id or False
    
    _defaults = {
        'period_length': 30,
        'direction_selection': 'Past',
        
        'date_start': time.strftime('%Y-%m-%d'),
        'date_end': time.strftime('%Y-%m-%d'),
        
        'period_id_start': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],
        'period_id_end': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],
        'fiscalyear_start': _get_fiscalyear,
        'fiscalyear_stop': _get_fiscalyear,
        'times': 'dates',
        'company_id': _get_company,
        }
    
    def review_report(self, cr, uid, ids, context=None):
        report_obj = self.pool.get('general.aged.partner.balance.review')
        report = self.browse(cr, uid, ids[0])
        self.account_id =False
        self.account_code = False
        self.account_name = False
        self.start_date = False
        self.end_date = False
        self.partner_id = False
        self.cr = cr
        self.uid = uid
        
        self.company_name = False
        self.company_address = False
        self.vat = False
        self.total_residual = 0
        self.type = False
        
        def get_company(o, company_id):
            if company_id:
                company_obj = self.pool.get('res.company').browse(self.cr, self.uid,company_id)
                self.company_name = company_obj.name or ''
                self.company_address = company_obj.street or ''
                self.vat = company_obj.vat or ''
            return True
             
        def get_company_name(o):
            get_header(o)
            return self.company_name
        
        def get_company_address(o):
            return self.company_address     
        
        def get_company_vat(o):
            return self.vat    
        
        def get_total_residual(o):
            return self.total_residual
        
        def get_account_name(o):
            if not self.account_code:
                get_account(o)
            return self.account_name
        
        def get_account_code(o):
            if not self.account_code:
                get_account(o)
            return self.account_code
            
        def get_header(o):
            #Get company info
            self.company_id = o.company_id and o.company_id.id or False
            get_company(o,self.company_id)
            
            self.account_id = o.account_id
            self.start_date = o.date_start and o.date_start or ''
            self.partner_id = o.partner_id and o.partner_id.id or 'null'
            self.type = o.check and o.check or False
            
        def get_start_date(o):
            if not self.start_date:
                get_header(o)
            return get_vietname_date(o,self.start_date) 
        
        
        def get_account(o):
            self.account_id = o.account_id and o.account_id or False
            if self.account_id:
                sql ='''
                    select id,code,name from account_account where id = %s
                '''%(self.account_id)
                cr.execute(sql)
                
                for line in cr.dictfetchall():
                    self.account_code = line['code']
                    self.account_name = line['name']
            
        
        def get_total_line(o):
            res = self.pool.get('sql.aged.partner.balance').get_total_line(self.cr, self.start_date,self.account_id,self.partner_id,self.type)
            return res
        
        def get_line(o):
            res = self.pool.get('sql.aged.partner.balance').get_line(self.cr, self.start_date,self.account_id,self.partner_id,self.type)
            return res
        
        def get_vietname_date(o, date):
            if not date:
                date = time.strftime(DATE_FORMAT)
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
        def get_line_review(o):
            res = []
            for seq,line in enumerate(get_line(o)): 
                res.append((0,0,{
                    'seq':line['seq'],
                    'partner_code':line['partner_code'],
                    'partner_name':line['partner_name'],
                    'voucher_no':line['voucher_no'],
                    'date_document':get_vietname_date(o,line['date_document']),
                    'date_due':get_vietname_date(o,line['date_due']),
                    'description':line['description'],
                    'origin_amount':line['origin_amount'],
                    'residual_30':line['residual_30'],
                    'residual_90':line['residual_90'],
                    'residual_180':line['residual_180'],
                    'residual_else':line['residual_else'],
                    'aging_day':line['aging_day'],
                     }))
            for line2 in get_total_line(o):
                res.append((0,0,{
                    'partner_name':'Tổng cộng',
                    'origin_amount':line2['origin_amount'],
                    'residual_30':line2['residual_30'],
                    'residual_90':line2['residual_90'],
                    'residual_180':line2['residual_180'],
                    'residual_else':line2['residual_else'],
                     }))
            return res
        vals = {
            'name': get_company_name(report),
            'address_company': get_company_address(report),
            'vat_company': get_company_vat(report),
            'account_code': get_account_code(report),
            'account_name': get_account_name(report),
            'start_date': get_start_date(report),
            'general_aged_partner_balance_review_line':get_line_review(report),
        }
        report_id = report_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_report_partner', 'report_aged_partner_balance_review')
        return {
                    'name': 'Aged Partner Balance Review',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'general.aged.partner.balance.review',
                    'domain': [],
                    'view_id': res and res[1] or False,
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': report_id,
                }
    
    
    def print_report(self,cr,uid,ids,context=None):
        res = {}
        data = {'ids': context.get('active_ids', [])}
        data['model'] = 'general.aged.partner.balance'
        data['form'] = self.read(cr, uid, ids)[0]
        
        period_length = data['form']['period_length']
        if period_length<=0:
            raise osv.except_osv(_('User Error!'), _('You must set a period length greater than 0.'))
        if not data['form']['date_start']:
            raise osv.except_osv(_('User Error!'), _('You must set a start date.'))

        start = datetime.strptime(data['form']['date_start'], "%Y-%m-%d")

        if data['form']['direction_selection'] == 'Past':
            for i in range(5)[::-1]:
                stop = start - relativedelta(days=period_length)
                res[str(i)] = {
                    'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop - relativedelta(days=1)
        else:
            for i in range(5):
                stop = start + relativedelta(days=period_length)
                res[str(5-(i+1))] = {
                    'name': (i!=4 and str((i) * period_length)+'-' + str((i+1) * period_length) or ('+'+str(4 * period_length))),
                    'start': start.strftime('%Y-%m-%d'),
                    'stop': (i!=4 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop + relativedelta(days=1)
        data['form'].update(res)
        
        report_name = context['type_report'] 
        return {'type': 'ir.actions.report.xml', 'report_name': report_name , 'datas': data}
    
general_aged_partner_balance()

class general_report_partner_ledger(osv.osv_memory):
    _name = "general.report.partner.ledger"
    
    def get_account_combo (self,cr,uid,context=None):  
        result = []
        sql ='''
            select id ,code || '-' || name from account_account where code in (
            select distinct code from fn_get_account_liability()) 
            order by code
        '''
        cr.execute(sql)
        vouchers = cr.fetchall()
        for line in vouchers:
            result.append((line[0], line[1]))   
        return result
    
    
    def _get_fiscalyear(self, cr, uid, context=None):
        now = time.strftime('%Y-%m-%d')
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return fiscalyears and fiscalyears[0] or False
    
    _columns = {
        'times': fields.selection([
            ('periods', 'Periods'),
            ('dates','Dates'),
            ('years','Years')], 'Time', required=True ),
        'account_id': fields.many2one('account.account', 'Account',required=True, domain=[('type','in',('payable','receivable'))]),
        'period_id_start': fields.many2one('account.period', 'Start Period',  domain=[('state','=','draft')],),
        'period_id_end': fields.many2one('account.period', 'End Period',  domain=[('state','=','draft')],),
        'fiscalyear_start': fields.many2one('account.fiscalyear', 'Start Fiscalyear', domain=[('state','=','draft')],),
        'fiscalyear_stop': fields.many2one('account.fiscalyear', 'Stop Fiscalyear',  domain=[('state','=','draft')],),
        'date_start': fields.date('Date Start'),
        'date_end':   fields.date('Date end'),
        'partner_id':fields.many2one('res.partner','Partner',required=True, domain="[]"),
        #'account_id': fields.many2one('account.account', 'Account',required=True, domain=[('type','in',('payable','receivable'))]),
        'account_id': fields.selection(get_account_combo, 'Account',required=True),
        
        'company_id': fields.many2one('res.company', 'Company', required=True),
     }
    
    def _get_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id and user.company_id.id or False
    
    _defaults = {
        #'report_type':'payable',
        'times': 'periods',
        'date_start': time.strftime('%Y-%m-%d'),
        'date_end': time.strftime('%Y-%m-%d'),
        
        'period_id_start': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],
        'period_id_end': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],
        'fiscalyear_start': _get_fiscalyear,
        'fiscalyear_stop': _get_fiscalyear,
        'company_id': _get_company
        }
    
    def onchange_account(self,cr,uid,ids,report_type):
        dom = {}
        value = {}
        account_obj = self.pool.get('account.account')
        if report_type:
            acc_ids = account_obj.search(cr,uid,[('type','=',report_type)])
            if acc_ids:
                value ={'account_id':acc_ids}
                
        return {'value':value}
    def print_report(self, cr, uid, ids, context=None): 
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'general.report.partner.ledger'
        datas['form'] = self.read(cr, uid, ids)[0]
        
        report_name = context['type_report'] 
        return {'type': 'ir.actions.report.xml', 'report_name': report_name , 'datas': datas}
    
    def review_report_in(self, cr, uid, ids, context=None):
        report_obj = self.pool.get('general.report.partner.ledger.review')
        report = self.browse(cr, uid, ids[0])
        self.account_id =False
        self.times = False
        self.start_date = False
        self.end_date = False
        self.company_name = False
        self.company_address = False
        self.vat = False 
        self.cr = cr
        self.uid = uid
        self.account_code = False
        self.account_name = False
        self.partner_id = False
        self.partner_name = False
        self.header = False
        self.total_residual = 0
        self.type = False

        def get_total_residual(o):
            return self.total_residual
        
        def get_company(o, company_id):
            if company_id:
                company_obj = self.pool.get('res.company').browse(cr,uid,company_id)
                self.company_name = company_obj.name or ''
                self.company_address = company_obj.street or ''
                self.vat = company_obj.vat or ''
            return True
          
        def get_company_name(o):
            get_header(o)
            return self.company_name
     
        def get_company_address(o):
            return self.company_address     
         
        def get_company_vat(o):
            return self.vat    

        def get_account_name(o):
            if not self.account_code:
                get_account(o)
            return self.account_name
    
        def get_account_code(o):
            if not self.account_code:
                get_account(o)
            return self.account_code
         
        def get_vietname_date(o, date):
            if not date:
                return ''
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
         
        def get_id(self,get_id):
            if not get_id:
                return 1
            else:
                return get_id
            
        def get_header(o):
            self.times = o.times
            self.partner_id = o.partner_id and o.partner_id.id or False
            self.partner_name = o.partner_id and o.partner_id.name or ''
            #Get company info
            self.company_id = o.company_id and o.company_id.id or False
            get_company(o,self.company_id)
            
            if self.times =='periods':
                self.start_date = self.pool.get('account.period').browse(self.cr,self.uid,get_id(o,o.period_id_start.id)).date_start
                self.end_date   = self.pool.get('account.period').browse(self.cr,self.uid,get_id(o,o.period_id_end.id)).date_stop
                
            elif self.times == 'years':
                self.start_date = self.pool.get('account.fiscalyear').browse(self.cr,self.uid,get_id(o,o.fiscalyear_start.id)).date_start
                self.end_date   = self.pool.get('account.fiscalyear').browse(self.cr,self.uid,get_id(o,o.fiscalyear_stop.id)).date_stop
            else:
                self.start_date = o.date_start
                self.end_date = o.date_end
            
            return True

        def get_partner_title(o):
            if not self.partner_id: 
                header()
            partner_obj = self.pool.get('res.partner').browse(self.cr,1,self.partner_id)
            if partner_obj and partner_obj.customer == True:
                return  u"Khách hàng"
            else:
                return  u"Nhà cung cấp"
            
        def get_partner(o):
            if not self.partner_name:
                get_header(o)
            return self.partner_name
        
        def get_start_date(o):
            if not self.start_date:
                get_header(o)
            return get_vietname_date(o,self.start_date) 
        
        def get_end_date(o):
            if not self.end_date:
                get_header(o)
            return get_vietname_date(o,self.end_date) 
        
        def get_title(o):
            if not self.header:
                get_account(o)
                
            return self.header
        
        
        def get_account(o):
            self.account_id = o.account_id
            if self.account_id:
                sql ='''
                    select id,code,name,type from account_account where id = %s
                '''%(self.account_id)
                self.cr.execute(sql)
                for line in self.cr.dictfetchall():
                    self.account_code = line['code']
                    self.account_name = line['name']
                    
                    if line['type'] =='receivable':
                        self.header = u'SỔ CHI TIẾT PHẢI THU'
                    elif line['type'] == 'payable':
                        self.header = u'SỔ CHI TIẾT PHẢI TRẢ'
                    else:
                        if self.account_code[0] == '1':
                            self.header = u'SỔ CHI TIẾT PHẢI THU'
                        else:
                            self.header = u'SỔ CHI TIẾT PHẢI TRẢ'    
        def get_line(o):
            res = self.pool.get('sql.partner.ledger').get_line(self.cr, self.start_date,self.end_date,self.account_id,self.partner_id)
            return res   
         
        def get_info(o):
            mang=[]
            for line in get_line(o):
                if line['description']=='Số dư đầu kỳ':
                    mang.append((0,0,{
                            'description': line['description'] or '',
                            'acc_code':line['acc_code'] or '',
                            'amount_dr':line['amount_dr'] or '',
                            'amount_cr':line['amount_cr'] or '',
                                     }))
                if line['description'] not in ['Số dư đầu kỳ','Cộng số phát sinh','Số dư cuối kỳ']:
                    mang.append((0,0,{
                            'gl_date': line['gl_date'] or '',
                            'doc_date': line['doc_date'] or '',
                            'doc_no': line['doc_no'] or '',
                            'description': line['description'] or '',
                            'acc_code':line['acc_code'] or '',
                            'amount_dr':line['amount_dr'] or '',
                            'amount_cr':line['amount_cr'] or '',
                                     }))
                if line['description']=='Cộng số phát sinh':
                    mang.append((0,0,{
                            'description': line['description'] or '',
                            'acc_code':line['acc_code'] or '',
                            'amount_dr':line['amount_dr'] or '',
                            'amount_cr':line['amount_cr'] or '',
                                     }))
                if line['description']=='Số dư cuối kỳ':
                    mang.append((0,0,{
                            'description': line['description'] or '',
                            'acc_code':line['acc_code'] or '',
                            'amount_dr':line['amount_dr'] or '',
                            'amount_cr':line['amount_cr'] or '',
                                     }))
            return mang
        vals = {
            'name':get_title(report),
            'start_date':get_start_date(report),
            'end_date':get_end_date(report),
            'start_date_title':'Từ ngày',
            'end_date_title':'đến ngày',
            'ms_thue_title':'MST:',
            'sh_tk_title':'Số hiệu TK:',
            'sh_tk':get_account_code(report),
            'ten_tk_title':'Tên TK:',
            'ten_tk':get_account_name(report),
            'partner_title_title':'partner_title:',
            'partner_title':get_partner(report),
            'nguoi_nop_thue': get_company_name(report),
            'ms_thue': get_company_vat(report),
            'dia_chi': get_company_address(report),
            'general_report_partner_ledger_review_line':get_info(report),
        }
        report_id = report_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_report_partner', 'general_report_partner_ledger_review')
        return {
                    'name': 'General Report Partner Ledger Review',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'general.report.partner.ledger.review',
                    'domain': [],
                    'view_id': res and res[1] or False,
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': report_id,
                }

general_report_partner_ledger()

class general_report_partner_ledger_detail(osv.osv_memory):
    _name = "general.report.partner.ledger.detail"
    
    def get_account_combo (self,cr,uid,context=None):  
        result = []
        sql ='''
            select id ,code || '-' || name from account_account where code in (
            select distinct code from fn_get_account_liability()) 
            order by code
        '''
        cr.execute(sql)
        vouchers = cr.fetchall()
        for line in vouchers:
            result.append((line[0], line[1]))   
        return result
    
    def _get_fiscalyear(self, cr, uid, context=None):
        now = time.strftime('%Y-%m-%d')
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return fiscalyears and fiscalyears[0] or False
    
    _columns = {
        'times': fields.selection([
            ('periods', 'Periods'),
            ('dates','Dates'),
            ('years','Years')], 'Time', required=True ),
        
        'period_id_start': fields.many2one('account.period', 'Start Period',  domain=[('state','=','draft')],),
        'period_id_end': fields.many2one('account.period', 'End Period',  domain=[('state','=','draft')],),
        'fiscalyear_start': fields.many2one('account.fiscalyear', 'Start Fiscalyear', domain=[('state','=','draft')],),
        'fiscalyear_stop': fields.many2one('account.fiscalyear', 'Stop Fiscalyear',  domain=[('state','=','draft')],),
        'date_start': fields.date('Date Start'),
        'date_end':   fields.date('Date end'),
        #'account_id': fields.many2one('account.account', 'Account',domain=[('type','in',('receivable','payable'))],required=True),
        'account_id': fields.selection(get_account_combo, 'Account',required=True),
        
        'company_id': fields.many2one('res.company', 'Company', required=True),
     }
    
    def _get_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id and user.company_id.id or False
    
    _defaults = {
        'times': 'periods',
        'date_start': time.strftime('%Y-%m-%d'),
        'date_end': time.strftime('%Y-%m-%d'),
        
        'period_id_start': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],
        'period_id_end': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],
        
        'fiscalyear_start': _get_fiscalyear,
        'fiscalyear_stop': _get_fiscalyear,
        
        'company_id': _get_company
        }
    
    def review_report(self, cr, uid, ids, context=None):
        report_obj = self.pool.get('general.report.partner.ledger.detail.review')
        report = self.browse(cr, uid, ids[0])
        self.account_id =False
        self.account_code = False
        self.account_name = False
        self.start_date = False
        self.end_date = False
        self.partner_id = False
        self.partner_name = False
        self.uid = uid
        self.cr = cr
        self.company_name = False
        self.company_address = False
        self.vat = False
        self.total_residual = 0
        self.type = False
        
        def get_total_residual(o):
            return self.total_residual
    
        def get_company(o, company_id):
            if company_id:
                company_obj = self.pool.get('res.company').browse(self.cr, self.uid,company_id)
                self.company_name = company_obj.name or ''
                self.company_address = company_obj.street or ''
                self.vat = company_obj.vat or ''
            return True
                 
        def get_company_name(o):
            get_header(o)
            return self.company_name
        
        def get_company_address(o):
            return self.company_address     
        
        def get_company_vat(o):
            return self.vat    
        
        def get_account_name(o):
            if not self.account_code:
                get_account(o)
            return self.account_name
        
        def get_account_code(o):
            if not self.account_code:
                get_account(o)
            return self.account_code
            
#         def get_id(o,get_id):
#             wizard_data = self.localcontext['data']['form']
#             period_id = wizard_data[get_id][0] or wizard_data[get_id][0] or False
#             if not period_id:
#                 return 1
#             else:
#                 return period_id
                
        def get_header(o):
            self.times = o.times
            #Get company info
            self.company_id = o.company_id and o.company_id.id or False
            get_company(o,self.company_id)
            
            if self.times =='periods':
                self.start_date = self.pool.get('account.period').browse(self.cr,self.uid,o.period_id_start.id).date_start
                self.end_date   = self.pool.get('account.period').browse(self.cr,self.uid,o.period_id_end.id).date_stop
                
            elif self.times == 'years':
                self.start_date = self.pool.get('account.fiscalyear').browse(self.cr,self.uid,o.fiscalyear_start.id).date_start
                self.end_date   = self.pool.get('account.fiscalyear').browse(self.cr,self.uid,o.fiscalyear_stop.id).date_stop
            else:
                self.start_date = o.date_start
                self.end_date = o.date_end
        
        def get_start_date(o):
            if not self.start_date:
                get_header(o)
            return get_vietname_date(o,self.start_date) 
        
        def get_end_date(o):
            if not self.end_date:
                get_header(o)
            return get_vietname_date(o,self.end_date) 
        
        def get_account(o):
            self.account_id = o.account_id and o.account_id or False
            if self.account_id:
                sql ='''
                    select id,code,name from account_account where id = %s
                '''%(self.account_id)
                cr.execute(sql)
                
                for line in cr.dictfetchall():
                    self.account_code = line['code']
                    self.account_name = line['name']
            
        
        def get_vietname_date(o, date):
            if not date:
                date = time.strftime(DATE_FORMAT)
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
        def get_total_line(o):
            res = self.pool.get('sql.partner.ledger.detail').get_total_line(self.cr, self.start_date,self.end_date,self.account_id)
            return res
        
        def get_line(o):
            res = self.pool.get('sql.partner.ledger.detail').get_line(self.cr, self.start_date,self.end_date,self.account_id)
            return res
        
        def get_line_review(o):
            res = []
            for line in get_line(o): 
                res.append((0,0,{
                    'seq':line['seq'],
                    'partner_code':line['partner_code'],
                    'partner_name':line['partner_name'],
                    'begin_dr':line['begin_dr'],
                    'begin_cr':line['begin_cr'],
                    'period_dr':line['period_dr'],
                    'period_cr':line['period_cr'],
                    'end_dr':line['end_dr'],
                    'end_cr':line['end_cr'],
                     }))
            for line2 in get_total_line(o):
                res.append((0,0,{
                    'partner_name':'Tổng cộng',
                    'begin_dr':line2['begin_dr'],
                    'begin_cr':line2['begin_cr'],
                    'period_dr':line2['period_dr'],
                    'period_cr':line2['period_cr'],
                    'end_dr':line2['end_dr'],
                    'end_cr':line2['end_cr'],
                     }))
            return res
        
        vals = {
            'name': get_company_name(report),
            'address_company': get_company_address(report),
            'vat_company': get_company_vat(report),
            'account_code': get_account_code(report),
            'account_name': get_account_name(report),
            'start_date': get_start_date(report),
            'end_date': get_end_date(report),
            'general_report_partner_ledger_detail_review_line':get_line_review(report),
        }
        report_id = report_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_report_partner', 'report_general_report_partner_ledger_detail_review')
        return {
                    'name': 'General Report Partner Ledger Detail Review',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'general.report.partner.ledger.detail.review',
                    'domain': [],
                    'view_id': res and res[1] or False,
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': report_id,
                }
    
    def print_report(self, cr, uid, ids, context=None): 
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'general.report.partner.ledger.detail'
        datas['form'] = self.read(cr, uid, ids)[0]
        
        report_name = context['type_report'] 
        return {'type': 'ir.actions.report.xml', 'report_name': report_name , 'datas': datas}

general_report_partner_ledger_detail()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
