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


class chat_luong_wizard(osv.osv_memory):
    _name = "chat.luong.wizard"    
     
    _columns = {
        'chat_luong_id':fields.many2one('chat.luong','Chất lượng'),
        'hopdong_id':fields.many2one('hop.dong','Hợp đồng'),
     }
        
    def bt_ok(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids):
            self.pool.get('hop.dong').write(cr,uid,[line.hopdong_id.id],{
                                                                         'chat_luong': line.chat_luong_id.name,
                                                                         })
        return True
        
chat_luong_wizard()
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
