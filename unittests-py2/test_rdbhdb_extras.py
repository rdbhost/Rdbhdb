#!/usr/bin/env python

import unittest
import os, sys
import accounts

sys.path.insert(0, '..\lib')

from rdbhdb import rdbhdb
from rdbhdb import extras

need_version = '0.9.3'


class test_Rdbhdb_extras(unittest.TestCase):
    driver = rdbhdb
    xtras = extras

    # get choice of server from environment
    HOST = os.environ.get('RDBHOST_TEST', "dev.rdbhost.com").strip("'")
    #print >> sys.stderr, 'Using SERVER', HOST

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
        except Exception, e:
            print 'connection not made. %s db must be created online.'%e[0]
            sys.exit(2)
        #self.tearDown()

    def tearDown(self):
        ''' self.drivers should override this method to perform required cleanup
            if any is necessary, such as deleting the test database.
            The default drops the tables that may be created.
        '''
        con = self._connect()
        try:
            cur = con.cursor()
            for ddl in (self.xddl1, self.xddl2, self.xddl3):
                try: 
                    cur.execute(ddl)
                    con.commit()
                except self.driver.Error, e: 
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

    def _logconnect(self):
        try:
            kw = self.connect_kw_args
            host, role, authcode = self.HOST, kw['role'], kw['authcode']
            return self.xtras.LoggingConnection(
                #*self.connect_args, **self.connect_kw_args
                host, role, authcode )
        except AttributeError:
            self.fail("No connect method found in self.driver module")

    def test0_host(self):
        print 'using server', self.HOST
        
    def test1_version(self):
        """Verify correct API module version in use."""
        lVersion = rdbhdb.__version__.split('.')
        nVersion = need_version.split('.')
        self.assert_(lVersion >= nVersion, rdbhdb.__version__)

    def test_Psycopg_Logging_Cursor_fetchone(self):
        #con = self._connect()
        logcon = self._logconnect()
        try:
            f = open('cursor.log', 'w')
            logcon.initialize(f)
            cur = logcon.cursor()

            # cursor.fetchone should raise an Error if called before
            # executing a select-type query
            self.assertRaises(self.driver.Error, cur.fetchone)

            # cursor.fetchone should raise an Error if called after
            # executing a query that cannnot return rows
            self.executeDDL1(cur)
            self.assertRaises(self.driver.Error, cur.fetchone)

            cur.execute('select name from %scities' % self.table_prefix)
            self.assertEqual(cur.fetchone(), None,
                'cursor.fetchone should return None if a query retrieves '
                'no rows'
                )
            self.failUnless(cur.rowcount in (-1, 0))

            # cursor.fetchone should raise an Error if called after
            # executing a query that cannnot return rows
            cur.execute("insert into %scities values ('Victoria Bitter')" % (
                self.table_prefix
                ))
            self.assertRaises(self.driver.Error, cur.fetchone)

            cur.execute('select name from %scities' % self.table_prefix)
            r = cur.fetchone()
            self.assertEqual(len(r), 1,
                'cursor.fetchone should have retrieved a single row'
                )
            self.assertEqual(r[0], 'Victoria Bitter',
                'cursor.fetchone retrieved incorrect data'
                )
            self.assertEqual(cur.fetchone(), None,
                'cursor.fetchone should return None if no more rows available'
                )
            self.failUnless(cur.rowcount in (-1, 1))
        finally:
            logcon.close()

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

    def test_Psycopg_Logging_Cursor_fetchmany(self):
        #con = self._connect()
        logcon = self._logconnect()
        try:
            f = open('cursor.log', 'w')
            logcon.initialize(f)
            cur = logcon.cursor()

            # cursor.fetchmany should raise an Error if called without
            #issuing a query
            self.assertRaises(self.driver.Error, cur.fetchmany, 4)

            self.executeDDL1(cur)
            for sql in self._populate():
                cur.execute(sql)

            cur.execute('select name from %scities' % self.table_prefix)
            r = cur.fetchmany()
            self.assertEqual(len(r), 1,
                'cursor.fetchmany retrieved incorrect number of rows, '
                'default of arraysize is one.'
                )
            cur.arraysize=10
            r = cur.fetchmany(3) # Should get 3 rows
            self.assertEqual(len(r), 3,
                'cursor.fetchmany retrieved incorrect number of rows'
                )
            r = cur.fetchmany(4) # Should get 2 more
            self.assertEqual(len(r), 2,
                'cursor.fetchmany retrieved incorrect number of rows'
                )
            r = cur.fetchmany(4) # Should be an empty sequence
            self.assertEqual(len(r), 0,
                'cursor.fetchmany should return an empty sequence after '
                'results are exhausted'
            )
            self.failUnless(cur.rowcount in (-1, 6))

            # Same as above, using cursor.arraysize
            cur.arraysize=4
            cur.execute('select name from %scities' % self.table_prefix)
            r = cur.fetchmany() # Should get 4 rows
            self.assertEqual(len(r), 4,
                'cursor.arraysize not being honoured by fetchmany'
                )
            r = cur.fetchmany() # Should get 2 more
            self.assertEqual(len(r), 2)
            r = cur.fetchmany() # Should be an empty sequence
            self.assertEqual(len(r), 0)
            self.failUnless(cur.rowcount in (-1, 6))

            cur.arraysize=6
            cur.execute('select name from %scities' % self.table_prefix)
            rows = cur.fetchmany() # Should get all rows
            self.failUnless(cur.rowcount in (-1, 6))
            self.assertEqual(len(rows), 6)
            self.assertEqual(len(rows), 6)
            rows = [r[0] for r in rows]
            rows.sort()
          
            # Make sure we get the right data back out
            for i in range(0, 6):
                self.assertEqual(rows[i], self.samples[i],
                    'incorrect data retrieved by cursor.fetchmany'
                    )

            rows = cur.fetchmany() # Should return an empty list
            self.assertEqual(len(rows), 0,
                'cursor.fetchmany should return an empty sequence if '
                'called after the whole result set has been fetched'
                )
            self.failUnless(cur.rowcount in (-1, 6))

            self.executeDDL2(cur)
            cur.execute('select name from %sstates' % self.table_prefix)
            r = cur.fetchmany() # Should get empty sequence
            self.assertEqual(len(r), 0,
                'cursor.fetchmany should return an empty sequence if '
                'query retrieved no rows'
                )
            self.failUnless(cur.rowcount in (-1, 0))

        finally:
            logcon.close()

    def test_Psycopg_Logging_Cursor_fetchall(self):
        #con = self._connect()
        logcon = self._logconnect()
        try:
            f = open('cursor.log', 'w')
            logcon.initialize(f)
            cur = logcon.cursor()
            # cursor.fetchall should raise an Error if called
            # without executing a query that may return rows (such
            # as a select)
            self.assertRaises(self.driver.Error, cur.fetchall)

            self.executeDDL1(cur)
            for sql in self._populate():
                cur.execute(sql)

            # cursor.fetchall should raise an Error if called
            # after executing a a statement that cannot return rows
            self.assertRaises(self.driver.Error, cur.fetchall)

            cur.execute('select name from %scities' % self.table_prefix)
            rows = cur.fetchall()
            self.failUnless(cur.rowcount in (-1, len(self.samples)))
            self.assertEqual(len(rows), len(self.samples),
                'cursor.fetchall did not retrieve all rows'
                )
            rows = [r[0] for r in rows]
            rows.sort()
            for i in range(0, len(self.samples)):
                self.assertEqual(rows[i], self.samples[i],
                'cursor.fetchall retrieved incorrect rows'
                )
            rows = cur.fetchall()
            self.assertEqual(
                len(rows), 0,
                'cursor.fetchall should return an empty list if called '
                'after the whole result set has been fetched'
                )
            self.failUnless(cur.rowcount in (-1, len(self.samples)))

            self.executeDDL2(cur)
            cur.execute('select name from %sstates' % self.table_prefix)
            rows = cur.fetchall()
            self.failUnless(cur.rowcount in (-1, 0))
            self.assertEqual(len(rows), 0,
                'cursor.fetchall should return an empty list if '
                'a select query returns no rows'
                )
            
        finally:
            logcon.close()
    
    def test_Psycopg_Logging_Cursor_mixedfetch(self):
        #con = self._connect()
        logcon = self._logconnect()
        try:
            f = open('cursor.log', 'w')
            logcon.initialize(f)
            cur = logcon.cursor()
            self.executeDDL1(cur)
            for sql in self._populate():
                cur.execute(sql)

            cur.execute('select name from %scities' % self.table_prefix)
            rows1  = cur.fetchone()
            rows23 = cur.fetchmany(2)
            rows4  = cur.fetchone()
            rows56 = cur.fetchall()
            self.failUnless(cur.rowcount in (-1, 6))
            self.assertEqual(len(rows23), 2,
                'fetchmany returned incorrect number of rows'
                )
            self.assertEqual(len(rows56), 2,
                'fetchall returned incorrect number of rows'
                )

            rows = [rows1[0]]
            rows.extend([rows23[0][0], rows23[1][0]])
            rows.append(rows4[0])
            rows.extend([rows56[0][0], rows56[1][0]])
            rows.sort()
            for i in range(0, len(self.samples)):
                self.assertEqual(rows[i], self.samples[i],
                    'incorrect data retrieved or inserted'
                    )
        finally:
            logcon.close()
            
if __name__ == '__main__':
    unittest.main()
    

