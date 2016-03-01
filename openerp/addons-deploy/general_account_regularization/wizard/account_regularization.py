# -*- encoding: utf-8 -*-
##############################################################################
#
#
##############################################################################
from osv import osv, fields
from tools.translate import _
import time
from datetime import datetime

class wizard_regularize(osv.osv):
	_name = "wizard.regularize"
	_columns = {
#		'fiscalyear': fields.many2one('account.fiscalyear', 'Fiscal year', help='Fiscal Year for the write move', required=True),
		'journal_id': fields.many2one('account.journal', 'Journal', help='Journal for the move', required=True, states={'draft':[('readonly',False)]}),
		'period_id': fields.many2one('account.period', 'Period', help='Period for the move', required=True, states={'draft':[('readonly',False)]}),
		'date_move': fields.date('Date', help='Date for the move', required=True, states={'draft':[('readonly',False)]}),
		
		'balance_calc': fields.selection([('date','Date'),('period','Period')], 'Regularization time calculation', required=True, states={'draft':[('readonly',False)]}),
# 		'periods': fields.many2many('account.period', 'wizard_regularize_period', 'wizard_regularize_id', 'period_id', 'Periods', help='Periods to regularize', required=False),
		'date_to': fields.date('Date To', help='Include movements up to this date', required=False, states={'draft':[('readonly',False)]}),
		'acc_move_ids':fields.many2many('account.move','account_move_ket_chuyen_ref', 'wizard_regularize_id', 'acc_move_id','Account Move',readonly=True, states={'draft':[('readonly',False)]}),
		'state': fields.selection([
            ('draft','Nháp'),
            ('done','Đã kết chuyển'),
            ('cancel','Hủy bỏ'),
            ],'Trạng thái', select=True, readonly=True),
	}
    
	_defaults = {
		'state': 'draft',
		'balance_calc': lambda *a: 'period',
		'date_move': lambda *a: time.strftime('%Y-%m-%d'),
		'period_id': lambda self, cr, uid, c: self.pool.get('account.period').find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0],
    }
	
	def bt_huy(self, cr, uid, ids, context=None):
		line = self.browse(cr,uid,ids[0])
		sql = '''
		    select acc_move_id from account_move_ket_chuyen_ref where wizard_regularize_id = %s
		'''%(line.id)
		cr.execute(sql)
		huy_ids = [r[0] for r in cr.fetchall()]
		self.pool.get('account.move').button_cancel(cr,uid,huy_ids)
		sql = '''
		    delete from account_move_line where move_id in (select acc_move_id from account_move_ket_chuyen_ref where wizard_regularize_id = %s)
		'''%(line.id)
		cr.execute(sql)
		
		sql = '''
		    delete from account_move where id in (select acc_move_id from account_move_ket_chuyen_ref where wizard_regularize_id = %s)
		'''%(line.id)
		cr.execute(sql)
		return self.write(cr,uid,ids,{'state':'cancel'})
    
	def regularize(self, cr, uid, ids, context):
		this = self.browse(cr, uid, ids)[0]
		regu_objs = self.pool.get('account.regularization')
		regu_ids = regu_objs.search(cr, uid, [('balance_calc','=',this.balance_calc),('active','=',True)], order='sequence')
		if not regu_ids:
			raise osv.except_osv('Warning!', "There are no Regularization with type '%s'"%(this.balance_calc))
# 		date = this.date_move
		date = this.period_id.date_stop
		period = this.period_id.id or False
# 		journal = this.journal_id.id or False
		journal_ids = self.pool.get('account.journal').search(cr,uid,[('code','=','03'),('type','=','general')])
		journal = journal_ids[0]
		date_to = None
		period_ids = [period]
		if this.balance_calc == 'date':
			date_to = this.date_to
# 		else:
# 			period_ids = [x.id for x in this.periods]
		move_ids = regu_objs.regularize(cr, uid, regu_ids, context, date, period, journal, date_to, period_ids)
		var ={
                        'acc_move_ids':[(6, 0, move_ids)],
                        'state': 'done',
                      }
		return self.write(cr,uid,ids,var)
	
	


wizard_regularize()


