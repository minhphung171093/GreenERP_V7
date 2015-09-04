# -*- encoding: utf-8 -*-
##############################################################################
#
#
##############################################################################
{
	"name" : "GreenERP Account Regularizations",
	"version" : "6.1",
	"author" : "nguyentoanit@gmail.com",
	'website' : 'http://incomtech.com/',
	"license" : "GPL-3",
	"category" : "GreenERP",
	"description" : """ This module creates a new object in accounting, 
	very similar to the account models named account.regularization. 
	Within this object you can define regularization moves, 
	This is, accounting moves that will automatically calculate the balance of a set of accounts, 
	Set it to 0 and transfer the difference to a new account. This is used, for example with tax declarations or in some countries to create the 'Profit and Loss' regularization
""",
	"depends" : ["account","account_accountant",'green_erp_viruco_base'],
	"demo_xml" : [],
	"update_xml" : [
		"security/ir.model.access.csv",
		'wizard/account_regularization.xml',
		"account_regularization_view.xml",
		"menu.xml",
	],
	"active": False,
	"installable": True,

}
