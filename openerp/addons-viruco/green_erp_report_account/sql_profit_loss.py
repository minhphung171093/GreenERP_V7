# -*- coding: utf-8 -*-
# #############################################################################
# 
# #############################################################################
import tools
from osv import fields, osv
from tools.translate import _

class sql_profit_loss(osv.osv):
    _name = "sql.profit.loss"
    _auto = False
    
    def get_line(self, cr, start_date, end_date, times, company_id):
        query = '''
            select * from fin_profit_loss_report('%s', '%s', '%s', %s)
        ''' %(start_date, end_date, times, company_id)
        cr.execute(query)
        return cr.dictfetchall()
    
    def init(self, cr):
        self.fin_get_balance_all_pl(cr)
        self.fin_profit_loss_data(cr)
        self.fin_get_account_data(cr)
        self.fin_profit_loss_report(cr)
        self.fin_get_accumulated(cr)
        self.fin_get_doi_ung(cr)
        
        cr.commit()
        return True
    
    def fin_profit_loss_data(self, cr):
        cr.execute("select exists (select 1 from pg_type where typname = 'fin_profit_loss_data')")
        res = cr.fetchone()
        if res and res[0]:
            cr.execute('''delete from pg_type where typname = 'fin_profit_loss_data';
                            delete from pg_class where relname='fin_profit_loss_data';
                            commit;''')
        sql = '''
        CREATE TYPE fin_profit_loss_data AS
           (prior_amt1 numeric,
            curr_amt1 numeric,
            prior_amt2 numeric,
            curr_amt2 numeric,
            prior_amt3 numeric,
            curr_amt3 numeric,
            prior_amt4 numeric,
            curr_amt4 numeric,
            prior_amt5 numeric,
            curr_amt5 numeric,
            prior_amt6 numeric,
            curr_amt6 numeric,
            prior_amt7 numeric,
            curr_amt7 numeric,
            prior_amt8 numeric,
            curr_amt8 numeric,
            prior_amt9 numeric,
            curr_amt9 numeric,
            prior_amt10 numeric,
            curr_amt10 numeric,
            prior_amt11 numeric,
            curr_amt11 numeric,
            prior_amt12 numeric,
            curr_amt12 numeric,
            prior_amt13 numeric,
            curr_amt13 numeric,
            prior_amt14 numeric,
            curr_amt14 numeric,
            prior_amt15 numeric,
            curr_amt15 numeric,
            prior_amt16 numeric,
            curr_amt16 numeric,
            prior_amt17 numeric,
            curr_amt17 numeric,
            prior_amt18 numeric,
            curr_amt18 numeric,
            prior_amt71 numeric,
            curr_amt71 numeric);
        ALTER TYPE fin_profit_loss_data
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
    
    def fin_get_account_data(self, cr):
#         cr.execute("select exists (select 1 from pg_proc where proname = 'fin_get_account_data')")
#         res = cr.fetchone()
#         if res and res[0]:
#             return True
        sql = '''
        DROP FUNCTION IF EXISTS fin_get_account_data(IN date, IN date, IN integer, IN integer, IN integer) CASCADE;
        commit;
         
        CREATE OR REPLACE FUNCTION fin_get_account_data(IN date, IN date, IN integer, IN integer, IN integer)
          RETURNS TABLE(dr_amount numeric, cr_amount numeric) AS
        $BODY$
            select sum(aml.debit), sum(aml.credit)
            from account_move amh left join account_move_line aml 
                    on amh.id = aml.move_id
                    and amh.state = 'posted' and aml.state = 'valid'
                    and date(aml.date) between date($1::date) and date($2::date)
                left join account_regularization arh
                    on amh.regularization_id = arh.id
                left join account_regularization_rel rel on arh.id = rel.regularization_id
            where aml.account_id <> arh.debit_account_id and arh.sequence >= $3 and arh.sequence <= $4
                and amh.company_id = $5
        $BODY$
          LANGUAGE sql VOLATILE
          COST 100
          ROWS 1000;
        ALTER FUNCTION fin_get_account_data(date, date, integer, integer, integer)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
    
    def fin_get_balance_all_pl(self,cr):
        sql = '''
        DROP FUNCTION IF EXISTS fin_get_balance_all_pl(date, date, text, character varying, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_get_balance_all_pl(date, date, text, character varying, integer)
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
        ALTER FUNCTION fin_get_balance_all_pl(date, date, text, character varying, integer)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
    
    def fin_get_accumulated(self,cr):
        sql = '''
        DROP FUNCTION IF EXISTS fin_get_accumulated(date, date, text, character varying, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_get_accumulated(date, date, text, character varying, integer)
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
        ALTER FUNCTION fin_get_accumulated(date, date, text, character varying, integer)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True
    
    def fin_get_doi_ung(self,cr):
        sql = '''
        DROP FUNCTION IF EXISTS fin_get_doi_ung(date, date, text, text, character varying, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_get_doi_ung(date, date, text, text, character varying, integer)
          RETURNS numeric AS
        $BODY$
        DECLARE
            rec        record;
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
                    for rec in execute '
                        select sum(aml.debit) balance_dr, sum(aml.credit) balance_cr
                        from account_move amh left join account_move_line aml 
                                on amh.id = aml.move_id
                        where aml.account_id in ('||lst_account_du||') and aml.move_id=$1
                            ' using rec.id
                    loop
                        bal_dr = bal_dr + coalesce(rec.balance_dr, 0);
                        bal_cr = bal_cr + coalesce(rec.balance_cr, 0);
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
        ALTER FUNCTION fin_get_doi_ung(date, date, text, text, character varying, integer)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True

    def fin_profit_loss_report(self, cr):
#         cr.execute("select exists (select 1 from pg_proc where proname = 'fin_profit_loss_report')")
#         res = cr.fetchone()
#         if res and res[0]:
#             return True
        sql = '''
        DROP FUNCTION IF EXISTS fin_profit_loss_report(date, date, character varying, integer) CASCADE;
        commit;
        
        CREATE OR REPLACE FUNCTION fin_profit_loss_report(date, date, character varying, integer)
          RETURNS SETOF fin_profit_loss_data AS
        $BODY$
        DECLARE
            _cur_sdate    alias for $1;
            _cur_edate    alias for $2;
            _type        alias for $3;
            rec_pl        record;
            pl_data        fin_profit_loss_data%ROWTYPE;
            prior_sdate    date;
            prior_edate    date;
        BEGIN
            select * into prior_sdate,prior_edate from fn_get_prior_rangedate(_cur_sdate, _type);
            RAISE NOTICE 'Prior date range: % - %', prior_sdate, prior_edate;
            
            -- chỉ tiêu 1,2,3 (doanh thu 511)
            
            -- 1. lấy chỉ tiêu 01 MS 01
            pl_data.prior_amt1 = fin_get_accumulated(prior_sdate, prior_edate, '511', 'cr', $4);
            pl_data.curr_amt1 = fin_get_accumulated(_cur_sdate, _cur_edate, '511', 'cr', $4);
            
            -- 2. lấy chỉ tiêu 02 MS 02
            pl_data.prior_amt2 = fin_get_doi_ung(prior_sdate, prior_edate, '511', '521', 'cr', $4);
            pl_data.curr_amt2 = fin_get_doi_ung(_cur_sdate, _cur_edate, '511', '521', 'cr', $4);
            
            -- 3. lấy chỉ tiêu 03 MS 10
            pl_data.prior_amt3 = pl_data.prior_amt1 - pl_data.prior_amt2 ;
            pl_data.curr_amt3 = pl_data.curr_amt1 - pl_data.curr_amt2;
            
            -- 4. lấy chỉ tiêu 04 (giá vốn 632) MS 11
            pl_data.prior_amt4 = fin_get_doi_ung(prior_sdate, prior_edate, '632', '911', 'dr', $4);
            pl_data.curr_amt4 = fin_get_doi_ung(_cur_sdate, _cur_edate, '632', '911', 'dr', $4);
            
            -- 5. tính chỉ tiêu 05 (lợi nhuận gộp) MS 20 = 10 - 11 
            pl_data.prior_amt5 = pl_data.prior_amt3 - pl_data.prior_amt4;
            pl_data.curr_amt5 = pl_data.curr_amt3 - pl_data.curr_amt4;
            
            -- 6. lấy chỉ tiêu 06 (doanh thu tai chinh 515) MS 21
            pl_data.prior_amt6 = fin_get_doi_ung(prior_sdate, prior_edate, '515', '911', 'cr', $4);
            pl_data.curr_amt6 = fin_get_doi_ung(_cur_sdate, _cur_edate, '515', '911', 'cr', $4);
            
            -- 7. lấy chỉ tiêu 07 (chi phí tai chinh 635) MS 22
            pl_data.prior_amt6 = fin_get_doi_ung(prior_sdate, prior_edate, '635', '911', 'dr', $4);
            pl_data.curr_amt6 = fin_get_doi_ung(_cur_sdate, _cur_edate, '635', '911', 'dr', $4);
            
            -- 7.1. tách chi phí lãi vay 6351 MS 23
            pl_data.prior_amt71 = fin_get_balance_all_pl(prior_sdate, prior_edate, '6352', 'cr', $4);
            pl_data.curr_amt71 = fin_get_balance_all_pl(_cur_sdate, _cur_edate, '6352', 'cr', $4);
            
            -- 8. lấy chỉ tiêu 08 (chi phí bán hàng 641) MS 25
            pl_data.prior_amt6 = fin_get_doi_ung(prior_sdate, prior_edate, '641', '911', 'dr', $4);
            pl_data.curr_amt6 = fin_get_doi_ung(_cur_sdate, _cur_edate, '641', '911', 'dr', $4);
            
            -- 9. lấy chỉ tiêu 09 (chi phí quản lý 642) MS 26
            pl_data.prior_amt6 = fin_get_doi_ung(prior_sdate, prior_edate, '642', '911', 'dr', $4);
            pl_data.curr_amt6 = fin_get_doi_ung(_cur_sdate, _cur_edate, '642', '911', 'dr', $4);
            
            -- 10. tính chỉ tiêu 10 (lợi nhuận thuần) MS 30 = 20 + (21 - 22) - (25 + 26)
            pl_data.prior_amt10 = pl_data.prior_amt5 + (pl_data.prior_amt6 - pl_data.prior_amt7) - (pl_data.prior_amt8 + pl_data.prior_amt9);
            pl_data.curr_amt10 = pl_data.curr_amt5 + (pl_data.curr_amt6 - pl_data.curr_amt7) - (pl_data.curr_amt8 + pl_data.curr_amt9);
            
            -- 11. lấy chỉ tiêu 11 (thu nhập khác 711) MS 31
            pl_data.prior_amt6 = fin_get_doi_ung(prior_sdate, prior_edate, '711', '911', 'cr', $4);
            pl_data.curr_amt6 = fin_get_doi_ung(_cur_sdate, _cur_edate, '711', '911', 'cr', $4);
            
            -- 12. lấy chỉ tiêu 12 (chi phí khác 811) MS 32
            pl_data.prior_amt6 = fin_get_doi_ung(prior_sdate, prior_edate, '811', '911', 'dr', $4);
            pl_data.curr_amt6 = fin_get_doi_ung(_cur_sdate, _cur_edate, '811', '911', 'dr', $4);
            
            -- 13. tính chỉ tiêu 13 (lợi nhuận khác) MS 40 = 31 - 32
            pl_data.prior_amt13 = pl_data.prior_amt11 - pl_data.prior_amt12;
            pl_data.curr_amt13 = pl_data.curr_amt11 - pl_data.curr_amt12;
            
            -- 14. tính chỉ tiêu 14 (tổng lợi nhuận trước thuế) MS 50 = 30 + 40
            pl_data.prior_amt14 = pl_data.prior_amt10 + pl_data.prior_amt13;
            pl_data.curr_amt14 = pl_data.curr_amt10 + pl_data.curr_amt13;
            
            -- 15. lấy chỉ tiêu 15 (thuế TNDN hiện hành 8211) MS 51
            pl_data.prior_amt6 = -1*fin_get_doi_ung(prior_sdate, prior_edate, '8211', '911', 'dr', $4);
            pl_data.curr_amt6 = -1*fin_get_doi_ung(_cur_sdate, _cur_edate, '8211', '911', 'dr', $4);
            
            -- 16. lấy chỉ tiêu 16 (thuế TNDN hoãn lại 8212) MS 52
            pl_data.prior_amt6 = -1*fin_get_doi_ung(prior_sdate, prior_edate, '8212', '911', 'dr', $4);
            pl_data.curr_amt6 = -1*fin_get_doi_ung(_cur_sdate, _cur_edate, '8212', '911', 'dr', $4);
            
            -- 17. tính chỉ tiêu 17 (tổng lợi nhuận sau thuế) MS 60 = 50 - 51 - 52
            pl_data.prior_amt17 = pl_data.prior_amt14 - pl_data.prior_amt15 - pl_data.prior_amt16;
            pl_data.curr_amt17 = pl_data.curr_amt14 - pl_data.curr_amt15 - pl_data.curr_amt16;
            
            -- 18. tính chỉ tiêu 18 (khong tinh)
            
            -- 19. tính chỉ tiêu 19 (khong tinh)
            
            return next pl_data;
            return;
        END; $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100
          ROWS 1000;
        ALTER FUNCTION fin_profit_loss_report(date, date, character varying, integer)
          OWNER TO openerp;
        '''
        cr.execute(sql)
        return True

sql_profit_loss()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
