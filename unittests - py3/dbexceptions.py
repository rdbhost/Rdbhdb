#!/usr/bin/env python
''' Python DB API 2.0 driver compliance unit test suite. 
    
    This software is Public Domain and may be used without restrictions.

 "Now we have booze and barflies entering the discussion, plus rumours of
  DBAs on drugs... and I won't tell you what flashes through my mind each
  time I read the subject line with 'Anal Compliance' in it.  All around
  this is turning out to be a thoroughly unwholesome unit test."

    -- Ian Bicking
'''

__rcs_id__  = '$Id: dbapi20.py, v 1.10 2003/10/09 03:14:14 zenzen Exp $'
__version__ = '$Revision: 1.10 $'[11:-2]
__author__ = 'Stuart Bishop <zen@shangri-la.dropbear.id.au>'

import unittest
import time
import sys

# $Log: dbapi20.py, v $
# Revision 1.10  2003/10/09 03:14:14  zenzen
# Add test for DB API 2.0 optional extension, where database exceptions
# are exposed as attributes on the Connection object.
#
# Revision 1.9  2003/08/13 01:16:36  zenzen
# Minor tweak from Stefan Fleiter
#
# Revision 1.8  2003/04/10 00:13:25  zenzen
# Changes, as per suggestions by M.-A. Lemburg
# - Add a table prefix, to ensure namespace collisions can always be avoided
#
# Revision 1.7  2003/02/26 23:33:37  zenzen
# Break out DDL into helper functions, as per request by David Rushby
#
# Revision 1.6  2003/02/21 03:04:33  zenzen
# Stuff from Henrik Ekelund:
#     added test_None
#     added test_nextset & hooks
#
# Revision 1.5  2003/02/17 22:08:43  zenzen
# Implement suggestions and code from Henrik Eklund - test that cursor.arraysize
# defaults to 1 & generic cursor.callproc test added
#
# Revision 1.4  2003/02/15 00:16:33  zenzen
# Changes, as per suggestions and bug reports by M.-A. Lemburg,
# Matthew T. Kromer, Federico Di Gregorio and Daniel Dittmar
# - Class renamed
# - Now a subclass of TestCase, to avoid requiring the driver stub
#   to use multiple inheritance
# - Reversed the polarity of buggy test in test_description
# - Test exception heirarchy correctly
# - self.populate is now self._populate(), so if a driver stub
#   overrides self.ddl1 this change propogates
# - VARCHAR columns now have a width, which will hopefully make the
#   DDL even more portible (this will be reversed if it causes more problems)
# - cursor.rowcount being checked after various execute and fetchXXX methods
# - Check for fetchall and fetchmany returning empty lists after results
#   are exhausted (already checking for empty lists if select retrieved
#   nothing
# - Fix bugs in test_setoutputsize_basic and test_setinputsizes
#

class DatabaseExcTest(unittest.TestCase):
    ''' Test a database self.driver for DB API 2.0 compatibility.
        This implementation tests Gadfly, but the TestCase
        is structured so that other self.drivers can subclass this 
        test case to ensure compiliance with the DB-API. It is 
        expected that this TestCase may be expanded in the future
        if ambiguities or edge conditions are discovered.

        The 'Optional Extensions' are not yet being tested.

        self.drivers should subclass this test, overriding setUp, tearDown,
        self.driver, connect_args and connect_kw_args. Class specification
        should be as follows:

        import dbapi20 
        class mytest(dbapi20.DatabaseExcTest):
           [...] 

        Don't 'import DatabaseExcTest from dbapi20', or you will
        confuse the unit tester - just 'import dbapi20'.
    '''

    # The self.driver module. This should be the module where the 'connect'
    # method is to be found
    driver = None
    connect_args = () # List of arguments to pass to connect
    connect_kw_args = {} # Keyword arguments for connect
    table_prefix = 'dbexctest_' # If you need to specify a prefix for tables

    ddl1 = '''CREATE TABLE %sweather (
                                    city varchar(80),
                                    temp_lo int, -- low temperature
                                    temp_hi int, -- high temperature
                                    prcp real, -- precipitation
                                    date date
                                    );''' % table_prefix

    ddl2 = '''CREATE TABLE %scities (
                                   name varchar(80),
                                   location point
                                   );''' % table_prefix

    xddl1 = 'drop table %sweather' % table_prefix
    xddl2 = 'drop table %scities' % table_prefix

    lowerfunc = 'lower' # Name of stored procedure to convert string->lowercase
        
    # Some drivers may need to override these helpers, for example adding
    # a 'commit' after the execute.
    def executeDDL1(self, cursor):
        cursor.execute(self.ddl1)

    def executeDDL2(self, cursor):
        cursor.execute(self.ddl2)

    def setUp(self):
        ''' self.drivers should override this method to perform required setup
            if any is necessary, such as creating the database.
        '''
        pass

    def tearDown(self):
        ''' self.drivers should override this method to perform required cleanup
            if any is necessary, such as deleting the test database.
            The default drops the tables that may be created.
        '''
        con = self._connect()
        try:
            cur = con.cursor()
            for ddl in (self.xddl1, self.xddl2):
                try: 
                    cur.execute(ddl)
                    con.commit()
                except self.driver.Error: 
                    # Assume table didn't exist. Other tests will check if
                    # execute is busted.
                    pass
        finally:
            con.close()

    def _connect(self):
        try:
            return self.driver.connect(
                *self.connect_args, **self.connect_kw_args
                )
        except AttributeError:
            self.fail("No connect method found in self.driver module")

    def test_create_database(self):
        con = self._connect()
        cur = con.cursor()
        q = "CREATE DATABASE testdb"
        self.assertRaises(self.driver.InternalError, cur.execute, q)

    def test_grant_privilege(self):
        con = self._connect()
        cur = con.cursor()
        q = "GRANT ALL ON %sweather to s000043" % self.table_prefix
        self.assertRaises(self.driver.ProgrammingError, cur.execute, q)

    def test_closed_connection(self):
        con = self._connect()
        cur = con.cursor()
        self.executeDDL1(cur)
        q = "SELECT * FROM  %sweather" % self.table_prefix
        con.close()
        self.assertRaises(self.driver.ProgrammingError, cur.execute, q)

    def test_commit_on_closed_connection(self):
        con = self._connect()
        cur = con.cursor()
        self.executeDDL1(cur)
        q = "SELECT * FROM  %sweather" % self.table_prefix
        con.close()
        self.assertRaises(self.driver.ProgrammingError, con.commit)

    def test_close_on_closed_connection(self):
        con = self._connect()
        con.close()
        self.assertRaises(self.driver.ProgrammingError, con.close)

    def test_syntax_error1(self):
        con = self._connect()
        cur = con.cursor()
        self.executeDDL1(cur)
        q="INSERT INTO %sweather VALUE ('San Francisco', 46, 50, 0.25, '1994-11-27');" % self.table_prefix
        self.assertRaises(self.driver.ProgrammingError, cur.execute, q)

    def test_fetchone_before_select_query(self):
        con = self._connect()
        cur = con.cursor()
        self.assertRaises(self.driver.ProgrammingError, cur.fetchone)

    def test_fetchmany_before_select_query(self):
        con = self._connect()
        cur = con.cursor()
        self.assertRaises(self.driver.ProgrammingError, cur.fetchmany, 10)

    def test_fetchall_before_select_query(self):
        con = self._connect()
        cur = con.cursor()
        self.assertRaises(self.driver.ProgrammingError, cur.fetchall)

    def test_fetchone_after_non_result_fetching_query(self):
        con = self._connect()
        cur = con.cursor()
        self.executeDDL1(cur)
        q="INSERT INTO %sweather VALUES ('San Francisco', 46, 50, 0.25, '1994-11-27');" % self.table_prefix
        cur.execute(q)
        self.assertRaises(self.driver.ProgrammingError, cur.fetchone)

    def test_fetchmany_after_non_result_fetching_query(self):
        con = self._connect()
        cur = con.cursor()
        self.executeDDL1(cur)
        q="INSERT INTO %sweather VALUES ('San Francisco', 46, 50, 0.25, '1994-11-27');" % self.table_prefix
        cur.execute(q)
        self.assertRaises(self.driver.ProgrammingError, cur.fetchmany, 10)

    def test_fetchall_after_non_result_fetching_query(self):
        con = self._connect()
        cur = con.cursor()
        self.executeDDL1(cur)
        q="INSERT INTO %sweather VALUES ('San Francisco', 46, 50, 0.25, '1994-11-27');" % self.table_prefix
        cur.execute(q)
        self.assertRaises(self.driver.ProgrammingError, cur.fetchall)

    def test_fetch_gt_100_rows_1(self):
        con = self._connect()
        cur = con.cursor()
        self.executeDDL1(cur)
        q = "SELECT oid, typname, typelem FROM pg_type WHERE typtype = \'b\' ORDER BY oid"
        cur.execute(q)
        for i in range(100): cur.fetchone()
        self.assertRaises(self.driver.Warning, cur.fetchone)

    def test_fetch_gt_100_rows_2(self):
        con = self._connect()
        cur = con.cursor()
        self.executeDDL1(cur)
        q = "SELECT oid, typname, typelem FROM pg_type WHERE typtype = \'b\' ORDER BY oid"
        cur.execute(q)
        self.assertRaises(self.driver.Warning, cur.fetchmany, 111)

    def test_fetch_gt_100_rows_3(self):
        con = self._connect()
        cur = con.cursor()
        self.executeDDL1(cur)
        q = "SELECT oid, typname, typelem FROM pg_type WHERE typtype = \'b\' ORDER BY oid"
        cur.execute(q)
        self.assertRaises(self.driver.Warning, cur.fetchall)

    def test_drop_non_existent_table(self):
        con = self._connect()
        cur = con.cursor()
        q1="DROP TABLE IF EXISTS xyz;"
        q2="DROP TABLE xyz;"
        self.assertRaises(self.driver.ProgrammingError, cur.execute, q2)

    def test_create_existing_table(self):
        con = self._connect()
        cur = con.cursor()
        self.executeDDL1(cur)
        q="CREATE TABLE %sweather (city varchar(80);"%self.table_prefix
        self.assertRaises(self.driver.ProgrammingError, cur.execute, q)

    def test_copy_table_to_file(self):
        con = self._connect()
        cur = con.cursor()
        self.executeDDL1(cur)
        q="COPY %sweather TO 'xxx';"%self.table_prefix
        self.assertRaises(self.driver.ProgrammingError, cur.execute, q)

    def test_copy_table_from_file(self):
        con = self._connect()
        cur = con.cursor()
        self.executeDDL1(cur)
        q="COPY %sweather FROM 'xxx';"%self.table_prefix
        self.assertRaises(self.driver.ProgrammingError, cur.execute, q)
