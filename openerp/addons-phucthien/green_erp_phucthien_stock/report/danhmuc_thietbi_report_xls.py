# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_date_from':self.get_date_from,
            'get_date_to':self.get_date_to,
            'get_vietname_date': self.get_vietname_date,
            'get_dd_vanphong': self.get_dd_vanphong,
            'get_dd_kholanh': self.get_dd_kholanh,
            'get_ten_van_phong': self.get_ten_van_phong,
            'get_ten_kho_lanh': self.get_ten_kho_lanh,
            'get_lines': self.get_lines,
            
        })
        
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        tu_ngay = wizard_data['tu_ngay']
        den_ngay = wizard_data['den_ngay']
        svtm_obj = self.pool.get('ve.sinh.thangmay')
        sql = '''
            select id from ve_sinh_thangmay where name between '%s' and '%s' and state != 'huy'
        '''%(tu_ngay,den_ngay)
        self.cr.execute(sql)
        svtm_ids = [r[0] for r in self.cr.fetchall()]
        return svtm_obj.browse(self.cr, self.uid, svtm_ids)
        
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['tu_ngay'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['den_ngay'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_vietname_date(self, date):
        if not date:
            return ''
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
         
    def get_dd_vanphong(self):
        res = []
        wizard_data = self.localcontext['data']['form']
        tu_ngay = wizard_data['tu_ngay']
        den_ngay = wizard_data['den_ngay']
        sql ='''
            select * from dm_thietbi where dia_diem = 'van_phong' and ngay_mua between '%s' and '%s'
        ''' %(tu_ngay, den_ngay)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_dd_kholanh(self):
        res = []
        wizard_data = self.localcontext['data']['form']
        tu_ngay = wizard_data['tu_ngay']
        den_ngay = wizard_data['den_ngay']
        sql ='''
            select * from dm_thietbi where dia_diem = 'kho_lanh' and ngay_mua between '%s' and '%s'
        ''' %(tu_ngay, den_ngay)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_ten_van_phong(self, seq):
        if seq == 1:
            return 'Văn phòng'
        else:
            return ''
        
    def get_ten_kho_lanh(self, seq):
        if seq == 1:
            return 'Kho lạnh'
        else:
            return ''
    
