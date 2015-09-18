openerp.hr_login_logout = function (instance) {
    var _t = instance.web._t;
    var QWeb = instance.web.qweb;
    
    instance.web.Login.include({
        do_login: function (db, login, password) {
            var self = this;
            self.hide_error();
            self.$(".oe_login_pane").fadeOut("slow");
            return this.session.session_authenticate(db, login, password).then(function() {
                self.remember_last_used_database(db);
                if (self.has_local_storage && self.remember_credentials) {
                    localStorage.setItem(db + '|last_login', login);
                }
                self.trigger('login_successful');
                var employee = new instance.web.DataSetSearch(self, 'hr.employee', self.session.user_context, [
                    ['user_id', '=', self.session.uid]
                ]);
                var hr_employee = new instance.web.DataSet(self, 'hr.employee');
                employee.read_slice(['id', 'name']).then(function (res) {
                    employee_id = res[0].id
                    if (employee_id) {
                        hr_employee.call('attendance_action_change', [
                            [employee_id]
                        ]).done(function (result) {
                            self.last_sign = new Date();
                            self.set({"signed_in": ! self.get("signed_in")});
                        });
                    }
                });
            }, function () {
                self.$(".oe_login_pane").fadeIn("fast", function() {
                    self.show_error(_t("Invalid username or password"));
                });
            });
        },
    });
    
    instance.web.UserMenu.include({
        on_menu_logout: function() {
            var self = this;
            var employee = new instance.web.DataSetSearch(self, 'hr.employee', self.session.user_context, [
                ['user_id', '=', self.session.uid]
            ]);
            if (employee) {
                var hr_employee = new instance.web.DataSet(self, 'hr.employee');
                employee.read_slice(['id', 'name', 'state', 'last_sign', 'attendance_access']).then(function (res) {
                    if (_.isEmpty(res) )
                        return;
                    if (res[0].attendance_access === false){
                        return;
                    }
                    self.employee = res[0];
                    if (self.employee.id) {
                        hr_employee.call('attendance_action_change', [
                            [self.employee.id]
                        ]).done(function (result) {
                            self.last_sign = instance.web.str_to_datetime(self.employee.last_sign);
                            self.set({"signed_in": self.employee.state !== "absent"});
                        });
                        self.trigger('user_logout');
                    }
                });
            } else {
                self.trigger('user_logout');
            }
        }
    });
    
    instance.web.WebClient.include({
        on_logout: function() {
            var self = this;
            if (!this.has_uncommitted_changes()) {
                this.session.session_logout().done(function () {
                    $(window).unbind('hashchange', self.on_hashchange);
                    self.do_push_state({});
                    instance.web.redirect('/');
                });
            }
        },
    });
}