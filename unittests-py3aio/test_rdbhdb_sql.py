#!/usr/bin/env python
''' unit test suite for SQL parsing features of rdbhdb.'''

import unittest
import time
import sys, os

import accounts
import asyncio

sys.path.insert(0, '..\lib')

from rdbhdb import rdbhdb

def asyncio_meth_ruc(f):
    def asy(self, *args):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(f(self, *args))
    return asy
def asyncio_ruc(f):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(f())

need_version = '0.9.6'


class test_Rdbhdb_sql(unittest.TestCase):

    driver = rdbhdb
    # get choice of server from environment
    HOST = os.environ.get('RDBHOST_TEST', "dev.rdbhost.com").strip("'")
    #print >> sys.stderr, 'Using SERVER', HOST

    connect_args = ()
    connect_kw_args = {
        'asyncio': True,
        'role': accounts.demo['role'],
        'authcode': accounts.demo['authcode'],
        'host': HOST}

    table_prefix = 'extras_' # If you need to specify a prefix for tables

    ddl1 = '''CREATE TABLE %sbig (value) AS SELECT * FROM generate_series(0, 509);''' % table_prefix
    xddl1 = 'drop table %sbig' % table_prefix

    lowerfunc = 'lower' # Name of stored procedure to convert string->lowercase
        
    # Some drivers may need to override these helpers, for example adding
    # a 'commit' after the execute.
    def executeDDL1(self, cursor):
        yield from cursor.execute(self.ddl1)

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
            for ddl in (self.xddl1, ):
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

    def _fetch(self, q, ct=50):
        con = self._connect()
        #con.autorefill = True
        try:
            cur = con.cursor()
            yield from self.executeDDL1(cur)
            yield from cur.execute(q, ())
            #results = cur.fetchmany(ct)
            results = cur.fetchall()
            self.assertEqual(len(results), ct, 'fetchmany wanted %s records, got %s' % (ct, len(results)))
        finally:
            con.close()

    def test000_host(self):
        """Announce which server we are using. """
        print('using server', self.HOST, file=sys.stderr, end=" ")
        
    def test001_version(self):
        """Verify correct version of DB API module. """
        self.assertTrue(rdbhdb.__version__ >= need_version, rdbhdb.__version__)

    @asyncio_meth_ruc
    def test01_limit5(self):
        """Tests small limit. """
        q = 'SELECT * FROM %sbig LIMIT 5' % self.table_prefix
        yield from self._fetch(q, 5)
        
    @asyncio_meth_ruc
    def test02_limit250(self):
        """Tests high 250 limit"""
        q = 'SELECT * FROM %sbig LIMIT 250' % self.table_prefix
        yield from self._fetch(q, 250)

    @asyncio_meth_ruc
    def test03_commented25_lim(self):
        """Test dblhyphen comment. """
        q = """SELECT * FROM %sbig 
               -- LIMIT 25 
               WHERE value < 100
            """ % self.table_prefix
        yield from self._fetch(q, 100)
        
    @asyncio_meth_ruc
    def test04_commented250_lim(self):
        """Test dblhyphen comment with limit. """
        q = """SELECT * FROM %sbig 
               -- LIMIT 25 
               WHERE value < 300
               LIMIT 250
            """ % self.table_prefix
        yield from self._fetch(q, 250)
        
    @asyncio_meth_ruc
    def test05_nestedcomment250_lim(self):
        """Tests nested comments with high limit"""
        q = """SELECT * FROM %sbig 
               /* beginning of comment that
                 /* nests once */  OFFSET 100
                 how about that. Limit 200 */
               WHERE value < 300
               LIMIT 250
            """ % self.table_prefix
        yield from self._fetch(q, 250)
            
    @asyncio_meth_ruc
    def test06_nestedcomment150_limoff(self):
        """Tests nested comments with limit and offset. """
        q = """SELECT * FROM %sbig 
               /* beginning of comment that
                 /* nests once */  OFFSET 100
                 how about that. Limit 200 */
               WHERE value < 300
               LIMIT 250
               OFFSET 150
            """ % self.table_prefix
        yield from self._fetch(q, 150)

    @asyncio_meth_ruc
    def test07_subsel150_lim(self):
        """Tests subselect with limit 150"""
        q = """SELECT * FROM %sbig 
               WHERE value IN (SELECT * FROM %sbig LIMIT 150)
               LIMIT 250
            """ % (self.table_prefix, self.table_prefix)
        yield from self._fetch(q, 150)
        
    @asyncio_meth_ruc
    def test08_postcomment_lim(self):
        """Test -- commenting w/o newline"""
        q = """SELECT 1+1;
            --CREATE table %sdummy (); 
            """ % self.table_prefix
        yield from self._fetch(q, 1)

        
if __name__ == '__main__':
    unittest.main()
