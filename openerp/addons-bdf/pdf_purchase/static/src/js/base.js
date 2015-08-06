openerp.pdf_purchase = function (instance) {
    var _t = instance.web._t;
    var QWeb = instance.web.qweb;
    
    instance.web.Login.include({
    
    	start: function() {
		    var self = this;
		    self.$el.find("form").submit(self.on_submit);
		    self.$el.find('.oe_login_manage_db').click(function() {
		        self.do_action("database_manager");
		    });
		    self.on('change:database_selector', this, function() {
		        this.database_selected(this.get('database_selector'));
		    });
		    var d = $.when();
		    if ($.param.fragment().token) {
		        self.params.token = $.param.fragment().token;
		    }
		    // used by dbmanager.do_create via internal client action
		    if (self.params.db && self.params.login && self.params.password) {
		        d = self.do_login(self.params.db, self.params.login, self.params.password);
		    } else {
		        d = self.rpc("/web/database/get_list", {})
		            .done(self.on_db_loaded)
		            .fail(self.on_db_failed)
		            .always(function() {
		                if (self.selected_db && self.has_local_storage && self.remember_credentials) {
		                    self.$("[name=login]").val(localStorage.getItem(self.selected_db + '|last_login') || '');
		                }
		            });
		    }
		    return d;
		},
    	
        do_login: function (db, login, password) {
            var self = this;
            self.hide_error();
            self.$(".oe_login_pane").fadeOut("slow");
            return this.session.session_authenticate(db, login, password).then(function() {
            	var bdf = new instance.web.DataSet(self, 'bdf.purchase');
		        if (self.params && self.params.approve_pr_by_mail && self.params.id) {
		        	bdf_id = self.params.id
		            bdf.call('approve_pr_by_mail', [
		                [bdf_id]
		            ]).done(function (result) {
		            alert(_t("Approved Successfull"));
		            logout = new instance.web.WebClient();
		            logout.on_logout();
		            });
		        }
		        if (self.params && self.params.reject_pr_by_mail && self.params.id) {
		        	bdf_id = self.params.id
		            bdf.call('reject_pr_by_mail', [
		                [bdf_id]
		            ]).done(function (result) {
		            alert(_t("Rejected Successfull"));
		            logout = new instance.web.WebClient();
		            logout.on_logout();
		            });
		        }
                self.remember_last_used_database(db);
                if (self.has_local_storage && self.remember_credentials) {
                    localStorage.setItem(db + '|last_login', login);
                }
                self.trigger('login_successful');
                
            }, function () {
                self.$(".oe_login_pane").fadeIn("fast", function() {
                    self.show_error(_t("Invalid username or password"));
                });
            });
        },
    });
}