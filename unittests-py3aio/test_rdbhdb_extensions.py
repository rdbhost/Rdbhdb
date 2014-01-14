#!/usr/bin/env python

import unittest
import os, sys
import accounts
import asyncio

sys.path.insert(0, '..\lib')

from rdbhdb import rdbhdb
from rdbhdb import extensions

def asyncio_meth_ruc(f):
    def asy(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(f(self))
    return asy
def asyncio_ruc(f):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(f())

need_version = '0.9.6'


class test_Rdbhdb_extensions(unittest.TestCase):
    driver = rdbhdb
    ext = extensions

    # get choice of server from environment
    HOST = os.environ.get('RDBHOST_TEST', "dev.rdbhost.com").strip("'")
    #print >> sys.stderr, 'Using SERVER', HOST

    connect_args = ()
    connect_kw_args = {
        'asyncio': True,
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
        yield from cursor.execute(self.ddl1)

    def executeDDL2(self, cursor):
        yield from cursor.execute(self.ddl2)

    def executeDDL3(self, cursor):
        yield from cursor.execute(self.ddl3)

    def setUp(self):
        # Call superclass setUp In case this does something in the
        # future
        try:
            con = self._connect()
            con.close()
        except Exception as e:
            print('connection not made. %s db must be created online.'%e.args[0])
            sys.exit(2)

    @asyncio_meth_ruc
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
                    yield from cur.execute(ddl)
                    con.commit()
                except self.driver.Error: 
                    # Assume table didn't exist. Other tests will check if
                    # execute is busted.
                    pass
        finally:
            con.close()

    def _connect(self):
        try:
            return self.driver.connect(*self.connect_args, **self.connect_kw_args)
        except AttributeError:
            self.fail("No connect method found in self.driver module")

    def test0_host(self):
        print('using server', self.HOST, end=" ")
        
    def test1_version(self):
        self.assertTrue(rdbhdb.__version__ >= need_version, rdbhdb.__version__)

    @asyncio_meth_ruc
    def test_DictCursor_fetchone(self):
        con = self._connect()
        try:
            cur = con.cursor(cursor_factory=self.ext.AsyncDictCursor)

            # cursor.fetchone should raise an Error if called before
            # executing a select-type query
            self.assertRaises(self.driver.Error, cur.fetchone)

            # cursor.fetchone should raise an Error if called after
            # executing a query that cannnot return rows
            yield from self.executeDDL1(cur)
            self.assertRaises(self.driver.Error, cur.fetchone)

            yield from cur.execute('select name from %scities' % self.table_prefix)
            self.assertEqual(cur.fetchone(), None, 'cursor.fetchone should return None if a query retrieves no rows')
            self.assertTrue(cur.rowcount in (-1, 0))

            # cursor.fetchone should raise an Error if called after
            # executing a query that cannnot return rows
            yield from cur.execute("INSERT INTO %scities VALUES ('San Francisco');" % self.table_prefix)
            self.assertRaises(self.driver.Error, cur.fetchone)

            yield from cur.execute('select name from %scities' % self.table_prefix)
            r = cur.fetchone()
            self.assertEqual(len(r), 1, 'cursor.fetchone should have retrieved a single row')
            self.assertEqual(r['name'], 'San Francisco', 'cursor.fetchone retrieved incorrect data')
            self.assertEqual(cur.fetchone(), None, 'cursor.fetchone should return None if no more rows available')
            self.assertTrue(cur.rowcount in (-1, 1))
        finally:
            con.close()

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

    @asyncio_meth_ruc
    def test_DictCursor_fetchmany(self):
        con = self._connect()
        try:
            cur = con.cursor(cursor_factory=self.ext.AsyncDictCursor)

            # cursor.fetchmany should raise an Error if called without
            #issuing a query
            self.assertRaises(self.driver.Error, cur.fetchmany, 4)

            yield from self.executeDDL1(cur)
            for sql in self._populate():
                yield from cur.execute(sql)

            yield from cur.execute('select name from %scities' % self.table_prefix)
            r = cur.fetchmany()
            self.assertEqual(len(r), 1, 'cursor.fetchmany retrieved incorrect number of rows, default of arraysize is one.' )
            cur.arraysize=10
            r = cur.fetchmany(3) # Should get 3 rows
            self.assertEqual(len(r), 3, 'cursor.fetchmany retrieved incorrect number of rows')
            r = cur.fetchmany(4) # Should get 2 more
            self.assertEqual(len(r), 2, 'cursor.fetchmany retrieved incorrect number of rows')
            r = cur.fetchmany(4) # Should be an empty sequence
            self.assertEqual(len(r), 0, 'cursor.fetchmany should return an empty sequence after results are exhausted' )
            self.assertTrue(cur.rowcount in (-1, 6))

            # Same as above, using cursor.arraysize
            cur.arraysize=4
            yield from cur.execute('select name from %scities' % self.table_prefix)
            r = cur.fetchmany() # Should get 4 rows
            self.assertEqual(len(r), 4, 'cursor.arraysize not being honoured by fetchmany')
            r = cur.fetchmany() # Should get 2 more
            self.assertEqual(len(r), 2)
            r = cur.fetchmany() # Should be an empty sequence
            self.assertEqual(len(r), 0)
            self.assertTrue(cur.rowcount in (-1, 6))

            cur.arraysize=6
            yield from cur.execute('select name from %scities' % self.table_prefix)
            rows = cur.fetchmany() # Should get all rows
            self.assertTrue(cur.rowcount in (-1, 6))
            self.assertEqual(len(rows), 6)
            rows = [r['name'] for r in rows]
            rows.sort()
          
            # Make sure we get the right data back out
            for i in range(0, 6):
                self.assertEqual(rows[i], self.samples[i], 'incorrect data retrieved by cursor.fetchmany ...')

            rows = cur.fetchmany() # Should return an empty list
            self.assertEqual(len(rows), 0, 'cursor.fetchmany should return an empty sequence if called after the whole result set has been fetched')
            self.assertTrue(cur.rowcount in (-1, 6))

            yield from self.executeDDL2(cur)
            yield from cur.execute('select name from %sstates' % self.table_prefix)
            r = cur.fetchmany() # Should get empty sequence
            self.assertEqual(len(r), 0, 'cursor.fetchmany should return an empty sequence if query retrieved no rows')
            self.assertTrue(cur.rowcount in (-1, 0))

        finally:
            con.close()

    @asyncio_meth_ruc
    def test_DictCursor_fetchall(self):
        con = self._connect()
        try:
            cur = con.cursor(cursor_factory=self.ext.AsyncDictCursor)
            # cursor.fetchall should raise an Error if called
            # without executing a query that may return rows (such
            # as a select)
            self.assertRaises(self.driver.Error, cur.fetchall)

            yield from self.executeDDL1(cur)
            for sql in self._populate():
                yield from cur.execute(sql)

            # cursor.fetchall should raise an Error if called
            # after executing a a statement that cannot return rows
            self.assertRaises(self.driver.Error, cur.fetchall)

            yield from cur.execute('select name from %scities' % self.table_prefix)
            rows = cur.fetchall()
            self.assertTrue(cur.rowcount in (-1, len(self.samples)))
            self.assertEqual(len(rows), len(self.samples), 'cursor.fetchall did not retrieve all rows')
            rows = [r['name'] for r in rows]
            rows.sort()
            for i in range(0, len(self.samples)):
                self.assertEqual(rows[i], self.samples[i], 'cursor.fetchall retrieved incorrect rows')
            rows = cur.fetchall()
            self.assertEqual(len(rows), 0,
                             'cursor.fetchall should return an empty list if called after the whole result set has been fetched')
            self.assertTrue(cur.rowcount in (-1, len(self.samples)))

            yield from self.executeDDL2(cur)
            yield from cur.execute('select name from %sstates' % self.table_prefix)
            rows = cur.fetchall()
            self.assertTrue(cur.rowcount in (-1, 0))
            self.assertEqual(len(rows), 0, 'cursor.fetchall should return an empty list if a select query returns no rows')
            
        finally:
            con.close()
    
    @asyncio_meth_ruc
    def test_DictCursor_mixedfetch(self):
        con = self._connect()
        try:
            cur = con.cursor(cursor_factory=self.ext.AsyncDictCursor)
            yield from self.executeDDL1(cur)
            for sql in self._populate():
                yield from cur.execute(sql)

            yield from cur.execute('select name from %scities' % self.table_prefix)
            rows1  = cur.fetchone()
            rows23 = cur.fetchmany(2)
            rows4  = cur.fetchone()
            rows56 = cur.fetchall()
            self.assertTrue(cur.rowcount in (-1, 6))
            self.assertEqual(len(rows23), 2, 'fetchmany returned incorrect number of rows')
            self.assertEqual(len(rows56), 2, 'fetchall returned incorrect number of rows')

            rows = []
            rows.extend([rows1])
            rows.extend(rows23)
            rows.extend([rows4])
            rows.extend(rows56)
            #rows.sort()
            for i in range(0, len(self.samples)):
                self.assertEqual(rows[i]['name'], self.samples[i], 'incorrect data retrieved or inserted' )
        finally:
            con.close()

        
if __name__ == '__main__':
    unittest.main()
    