#!/usr/bin/env python
''' unit test suite for multi-record set features of rdbhost, and the nextset
    cursor method of rdbhdb.   
'''

import unittest
import time
import sys, os

import accounts

sys.path.insert(0, '..\lib')

from rdbhdb import rdbhdb

need_version = '0.9.3'

class test_nextset(unittest.TestCase):

    driver = rdbhdb

    # get choice of server from environment
    HOST = os.environ.get('RDBHOST_TEST', "dev.rdbhost.com").strip("'")

    connect_args = ()
    connect_kw_args = {
        'role': accounts.demo['role'],
        'authcode': accounts.demo['authcode'],
        'host': HOST }

    lower_func = 'lower' # For stored procedure test

    table_prefix = 'extras_' # If you need to specify a prefix for tables

    ddl1 = '''CREATE TABLE %scities (name varchar(80));''' % table_prefix
    ddl2 = '''CREATE TABLE %sstates (name varchar(80));''' % table_prefix
    ddl3 = '''CREATE TABLE %sTest (value) AS SELECT * FROM generate_series(0, 509);''' % table_prefix

    xddl1 = 'drop table %scities' % table_prefix
    xddl2 = 'drop table %sstates' % table_prefix
    xddl3 = 'drop table %sTest' % table_prefix
    xddl4 = 'drop table %sdummy' % table_prefix

    lowerfunc = 'lower' # Name of stored procedure to convert string->lowercase
        
    # Some drivers may need to override these helpers, for example adding
    # a 'commit' after the execute.
    def executeDDL1(self, cursor):
        cursor.execute(self.ddl1)

    def executeDDL2(self, cursor):
        cursor.execute(self.ddl2)

    def executeDDL3(self, cursor):
        cursor.execute(self.ddl3)

    def setUp(self):
        # Call superclass setUp In case this does something in the
        # future
        try:
            con = self._connect()
            con.close()
        except Exception as e:
            print('connection not made. %s db must be created online.'%e.args[0])
            sys.exit(2)

    def tearDown(self):
        ''' self.drivers should override this method to perform required cleanup
            if any is necessary, such as deleting the test database.
            The default drops the tables that may be created.
        '''
        con = self._connect()
        try:
            cur = con.cursor()
            for ddl in (self.xddl1, self.xddl2, self.xddl3, self.xddl4):
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

    def test0_host(self):
        print('using SERVER', self.HOST, file=sys.stderr)
        
    def test1_version(self):
        self.assertTrue(rdbhdb.__version__ >= need_version, rdbhdb.__version__)

    samples = [
        'Atlanta',
        'Boston',
        'Chicago',
        'Houston',
        'Madison',
        'Memphis'
        ]

    def _populate(self):
        ''' Return a list of sql commands to setup the DB for the fetch
            tests.
        '''
        populate = [
            "insert into %scities values ('%s')" % (self.table_prefix, s)
                for s in self.samples
            ]
        return populate

    def test_nextset(self):
        con = self._connect()
        try:
            cur = con.cursor()

            self.executeDDL1(cur)
            self.executeDDL2(cur)
            for sql in self._populate():
                cur.execute(sql)

            q = '''select name from %scities;
                   create table %sdummy();
                   select name from %sstates;''' %\
                   ((self.table_prefix, )*3)
            cur.execute(q)
            
            # first (default) recordset
            r = cur.fetchall()
            self.assertEqual(len(r), 6,
                'cursor.fetchmany retrieved incorrect number of rows ')
            self.assertTrue(cur.rowcount in (-1, 6))
          
            # Make sure we get the right data back out
            for i in range(0, 6):
                self.assertEqual(str(r[i][0]), str(self.samples[i]),
                    'incorrect data retrieved by cursor.fetchmany %s %s'%\
                    (r[i], self.samples[i]))

            # next recordset (no data)
            s = cur.nextset()
            self.assertTrue(s, 'nextset return false neg')
            self.assertRaises(rdbhdb.Error, cur.fetchall)
            self.assertTrue(cur.rowcount == -1, cur.rowcount)
            self.assertTrue(not cur._records)
            
            # next recordset (0 recs)
            s = cur.nextset()
            self.assertTrue(s, 'nextset return false neg')
            r = cur.fetchall()
            self.assertTrue(cur.rowcount == 0, cur.rowcount)
            self.assertTrue(len(cur._records)==0)
            
            # no more recordsets
            s = cur.nextset()
            self.assertTrue(not s, 'nextset return false pos at end of data')
            self.assertRaises(rdbhdb.Error, cur.fetchall)
            self.assertTrue(cur.rowcount == -1, cur.rowcount)
            self.assertTrue(not cur._records)
            
        finally:
            con.close()

    def test_limits(self):
        con = self._connect()
        try:
            cur = con.cursor()

            self.executeDDL1(cur)
            self.executeDDL2(cur)
            for sql in self._populate():
                cur.execute(sql)
            self.executeDDL3(cur)
            q = '''select name from %scities;
                   create table %sdummy();
                   select value, '0' from %sTest;''' %\
                   ((self.table_prefix, )*3)
            cur.execute(q)
            
            # first (default) recordset
            r = cur.fetchall()
            self.assertEqual(len(r), 6,
                'cursor.fetchmany retrieved incorrect number of rows %s 6'%\
                len(r))
            self.assertTrue(cur.rowcount in (-1, 6))
          
            # next recordset (no data)
            s = cur.nextset()
            self.assertTrue(s, 'nextset return false neg')
            self.assertRaises(rdbhdb.Error, cur.fetchall)
            self.assertTrue(cur.rowcount == -1, cur.rowcount)
            self.assertTrue(not cur._records)
            
            # next recordset (100-6 recs)
            s = cur.nextset()
            self.assertTrue(s, 'nextset return false neg')
            r = cur.fetchmany(100-6)
            self.assertTrue(cur.rowcount >= 100-6, cur.rowcount)
            self.assertTrue(len(r)==100-6, len(r))
            
            # no more recordsets
            s = cur.nextset()
            self.assertTrue(not s, 'nextset return false pos at end of data')
            self.assertRaises(rdbhdb.Error, cur.fetchall)
            self.assertTrue(cur.rowcount == -1, cur.rowcount)
            self.assertTrue(not cur._records)

        finally:
            con.close()
            
            
if __name__ == '__main__':
    unittest.main()
