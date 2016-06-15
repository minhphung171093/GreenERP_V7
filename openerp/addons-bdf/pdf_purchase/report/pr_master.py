# -*- coding: utf-8 -*-
##############################################################################
#
#    HLVSolution, Open Source Management Solution
#
##############################################################################


from report import report_sxw
import pooler
from osv import osv
from tools.translate import _
import random
import time
from datetime import datetime
import datetime
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)  
        res_user_obj = pool.get('res.users').browse(cr, uid, uid)
        self.amount = 0.0
        self.res_name = False
        self.num = 0
        self.localcontext.update({
            'get_date':self.get_date,
            'get_date_budget': self.get_date_budget,
            'get_label_for_bdf': self.get_label_for_bdf,
            'get_partner_address':self.get_partner_address,
            'get_vietname_datetime': self.get_vietname_datetime,
            'get_total_amount':self.get_total_amount,
            'get_alllocation':self.get_alllocation,
            'get_qrt':self.get_qrt,
            'get_total_fx_amount': self.get_total_fx_amount,
            'get_spending_detail_line': self.get_spending_detail_line,
            'get_request': self.get_request,
            'get_country_manager': self.get_country_manager,
            'get_procurement_detail_line':self.get_procurement_detail_line,
            'get_spending_detail_line_re': self.get_spending_detail_line_re,
            'get_finance_250': self.get_finance_250,
            'get_finance_500': self.get_finance_500,
            'get_function1': self.get_function1,
            'get_function2': self.get_function2,
            'get_function3': self.get_function3,
            'get_name_function1': self.get_name_function1,
            'get_name_function2': self.get_name_function2,
            'get_name_function3': self.get_name_function3,
            'get_allocation': self.get_allocation,
            'get_cell': self.get_cell,
            'get_label_bdf': self.get_label_bdf,
        })
    
    def get_request(self,o):
        if o.request_by_id:
            return True
        else:
            return False
    
    def get_allocation(self,o):
        key_account_obj = self.pool.get('master.key.accounts')
        self.cr.execute('''
            select key_account_id from bdf_allocation 
                where spending_detail_id in (select id from spending_detail where purchase_id = %s) and allocation is not null and allocation!=0 group by key_account_id order by key_account_id 
        ''',(o.id,))
        key_account_ids = [r[0] for r in self.cr.fetchall()]
        return key_account_obj.browse(self.cr, self.uid, key_account_ids)
    
    def get_cell(self, line,o,num):
        key_accounts = self.get_allocation(o)
        if len(key_accounts)>=num+1:
            self.cr.execute('''
                select allocation from bdf_allocation 
                    where key_account_id=%s and spending_detail_id =%s
            ''',(key_accounts[num].id,line.id,))
            allocations = [r[0] for r in self.cr.fetchall()]
            return allocations and allocations[0] or 0
        else:
            return ''
    
    def get_label_bdf(self,o,num):
        key_accounts = self.get_allocation(o)
        if len(key_accounts)>=num+1:
            return key_accounts[num].name
        else:
            return ''
    
    def get_country_manager(self, o):
        if o.country_manager_approve_id:
            return True
        else:
            return False
    
    def get_finance_250(self,o):
        if o.control_manager_approve_id:
            return True
        return False
    
    def get_finance_500(self,o):
        if o.fi_function_head_approve_id:
            return True
        return False
    
    def get_function1(self,o):
        if o.category_manager_approve_id or o.channel_manager_approve_id or o.product_manager_approve_id:
            return True
        return False
    
    def get_function2(self,o):
        if o.group_pm_approve_id:
            return True
        return False
    
    def get_function3(self,o):
        if o.function_head_approve_id or o.bu_manager_approve_id:
            return True
        return False
    
    def get_name_function1(self,o):
        if o.category_manager_approve_id:
            return o.category_manager_approve_id.name
        elif o.channel_manager_approve_id:
            return o.channel_manager_approve_id.name
        elif o.product_manager_approve_id:
            return o.product_manager_approve_id.name
        else:
            return ''
    
    def get_name_function2(self,o):
        if o.group_pm_approve_id:
            return o.group_pm_approve_id.name
        return ''
    
    def get_name_function3(self,o):
        if o.function_head_approve_id:
            return o.function_head_approve_id.name
        elif o.bu_manager_approve_id:
            return o.bu_manager_approve_id.name
        else:
            return ''
    
    def get_date(self,date):
        if date:
            d = datetime.datetime.strptime(date, "%Y-%m-%d")
            d = d.strftime("%d-%b-%y")
            return d
        else:
            return False
    
    def get_date_budget(self,date):
        if date:
            d = datetime.datetime.strptime(date, "%Y-%m-%d")
            d = d.strftime("%b-%y")
            return d
        else:
            return False
    
    def get_total_amount(self,obj):
        amount =0.0
        for i in obj:
            amount = amount + i.amt
        return amount
    
    def get_total_fx_amount(self,obj):
        amount =0.0
        for i in obj:
            amount = amount + i.fx_currency
        return amount
    
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)        
        return date.strftime('%d-%m-%Y')
    
    def get_vietname_datetime(self, date):
        if not date:
            date = time.strftime(DATETIME_FORMAT)
        date = datetime.strptime(date, DATETIME_FORMAT)        
        return date.strftime('%d-%m-%Y')
    
    def get_partner_address(self, order):
        address = ''
        address += order.partner_id and order.partner_id.street or '' + ' ,' 
        address += order.partner_id and order.partner_id.city or '' + ' ,' 
        address += order.partner_id and order.partner_id.state_id and order.partner_id and order.partner_id.state_id.name or ''
                
        return address
    
    def get_alllocation(self,pur):
        sql='''
            select distinct mka.name ,mka.id from bdf_allocation b_all
                inner join master_regions  mr on b_all.regions_id = mr.id
                inner join master_key_accounts mka on mka.id = mr.account_id
                where spending_detail_id in (select id from spending_detail where purchase_id = %s)
        '''%(pur)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_qrt(self,pur_id,re_id):
        sql='''
            select allocation from bdf_allocation where spending_detail_id = %s and regions_id = %s
        '''%(pur_id,re_id)
        self.cr.execute(sql)
        for i in self.cr.dictfetchall():
            return i['allocation'] or 0
        return 0
    
    def get_label_for_bdf(self,o,num):
        if o.channel.name == 'MT':
            if num==1:
                label = 'COOP'
            elif num==2:
                label = 'METRO'
            elif num==3:
                label = 'BIG C'
            elif num==4:
                label = 'HYPER'
            elif num==5:
                label = 'INDEPT'
            elif num==6:
                label = 'GUARDIAN'
        elif o.channel.name == 'GT':
            if num==1:
                label = 'CENTRAL'
            elif num==2:
                label = 'HCM'
            elif num==3:
                label = 'MEKONG'
            elif num==4:
                label = 'NORTH 1'
            elif num==5:
                label = 'NORTH 2'
            elif num==6:
                label = 'SE'
        elif o.channel.name in ['PHARMACY','HOSPITAL']:
            if num==1:
                label = 'HCM'
            elif num==2:
                label = 'CENTRAL'
            elif num==3:
                label = 'MEKONG'
            elif num==4:
                label = 'NORTH'
            elif num==5:
                label = 'HANOI'
            elif num==6:
                label = 'SEAST'
        else:
            label = ''
        return label
    
    def get_spending_detail_line(self,o):
        res = []
        for seq,line in enumerate(o.spending_detail_line):
            allocation_by_month = 0
            month = ''
            if seq==0:
                month = 'Jan'
                sql = '''
                    select allocation from bdf_allocation_month where month='jan' and purchase_id=%s 
                '''%(o.id)
                self.cr.execute()
                allocation = self.cr.fetchone()
                allocation_by_month = allocation and allocation[0] or 0
            if seq==1:
                month = 'Feb'
                sql = '''
                    select allocation from bdf_allocation_month where month='feb' and purchase_id=%s 
                '''%(o.id)
                self.cr.execute()
                allocation = self.cr.fetchone()
                allocation_by_month = allocation and allocation[0] or 0
            if seq==2:
                month = 'Mar'
                sql = '''
                    select allocation from bdf_allocation_month where month='mar' and purchase_id=%s 
                '''%(o.id)
                self.cr.execute()
                allocation = self.cr.fetchone()
                allocation_by_month = allocation and allocation[0] or 0
            if seq==3:
                month = 'Apr'
                sql = '''
                    select allocation from bdf_allocation_month where month='apr' and purchase_id=%s 
                '''%(o.id)
                self.cr.execute()
                allocation = self.cr.fetchone()
                allocation_by_month = allocation and allocation[0] or 0
            if seq==4:
                month = 'May'
                sql = '''
                    select allocation from bdf_allocation_month where month='may' and purchase_id=%s 
                '''%(o.id)
                self.cr.execute()
                allocation = self.cr.fetchone()
                allocation_by_month = allocation and allocation[0] or 0
            if seq==5:
                month = 'Jun'
                sql = '''
                    select allocation from bdf_allocation_month where month='jun' and purchase_id=%s 
                '''%(o.id)
                self.cr.execute()
                allocation = self.cr.fetchone()
                allocation_by_month = allocation and allocation[0] or 0
            if seq==6:
                month = 'Jul'
                sql = '''
                    select allocation from bdf_allocation_month where month='jul' and purchase_id=%s 
                '''%(o.id)
                self.cr.execute()
                allocation = self.cr.fetchone()
                allocation_by_month = allocation and allocation[0] or 0
            if seq==7:
                month = 'Aug'
                sql = '''
                    select allocation from bdf_allocation_month where month='aug' and purchase_id=%s 
                '''%(o.id)
                self.cr.execute()
                allocation = self.cr.fetchone()
                allocation_by_month = allocation and allocation[0] or 0
            if seq==8:
                month = 'Sep'
                sql = '''
                    select allocation from bdf_allocation_month where month='sep' and purchase_id=%s 
                '''%(o.id)
                self.cr.execute()
                allocation = self.cr.fetchone()
                allocation_by_month = allocation and allocation[0] or 0
            if seq==9:
                month = 'Oct'
                sql = '''
                    select allocation from bdf_allocation_month where month='oct' and purchase_id=%s 
                '''%(o.id)
                self.cr.execute()
                allocation = self.cr.fetchone()
                allocation_by_month = allocation and allocation[0] or 0
            if seq==10:
                month = 'Nov'
                sql = '''
                    select allocation from bdf_allocation_month where month='nov' and purchase_id=%s 
                '''%(o.id)
                self.cr.execute()
                allocation = self.cr.fetchone()
                allocation_by_month = allocation and allocation[0] or 0
            if seq==11:
                month = 'Dec'
                sql = '''
                    select allocation from bdf_allocation_month where month='dec' and purchase_id=%s 
                '''%(o.id)
                self.cr.execute()
                allocation = self.cr.fetchone()
                allocation_by_month = allocation and allocation[0] or 0
            res.append({
                'cat_code': line.sub_cat and line.sub_cat.name or '',
                'cat': line.cat and line.cat.name or '',
                'sub_cat': line.sub_cat and line.sub_cat.sub_cat or '',
                'project_id': line.project_id,
                'product': line.product_id and line.product_id.name or '',
                'account': line.account_id and line.account_id.code + ' '+line.account_id.name or '',
                'qty': line.qty,
                'price_unit': line.price_unit,
                'amt': line.amt,
                'io': line.io_id and line.io_id.name or '',
                'allocation_by_cat': line.allocation_by_cat,
                'month': month,
                'allocation_by_month': allocation_by_month,
            })
        if len(o.spending_detail_line)<13:
            for seq in range(len(o.spending_detail_line),13):
                allocation_by_month = 0
                month = ''
                if seq==0:
                    month = 'Jan'
                    sql = '''
                        select allocation from bdf_allocation_month where month='jan' and purchase_id=%s 
                    '''%(o.id)
                    self.cr.execute()
                    allocation = self.cr.fetchone()
                    allocation_by_month = allocation and allocation[0] or 0
                if seq==1:
                    month = 'Feb'
                    sql = '''
                        select allocation from bdf_allocation_month where month='feb' and purchase_id=%s 
                    '''%(o.id)
                    self.cr.execute()
                    allocation = self.cr.fetchone()
                    allocation_by_month = allocation and allocation[0] or 0
                if seq==2:
                    month = 'Mar'
                    sql = '''
                        select allocation from bdf_allocation_month where month='mar' and purchase_id=%s 
                    '''%(o.id)
                    self.cr.execute()
                    allocation = self.cr.fetchone()
                    allocation_by_month = allocation and allocation[0] or 0
                if seq==3:
                    month = 'Apr'
                    sql = '''
                        select allocation from bdf_allocation_month where month='apr' and purchase_id=%s 
                    '''%(o.id)
                    self.cr.execute()
                    allocation = self.cr.fetchone()
                    allocation_by_month = allocation and allocation[0] or 0
                if seq==4:
                    month = 'May'
                    sql = '''
                        select allocation from bdf_allocation_month where month='may' and purchase_id=%s 
                    '''%(o.id)
                    self.cr.execute()
                    allocation = self.cr.fetchone()
                    allocation_by_month = allocation and allocation[0] or 0
                if seq==5:
                    month = 'Jun'
                    sql = '''
                        select allocation from bdf_allocation_month where month='jun' and purchase_id=%s 
                    '''%(o.id)
                    self.cr.execute()
                    allocation = self.cr.fetchone()
                    allocation_by_month = allocation and allocation[0] or 0
                if seq==6:
                    month = 'Jul'
                    sql = '''
                        select allocation from bdf_allocation_month where month='jul' and purchase_id=%s 
                    '''%(o.id)
                    self.cr.execute()
                    allocation = self.cr.fetchone()
                    allocation_by_month = allocation and allocation[0] or 0
                if seq==7:
                    month = 'Aug'
                    sql = '''
                        select allocation from bdf_allocation_month where month='aug' and purchase_id=%s 
                    '''%(o.id)
                    self.cr.execute()
                    allocation = self.cr.fetchone()
                    allocation_by_month = allocation and allocation[0] or 0
                if seq==8:
                    month = 'Sep'
                    sql = '''
                        select allocation from bdf_allocation_month where month='sep' and purchase_id=%s 
                    '''%(o.id)
                    self.cr.execute()
                    allocation = self.cr.fetchone()
                    allocation_by_month = allocation and allocation[0] or 0
                if seq==9:
                    month = 'Oct'
                    sql = '''
                        select allocation from bdf_allocation_month where month='oct' and purchase_id=%s 
                    '''%(o.id)
                    self.cr.execute()
                    allocation = self.cr.fetchone()
                    allocation_by_month = allocation and allocation[0] or 0
                if seq==10:
                    month = 'Nov'
                    sql = '''
                        select allocation from bdf_allocation_month where month='nov' and purchase_id=%s 
                    '''%(o.id)
                    self.cr.execute()
                    allocation = self.cr.fetchone()
                    allocation_by_month = allocation and allocation[0] or 0
                if seq==11:
                    month = 'Dec'
                    sql = '''
                        select allocation from bdf_allocation_month where month='dec' and purchase_id=%s 
                    '''%(o.id)
                    self.cr.execute()
                    allocation = self.cr.fetchone()
                    allocation_by_month = allocation and allocation[0] or 0
                res.append({
                    'cat_code': '',
                    'cat': '',
                    'sub_cat': '',
                    'project_id': '',
                    'product': '',
                    'account': '',
                    'qty': '',
                    'price_unit': '',
                    'amt': '',
                    'io': '',
                    'allocation_by_cat': '',
                    'month': month,
                    'allocation_by_month': allocation_by_month,
                })
        return res
        
    def get_procurement_detail_line(self,line):
        res = []
        if len(line)<7:
            for i in range(len(line)+1,8):
                res.append({'name':''})
        return res
    
    def get_spending_detail_line_re(self,o):
        res = []
        line = self.get_spending_detail_line(o)
        if len(line)<9:
            for i in range(len(line)+1,10):
                res.append({'name':''})
        return res
    
    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
