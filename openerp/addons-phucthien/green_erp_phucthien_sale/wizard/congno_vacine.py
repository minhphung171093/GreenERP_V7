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
from openerp.osv import osv,fields
from openerp.tools.translate import _


class congno_vacine(osv.osv_memory):
    _name = 'congno.vacine'
     
    _columns = {
        'date_from': fields.date('Từ ngày',required=True),
        'date_to': fields.date('Đến ngày',required=True),
#         'user_id': fields.many2many('res.users', string='Users', readonly=True),
        'user_id': fields.many2many('res.users', 'congno_user_ref', 'congno_id', 'user_id', 'Nhân Viên Bán Hàng'),  
    }
     
    _defaults = {
        'date_from': time.strftime('%Y-%m-01'),
        'date_to': time.strftime('%Y-%m-%d'),
        'user_id': lambda self,cr, uid, ctx: [(6,0,[uid])],
        
    }
     
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'congno.vacine' 
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'congno_vacine_report', 'datas': datas}
     
congno_vacine()

class congno_mypham(osv.osv_memory):
    _name = 'congno.mypham'
     
    _columns = {
        'period_id': fields.many2one('account.period','Tháng:'),
        'date_from': fields.date('Từ ngày',required=True),
        'date_to': fields.date('Đến ngày',required=True),
#         'user_id': fields.many2many('res.users', string='Users', readonly=True),
        'user_ids': fields.many2many('res.users', 'mypham_user_ref', 'mypham_id', 'user_id', 'Nhân Viên Bán Hàng'),  
    }
     
    _defaults = {
        'date_from': time.strftime('%Y-%m-01'),
        'date_to': time.strftime('%Y-%m-%d'),
        'user_ids': lambda self,cr, uid, ctx: [(6,0,[uid])],
    }
     
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'congno.mypham' 
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'congno_mypham_report', 'datas': datas}
     
congno_mypham()

class congno_duocpham(osv.osv_memory):
    _name = 'congno.duocpham'
     
    _columns = {
        'date_from': fields.date('Từ ngày',required=True),
        'date_to': fields.date('Đến ngày',required=True),
        'period_id': fields.many2one('account.period','Tháng:'),
        'user_ids': fields.many2many('res.users', 'duocpham_user_ref', 'duocpham_id', 'user_id', 'Nhân Viên Bán Hàng'),  
    }
     
    _defaults = {
        'date_from': time.strftime('%Y-%m-01'),
        'date_to': time.strftime('%Y-%m-%d'),
        'user_ids': lambda self,cr, uid, ctx: [(6,0,[uid])],
    }
     
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'congno.duocpham' 
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'congno_duocpham_report', 'datas': datas}
     
congno_duocpham()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

