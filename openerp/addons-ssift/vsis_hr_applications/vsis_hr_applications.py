# -*- encoding: utf-8 -*-
##############################################################################
#
#    General Solutions, Open Source Management Solution
#    Copyright (C) 2009 General Solutions (<http://gscom.vn>). All Rights Reserved
#
##############################################################################

from osv import fields, osv
import time
import netsvc
import pooler
import tools
from tools.translate import _
import datetime
import decimal_precision as dp
from tools import config
import httplib
import logging
_logger = logging.getLogger(__name__)

class hr_applicant(osv.osv):
    _inherit = 'hr.applicant'
    _columns = {
                'male':fields.boolean("Male/Nam:"),
                'female':fields.boolean("Female/Nữ:"),
                'education_id': fields.one2many('hr.education.background', 'applicant_id', 'Education Background'),
                'work_history_id': fields.one2many('hr.work.history', 'applicant_id', 'Work History'),
                'day_of_birth' :fields.date('Day Of Birth/Ngày sinh:'),
                'place_of_birth' :fields.char('Place of birth/Nơi sinh:',size=120),
                'single':fields.boolean('Single/Độc thân:'),
                'married':fields.boolean('Married/Đã Kết hôn:'),
                'national':fields.char('National/Quốc tịch:',size=120),
                'religion':fields.char('Religion/Tôn giáo:',size=120),
                'per_address':fields.char('Address/Tạm trú:',size=240),
                'resident_address':fields.char('Resident Add./Thườngtrú:',size=240),
                'id_pass':fields.char('ID Pass. / Số CMND:',size=240),
                'doi' :fields.date('DOI/Ngày cấp:'),
                'poi':fields.char('POI/Nơi cấp:',size=240),
                'Day_for_start_to_work' :fields.date(' Day for start to work:'),                
                }
    def onchange_male(self,cr,uid,ids,male,female):
        value ={}
        if male and female:
            value.update({'female':False})
        return {'value': value}
    
    def onchange_female(self,cr,uid,ids,male,female):
        value ={}
        if male and female:
            value.update({'male':False})
        return {'value': value }
    
    def onchange_single(self,cr,uid,ids,single,married):
        value ={}
        if single and married:
            value.update({'married':False})
        return {'value': value}
    
    def onchange_married(self,cr,uid,ids,single,married):
        value ={}
        if single and married:
            value.update({'single':False})
        return {'value': value }
    
hr_applicant()

class hr_foreign_languages(osv.osv):
    _name = "hr.foreign.languages"
    _order = "code"
    _description = "Foreign Languages"
    _columns = {
        'code' : fields.char('Code', 16, required=True),
        'name' : fields.char('Name', 128, required=True),
        'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the record without removing it."),
    }
    _defaults = {
        'active': True,
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
    ]
hr_foreign_languages()

class computer_skill(osv.osv):
    _name = "hr.computer.skill"
    _order = "code"
    _description = "Computer skill"
    _columns = {
        'code' : fields.char('Code', 16, required=True),
        'name' : fields.char('Name', 128, required=True),
        'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the record without removing it."),
    }
    _defaults = {
        'active': True,
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
    ]
computer_skill()

class hr_education_background(osv.osv):
    _name = "hr.education.background"
    _order = "period desc"
    _columns = {
        'applicant_id': fields.many2one('hr.applicant', 'applicant'),
        'degrees' : fields.many2one('hr.certification', 'Type Degrees'),
        'major_info' : fields.char('Major or course info', 1024),
        'school_name' : fields.char('School name', 1024),
        'period': fields.date('Period'),
        'foreign_languages_ids' : fields.many2many('hr.foreign.languages','foreign_education_rel', 'education_id','foreign_id', 'Foreign Languages'),
        'computer_skill_ids' : fields.many2many('hr.computer.skill','computer_education_rel', 'education_id','computer_id', 'Computer skill'),
        }   
    
hr_education_background()

class hr_work_history(osv.osv):
    _name = "hr.work.history"
    _columns = {
        'applicant_id': fields.many2one('hr.applicant', 'applicant'),        
        'period': fields.date('Period '),
        'company_name' : fields.char('Company Name', 1024),        
        'Position' : fields.char('Position', 1024),
        'responsible_area' : fields.text('Responsible Area'),
        'reason' : fields.text('Reason for leaving/job search'),
        }   
    
hr_work_history()
#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
