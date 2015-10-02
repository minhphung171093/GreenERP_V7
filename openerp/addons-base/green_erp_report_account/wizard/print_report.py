# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

import time
from datetime import datetime
from osv import fields, osv
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import decimal_precision as dp
from tools.translate import _
from openerp import SUPERUSER_ID
DATE_FORMAT = "%Y-%m-%d"

class report_account_in_out_tax(osv.osv_memory):
    _name = "report.account.in.out.tax"
    
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
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'shop_ids': fields.many2many('sale.shop', 'report_in_out_tax_shop_rel', 'product_id', 'shop_id', 'Shop'),
        'filter_type': fields.selection([
            ('1', 'Hợp lệ'),
            ('2','Tất cả')], 'Hiển thị', required=True ),
     }
    
    def _get_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id and user.company_id.id or False
    
    _defaults = {
        'filter_type':'1',
        'times': 'periods',
        'date_start': time.strftime('%Y-%m-%d'),
        'date_end': time.strftime('%Y-%m-%d'),
        
        'period_id_start': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],
        'period_id_end': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],
        
        'fiscalyear_start': _get_fiscalyear,
        'fiscalyear_stop': _get_fiscalyear,
        
        'company_id': _get_company,
        }
    
    
    def finance_report(self, cr, uid, ids, context=None): 
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'report.accounting'
        datas['form'] = self.read(cr, uid, ids)[0]
        
        report_name = context['type_report'] 
        return {'type': 'ir.actions.report.xml', 'report_name': report_name , 'datas': datas}
    
    def review_report_in(self, cr, uid, ids, context=None):
        report_obj = self.pool.get('report.account.in.out.tax.review')
        report = self.browse(cr, uid, ids[0])
        vals = {
            'nguoi_nop_thue': report.company_id.name or '',
            'ms_thue': report.company_id.vat or '',
        }
        report_id = report_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_report_account', 'report_tax_vat_input_review')
        return {
                    'name': 'Taxes VAT INPUT',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'report.account.in.out.tax.review',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': report_id,
                }
    
report_account_in_out_tax()

class account_ledger_report(osv.osv_memory):
    _name = "account.ledger.report"    
    
    def _get_fiscalyear(self, cr, uid, context=None):
        now = time.strftime('%Y-%m-%d')
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return fiscalyears and fiscalyears[0] or False
            
    _columns = {
        'shop_ids': fields.many2many('sale.shop', 'account_ledger_report_shop_rel', 'wizard_id', 'shop_id', 'Shops', required=True),
        
        'times': fields.selection([
            ('dates','Date'),
            ('periods', 'Periods'),
            ('quarter','Quarter'),
            ('years','Years')], 'Periods Type', required=True ),
        'period_id_start': fields.many2one('account.period', 'Period',  domain=[('state','=','draft')],),
        'period_id_end': fields.many2one('account.period', 'End Period',  domain=[('state','=','draft')],),
        'fiscalyear_start': fields.many2one('account.fiscalyear', 'From Fiscalyear', domain=[('state','=','draft')],),
        'fiscalyear_stop': fields.many2one('account.fiscalyear', 'To Fiscalyear',  domain=[('state','=','draft')],),
        'date_start': fields.date('Date start'),
        'date_end':   fields.date('Date end'),
        'quarter':fields.selection([
            ('1', '1'),
            ('2','2'),
            ('3','3'),
            ('4','4')], 'Quarter'),
        'showdetails':fields.boolean('Get Detail'),
        'account_id': fields.many2one('account.account', 'Account', required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
     }
    
    def _get_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id and user.company_id.id or False
    
    def _get_shop_ids(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return [x.id for x in user.shop_ids]
    
    _defaults = {
        'shop_ids': _get_shop_ids,
        'times': 'periods',
        'date_start': time.strftime('%Y-%m-%d'),
        'date_end': time.strftime('%Y-%m-%d'),        
        'period_id_start': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],
        'period_id_end': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],        
        'fiscalyear_start': _get_fiscalyear,
        'fiscalyear_stop': _get_fiscalyear,
        'quarter': '1',
        'company_id': _get_company,
        'showdetails':True
        }
    
    def finance_report(self, cr, uid, ids, context=None): 
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'account.ledger.report'
        datas['form'] = self.read(cr, uid, ids)[0]    
        this = self.browse(cr,uid,ids[0])
        if this.showdetails:
            report_name = 'account_detail_ledger_report'
        else:
            report_name = 'account_ledger_report'
            
        return {'type': 'ir.actions.report.xml', 'report_name': report_name , 'datas': datas}
    
    def review_report(self, cr, uid, ids, context=None):
        report_obj = self.pool.get('account.ledger.report.review')
#         report = self.browse(cr, uid, ids[0])
        ###
        self.company_name = ''
        self.company_address = ''
        self.vat = ''
        self.company_id = False
        def get_company(o,company_id):
            if company_id:
                company_obj = self.pool.get('res.company').browse(cr, uid,company_id)
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
            
        def get_id(o,times):
            if times =='periods':
                period_id = o.period_id_start and o.period_id_start.id or False
            if times in ['years','quarter']:
                period_id = o.fiscalyear_start and o.fiscalyear_start.id or False
            if not period_id:
                return 1
            else:
                return period_id
        
        self.start_date = False
        self.end_date  = False
        def get_quarter_date(o,year,quarter):
            self.start_date = False
            self.end_date  = False
            if quarter == '1':
                self.start_date = '''%s-01-01'''%(year)
                self.end_date = year + '-03-31'
            elif quarter == '2':
                self.start_date = year+'-04-01'
                self.end_date =year+'-06-30'
            elif quarter == '3':
                self.start_date = year+'-07-01'
                self.end_date = year+'-09-30'
            else:
                self.start_date = year+'-10-01'
                self.end_date = year+'-12-31'
        
        self.times = False
#         self.company_id = False
        self.showdetail = False
        self.shop_ids = []
        def get_header(o):
            self.times = o.times
            #Get company info
            self.company_id = o.company_id and o.company_id.id or False
            get_company(o,self.company_id)
            #Get shops
            self.shop_ids = [shop.id for shop in o.shop_ids]
#                 shop_ids.append(shop)
            
            if self.times =='periods':
                self.start_date = self.pool.get('account.period').browse(cr,uid,get_id(o,self.times)).date_start
                self.end_date   = self.pool.get('account.period').browse(cr,uid,get_id(o,self.times)).date_stop
            elif self.times == 'years':
                self.start_date = self.pool.get('account.fiscalyear').browse(cr,uid,get_id(o,self.times)).date_start
                self.end_date   = self.pool.get('account.fiscalyear').browse(cr,uid,get_id(o,self.times)).date_stop
            elif self.times == 'dates':
                self.start_date = o.date_start
                self.end_date   = o.date_end
                
            else:
                quarter = o.quarter or False
                year = self.pool.get('account.fiscalyear').browse(cr,uid,get_id(o,self.times)).name
                get_quarter_date(o,year, quarter)
                
            showdetail = o.showdetails or False
                
        def get_start_date(o):
            get_header(o)
            return get_vietname_date(self.start_date) 
        
        def get_end_date(o):
            return get_vietname_date(self.end_date) 
        
        self.account_id = False
        
        def get_account(o):
            values ={}
            self.account_id = o.account_id and o.account_id.id or False
            if self.account_id:
                account_obj = self.pool.get('account.account').browse(cr,uid,self.account_id)
                values ={
                         'account_code': account_obj.code,
                         'account_name':account_obj.name,
                         }
                return values
        
        def get_vietname_date(date):
            if not date:
                date = time.strftime(DATE_FORMAT)
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
        def get_line(o):
            get_account(o)
            if not self.start_date:
                get_header(o)
            return self.pool.get('sql.account.ledger').get_line(cr, self.start_date, self.end_date, self.account_id, self.showdetail, self.company_id, self.shop_ids)
        
        def show_dauky(o):
            shop = [s.id for s in o.shop_ids]
            self.shop_ids = shop and shop[0] or False
            sql='''
                select 'So du dau ky' as description,                   
                        case when dr_amount > cr_amount then dr_amount - cr_amount
                            else 0 end dr_amount,
                        case when dr_amount < cr_amount then  cr_amount - dr_amount
                            else 0 end cr_amount
                    from (
                            select sum(debit) dr_amount, sum(credit) cr_amount
                            from (
                                select aml.debit,aml.credit
                                from account_move amh join account_move_line aml
                                        on amh.id = aml.move_id
                                        and amh.shop_id = ('%(shop_ids)s')
                                        and amh.company_id= '%(company_id)s'
                                        and amh.state = 'posted'
                                        and aml.state = 'valid' and date_trunc('year', aml.date) = date_trunc('year', '%(start_date)s'::date)
                                    join account_journal ajn on amh.journal_id = ajn.id and ajn.type = 'situation'
                                    join fn_get_account_child_id(%(account_id)s) acc on aml.account_id = acc.id
                                union all
                                select aml.debit,aml.credit
                                from account_move amh join account_move_line aml
                                        on amh.id = aml.move_id
                                        and amh.shop_id = ('%(shop_ids)s')
                                        and amh.company_id= '%(company_id)s'
                                        and amh.state = 'posted'
                                        and aml.state = 'valid' and date(aml.date) between
                                        date(date_trunc('year', '%(start_date)s'::date)) and date('%(start_date)s'::date - 1)
                                    join account_journal ajn on amh.journal_id = ajn.id and ajn.type <> 'situation'
                                    join fn_get_account_child_id(%(account_id)s) acc on aml.account_id = acc.id
                                )x)y
                        
             '''%({
                      'start_date': self.start_date,
                      'end_date': self.end_date,
                      'shop_ids':self.shop_ids,
                      'company_id':self.company_id,
                      'account_id':self.account_id
              }) 
            cr.execute(sql)
            return cr.dictfetchall()
        
        def get_trongky(o):
            res =[]
            sql='''
                SELECT aml.move_id,sum(abs(aml.debit-aml.credit)) sum_cr
                    FROM account_move_line aml 
                        JOIN account_move am on am.id = aml.move_id
                    WHERE aml.account_id in (SELECT id from fn_get_account_child_id('%(account_id)s'))
                    and aml.shop_id = ('%(shop_ids)s')
                    and aml.company_id= '%(company_id)s'
                    and am.state = 'posted'
                    and aml.state = 'valid' and date(aml.date) between '%(start_date)s'::date and '%(end_date)s'::date
                    group by aml.move_id,am.date,am.date_document
                    order by am.date,am.date_document
            '''%({
                      'start_date': self.start_date,
                      'end_date': self.end_date,
                      'shop_ids':self.shop_ids,
                      'company_id':self.company_id,
                      'account_id':self.account_id
              })
            cr.execute(sql)
            for line in cr.dictfetchall():
                sql='''
                   SELECT sum(abs(aml.debit-aml.credit)) sum_dr
                        FROM account_move_line aml 
                            JOIN account_move am on am.id = aml.move_id
                        WHERE aml.account_id not in (SELECT id from fn_get_account_child_id('%(account_id)s'))
                        and aml.shop_id = ('%(shop_ids)s')
                        and aml.company_id= '%(company_id)s'
                        and am.state = 'posted'
                        and aml.state = 'valid' and date(aml.date) between '%(start_date)s'::date and '%(end_date)s'::date
                        and am.id = %(move_id)s
                '''%({
                          'start_date': self.start_date,
                          'end_date': self.end_date,
                          'shop_ids':self.shop_ids,
                          'company_id':self.company_id,
                          'account_id':self.account_id,
                          'move_id':line['move_id']
                  })
                cr.execute(sql)
                for i in cr.dictfetchall():
                    if line['sum_cr'] == i['sum_dr']:    
                        sql='''
                        SELECT  am.date gl_date, coalesce(am.date_document,am.date) doc_date, am.name doc_no, 
                                coalesce(aih.comment, coalesce(avh.narration,
                                    coalesce(am.narration, am.ref))) description,acc.code acc_code,                    
                        aml.debit,aml.credit
                        FROM account_move_line aml 
                            JOIN account_move am on am.id = aml.move_id
                            LEFT JOIN account_invoice aih on aml.move_id = aih.move_id -- lien ket voi invoice
                            LEFT JOIN account_voucher avh on aml.move_id = avh.move_id -- lien ket thu/chi
                            LEFT JOIN account_account acc on acc.id = aml.account_id
                        WHERE aml.account_id not in (SELECT id from fn_get_account_child_id('%(account_id)s'))
                        and aml.shop_id = ('%(shop_ids)s')
                        and aml.company_id= '%(company_id)s'
                        and am.state = 'posted'
                        and aml.state = 'valid' and date(aml.date) between '%(start_date)s'::date and '%(end_date)s'::date
                                and am.id = %(move_id)s
                        ORDER BY am.date,am.date_document
                        '''%({
                                  'start_date': self.start_date,
                                  'end_date': self.end_date,
                                  'shop_ids':self.shop_ids,
                                  'company_id':self.company_id,
                                  'account_id':self.account_id,
                                  'move_id':line['move_id']
                          })
                        cr.execute(sql)
                        for j in cr.dictfetchall():
                            res.append({
                                         'gl_date':j['gl_date'],
                                         'doc_date':j['doc_date'],
                                         'doc_no':j['doc_no'],
                                         'description':j['description'],
                                         'acc_code':j['acc_code'],
                                         'debit':j['credit'] or 0.0,
                                         'credit':j['debit'] or 0.0
                                     })
                    else:
                        # truong hop lien ket nhiều nhiều
                        sql='''
                            select row_number() over(order by am.date, am.date_document, am.name)::int seq, 
                                am.date gl_date, coalesce(am.date_document,am.date) doc_date, am.name doc_no, 
                                coalesce(aih.comment, coalesce(avh.narration,
                                    coalesce(am.narration, am.ref))) description,
                                case when aml.debit != 0
                                    then
                                        array_to_string(ARRAY(SELECT DISTINCT a.code
                                                              FROM account_move_line m2
                                                              LEFT JOIN account_account a ON (m2.account_id=a.id)
                                                              WHERE m2.move_id = aml.move_id
                                                              AND m2.credit != 0.0), ', ') 
                                    else
                                        array_to_string(ARRAY(SELECT DISTINCT a.code
                                                              FROM account_move_line m2
                                                              LEFT JOIN account_account a ON (m2.account_id=a.id)
                                                              WHERE m2.move_id = aml.move_id
                                                              AND m2.credit = 0.0), ', ')
                                    end acc_code,
                                aml.debit, aml.credit
                            from account_move_line aml
                                join account_move am on aml.move_id=am.id
                                and am.id=%(move_id)s
                                and am.state = 'posted'
                                and aml.state = 'valid'
                                and aml.account_id in (SELECT id from fn_get_account_child_id('%(account_id)s'))
                            left join account_invoice aih on aml.move_id = aih.move_id -- lien ket voi invoice
                            left join account_voucher avh on aml.move_id = avh.move_id -- lien ket thu/chi
                            order by am.date, am.date_document, am.name, acc_code
                         '''%({
                              'move_id':line['move_id'],
                              'account_id':self.account_id,
                          })
                        cr.execute(sql)
                        for j in cr.dictfetchall():
                            res.append({
                                         'gl_date':j['gl_date'],
                                         'doc_date':j['doc_date'],
                                         'doc_no':j['doc_no'],
                                         'description':j['description'],
                                         'acc_code':j['acc_code'],
                                         'debit':j['debit'] or 0.0,
                                         'credit':j['credit'] or 0.0
                                     })
                
            return res
        
        def get_sum_trongky(o):
            sql='''
                SELECT 'So phat sinh trong ky'::character varying description,
                        sum(aml.debit) dr_amount, sum(aml.credit) cr_amount
                    FROM account_move_line aml
                        join account_move am on aml.move_id=am.id
                        and aml.shop_id = ('%(shop_ids)s')
                        and aml.company_id= '%(company_id)s'
                        and am.state = 'posted'
                        and aml.state = 'valid' and date(aml.date) between '%(start_date)s'::date and '%(end_date)s'::date
                        join fn_get_account_child_id('%(account_id)s') acc on aml.account_id = acc.id
            '''%({
                      'start_date': self.start_date,
                      'end_date': self.end_date,
                      'shop_ids':self.shop_ids,
                      'company_id':self.company_id,
                      'account_id':self.account_id
              })
            cr.execute(sql)
            return cr.dictfetchall()
        
        def get_cuoiky(o):
            sql='''
                SELECT 'So du cuoi ky' as description,
                    case when dr_amount > cr_amount then dr_amount - cr_amount
                        else 0 end dr_amount,
                    case when dr_amount < cr_amount then  cr_amount - dr_amount
                        else 0 end cr_amount
                from (
                        select sum(aml.debit) dr_amount, sum(aml.credit) cr_amount
                        from account_move amh join account_move_line aml 
                                on amh.id = aml.move_id
                                and amh.shop_id = ('%(shop_ids)s')
                                and amh.company_id= '%(company_id)s'
                                and amh.state = 'posted'
                                and aml.state = 'valid' and date(aml.date)
                                between date(date_trunc('year', '%(end_date)s'::date)) and '%(end_date)s'::date
                            join fn_get_account_child_id('%(account_id)s') acc on aml.account_id = acc.id)x 
            '''%({
                  'start_date': self.start_date,
                  'end_date': self.end_date,
                  'shop_ids':self.shop_ids,
                  'company_id':self.company_id,
                  'account_id':self.account_id
              })
            cr.execute(sql)
            return cr.dictfetchall()
                
        
        def get_line_detail(o):
            if not self.start_date:
                get_header()


        o = self.browse(cr, uid, ids[0])
        report_line = []
        if not o.showdetails:
            vals = {
                'name': 'Account Ledger Report',
                'don_vi': get_company_name(o),
                'dia_chi': get_company_address(o),
                'ms_thue': get_company_vat(o),
                'account_code': get_account(o)['account_code'],
                'account_name': get_account(o)['account_name'],
                'date_from': get_start_date(o),
                'date_to': get_end_date(o),
            }
            for line in get_line(o):
                if line['description'] == 'Số dư đầu kỳ':
                    report_line.append((0,0,{
                        'ngay_ghso': '',
                        'so_hieu': '',
                        'ngay_thang': '',
                        'dien_giai': line['description'] or '',
                        'tk_doi_ung': '',
                        'so_ps_no': line['debit'] or '',
                        'so_ps_co': line['credit'] or '',
                    }))
                if line['description'] not in('Số dư đầu kỳ','Số phát sinh trong kỳ','Số dư cuối kỳ'):
                    report_line.append((0,0,{
                        'ngay_ghso': get_vietname_date(line['gl_date']),
                        'so_hieu': line['doc_no'],
                        'ngay_thang': get_vietname_date(line['doc_date']),
                        'dien_giai': line['description'] or '',
                        'tk_doi_ung': line['acc_code'],
                        'so_ps_no': line['debit'] or '',
                        'so_ps_co': line['credit'] or '',
                    }))
                if line['description'] == 'Số phát sinh trong kỳ':
                    report_line.append((0,0,{
                        'ngay_ghso': '',
                        'so_hieu': '',
                        'ngay_thang': '',
                        'dien_giai': line['description'] or '',
                        'tk_doi_ung': '',
                        'so_ps_no': line['debit'] or '',
                        'so_ps_co': line['credit'] or '',
                    }))
                if line['description'] == 'Số dư cuối kỳ':
                    report_line.append((0,0,{
                        'ngay_ghso': '',
                        'so_hieu': '',
                        'ngay_thang': '',
                        'dien_giai': line['description'] or '',
                        'tk_doi_ung': '',
                        'so_ps_no': line['debit'] or '',
                        'so_ps_co': line['credit'] or '',
                    }))
            vals.update({'ledger_review_line' : report_line, })
            report_id = report_obj.create(cr, uid, vals)
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                            'green_erp_report_account', 'account_ledger_report_review')
            return {
                        'name': 'Account Ledger Report',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'account.ledger.report.review',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'res_id': report_id,
                    }
        else:
            vals = {
                'name': 'Account Detail Ledger Report',
                'don_vi': get_company_name(o),
                'dia_chi': get_company_address(o),
                'ms_thue': get_company_vat(o),
                'account_code': get_account(o)['account_code'],
                'account_name': get_account(o)['account_name'],
                'date_from': get_start_date(o),
                'date_to': get_end_date(o),
            }
            for line in show_dauky(o):
                report_line.append((0,0,{
                    'ngay_ghso': '',
                    'so_hieu': '',
                    'ngay_thang': '',
                    'dien_giai': '- Số dư đầu kỳ',
                    'tk_doi_ung': '',
                    'so_ps_no': line['dr_amount'],
                    'so_ps_co': line['cr_amount'],
                }))
                report_line.append((0,0,{
                    'ngay_ghso': '',
                    'so_hieu': '',
                    'ngay_thang': '',
                    'dien_giai': '- Số phát sinh trong kỳ',
                    'tk_doi_ung': '',
                    'so_ps_no': '',
                    'so_ps_co': '',
                }))
            for line1 in get_trongky(o):
                report_line.append((0,0,{
                    'ngay_ghso': get_vietname_date(line1['gl_date']),
                    'so_hieu': line1['doc_no'],
                    'ngay_thang': get_vietname_date(line1['doc_date']),
                    'dien_giai': line1['description'] or '',
                    'tk_doi_ung': line1['acc_code'],
                    'so_ps_no': line1['debit'] or '',
                    'so_ps_co': line1['credit'] or '',
                }))
            for line2 in get_sum_trongky(o): 
                report_line.append((0,0,{
                    'ngay_ghso': '',
                    'so_hieu': '',
                    'ngay_thang': '',
                    'dien_giai': '- Cộng số phát sinh trong kỳ',
                    'tk_doi_ung': '',
                    'so_ps_no': line2['dr_amount'],
                    'so_ps_co': line2['cr_amount'],
                }))
            for line3 in get_cuoiky(o):
                report_line.append((0,0,{
                    'ngay_ghso': '',
                    'so_hieu': '',
                    'ngay_thang': '',
                    'dien_giai': '- Số dư cuối kỳ',
                    'tk_doi_ung': '',
                    'so_ps_no': line3['dr_amount'],
                    'so_ps_co': line3['cr_amount'],
                }))
            vals.update({'ledger_review_line' : report_line, })
            report_id = report_obj.create(cr, uid, vals)
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                            'green_erp_report_account', 'account_detail_ledger_report_review')
            return {
                        'name': 'Account Detail Ledger Report',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'account.ledger.report.review',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'res_id': report_id,
                    }
            
    
account_ledger_report()


class general_ledger_report(osv.osv_memory):
    _name = "general.ledger.report"
    
    def _get_fiscalyear(self, cr, uid, context=None):
        now = time.strftime('%Y-%m-%d')
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return fiscalyears and fiscalyears[0] or False
            
    _columns = {
        'shop_ids': fields.many2many('sale.shop', 'general_ledger_report_shop_rel', 'wizard_id', 'shop_id', 'Shops', required=True),
        
        'times': fields.selection([
            ('dates','Date'),
            ('periods', 'Periods'),
            ('quarter','Quarter'),
            ('years','Years')], 'Periods Type', required=True ),
        'period_id_start': fields.many2one('account.period', 'Period',  domain=[('state','=','draft')],),
        'period_id_end': fields.many2one('account.period', 'End Period',  domain=[('state','=','draft')],),
        'fiscalyear_start': fields.many2one('account.fiscalyear', 'Fiscalyear', domain=[('state','=','draft')],),
        'fiscalyear_stop': fields.many2one('account.fiscalyear', 'Stop Fiscalyear',  domain=[('state','=','draft')],),
        'date_start': fields.date('Date Start'),
        'date_end':   fields.date('Date end'),
        'quarter':fields.selection([
            ('1', '1'),
            ('2','2'),
            ('3','3'),
            ('4','4')], 'Quarter'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
     }
    
    def _get_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id and user.company_id.id or False
        
    def _get_shop_ids(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return [x.id for x in user.shop_ids]
    
    _defaults = {
        'shop_ids': _get_shop_ids,
        'times': 'periods',
        'date_start': time.strftime('%Y-%m-%d'),
        'date_end': time.strftime('%Y-%m-%d'),        
        'period_id_start': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],
        'period_id_end': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],        
        'fiscalyear_start': _get_fiscalyear,
        'fiscalyear_stop': _get_fiscalyear,
        'quarter': '1',
        'company_id': _get_company,
        }
    
    def finance_report(self, cr, uid, ids, context=None): 
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'general.ledger.report'
        datas['form'] = self.read(cr, uid, ids)[0]        
        report_name = context['type_report']             
        return {'type': 'ir.actions.report.xml', 'report_name': report_name , 'datas': datas}
    
general_ledger_report()

class general_trial_balance(osv.osv_memory):
    _name = "general.trial.balance"    
    def _get_fiscalyear(self, cr, uid, context=None):
        now = time.strftime('%Y-%m-%d')
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return fiscalyears and fiscalyears[0] or False
    
    def _get_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id and user.company_id.id or False
     
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
        
        'company_id': fields.many2one('res.company', 'Company', required=True),
     }
        
    _defaults = {
        'times': 'periods',
        'date_start': time.strftime('%Y-%m-%d'),
        'date_end': time.strftime('%Y-%m-%d'),        
        'period_id_start': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],
        'period_id_end': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],        
        'fiscalyear_start': _get_fiscalyear,
        'fiscalyear_stop': _get_fiscalyear,
        
        'company_id': _get_company,
        }
    
    def finance_report(self, cr, uid, ids, context=None): 
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'report.accounting'
        datas['form'] = self.read(cr, uid, ids)[0]        
        report_name = context['type_report']             
        return {'type': 'ir.actions.report.xml', 'report_name': report_name , 'datas': datas}
    
general_trial_balance()

class general_balance_sheet(osv.osv_memory):
    _name = "general.balance.sheet"    
    
    def _get_fiscalyear(self, cr, uid, context=None):
        now = time.strftime('%Y-%m-%d')
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return fiscalyears and fiscalyears[0] or False
    
    def _get_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id and user.company_id.id or False
    
    _columns = {
        'times': fields.selection([
            ('periods', 'Periods'),
            ('quarter','Quarter'),
            ('years','Years')], 'Periods Type', required=True ),
        'period_id_start': fields.many2one('account.period', 'Period',  domain=[('state','=','draft')],),
        'period_id_end': fields.many2one('account.period', 'End Perirod',  domain=[('state','=','draft')],),
        'fiscalyear_start': fields.many2one('account.fiscalyear', 'Fiscalyear', domain=[('state','=','draft')],),
        'fiscalyear_stop': fields.many2one('account.fiscalyear', 'Stop Fiscalyear',  domain=[('state','=','draft')],),
        'date_start': fields.date('Date Start'),
        'date_end':   fields.date('Date end'),
        'quarter':fields.selection([
            ('1', '1'),
            ('2','2'),
            ('3','3'),
            ('4','4')], 'Quarter'),
                
        'company_id': fields.many2one('res.company', 'Company', required=True),
     }
        
    _defaults = {
        'times': 'periods',
        'date_start': time.strftime('%Y-%m-%d'),
        'date_end': time.strftime('%Y-%m-%d'),        
        'period_id_start': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],
        'period_id_end': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],        
        'fiscalyear_start': _get_fiscalyear,
        'fiscalyear_stop': _get_fiscalyear,
        'quarter': '1',
        
        'company_id': _get_company,
        }
    
    def finance_report(self, cr, uid, ids, context=None): 
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'general.balance.sheet'
        datas['form'] = self.read(cr, uid, ids)[0]        
        report_name = context['type_report']             
        return {'type': 'ir.actions.report.xml', 'report_name': report_name , 'datas': datas}
    
general_balance_sheet()

class general_account_profit_loss(osv.osv_memory):
    _name = "general.account.profit.loss"    
    
    def _get_fiscalyear(self, cr, uid, context=None):
        now = time.strftime('%Y-%m-%d')
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return fiscalyears and fiscalyears[0] or False
    
    def _get_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id and user.company_id.id or False
    
    _columns = {
        'times': fields.selection([
            ('periods', 'Periods'),
            ('quarter','Quarter'),
            ('years','Years')], 'Periods Type', required=True ),
        'period_id_start': fields.many2one('account.period', 'Start Period',  domain=[('state','=','draft')],),
        'period_id_end': fields.many2one('account.period', 'End Period',  domain=[('state','=','draft')],),
        'fiscalyear_start': fields.many2one('account.fiscalyear', 'Start Fiscalyear', domain=[('state','=','draft')],),
        'fiscalyear_stop': fields.many2one('account.fiscalyear', 'Stop Fiscalyear',  domain=[('state','=','draft')],),
        'date_start': fields.date('Date Start'),
        'date_end':   fields.date('Date end'),
        'quarter':fields.selection([
            ('1', '1'),
            ('2','2'),
            ('3','3'),
            ('4','4')], 'Quarter'),
        
        'company_id': fields.many2one('res.company', 'Company', required=True),
     }
        
    _defaults = {
        'times': 'periods',
        'date_start': time.strftime('%Y-%m-%d'),
        'date_end': time.strftime('%Y-%m-%d'),        
        'period_id_start': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],
        'period_id_end': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],        
        'fiscalyear_start': _get_fiscalyear,
        'fiscalyear_stop': _get_fiscalyear,
        'quarter': '1',
        
        'company_id': _get_company,
        }
    
    def finance_report(self, cr, uid, ids, context=None): 
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'general.account.profit.loss'
        datas['form'] = self.read(cr, uid, ids)[0]        
        report_name = context['type_report']             
        return {'type': 'ir.actions.report.xml', 'report_name': report_name , 'datas': datas}
    
general_account_profit_loss()

class luuchuyen_tiente(osv.osv_memory):
    _name = "luuchuyen.tiente"    
    
    def _get_fiscalyear(self, cr, uid, context=None):
        now = time.strftime('%Y-%m-%d')
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return fiscalyears and fiscalyears[0] or False
    
    def _get_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id and user.company_id.id or False
    
    _columns = {
        'times': fields.selection([
            ('periods', 'Periods'),
            ('quarter','Quarter'),
            ('years','Years')], 'Periods Type', required=True ),
        'period_id_start': fields.many2one('account.period', 'Start Period',  domain=[('state','=','draft')],),
        'period_id_end': fields.many2one('account.period', 'End Period',  domain=[('state','=','draft')],),
        'fiscalyear_start': fields.many2one('account.fiscalyear', 'Start Fiscalyear', domain=[('state','=','draft')],),
        'fiscalyear_stop': fields.many2one('account.fiscalyear', 'Stop Fiscalyear',  domain=[('state','=','draft')],),
        'date_start': fields.date('Date Start'),
        'date_end':   fields.date('Date end'),
        'quarter':fields.selection([
            ('1', '1'),
            ('2','2'),
            ('3','3'),
            ('4','4')], 'Quarter'),
        
        'company_id': fields.many2one('res.company', 'Company', required=True),
     }
        
    _defaults = {
        'times': 'periods',
        'date_start': time.strftime('%Y-%m-%d'),
        'date_end': time.strftime('%Y-%m-%d'),        
        'period_id_start': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],
        'period_id_end': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],        
        'fiscalyear_start': _get_fiscalyear,
        'fiscalyear_stop': _get_fiscalyear,
        'quarter': '1',
        
        'company_id': _get_company,
        }
    
    def finance_report(self, cr, uid, ids, context=None): 
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'luuchuyen.tiente'
        datas['form'] = self.read(cr, uid, ids)[0]        
        report_name = context['type_report']             
        return {'type': 'ir.actions.report.xml', 'report_name': report_name , 'datas': datas}
    
luuchuyen_tiente()

class so_quy(osv.osv_memory):
    _name = "so.quy"    
    
    def default_get(self, cr, uid, fields, context=None):
        if not context:
            context = {}
        res = super(so_quy, self).default_get(cr, uid, fields, context=context)
        account_ids = []
        if context.get('report_type','')=='soquy_tienmat_report':
            account_ids = self.pool.get('account.account').search(cr, uid, [('code','=','111')])
        if context.get('report_type','')=='so_tiengui_nganhang_report':
            account_ids = self.pool.get('account.account').search(cr, uid, [('code','=','112')])
        res.update({'account_id': account_ids and account_ids[0] or False})
        return res
    
    def _get_fiscalyear(self, cr, uid, context=None):
        now = time.strftime('%Y-%m-%d')
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return fiscalyears and fiscalyears[0] or False
            
    _columns = {
        'shop_ids': fields.many2many('sale.shop', 'so_quy_report_shop_rel', 'wizard_id', 'shop_id', 'Shops', required=True),
        
        'times': fields.selection([
            ('dates','Date'),
            ('periods', 'Periods'),
            ('quarter','Quarter'),
            ('years','Years')], 'Periods Type', required=True ),
        'period_id_start': fields.many2one('account.period', 'Period',  domain=[('state','=','draft')],),
        'period_id_end': fields.many2one('account.period', 'End Period',  domain=[('state','=','draft')],),
        'fiscalyear_start': fields.many2one('account.fiscalyear', 'From Fiscalyear', domain=[('state','=','draft')],),
        'fiscalyear_stop': fields.many2one('account.fiscalyear', 'To Fiscalyear',  domain=[('state','=','draft')],),
        'date_start': fields.date('Date start'),
        'date_end':   fields.date('Date end'),
        'quarter':fields.selection([
            ('1', '1'),
            ('2','2'),
            ('3','3'),
            ('4','4')], 'Quarter'),
        'account_id': fields.many2one('account.account', 'Account', required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'showdetails':fields.boolean('Get Detail'),
     }
    
    def _get_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id and user.company_id.id or False
    
    def _get_shop_ids(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return [x.id for x in user.shop_ids]
    
    _defaults = {
        'shop_ids': _get_shop_ids,
        'times': 'periods',
        'date_start': time.strftime('%Y-%m-%d'),
        'date_end': time.strftime('%Y-%m-%d'),        
        'period_id_start': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],
        'period_id_end': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],        
        'fiscalyear_start': _get_fiscalyear,
        'fiscalyear_stop': _get_fiscalyear,
        'quarter': '1',
        'company_id': _get_company,
        'showdetails': True,
        }
    
    def finance_report(self, cr, uid, ids, context=None): 
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'so.quy'
        datas['form'] = self.read(cr, uid, ids)[0]    
        report_name = context['type_report']
        if report_name=='soquy_tienmat_report':
            this = self.browse(cr,uid,ids[0])
            if this.showdetails:
                report_name = 'soquy_tienmat_chitiet_report'
            else:
                report_name = 'soquy_tienmat_report'
        return {'type': 'ir.actions.report.xml', 'report_name': report_name , 'datas': datas}
    
    def review_report(self, cr, uid, ids, context=None):
        report_obj = self.pool.get('so.quy.review')
        ###
        self.company_name = ''
        self.company_address = ''
        self.vat = ''
        self.company_id = False
        def get_company(o,company_id):
            if company_id:
                company_obj = self.pool.get('res.company').browse(cr, uid,company_id)
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
            
        def get_id(o,times):
            if times =='periods':
                period_id = o.period_id_start and o.period_id_start.id or False
            if times in ['years','quarter']:
                period_id = o.fiscalyear_start and o.fiscalyear_start.id or False
            if not period_id:
                return 1
            else:
                return period_id
        
        self.start_date = False
        self.end_date  = False
        def get_quarter_date(o,year,quarter):
            self.start_date = False
            self.end_date  = False
            if quarter == '1':
                self.start_date = '''%s-01-01'''%(year)
                self.end_date = year + '-03-31'
            elif quarter == '2':
                self.start_date = year+'-04-01'
                self.end_date =year+'-06-30'
            elif quarter == '3':
                self.start_date = year+'-07-01'
                self.end_date = year+'-09-30'
            else:
                self.start_date = year+'-10-01'
                self.end_date = year+'-12-31'
        
        self.times = False
        self.showdetail = False
        self.shop_ids = []
        def get_header(o):
            self.times = o.times
            #Get company info
            self.company_id = o.company_id and o.company_id.id or False
            get_company(o,self.company_id)
            #Get shops
            self.shop_ids = [shop.id for shop in o.shop_ids]
#                 shop_ids.append(shop)
            
            if self.times =='periods':
                self.start_date = self.pool.get('account.period').browse(cr,uid,get_id(o,self.times)).date_start
                self.end_date   = self.pool.get('account.period').browse(cr,uid,get_id(o,self.times)).date_stop
            elif self.times == 'years':
                self.start_date = self.pool.get('account.fiscalyear').browse(cr,uid,get_id(o,self.times)).date_start
                self.end_date   = self.pool.get('account.fiscalyear').browse(cr,uid,get_id(o,self.times)).date_stop
            elif self.times == 'dates':
                self.start_date = o.date_start
                self.end_date   = o.date_end
                
            else:
                quarter = o.quarter or False
                year = self.pool.get('account.fiscalyear').browse(cr,uid,get_id(o,self.times)).name
                get_quarter_date(o,year, quarter)
                
            showdetail = o.showdetails or False
                
        def get_start_date(o):
            get_header(o)
            return get_vietname_date(self.start_date) 
        
        def get_end_date(o):
            return get_vietname_date(self.end_date) 
        
        self.account_id = False
        
        def get_account(o):
            values ={}
            self.account_id = o.account_id and o.account_id.id or False
            if self.account_id:
                account_obj = self.pool.get('account.account').browse(cr,uid,self.account_id)
                values ={
                         'account_code': account_obj.code,
                         'account_name':account_obj.name,
                         }
                return values
        
        def get_vietname_date(date):
            if not date:
                date = time.strftime(DATE_FORMAT)
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
        self.ton = 0
        def show_dauky(o):
            shop = [s.id for s in o.shop_ids]
            self.shop_ids = shop and shop[0] or False
            sql='''
                select 'So du dau ky' as description,                   
                        case when dr_amount > cr_amount then dr_amount - cr_amount
                            else cr_amount - dr_amount end ton
                    from (
                            select sum(debit) dr_amount, sum(credit) cr_amount
                            from (
                                select aml.debit,aml.credit
                                from account_move amh join account_move_line aml
                                        on amh.id = aml.move_id
                                        and amh.shop_id = ('%(shop_ids)s')
                                        and amh.company_id= '%(company_id)s'
                                        and amh.state = 'posted'
                                        and aml.state = 'valid' and date_trunc('year', aml.date) = date_trunc('year', '%(start_date)s'::date)
                                    join account_journal ajn on amh.journal_id = ajn.id and ajn.type = 'situation'
                                    join fn_get_account_child_id(%(account_id)s) acc on aml.account_id = acc.id
                                union all
                                select aml.debit,aml.credit
                                from account_move amh join account_move_line aml
                                        on amh.id = aml.move_id
                                        and amh.shop_id = ('%(shop_ids)s')
                                        and amh.company_id= '%(company_id)s'
                                        and amh.state = 'posted'
                                        and aml.state = 'valid' and date(aml.date) between
                                        date(date_trunc('year', '%(start_date)s'::date)) and date('%(start_date)s'::date - 1)
                                    join account_journal ajn on amh.journal_id = ajn.id and ajn.type <> 'situation'
                                    join fn_get_account_child_id(%(account_id)s) acc on aml.account_id = acc.id
                                )x)y
                        
             '''%({
                      'start_date': self.start_date,
                      'end_date': self.end_date,
                      'shop_ids':self.shop_ids,
                      'company_id':self.company_id,
                      'account_id':self.account_id
              }) 
            cr.execute(sql)
            dauky = cr.dictfetchall()
            for l in dauky:
                self.ton += l['ton'] or 0
            return dauky
        
        def get_trongky(o):
            res =[]
            sql='''
                SELECT am.date gl_date, coalesce(am.date_document,am.date) doc_date, am.name doc_no, 
                                coalesce(aih.comment, coalesce(avh.narration,
                                    coalesce(am.narration, am.ref))) description,aml.debit,aml.credit
                    FROM account_move_line aml 
                        JOIN account_move am on am.id = aml.move_id
                        LEFT JOIN account_invoice aih on aml.move_id = aih.move_id -- lien ket voi invoice
                        LEFT JOIN account_voucher avh on aml.move_id = avh.move_id -- lien ket thu/chi
                        LEFT JOIN account_account acc on acc.id = aml.account_id
                    WHERE aml.account_id in (SELECT id from fn_get_account_child_id('%(account_id)s'))
                    and aml.shop_id = ('%(shop_ids)s')
                    and aml.company_id= '%(company_id)s'
                    and am.state = 'posted'
                    and aml.state = 'valid' and date(aml.date) between '%(start_date)s'::date and '%(end_date)s'::date
                    order by am.date,am.date_document
            '''%({
                      'start_date': self.start_date,
                      'end_date': self.end_date,
                      'shop_ids':self.shop_ids,
                      'company_id':self.company_id,
                      'account_id':self.account_id
              })
            cr.execute(sql)
            for line in cr.dictfetchall():
                if line['debit'] and not line['credit']:
                    doc_no_thu = line['doc_no']
                    doc_no_chi = ''
                else:
                    doc_no_chi = line['doc_no']
                    doc_no_thu = ''
                self.ton += (line['debit'] - line['credit'])
                res.append({
                             'gl_date':line['gl_date'],
                             'doc_date':line['doc_date'],
                             'doc_no_thu': doc_no_thu,
                             'doc_no_chi':doc_no_chi,
                             'description':line['description'],
                             'debit':line['debit'] or 0.0,
                             'credit':line['credit'] or 0.0,
                             'ton': self.ton,
                         })
                
            return res
            
            
        
        def get_sum_trongky(o):
            sql='''
                SELECT 'So phat sinh trong ky'::character varying description,
                        sum(aml.debit) dr_amount, sum(aml.credit) cr_amount
                    FROM account_move_line aml
                        join account_move am on aml.move_id=am.id
                        and aml.shop_id = ('%(shop_ids)s')
                        and aml.company_id= '%(company_id)s'
                        and am.state = 'posted'
                        and aml.state = 'valid' and date(aml.date) between '%(start_date)s'::date and '%(end_date)s'::date
                        join fn_get_account_child_id('%(account_id)s') acc on aml.account_id = acc.id
            '''%({
                      'start_date': self.start_date,
                      'end_date': self.end_date,
                      'shop_ids':self.shop_ids,
                      'company_id':self.company_id,
                      'account_id':self.account_id
              })
            cr.execute(sql)
            return cr.dictfetchall()
        
        def get_cuoiky(o):
            sql='''
                SELECT 'So du cuoi ky' as description,
                    case when dr_amount > cr_amount then dr_amount - cr_amount
                        else cr_amount - dr_amount end ton
                from (
                        select sum(aml.debit) dr_amount, sum(aml.credit) cr_amount
                        from account_move amh join account_move_line aml 
                                on amh.id = aml.move_id
                                and amh.shop_id = ('%(shop_ids)s')
                                and amh.company_id= '%(company_id)s'
                                and amh.state = 'posted'
                                and aml.state = 'valid' and date(aml.date)
                                between date(date_trunc('year', '%(end_date)s'::date)) and '%(end_date)s'::date
                            join fn_get_account_child_id('%(account_id)s') acc on aml.account_id = acc.id)x 
            '''%({
                  'start_date': self.start_date,
                  'end_date': self.end_date,
                  'shop_ids':self.shop_ids,
                  'company_id':self.company_id,
                  'account_id':self.account_id
              })
            cr.execute(sql)
            return cr.dictfetchall()
                
        
        def get_line(o):
            if not self.start_date:
                get_header()
                
        def get_trongky_chitiet(o):
            res =[]
            sql='''
                SELECT aml.move_id,sum(abs(aml.debit-aml.credit)) sum_cr
                    FROM account_move_line aml 
                        JOIN account_move am on am.id = aml.move_id
                    WHERE aml.account_id in (SELECT id from fn_get_account_child_id('%(account_id)s'))
                    and aml.shop_id = ('%(shop_ids)s')
                    and aml.company_id= '%(company_id)s'
                    and am.state = 'posted'
                    and aml.state = 'valid' and date(aml.date) between '%(start_date)s'::date and '%(end_date)s'::date
                    group by aml.move_id,am.date,am.date_document
                    order by am.date,am.date_document
            '''%({
                      'start_date': self.start_date,
                      'end_date': self.end_date,
                      'shop_ids':self.shop_ids,
                      'company_id':self.company_id,
                      'account_id':self.account_id
              })
            cr.execute(sql)
            for line in cr.dictfetchall():
                sql='''
                   SELECT sum(abs(aml.debit-aml.credit)) sum_dr
                        FROM account_move_line aml 
                            JOIN account_move am on am.id = aml.move_id
                        WHERE aml.account_id not in (SELECT id from fn_get_account_child_id('%(account_id)s'))
                        and aml.shop_id = ('%(shop_ids)s')
                        and aml.company_id= '%(company_id)s'
                        and am.state = 'posted'
                        and aml.state = 'valid' and date(aml.date) between '%(start_date)s'::date and '%(end_date)s'::date
                        and am.id = %(move_id)s
                '''%({
                          'start_date': self.start_date,
                          'end_date': self.end_date,
                          'shop_ids':self.shop_ids,
                          'company_id':self.company_id,
                          'account_id':self.account_id,
                          'move_id':line['move_id']
                  })
                cr.execute(sql)
                for i in cr.dictfetchall():
                    if line['sum_cr'] == i['sum_dr']:    
                        sql='''
                        SELECT  am.date gl_date, coalesce(am.date_document,am.date) doc_date, am.name doc_no, 
                                coalesce(aih.comment, coalesce(avh.narration,
                                    coalesce(am.narration, am.ref))) description,acc.code acc_code,                    
                        aml.debit,aml.credit
                        FROM account_move_line aml 
                            JOIN account_move am on am.id = aml.move_id
                            LEFT JOIN account_invoice aih on aml.move_id = aih.move_id -- lien ket voi invoice
                            LEFT JOIN account_voucher avh on aml.move_id = avh.move_id -- lien ket thu/chi
                            LEFT JOIN account_account acc on acc.id = aml.account_id
                        WHERE aml.account_id not in (SELECT id from fn_get_account_child_id('%(account_id)s'))
                        and aml.shop_id = ('%(shop_ids)s')
                        and aml.company_id= '%(company_id)s'
                        and am.state = 'posted'
                        and aml.state = 'valid' and date(aml.date) between '%(start_date)s'::date and '%(end_date)s'::date
                                and am.id = %(move_id)s
                        ORDER BY am.date,am.date_document
                        '''%({
                                  'start_date': self.start_date,
                                  'end_date': self.end_date,
                                  'shop_ids':self.shop_ids,
                                  'company_id':self.company_id,
                                  'account_id':self.account_id,
                                  'move_id':line['move_id']
                          })
                        cr.execute(sql)
                        for j in cr.dictfetchall():
                            if j['credit'] and not j['debit']:
                                doc_no_thu = j['doc_no']
                                doc_no_chi = ''
                            else:
                                doc_no_chi = j['doc_no']
                                doc_no_thu = ''
                            self.ton += (j['credit'] - j['debit'])
                            res.append({
                                         'gl_date':j['gl_date'],
                                         'doc_date':j['doc_date'],
                                         'doc_no_thu': doc_no_thu,
                                         'doc_no_chi':doc_no_chi,
                                         'description':j['description'],
                                         'acc_code':j['acc_code'],
                                         'debit':j['credit'] or 0.0,
                                         'credit':j['debit'] or 0.0,
                                         'ton': self.ton,
                                     })
                    else:
                        # truong hop lien ket nhiều nhiều
                        sql='''
                            select row_number() over(order by am.date, am.date_document, am.name)::int seq, 
                                am.date gl_date, coalesce(am.date_document,am.date) doc_date, am.name doc_no, 
                                coalesce(aih.comment, coalesce(avh.narration,
                                    coalesce(am.narration, am.ref))) description,
                                case when aml.debit != 0
                                    then
                                        array_to_string(ARRAY(SELECT DISTINCT a.code
                                                              FROM account_move_line m2
                                                              LEFT JOIN account_account a ON (m2.account_id=a.id)
                                                              WHERE m2.move_id = aml.move_id
                                                              AND m2.credit != 0.0), ', ') 
                                    else
                                        array_to_string(ARRAY(SELECT DISTINCT a.code
                                                              FROM account_move_line m2
                                                              LEFT JOIN account_account a ON (m2.account_id=a.id)
                                                              WHERE m2.move_id = aml.move_id
                                                              AND m2.credit = 0.0), ', ')
                                    end acc_code,
                                aml.debit, aml.credit
                            from account_move_line aml
                                join account_move am on aml.move_id=am.id
                                and am.id=%(move_id)s
                                and am.state = 'posted'
                                and aml.state = 'valid'
                                and aml.account_id in (SELECT id from fn_get_account_child_id('%(account_id)s'))
                            left join account_invoice aih on aml.move_id = aih.move_id -- lien ket voi invoice
                            left join account_voucher avh on aml.move_id = avh.move_id -- lien ket thu/chi
                            order by am.date, am.date_document, am.name, acc_code
                         '''%({
                              'move_id':line['move_id'],
                              'account_id':self.account_id,
                          })
                        cr.execute(sql)
                        for j in cr.dictfetchall():
                            if j['debit'] and not j['credit']:
                                doc_no_thu = j['doc_no']
                                doc_no_chi = ''
                            else:
                                doc_no_chi = j['doc_no']
                                doc_no_thu = ''
                            self.ton += (j['debit'] - j['credit'])
                            res.append({
                                         'gl_date':j['gl_date'],
                                         'doc_date':j['doc_date'],
                                         'doc_no_thu': doc_no_thu,
                                         'doc_no_chi':doc_no_chi,
                                         'description':j['description'],
                                         'acc_code':j['acc_code'],
                                         'debit':j['debit'] or 0.0,
                                         'credit':j['credit'] or 0.0,
                                         'ton': self.ton,
                                     })
                
            return res
        
        def get_trongky_tienmat(o):
            res =[]
            sql='''
                SELECT aml.move_id,sum(abs(aml.debit-aml.credit)) sum_cr
                    FROM account_move_line aml 
                        JOIN account_move am on am.id = aml.move_id
                    WHERE aml.account_id in (SELECT id from fn_get_account_child_id('%(account_id)s'))
                    and aml.shop_id = ('%(shop_ids)s')
                    and aml.company_id= '%(company_id)s'
                    and am.state = 'posted'
                    and aml.state = 'valid' and date(aml.date) between '%(start_date)s'::date and '%(end_date)s'::date
                    group by aml.move_id,am.date,am.date_document
                    order by am.date,am.date_document
            '''%({
                      'start_date': self.start_date,
                      'end_date': self.end_date,
                      'shop_ids':self.shop_ids,
                      'company_id':self.company_id,
                      'account_id':self.account_id
              })
            cr.execute(sql)
            for line in cr.dictfetchall():
                sql='''
                   SELECT sum(abs(aml.debit-aml.credit)) sum_dr
                        FROM account_move_line aml 
                            JOIN account_move am on am.id = aml.move_id
                        WHERE aml.account_id not in (SELECT id from fn_get_account_child_id('%(account_id)s'))
                        and aml.shop_id = ('%(shop_ids)s')
                        and aml.company_id= '%(company_id)s'
                        and am.state = 'posted'
                        and aml.state = 'valid' and date(aml.date) between '%(start_date)s'::date and '%(end_date)s'::date
                        and am.id = %(move_id)s
                '''%({
                          'start_date': self.start_date,
                          'end_date': self.end_date,
                          'shop_ids':self.shop_ids,
                          'company_id':self.company_id,
                          'account_id':self.account_id,
                          'move_id':line['move_id']
                  })
                cr.execute(sql)
                for i in cr.dictfetchall():
                    if line['sum_cr'] == i['sum_dr']:    
                        sql='''
                        SELECT  am.date gl_date, coalesce(am.date_document,am.date) doc_date, am.name doc_no, 
                                coalesce(aih.comment, coalesce(avh.narration,
                                    coalesce(am.narration, am.ref))) description,acc.code acc_code,                    
                        aml.debit,aml.credit
                        FROM account_move_line aml 
                            JOIN account_move am on am.id = aml.move_id
                            LEFT JOIN account_invoice aih on aml.move_id = aih.move_id -- lien ket voi invoice
                            LEFT JOIN account_voucher avh on aml.move_id = avh.move_id -- lien ket thu/chi
                            LEFT JOIN account_account acc on acc.id = aml.account_id
                        WHERE aml.account_id not in (SELECT id from fn_get_account_child_id('%(account_id)s'))
                        and aml.shop_id = ('%(shop_ids)s')
                        and aml.company_id= '%(company_id)s'
                        and am.state = 'posted'
                        and aml.state = 'valid' and date(aml.date) between '%(start_date)s'::date and '%(end_date)s'::date
                                and am.id = %(move_id)s
                        ORDER BY am.date,am.date_document
                        '''%({
                                  'start_date': self.start_date,
                                  'end_date': self.end_date,
                                  'shop_ids':self.shop_ids,
                                  'company_id':self.company_id,
                                  'account_id':self.account_id,
                                  'move_id':line['move_id']
                          })
                        cr.execute(sql)
                        for j in self.cr.dictfetchall():
                            self.ton += (j['credit'] - j['debit'])
                            res.append({
                                         'gl_date':j['gl_date'],
                                         'doc_date':j['doc_date'],
                                         'doc_no': j['doc_no'],
                                         'description':j['description'],
                                         'acc_code':j['acc_code'],
                                         'debit':j['credit'] or 0.0,
                                         'credit':j['debit'] or 0.0,
                                         'ton': self.ton,
                                     })
                    else:
                        # truong hop lien ket nhiều nhiều
                        sql='''
                            select row_number() over(order by am.date, am.date_document, am.name)::int seq, 
                                am.date gl_date, coalesce(am.date_document,am.date) doc_date, am.name doc_no, 
                                coalesce(aih.comment, coalesce(avh.narration,
                                    coalesce(am.narration, am.ref))) description,
                                case when aml.debit != 0
                                    then
                                        array_to_string(ARRAY(SELECT DISTINCT a.code
                                                              FROM account_move_line m2
                                                              LEFT JOIN account_account a ON (m2.account_id=a.id)
                                                              WHERE m2.move_id = aml.move_id
                                                              AND m2.credit != 0.0), ', ') 
                                    else
                                        array_to_string(ARRAY(SELECT DISTINCT a.code
                                                              FROM account_move_line m2
                                                              LEFT JOIN account_account a ON (m2.account_id=a.id)
                                                              WHERE m2.move_id = aml.move_id
                                                              AND m2.credit = 0.0), ', ')
                                    end acc_code,
                                aml.debit, aml.credit
                            from account_move_line aml
                                join account_move am on aml.move_id=am.id
                                and am.id=%(move_id)s
                                and am.state = 'posted'
                                and aml.state = 'valid'
                                and aml.account_id in (SELECT id from fn_get_account_child_id('%(account_id)s'))
                            left join account_invoice aih on aml.move_id = aih.move_id -- lien ket voi invoice
                            left join account_voucher avh on aml.move_id = avh.move_id -- lien ket thu/chi
                            order by am.date, am.date_document, am.name, acc_code
                         '''%({
                              'move_id':line['move_id'],
                              'account_id':self.account_id,
                          })
                        cr.execute(sql)
                        for j in cr.dictfetchall():
                            self.ton += (j['debit'] - j['credit'])
                            res.append({
                                         'gl_date':j['gl_date'],
                                         'doc_date':j['doc_date'],
                                         'doc_no':j['doc_no'],
                                         'description':j['description'],
                                         'acc_code':j['acc_code'],
                                         'debit':j['debit'] or 0.0,
                                         'credit':j['credit'] or 0.0,
                                         'ton': self.ton,
                                     })
                
            return res
            
        o = self.browse(cr, uid, ids[0])
        report_line = []
        report_name = context['type_report']
        if report_name=='soquy_tienmat_report':
            if not o.showdetails:
                vals = {
                    'name': 'So Quy',
                    'don_vi': get_company_name(o),
                    'dia_chi': get_company_address(o),
                    'account_code': get_account(o)['account_code'],
                    'account_name': get_account(o)['account_name'],
                    'date_from': get_start_date(o),
                    'date_to': get_end_date(o),
                }
                for line in  show_dauky(o):
                    report_line.append((0,0,{
                    'ngay_ghso': '',
                    'ngay_thang': '',
                    'so_hieu_thu': '',
                    'so_hieu_chi': '',
                    'dien_giai': '- Số dư đầu kỳ',
                    'so_ps_no': '',
                    'so_ps_co': '',
                    'so_ps_ton': line['ton'],
                    }))
                    report_line.append((0,0,{
                        'ngay_ghso': '',
                        'ngay_thang': '',
                        'so_hieu_thu': '',
                        'so_hieu_chi': '',
                        'dien_giai': '- Số phát sinh trong kỳ',
                        'so_ps_no': '',
                        'so_ps_co': '',
                        'so_ps_ton': '',
                    }))
                for line1 in get_trongky(o):
                    report_line.append((0,0,{
                        'ngay_ghso': get_vietname_date(line1['gl_date']),
                        'ngay_thang': get_vietname_date(line1['doc_date']),
                        'so_hieu_thu': line1['doc_no_thu'],
                        'so_hieu_chi': line1['doc_no_chi'],
                        'dien_giai': line1['description'] or '',
                        'so_ps_no': line1['debit'],
                        'so_ps_co': line1['credit'],
                        'so_ps_ton': line1['ton'],
                    }))
                for line2 in get_sum_trongky(o): 
                    report_line.append((0,0,{
                        'ngay_ghso': '',
                        'ngay_thang': '',
                        'so_hieu_thu': '',
                        'so_hieu_chi': '',
                        'dien_giai': '- Cộng số phát sinh trong kỳ',
                        'so_ps_no': line2['dr_amount'],
                        'so_ps_co': line2['cr_amount'],
                        'so_ps_ton': '',
                    }))
                for line3 in get_cuoiky(o):
                    report_line.append((0,0,{
                    'ngay_ghso': '',
                    'ngay_thang': '',
                    'so_hieu_thu': '',
                    'so_hieu_chi': '',
                    'dien_giai': '- Số tồn cuối kỳ',
                    'so_ps_no': '',
                    'so_ps_co': '',
                    'so_ps_ton': line3['ton'],
                    }))
                vals.update({'so_quy_line' : report_line, })
                report_id = report_obj.create(cr, uid, vals)
                res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                                'green_erp_report_account', 'so_quy_chung_review')
                return {
                            'name': 'So Quy',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': 'so.quy.review',
                            'domain': [],
                            'type': 'ir.actions.act_window',
                            'target': 'current',
                            'res_id': report_id,
                        }
            else:
                vals = {
                    'name': 'So Quy Chi Tiet',
                    'don_vi': get_company_name(o),
                    'dia_chi': get_company_address(o),
                    'account_code': get_account(o)['account_code'],
                    'account_name': get_account(o)['account_name'],
                    'date_from': get_start_date(o),
                    'date_to': get_end_date(o),
                }
                for line in  show_dauky(o):
                    report_line.append((0,0,{
                    'ngay_ghso': '',
                    'ngay_thang': '',
                    'so_hieu_thu': '',
                    'so_hieu_chi': '',
                    'dien_giai': '- Số dư đầu kỳ',
                    'tk_doi_ung':'',
                    'so_ps_no': '',
                    'so_ps_co': '',
                    'so_ps_ton': line['ton'],
                    }))
                    report_line.append((0,0,{
                        'ngay_ghso': '',
                        'ngay_thang': '',
                        'so_hieu_thu': '',
                        'so_hieu_chi': '',
                        'dien_giai': '- Số phát sinh trong kỳ',
                        'tk_doi_ung':'',
                        'so_ps_no': '',
                        'so_ps_co': '',
                        'so_ps_ton': '',
                    }))
                for line1 in get_trongky_chitiet(o):
                    report_line.append((0,0,{
                        'ngay_ghso': get_vietname_date(line1['gl_date']),
                        'ngay_thang': get_vietname_date(line1['doc_date']),
                        'so_hieu_thu': line1['doc_no_thu'],
                        'so_hieu_chi': line1['doc_no_chi'],
                        'dien_giai': line1['description'] or '',
                        'tk_doi_ung':line1['acc_code'],
                        'so_ps_no': line1['debit'],
                        'so_ps_co': line1['credit'],
                        'so_ps_ton': line1['ton'],
                    }))
                for line2 in get_sum_trongky(o): 
                    report_line.append((0,0,{
                        'ngay_ghso': '',
                        'ngay_thang': '',
                        'so_hieu_thu': '',
                        'so_hieu_chi': '',
                        'dien_giai': '- Cộng số phát sinh trong kỳ',
                        'so_ps_no': line2['dr_amount'],
                        'so_ps_co': line2['cr_amount'],
                        'so_ps_ton': '',
                    }))
                for line3 in get_cuoiky(o):
                    report_line.append((0,0,{
                    'ngay_ghso': '',
                    'ngay_thang': '',
                    'so_hieu_thu': '',
                    'so_hieu_chi': '',
                    'dien_giai': '- Số tồn cuối kỳ',
                    'so_ps_no': '',
                    'so_ps_co': '',
                    'so_ps_ton': line3['ton'],
                    }))
                vals.update({'so_quy_line' : report_line, })
                report_id = report_obj.create(cr, uid, vals)
                res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                                'green_erp_report_account', 'so_quy_chi_tiet_review')
                return {
                            'name': 'So Quy Chi Tiet',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': 'so.quy.review',
                            'domain': [],
                            'type': 'ir.actions.act_window',
                            'target': 'current',
                            'res_id': report_id,
                        }
        if report_name=='so_tiengui_nganhang_report':
            vals = {
                    'name': 'So tien gui ngan hang',
                    'don_vi': get_company_name(o),
                    'dia_chi': get_company_address(o),
                    'account_code': get_account(o)['account_code'],
                    'account_name': get_account(o)['account_name'],
                    'date_from': get_start_date(o),
                    'date_to': get_end_date(o),
                }
            for line in  show_dauky(o):
                report_line.append((0,0,{
                'ngay_ghso': '',
                'ngay_thang': '',
                'so_hieu_thu': '',
                'dien_giai': '- Số dư đầu kỳ',
                'tk_doi_ung':'',
                'so_ps_no': '',
                'so_ps_co': '',
                'so_ps_ton': line['ton'],
                }))
                report_line.append((0,0,{
                    'ngay_ghso': '',
                    'ngay_thang': '',
                    'so_hieu_thu': '',
                    'dien_giai': '- Số phát sinh trong kỳ',
                    'tk_doi_ung':'',
                    'so_ps_no': '',
                    'so_ps_co': '',
                    'so_ps_ton': '',
                }))
            for line1 in get_trongky_tienmat(o):
                report_line.append((0,0,{
                    'ngay_ghso': get_vietname_date(line1['gl_date']),
                    'ngay_thang': get_vietname_date(line1['doc_date']),
                    'so_hieu_thu': line1['doc_no'],
                    'dien_giai': line1['description'] or '',
                    'tk_doi_ung':line1['acc_code'],
                    'so_ps_no': line1['debit'],
                    'so_ps_co': line1['credit'],
                    'so_ps_ton': line1['ton'],
                }))
            for line2 in get_sum_trongky(o): 
                report_line.append((0,0,{
                    'ngay_ghso': '',
                    'ngay_thang': '',
                    'so_hieu_thu': '',
                    'dien_giai': '- Cộng số phát sinh trong kỳ',
                    'tk_doi_ung':'',
                    'so_ps_no': line2['dr_amount'],
                    'so_ps_co': line2['cr_amount'],
                    'so_ps_ton': '',
                }))
            for line3 in get_cuoiky(o):
                report_line.append((0,0,{
                'ngay_ghso': '',
                'ngay_thang': '',
                'so_hieu_thu': '',
                'dien_giai': '- Số tồn cuối kỳ',
                'tk_doi_ung':'',
                'so_ps_no': '',
                'so_ps_co': '',
                'so_ps_ton': line3['ton'],
                }))
            vals.update({'so_quy_line' : report_line, })
            report_id = report_obj.create(cr, uid, vals)
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                            'green_erp_report_account', 'so_tiengui_nganhang_review')
            return {
                        'name': 'So tien gui ngan hang',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'so.quy.review',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'res_id': report_id,
                    }
            
                    
        
        
    
so_quy()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
