# -*- coding: utf-8 -*-
# #############################################################################
# 
# #############################################################################
import tools
from osv import fields, osv
from tools.translate import _
import openerp.tools as tools
import decimal_precision as dp
import openerp.modules
import sys
import os
import logging
_logger = logging.getLogger(__name__)

class sql_function(osv.osv):
    _name = "sql.function"
    _auto = False
    
    def init(self, cr):
        self.fn_get_account_child_id(cr)
        cr.commit()
        return True
    
    def fn_get_account_child_id(self, cr):
        sql = '''
        DROP FUNCTION IF EXISTS fn_get_account_child_id(parent integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fn_get_account_child_id(parent integer)
          RETURNS SETOF account_account AS
        $BODY$
                SELECT  account_account
                FROM    account_account
                WHERE   id = $1
                UNION ALL
                SELECT  fn_get_account_child_id(id)
                FROM    account_account     
                WHERE   parent_id = $1
        $BODY$
          LANGUAGE sql VOLATILE
          COST 100
          ROWS 1000;
        --ALTER FUNCTION fn_get_account_child_id(integer)
          --OWNER TO openerp;
        '''
        cr.execute(sql)
        return True

sql_function()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
