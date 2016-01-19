# -*- coding: utf-8 -*-
# #############################################################################
# 
# #############################################################################
import tools
from osv import fields, osv
from tools.translate import _

class sql_luuhuyen_tiente(osv.osv):
    _name = "sql.luuhuyen.tiente"
    _auto = False
    
    def get_line_tructiep(self, cr, start_date, end_date, times, company_id):
        query = '''
            select * from fin_luuhuyen_tiente_tructiep_report('%s', '%s', '%s', %s)
        ''' %(start_date, end_date, times, company_id)
        cr.execute(query)
        return cr.dictfetchall()
    
    def init(self, cr):
        self.fin_luuhuyen_tiente_tructiep_data(cr)
        self.fin_get_doi_ung_lctt(cr)
        self.fin_get_accumulated_lctt(cr)
        self.fin_get_tru_doi_ung_lctt(cr)
        self.fin_get_balance_all_lctt(cr)
        self.fin_luuhuyen_tiente_tructiep_report(cr)
        cr.commit()
        return True


    def fin_get_balance_all_lctt(self,cr):
        sql = '''
        DROP FUNCTION IF EXISTS fin_get_balance_all_lctt(date, date, text, character varying, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_get_balance_all_lctt(date, date, text, character varying, integer)
          RETURNS numeric AS
        $BODY$
        DECLARE
            rec        record;
            lst_account    text = '';
            bal_dr    numeric = 0;
            bal_cr    numeric = 0;
        BEGIN
            lst_account = fin_get_array_accountid($3);
            
            if lst_account <> '' then
                for rec in execute '
                        select  sum(aml.debit) balance_dr, sum(aml.credit) balance_cr
                        from account_move amh left join account_move_line aml 
                                on amh.id = aml.move_id
                            left join account_journal ajn on aml.journal_id = ajn.id
                        where amh.state = ''posted'' and aml.state = ''valid''
                            and ajn.type = ''situation'' and aml.account_id in ('||lst_account||')
                            and date_trunc(''year'', aml.date) = date_trunc(''year'', date($1))
                            and amh.company_id = $3
                        union all
                        select  sum(aml.debit) balance_dr, sum(aml.credit) balance_cr
                        from account_move amh left join account_move_line aml 
                                on amh.id = aml.move_id
                            left join account_journal ajn on aml.journal_id = ajn.id
                        where amh.state = ''posted'' and aml.state = ''valid''
                            and ajn.type != ''situation'' and aml.account_id in ('||lst_account||')
                            and date_trunc(''day'', aml.date) between date_trunc(''year'', date($1))
                            and date($2)
                            and amh.company_id = $3' using $1, $2, $5
                loop
                    bal_dr = bal_dr + coalesce(rec.balance_dr, 0);
                    bal_cr = bal_cr + coalesce(rec.balance_cr, 0);
                end loop;
            else
                bal_dr = 0;
                bal_cr = 0;
            end if;
            
            if $4 = 'dr' then
                return (bal_dr - bal_cr);
            else
                return (bal_cr - bal_dr);
            end if;
            
        END;$BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION fin_get_balance_all_lctt(date, date, text, character varying, integer)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True

    def fin_luuhuyen_tiente_tructiep_data(self, cr):
        sql = '''
            DROP TYPE IF EXISTS fin_luuhuyen_tiente_tructiep_data CASCADE;
            commit;
        '''
        cr.execute(sql)
        cr.execute("select exists (select 1 from pg_type where typname = 'fin_luuhuyen_tiente_tructiep_data')")
        res = cr.fetchone()
        if res and res[0]:
            cr.execute('''delete from pg_type where typname = 'fin_luuhuyen_tiente_tructiep_data';
                            delete from pg_class where relname='fin_luuhuyen_tiente_tructiep_data';
                            commit;''')
        sql = '''
        CREATE TYPE fin_luuhuyen_tiente_tructiep_data AS
           (prior_amt01 numeric,
            curr_amt01 numeric,
            prior_amt02 numeric,
            curr_amt02 numeric,
            prior_amt03 numeric,
            curr_amt03 numeric,
            prior_amt04 numeric,
            curr_amt04 numeric,
            prior_amt05 numeric,
            curr_amt05 numeric,
            prior_amt06 numeric,
            curr_amt06 numeric,
            prior_amt07 numeric,
            curr_amt07 numeric,
            prior_amt20 numeric,
            curr_amt20 numeric,
            prior_amt21 numeric,
            curr_amt21 numeric,
            prior_amt22 numeric,
            curr_amt22 numeric,
            prior_amt23 numeric,
            curr_amt23 numeric,
            prior_amt24 numeric,
            curr_amt24 numeric,
            prior_amt25 numeric,
            curr_amt25 numeric,
            prior_amt26 numeric,
            curr_amt26 numeric,
            prior_amt27 numeric,
            curr_amt27 numeric,
            prior_amt30 numeric,
            curr_amt30 numeric,
            prior_amt31 numeric,
            curr_amt31 numeric,
            prior_amt32 numeric,
            curr_amt32 numeric,
            prior_amt33 numeric,
            curr_amt33 numeric,
            prior_amt34 numeric,
            curr_amt34 numeric,
            prior_amt35 numeric,
            curr_amt35 numeric,
            prior_amt36 numeric,
            curr_amt36 numeric,
            prior_amt40 numeric,
            curr_amt40 numeric,
            prior_amt50 numeric,
            curr_amt50 numeric,
            prior_amt60 numeric,
            curr_amt60 numeric,
            prior_amt61 numeric,
            curr_amt61 numeric,
            prior_amt70 numeric,
            curr_amt70 numeric);
        ALTER TYPE fin_luuhuyen_tiente_tructiep_data
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True

    def fin_get_accumulated_lctt(self,cr):#lay luy ke no hoac co cua nhug tai khoan trong $3
        sql = '''
        DROP FUNCTION IF EXISTS fin_get_accumulated_lctt(date, date, text, character varying, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_get_accumulated_lctt(date, date, text, character varying, integer)
          RETURNS numeric AS
        $BODY$
        DECLARE
            rec        record;
            lst_account    text = '';
            bal_dr    numeric = 0;
            bal_cr    numeric = 0;
        BEGIN
            lst_account = fin_get_array_accountid($3);
            
            if lst_account <> '' then
                for rec in execute '
                        select  sum(aml.debit) balance_dr, sum(aml.credit) balance_cr
                        from account_move amh left join account_move_line aml 
                                on amh.id = aml.move_id
                            left join account_journal ajn on aml.journal_id = ajn.id
                        where amh.state = ''posted'' and aml.state = ''valid''
                            and ajn.type = ''situation'' and aml.account_id in ('||lst_account||')
                            and date_trunc(''year'', aml.date) = date_trunc(''year'', date($1))
                            and amh.company_id = $3
                        union all
                        select  sum(aml.debit) balance_dr, sum(aml.credit) balance_cr
                        from account_move amh left join account_move_line aml 
                                on amh.id = aml.move_id
                            left join account_journal ajn on aml.journal_id = ajn.id
                        where amh.state = ''posted'' and aml.state = ''valid''
                            and ajn.type != ''situation'' and aml.account_id in ('||lst_account||')
                            and date_trunc(''day'', aml.date) between date_trunc(''year'', date($1))
                            and date($2)
                            and amh.company_id = $3' using $1, $2, $5
                
                loop
                    bal_dr = bal_dr + coalesce(rec.balance_dr, 0);
                    bal_cr = bal_cr + coalesce(rec.balance_cr, 0);
                end loop;
            else
                bal_dr = 0;
                bal_cr = 0;
            end if;
            
            if $4 = 'dr' then
                return bal_dr;
            else
                return bal_cr;
            end if;
            
        END;$BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION fin_get_accumulated_lctt(date, date, text, character varying, integer)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
    
    def fin_get_doi_ung_lctt(self,cr):
        #tim nhung account move co line la nhug tai khoan trong $3 va lay doi dung no hoac co cua cac tai khoan trong $4
        #loc lai la hoat dong nao dua vao tieu chi trong $5
        sql = '''
        DROP FUNCTION IF EXISTS fin_get_doi_ung_lctt(date, date, text, text, character varying, character varying, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_get_doi_ung_lctt(date, date, text, text, character varying, character varying, integer)
          RETURNS numeric AS
        $BODY$
        DECLARE
            rec        record;
            rec2        record;
            rec3        record;
            lst_account    text = '';
            lst_account_du    text = '';
            bal_dr    numeric = 0;
            bal_cr    numeric = 0;
        BEGIN
            lst_account = fin_get_array_accountid($3);
            lst_account_du = fin_get_array_accountid($4);
            
            if lst_account <> '' and lst_account_du <> '' then
                for rec in execute '
                    select amh.id
                        from account_move amh left join account_move_line aml 
                                on amh.id = aml.move_id
                            left join account_journal ajn on aml.journal_id = ajn.id
                        where amh.state = ''posted'' and aml.state = ''valid''
                            and ajn.type = ''situation'' and aml.account_id in ('||lst_account||')
                            and date_trunc(''year'', aml.date) = date_trunc(''year'', date($1))
                            and amh.company_id = $3
                        group by amh.id
                    union all
                    select amh.id
                        from account_move amh left join account_move_line aml 
                                on amh.id = aml.move_id
                            left join account_journal ajn on aml.journal_id = ajn.id
                        where amh.state = ''posted'' and aml.state = ''valid''
                            and ajn.type != ''situation'' and aml.account_id in ('||lst_account||')
                            and date_trunc(''day'', aml.date) between date_trunc(''year'', date($1))
                            and date($2)
                            and amh.company_id = $3
                        group by amh.id
                        ' using $1, $2, $7
                
                loop
                    for rec2 in execute '
                        select sum(aml.debit) balance_dr, sum(aml.credit) balance_cr
                        from account_move amh left join account_move_line aml 
                                on amh.id = aml.move_id
                        where aml.account_id in ('||lst_account_du||') and aml.move_id=$1 and type_lctt=$2 
                            ' using rec.id,$5
                    loop
                        bal_dr = bal_dr + coalesce(rec2.balance_dr, 0);
                        bal_cr = bal_cr + coalesce(rec2.balance_cr, 0);
                    end loop;
                end loop;
            else
                bal_dr = 0;
                bal_cr = 0;
            end if;
            
            if $6 = 'dr' then
                return bal_dr;
            else
                return bal_cr;
            end if;
            
        END;$BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION fin_get_doi_ung_lctt(date, date, text, text, character varying, character varying, integer)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
    
#     def fin_get_doi_ung_lctt(self,cr):#tim nhung account move co line la nhug tai khoan trong $3 va lay doi dung no hoac co cua cac tai khoan trong $4
#         sql = '''
#         DROP FUNCTION IF EXISTS fin_get_doi_ung_lctt(date, date, text, text, character varying, integer) CASCADE;
#         commit;
#         
#         CREATE OR REPLACE FUNCTION fin_get_doi_ung_lctt(date, date, text, text, character varying, integer)
#           RETURNS numeric AS
#         $BODY$
#         DECLARE
#             rec        record;
#             rec2        record;
#             rec3        record;
#             lst_account    text = '';
#             lst_account_du    text = '';
#             bal_dr    numeric = 0;
#             bal_cr    numeric = 0;
#         BEGIN
#             lst_account = fin_get_array_accountid($3);
#             lst_account_du = fin_get_array_accountid($4);
#             
#             if lst_account <> '' and lst_account_du <> '' then
#                 for rec in execute '
#                     select amh.id
#                         from account_move amh left join account_move_line aml 
#                                 on amh.id = aml.move_id
#                             join account_journal ajn on aml.journal_id = ajn.id
#                         where amh.state = ''posted'' and aml.state = ''valid''
#                             and ajn.type = ''situation'' and aml.account_id in ('||lst_account||')
#                             and date_trunc(''year'', aml.date) = date_trunc(''year'', date($1))
#                             and amh.company_id = $3
#                         group by amh.id
#                     union all
#                     select amh.id
#                         from account_move amh join account_move_line aml 
#                                 on amh.id = aml.move_id
#                             join account_journal ajn on aml.journal_id = ajn.id
#                         where amh.state = ''posted'' and aml.state = ''valid''
#                             and ajn.type != ''situation'' and aml.account_id in ('||lst_account||')
#                             and date_trunc(''day'', aml.date) between date_trunc(''year'', date($1))
#                             and date($2)
#                             and amh.company_id = $3
#                         group by amh.id
#                         ' using $1, $2, $6
#                 
#                 loop
#                     for rec2 in execute '
#                         select sum(aml.debit) balance_dr, sum(aml.credit) balance_cr
#                         from account_move amh join account_move_line aml 
#                                 on amh.id = aml.move_id
#                         where aml.account_id in ('||lst_account_du||') and aml.move_id=$1
#                             ' using rec.id
#                     loop
#                         bal_dr = bal_dr + coalesce(rec2.balance_dr, 0);
#                         bal_cr = bal_cr + coalesce(rec2.balance_cr, 0);
#                     end loop;
#                 end loop;
#             else
#                 bal_dr = 0;
#                 bal_cr = 0;
#             end if;
#             
#             if $5 = 'dr' then
#                 return bal_dr;
#             else
#                 return bal_cr;
#             end if;
#             
#         END;$BODY$
#           LANGUAGE plpgsql VOLATILE
#           COST 100;
#         ALTER FUNCTION fin_get_doi_ung_lctt(date, date, text, text, character varying, integer)
#           OWNER TO openerp;
#         '''
#         cr.execute(sql)
#         return True

    def fin_get_tru_doi_ung_lctt(self,cr):#tim nhung account move co line la nhug tai khoan trong $3 va doi ung k phai la nhug tai khoan trong $4
        sql = '''
        DROP FUNCTION IF EXISTS fin_get_tru_doi_ung_lctt(date, date, text, text, character varying, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_get_tru_doi_ung_lctt(date, date, text, text, character varying, integer)
          RETURNS numeric AS
        $BODY$
        DECLARE
            rec        record;
            rec2        record;
            rec3        record;
            lst_account    text = '';
            lst_account_du    text = '';
            bal_dr    numeric = 0;
            bal_cr    numeric = 0;
        BEGIN
            lst_account = fin_get_array_accountid($3);
            lst_account_du = fin_get_array_accountid($4);
            
            if lst_account <> '' and lst_account_du <> '' then
                for rec in execute '
                    select amh.id
                        from account_move amh left join account_move_line aml 
                                on amh.id = aml.move_id
                            left join account_journal ajn on aml.journal_id = ajn.id
                        where amh.state = ''posted'' and aml.state = ''valid''
                            and ajn.type = ''situation'' and aml.account_id in ('||lst_account||')
                            and date_trunc(''year'', aml.date) = date_trunc(''year'', date($1))
                            and amh.company_id = $3
                        group by amh.id
                    union all
                    select amh.id
                        from account_move amh left join account_move_line aml 
                                on amh.id = aml.move_id
                            left join account_journal ajn on aml.journal_id = ajn.id
                        where amh.state = ''posted'' and aml.state = ''valid''
                            and ajn.type != ''situation'' and aml.account_id in ('||lst_account||')
                            and date_trunc(''day'', aml.date) between date_trunc(''year'', date($1))
                            and date($2)
                            and amh.company_id = $3
                        group by amh.id
                        ' using $1, $2, $6
                
                loop
                    for rec2 in execute '
                        select case when count(aml.id)!=0 then count(aml.id) else 0 end num_of_amh
                            from account_move_line aml 
                            where aml.account_id in ('||lst_account_du||') and aml.move_id=$1
                            ' using rec.id
                    loop
                        if rec2.num_of_amh=0 then
                            for rec3 in execute '
                                select sum(aml.debit) balance_dr, sum(aml.credit) balance_cr
                                    from account_move amh left join account_move_line aml 
                                            on amh.id = aml.move_id
                                    where aml.account_id in ('||lst_account||') and aml.move_id=$1
                                        ' using rec.id
                            loop
                                bal_dr = bal_dr + coalesce(rec3.balance_dr, 0);
                                bal_cr = bal_cr + coalesce(rec3.balance_cr, 0);
                            end loop;
                        else
                            bal_dr = 0;
                            bal_cr = 0;
                        end if;
                    end loop;
                end loop;
            else
                bal_dr = 0;
                bal_cr = 0;
            end if;
            
            if $5 = 'dr' then
                return bal_dr;
            else
                return bal_cr;
            end if;
            
        END;$BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100;
        ALTER FUNCTION fin_get_tru_doi_ung_lctt(date, date, text, text, character varying, integer)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True

    def fin_luuhuyen_tiente_tructiep_report(self, cr):
        sql = '''
        DROP FUNCTION IF EXISTS fin_luuhuyen_tiente_tructiep_report(date, date, character varying, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_luuhuyen_tiente_tructiep_report(date, date, character varying, integer)
          RETURNS SETOF fin_luuhuyen_tiente_tructiep_data AS
        $BODY$
        DECLARE
            _cur_sdate    alias for $1;
            _cur_edate    alias for $2;
            _type        alias for $3;
            rec_pl        record;
            pl_data        fin_luuhuyen_tiente_tructiep_data%ROWTYPE;
            prior_sdate    date;
            prior_edate    date;
        BEGIN
            select * into prior_sdate,prior_edate from fn_get_prior_rangedate(_cur_sdate, _type);
            RAISE NOTICE 'Prior date range: % - %', prior_sdate, prior_edate;
            
            -- 1. lấy chỉ tiêu 01
            pl_data.prior_amt01 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112', '511 131 121 515', 'cr', 'hdkd', $4);
            pl_data.curr_amt01 = fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112', '511 131 121 515', 'cr', 'hdkd', $4);
            
            -- 2. lấy chỉ tiêu 02
            pl_data.prior_amt02 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112', '331 152 153 154 155 156 157 158 121 623 621 622 627 632 242', 'dr', 'hdkd', $4);
            pl_data.curr_amt02 = -1*fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112', '331 152 153 154 155 156 157 158 121 623 621 622 627 632 242', 'dr', 'hdkd', $4);
            
            -- 3. lấy chỉ tiêu 03
            pl_data.prior_amt03 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112', '334', 'dr', 'hdkd', $4);
            pl_data.curr_amt03 =  -1*fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112', '334', 'dr', 'hdkd', $4);
            
            -- 4. lấy chỉ tiêu 04 -> có dấu ... là còn thêm tài khoản khác nữa hay đã hết?
            pl_data.prior_amt04 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '635 335 242', 'dr', 'hdkd', $4);
            pl_data.curr_amt04 =  -1*fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '635 335 242', 'dr', 'hdkd', $4);
                                
            -- 5. lấy chỉ tiêu 05
            pl_data.prior_amt05 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '3334', 'dr', 'hdkd', $4);
            pl_data.curr_amt05 =  -1*fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '3334', 'dr', 'hdkd', $4);
            
            -- 6. lấy chỉ tiêu 06
            pl_data.prior_amt06 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112', '711 133 141 244 1381 1388 333 136 336', 'cr', 'hdkd', $4);
            pl_data.curr_amt06 =  fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112', '711 133 141 244 1381 1388 333 136 336', 'cr', 'hdkd', $4);
            
            -- 7. lấy chỉ tiêu 07 -> có dấu ... là còn thêm tài khoản khác nữa hay đã hết?
            pl_data.prior_amt07 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112', '811 161 244 333 338 334 352 353 356 136 336', 'hdkd', 'dr', $4);
            pl_data.curr_amt07 =  -1*fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112', '811 161 244 333 338 334 352 353 356 136 336', 'hdkd', 'dr', $4);
            
            -- 8. lấy chỉ tiêu 20
            pl_data.prior_amt20 = pl_data.prior_amt01 + pl_data.prior_amt02 + pl_data.prior_amt03 + pl_data.prior_amt04 + pl_data.prior_amt05 + pl_data.prior_amt06 + pl_data.prior_amt07;
            pl_data.curr_amt20 = pl_data.curr_amt01 + pl_data.curr_amt02 + pl_data.curr_amt03 + pl_data.curr_amt04 + pl_data.curr_amt05 + pl_data.curr_amt06 + pl_data.curr_amt07;
            
            -- 9. lấy chỉ tiêu 21 -> có dấu ... là còn thêm tài khoản khác nữa hay đã hết?
            pl_data.prior_amt21 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '211 213 217 241 331 152 153 635 242 244 334 623 338 1388 1381', 'hddt', 'dr', $4);
            pl_data.curr_amt21 =  -1*fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '211 213 217 241 331 152 153 635 242 244 334 623 338 1388 1381', 'hddt', 'dr', $4);
                                
            -- 10. lấy chỉ tiêu 22
            pl_data.prior_amt22 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '5117 711 131', 'cr', 'hddt', $4) -
                                fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '811 632', 'dr', 'hddt', $4);
            pl_data.curr_amt22 =  fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '5117 711 131', 'cr', 'hddt', $4) -
                                fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '811 632', 'dr', 'hddt', $4);
                                
            -- 11. lấy chỉ tiêu 23 -> trừ 12811 và 12881
            pl_data.prior_amt23 = -1*(fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '128 171', 'dr', 'hddt', $4) -
                                    fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '12811 12881', 'dr', 'hddt', $4));
            pl_data.curr_amt23 =  -1*(fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '128 171', 'dr', 'hddt', $4) -
                                    fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '12811 12881', 'dr', 'hddt', $4));
            
            -- 12. lấy chỉ tiêu 24 -> trừ 12811 và 12881
            pl_data.prior_amt24 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '128 171', 'cr', 'hddt', $4) -
                                    fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '12811 12881', 'cr', 'hddt', $4);
            pl_data.curr_amt24 =  fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '128 171', 'cr', 'hddt', $4) -
                                    fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '12811 12881', 'cr', 'hddt', $4);
            
            -- 13. lấy chỉ tiêu 25
            pl_data.prior_amt25 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '221 222 2281 2288 331', 'dr', 'hddt', $4);
            pl_data.curr_amt25 =  -1*fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '221 222 2281 2288 331', 'dr', 'hddt', $4);
            
            -- 14. lấy chỉ tiêu 26
            pl_data.prior_amt26 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '221 222 2281 2288 331', 'cr', 'hddt', $4);
            pl_data.curr_amt26 =  fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '221 222 2281 2288 331', 'cr', 'hddt', $4);
            
            -- 15. lấy chỉ tiêu 27
            pl_data.prior_amt27 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '515', 'cr', 'hddt', $4);
            pl_data.curr_amt27 =  fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '515', 'cr', 'hddt', $4);
            
            -- 16. lấy chỉ tiêu 30
            pl_data.prior_amt30 = pl_data.prior_amt21 + pl_data.prior_amt22 + pl_data.prior_amt23 + pl_data.prior_amt24 + pl_data.prior_amt25 + pl_data.prior_amt26 + pl_data.prior_amt27;
            pl_data.curr_amt30 =  pl_data.curr_amt21 + pl_data.curr_amt22 + pl_data.curr_amt23 + pl_data.curr_amt24 + pl_data.curr_amt25 + pl_data.curr_amt26 + pl_data.curr_amt27;
            
            -- 17. lấy chỉ tiêu 31
            pl_data.prior_amt31 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '411 419 1385', 'cr', 'hdtc', $4) -
                                    fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '41112', 'cr', 'hdtc', $4);
            pl_data.curr_amt31 =  fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '411 419 1385', 'cr', 'hdtc', $4) -
                                    fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '41112', 'cr', 'hdtc', $4);
            
            -- 18. lấy chỉ tiêu 32
            pl_data.prior_amt32 = -1*(fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '411 419 1385', 'dr', 'hdtc', $4) -
                                        fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '41112', 'dr', 'hdtc', $4));
            pl_data.curr_amt32 =  -1*(fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '411 419 1385', 'dr', 'hdtc', $4) -
                                        fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '41112', 'dr', 'hdtc', $4));
            
            -- 19. lấy chỉ tiêu 33
            pl_data.prior_amt33 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '171 3411 3431 3432 41112', 'cr', 'hdtc', $4);
            pl_data.curr_amt33 =  fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '171 3411 3431 3432 41112', 'cr', 'hdtc', $4);
                                
            -- 20. lấy chỉ tiêu 34
            pl_data.prior_amt34 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '171 3411 3431 3432 41112', 'dr', 'hdtc', $4);
            pl_data.curr_amt34 =  -1*fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '171 3411 3431 3432 41112', 'dr', 'hdtc', $4);
                                
            -- 21. lấy chỉ tiêu 35
            pl_data.prior_amt35 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '3412', 'dr', 'hdtc', $4);
            pl_data.curr_amt35 =  -1*fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '3412', 'dr', 'hdtc', $4);
                                
            -- 22. lấy chỉ tiêu 36
            pl_data.prior_amt36 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '421 3385', 'dr', 'hdtc', $4);
            pl_data.curr_amt36 =  -1*fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '111 112 113', '421 3385', 'dr', 'hdtc', $4);
            
            -- 23. lấy chỉ tiêu 40
            pl_data.prior_amt40 = pl_data.prior_amt31 + pl_data.prior_amt32 + pl_data.prior_amt33 + pl_data.prior_amt34 + pl_data.prior_amt35 + pl_data.prior_amt36;
            pl_data.curr_amt40 =  pl_data.curr_amt31 + pl_data.curr_amt32 + pl_data.curr_amt33 + pl_data.curr_amt34 + pl_data.curr_amt35 + pl_data.curr_amt36;
            
            -- 24. lấy chỉ tiêu 50
            pl_data.prior_amt50 = pl_data.prior_amt20 + pl_data.prior_amt30 + pl_data.prior_amt40;
            pl_data.curr_amt50 =  pl_data.curr_amt20 + pl_data.curr_amt30 + pl_data.curr_amt40;
            
            -- 25. lấy chỉ tiêu 60
            pl_data.prior_amt60 = fin_get_balance_all_lctt(prior_sdate, prior_edate, '111 112 113', 'dr', $4) +
                                fin_get_balance_all_lctt(prior_sdate, prior_edate, '12811 12881', 'dr', $4);
            pl_data.curr_amt60 =  fin_get_balance_all_lctt(_cur_sdate, _cur_edate, '111 112 113', 'dr', $4) +
                                fin_get_balance_all_lctt(_cur_sdate, _cur_edate, '12811 12881', 'dr', $4);
            
            -- 26. lấy chỉ tiêu 61
            pl_data.prior_amt61 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '4131', 'cr', 'hdtc', $4);
            if pl_data.prior_amt61=0 then
                pl_data.prior_amt61 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '4131', 'dr', 'hdtc', $4);
            end if;
            pl_data.curr_amt61 =  fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '4131', 'cr', 'hdtc', $4);
            if pl_data.curr_amt61=0 then
                pl_data.curr_amt61 =  -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '111 112 113', '4131', 'dr', 'hdtc', $4);
            end if;
            
            -- 27. lấy chỉ tiêu 70
            pl_data.prior_amt70 = pl_data.prior_amt50 + pl_data.prior_amt60 + pl_data.prior_amt61;
            pl_data.curr_amt70 =  pl_data.curr_amt50 + pl_data.curr_amt60 + pl_data.curr_amt61;
            
            return next pl_data;
            return;
        END; $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100
          ROWS 1000;
        ALTER FUNCTION fin_luuhuyen_tiente_tructiep_report(date, date, character varying, integer)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
# Function su dung cach cu
#     def fin_luuhuyen_tiente_tructiep_report(self, cr):
#         sql = '''
#         DROP FUNCTION IF EXISTS fin_luuhuyen_tiente_tructiep_report(date, date, character varying, integer) CASCADE;
#         commit;
#         
#         CREATE OR REPLACE FUNCTION fin_luuhuyen_tiente_tructiep_report(date, date, character varying, integer)
#           RETURNS SETOF fin_luuhuyen_tiente_tructiep_data AS
#         $BODY$
#         DECLARE
#             _cur_sdate    alias for $1;
#             _cur_edate    alias for $2;
#             _type        alias for $3;
#             rec_pl        record;
#             pl_data        fin_luuhuyen_tiente_tructiep_data%ROWTYPE;
#             prior_sdate    date;
#             prior_edate    date;
#         BEGIN
#             select * into prior_sdate,prior_edate from fn_get_prior_rangedate(_cur_sdate, _type);
#             RAISE NOTICE 'Prior date range: % - %', prior_sdate, prior_edate;
#             
#             -- 1. lấy chỉ tiêu 01
#             pl_data.prior_amt01 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '131', '111 112', 'dr', $4) +
#                                 fin_get_doi_ung_lctt(prior_sdate, prior_edate, '5111 5112 5113 333 121 515', '111 112', 'dr', $4) +
#                                 fin_get_tru_doi_ung_lctt(prior_sdate, prior_edate, '131', '111 112', 'cr', $4) +
#                                 fin_get_tru_doi_ung_lctt(prior_sdate, prior_edate, '5111 5112 5113 333 121 515', '111 112 131 138', 'cr', $4);
#             pl_data.curr_amt01 = fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '131', '111 112', 'dr', $4) +
#                                 fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '5111 5112 5113 333 121 515', '111 112', 'dr', $4) +
#                                 fin_get_tru_doi_ung_lctt(_cur_sdate, _cur_edate, '131', '111 112', 'cr', $4) +
#                                 fin_get_tru_doi_ung_lctt(_cur_sdate, _cur_edate, '5111 5112 5113 333 121 515', '111 112 131 138', 'cr', $4);
#             
#             -- 2. lấy chỉ tiêu 02
#             pl_data.prior_amt02 = -1*(fin_get_doi_ung_lctt(prior_sdate, prior_edate, '151 152 153 156 133 627 641 642 133 121', '111 112', 'cr', $4) +
#                                 fin_get_doi_ung_lctt(prior_sdate, prior_edate, '331', '111 112', 'cr', $4) +
#                                 fin_get_tru_doi_ung_lctt(prior_sdate, prior_edate, '331', '111 112', 'dr', $4) +
#                                 fin_get_tru_doi_ung_lctt(prior_sdate, prior_edate, '151 152 153 156 133 627 641 642 133 121', '111 112 331', 'dr', $4));
#             pl_data.curr_amt02 = -1*(fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '151 152 153 156 133 627 641 642 133 121', '111 112', 'cr', $4) +
#                                 fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '331', '111 112', 'cr', $4) +
#                                 fin_get_tru_doi_ung_lctt(_cur_sdate, _cur_edate, '331', '111 112', 'dr', $4) +
#                                 fin_get_tru_doi_ung_lctt(_cur_sdate, _cur_edate, '151 152 153 156 133 627 641 642 133 121', '111 112 331', 'dr', $4));
#             
#             -- 3. lấy chỉ tiêu 03
#             pl_data.prior_amt03 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '334', '111 112', 'cr', $4);
#             pl_data.curr_amt03 =  -1*fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '334', '111 112', 'cr', $4);
#             
#             -- 4. lấy chỉ tiêu 04
#             pl_data.prior_amt04 = -1*(fin_get_doi_ung_lctt(prior_sdate, prior_edate, '635 242 335', '111 112', 'cr', $4) +
#                                 fin_get_tru_doi_ung_lctt(prior_sdate, prior_edate, '635 242 335', '111 112', 'dr', $4));
#             pl_data.curr_amt04 =  -1*(fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '635 242 335', '111 112', 'cr', $4) +
#                                 fin_get_tru_doi_ung_lctt(_cur_sdate, _cur_edate, '635 242 335', '111 112', 'dr', $4));
#                                 
#             -- 5. lấy chỉ tiêu 05
#             pl_data.prior_amt05 = -1*(fin_get_doi_ung_lctt(prior_sdate, prior_edate, '3334', '111 112', 'cr', $4) +
#                                 fin_get_tru_doi_ung_lctt(prior_sdate, prior_edate, '3334', '111 112', 'dr', $4));
#             pl_data.curr_amt05 =  -1*(fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '3334', '111 112', 'cr', $4) +
#                                 fin_get_tru_doi_ung_lctt(_cur_sdate, _cur_edate, '3334', '111 112', 'dr', $4));
#             
#             -- 6. lấy chỉ tiêu 06 hỏi lại
#             pl_data.prior_amt06 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '711 133 141 334 244 461 414 353', '111 112', 'dr', $4);
#             pl_data.curr_amt06 =  fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '711 133 141 334 244 461 414 353', '111 112', 'dr', $4);
#             
#             -- 7. lấy chỉ tiêu 07 hỏi lại
#             pl_data.prior_amt07 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '811 161 244 3331 3332 3333 3335 3336 3337 3338 3339 338 334 352 353 356', '111 112', 'cr', $4);
#             pl_data.curr_amt07 =  -1*fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '811 161 244 3331 3332 3333 3335 3336 3337 3338 3339 338 334 352 353 356', '111 112', 'cr', $4);
#             
#             -- 8. lấy chỉ tiêu 20
#             pl_data.prior_amt20 = pl_data.prior_amt01 + pl_data.prior_amt02 + pl_data.prior_amt03 + pl_data.prior_amt04 + pl_data.prior_amt05 + pl_data.prior_amt06 + pl_data.prior_amt07;
#             pl_data.curr_amt20 = pl_data.curr_amt01 + pl_data.curr_amt02 + pl_data.curr_amt03 + pl_data.curr_amt04 + pl_data.curr_amt05 + pl_data.curr_amt06 + pl_data.curr_amt07;
#             
#             -- 9. lấy chỉ tiêu 21
#             pl_data.prior_amt21 = -1*(fin_get_doi_ung_lctt(prior_sdate, prior_edate, '211 212 213 217 241 133 331', '111 112', 'cr', $4) +
#                                 fin_get_tru_doi_ung_lctt(prior_sdate, prior_edate, '211 212 213 217 241 133 331', '111 112', 'dr', $4));
#             pl_data.curr_amt21 =  -1*(fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '211 212 213 217 241 133 331', '111 112', 'cr', $4) +
#                                 fin_get_tru_doi_ung_lctt(_cur_sdate, _cur_edate, '211 212 213 217 241 133 331', '111 112', 'dr', $4));
#                                 
#             -- 10. lấy chỉ tiêu 22
#             pl_data.prior_amt22 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '711 5117 131', '111 112 113', 'dr', $4) -
#                                 fin_get_doi_ung_lctt(prior_sdate, prior_edate, '811 632', '111 112 113', 'cr', $4);
#             pl_data.curr_amt22 =  fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '711 5117 131', '111 112 113', 'dr', $4) -
#                                 fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '811 632', '111 112 113', 'cr', $4);
#                                 
#             -- 11. lấy chỉ tiêu 23
#             pl_data.prior_amt23 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '128 171', '111 112', 'cr', $4);
#             pl_data.curr_amt23 =  -1*fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '128 171', '111 112', 'cr', $4);
#             
#             -- 12. lấy chỉ tiêu 24
#             pl_data.prior_amt24 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '128 171', '111 112', 'dr', $4);
#             pl_data.curr_amt24 =  fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '128 171', '111 112', 'dr', $4);
#             
#             -- 13. lấy chỉ tiêu 25
#             pl_data.prior_amt25 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '221 222 2281 331', '111 112', 'cr', $4);
#             pl_data.curr_amt25 =  -1*fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '221 222 2281 331', '111 112', 'cr', $4);
#             
#             -- 14. lấy chỉ tiêu 26
#             pl_data.prior_amt26 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '221 222 2281 131', '111 112', 'dr', $4);
#             pl_data.curr_amt26 =  fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '221 222 2281 131', '111 112', 'dr', $4);
#             
#             -- 15. lấy chỉ tiêu 27
#             pl_data.prior_amt27 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '515', '111 112', 'dr', $4);
#             pl_data.curr_amt27 =  fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '515', '111 112', 'dr', $4);
#             
#             -- 16. lấy chỉ tiêu 30
#             pl_data.prior_amt30 = pl_data.prior_amt21 + pl_data.prior_amt22 + pl_data.prior_amt23 + pl_data.prior_amt24 + pl_data.prior_amt25 + pl_data.prior_amt26 + pl_data.prior_amt27;
#             pl_data.curr_amt30 =  pl_data.curr_amt21 + pl_data.curr_amt22 + pl_data.curr_amt23 + pl_data.curr_amt24 + pl_data.curr_amt25 + pl_data.curr_amt26 + pl_data.curr_amt27;
#             
#             -- 17. lấy chỉ tiêu 31
#             pl_data.prior_amt31 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '411', '111 112', 'dr', $4);
#             pl_data.curr_amt31 =  fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '411', '111 112', 'dr', $4);
#             
#             -- 18. lấy chỉ tiêu 32
#             pl_data.prior_amt32 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '411 419', '111 112', 'cr', $4);
#             pl_data.curr_amt32 =  -1*fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '411 419', '111 112', 'cr', $4);
#             
#             -- 19. lấy chỉ tiêu 33
#             pl_data.prior_amt33 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '171 3411 3431 3432 343', '111 112', 'dr', $4) +
#                                 fin_get_tru_doi_ung_lctt(prior_sdate, prior_edate, '343', '111 112', 'cr', $4);
#             pl_data.curr_amt33 =  fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '171 3411 3431 3432 343', '111 112', 'dr', $4) +
#                                 fin_get_tru_doi_ung_lctt(_cur_sdate, _cur_edate, '343', '111 112', 'cr', $4);
#                                 
#             -- 20. lấy chỉ tiêu 34
#             pl_data.prior_amt34 = -1*(fin_get_doi_ung_lctt(prior_sdate, prior_edate, '171 3411 3431 3432', '111 112', 'cr', $4) +
#                                 fin_get_tru_doi_ung_lctt(prior_sdate, prior_edate, '171 3411 3431 3432', '111 112', 'dr', $4));
#             pl_data.curr_amt34 =  -1*(fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '171 3411 3431 3432', '111 112', 'cr', $4) +
#                                 fin_get_tru_doi_ung_lctt(_cur_sdate, _cur_edate, '171 3411 3431 3432', '111 112', 'dr', $4));
#                                 
#             -- 21. lấy chỉ tiêu 35
#             pl_data.prior_amt35 = -1*(fin_get_doi_ung_lctt(prior_sdate, prior_edate, '3412', '111 112', 'cr', $4) +
#                                 fin_get_tru_doi_ung_lctt(prior_sdate, prior_edate, '3412', '111 112', 'dr', $4));
#             pl_data.curr_amt35 =  -1*(fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '3412', '111 112', 'cr', $4) +
#                                 fin_get_tru_doi_ung_lctt(_cur_sdate, _cur_edate, '3412', '111 112', 'dr', $4));
#                                 
#             -- 22. lấy chỉ tiêu 36
#             pl_data.prior_amt36 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '421 3388', '111 112', 'cr', $4);
#             pl_data.curr_amt36 =  -1*fin_get_doi_ung_lctt(_cur_sdate, _cur_edate, '421 3388', '111 112', 'cr', $4);
#             
#             -- 23. lấy chỉ tiêu 40
#             pl_data.prior_amt40 = pl_data.prior_amt31 + pl_data.prior_amt32 + pl_data.prior_amt33 + pl_data.prior_amt34 + pl_data.prior_amt35 + pl_data.prior_amt36;
#             pl_data.curr_amt40 =  pl_data.curr_amt31 + pl_data.curr_amt32 + pl_data.curr_amt33 + pl_data.curr_amt34 + pl_data.curr_amt35 + pl_data.curr_amt36;
#             
#             -- 24. lấy chỉ tiêu 50
#             pl_data.prior_amt50 = pl_data.prior_amt20 + pl_data.prior_amt30 + pl_data.prior_amt40;
#             pl_data.curr_amt50 =  pl_data.curr_amt20 + pl_data.curr_amt30 + pl_data.curr_amt40;
#             
#             -- 25. lấy chỉ tiêu 60
#             pl_data.prior_amt60 = fin_get_balance_all_lctt(prior_sdate, prior_edate, '111 112 113', 'dr', $4) +
#                                 fin_get_balance_all_lctt(prior_sdate, prior_edate, '1281 1288', 'dr', $4);
#             pl_data.curr_amt60 =  fin_get_balance_all_lctt(_cur_sdate, _cur_edate, '111 112 113', 'dr', $4) +
#                                 fin_get_balance_all_lctt(_cur_sdate, _cur_edate, '1281 1288', 'dr', $4);
#             
#             -- 26. lấy chỉ tiêu 61
#             pl_data.prior_amt61 = fin_get_doi_ung_lctt(prior_sdate, prior_edate, '4131', '1112 1122', 'dr', $4);
#             if pl_data.prior_amt61=0 then
#                 pl_data.prior_amt61 = -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '4131', '1112 1122', 'cr', $4);
#             end if;
#             pl_data.curr_amt61 =  fin_get_doi_ung_lctt(prior_sdate, prior_edate, '4131', '1112 1122', 'dr', $4);
#             if pl_data.curr_amt61=0 then
#                 pl_data.curr_amt61 =  -1*fin_get_doi_ung_lctt(prior_sdate, prior_edate, '4131', '1112 1122', 'cr', $4);
#             end if;
#             
#             -- 27. lấy chỉ tiêu 70
#             pl_data.prior_amt70 = pl_data.prior_amt50 + pl_data.prior_amt60 + pl_data.prior_amt61;
#             pl_data.curr_amt70 =  pl_data.curr_amt50 + pl_data.curr_amt60 + pl_data.curr_amt61;
#             
#             return next pl_data;
#             return;
#         END; $BODY$
#           LANGUAGE plpgsql VOLATILE
#           COST 100
#           ROWS 1000;
#         ALTER FUNCTION fin_luuhuyen_tiente_tructiep_report(date, date, character varying, integer)
#           OWNER TO openerp;
#         '''
#         cr.execute(sql)
#         return True

sql_luuhuyen_tiente()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
