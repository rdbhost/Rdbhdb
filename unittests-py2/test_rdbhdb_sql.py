#!/usr/bin/env python
''' unit test suite for SQL parsing features of rdbhdb.'''

import unittest
import time
import os, sys
import accounts

sys.path.insert(0, '..\lib')

from rdbhdb import rdbhdb

need_version = '0.11.0'

class test_Rdbhdb_sql(unittest.TestCase):

    driver = rdbhdb
    # get choice of server from environment
    HOST = os.environ.get('RDBHOST_TEST', "dev.rdbhost.com").strip("'")

    connect_args = ()
    connect_kw_args = {
        'role': accounts.demo['role'],
        'authcode': accounts.demo['authcode'],
        'host': HOST }

    table_prefix = 'extras_' # If you need to specify a prefix for tables

    ddl1 = '''CREATE TABLE %sbig (value) AS SELECT * FROM generate_series(0, 509);''' % table_prefix
    xddl1 = 'drop table %sbig' % table_prefix

    lowerfunc = 'lower' # Name of stored procedure to convert string->lowercase
        
    # Some drivers may need to override these helpers, for example adding
    # a 'commit' after the execute.
    def executeDDL1(self, cursor):
        cursor.execute(self.ddl1)

    def setUp(self):
        # Call superclass setUp In case this does something in the
        # future
        try:
            con = self._connect()
            con.close()
        except Exception, e:
            print 'connection not made. %s db must be created online.'%e[0]
            sys.exit(2)

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

    def _fetch(self, q, ct=50):
        con = self._connect()
        con.autorefill = True
        try:
            cur = con.cursor()
            self.executeDDL1(cur)
            cur.execute(q, ())
            #results = cur.fetchmany(ct)
            results = cur.fetchall()
            self.assertEqual(len(results), ct,
                'fetchmany wanted %s records, got %s'%(ct, len(results))
                )
        finally:
            con.close()

    def _fetchOne(self, q, args=()):
        con = self._connect()
        try:
            cur = con.cursor()
            cur.execute(q, args)
            results = cur.fetchone()
            return results
        finally:
            con.close()

    def test000_host(self):
        """Announce which server we are using. """
        print >> sys.stderr, 'using server', self.HOST,
        
    def test1_version(self):
        """Verify correct API module version in use."""
        lVersion = rdbhdb.__version__.split('.')
        nVersion = need_version.split('.')
        self.assert_(lVersion >= nVersion, rdbhdb.__version__)

    def test01_limit5(self):
        """Tests small limit. """
        q = 'SELECT * FROM %sbig LIMIT 5' % self.table_prefix
        self._fetch(q, 5)
        
    def test02_limit250(self):
        """Tests high 250 limit"""
        q = 'SELECT * FROM %sbig LIMIT 250' % self.table_prefix
        self._fetch(q, 250)

    def test03_commented25_lim(self):
        """Test dblhyphen comment. """
        q = """SELECT * FROM %sbig 
               -- LIMIT 25 
               WHERE value < 300
            """ % self.table_prefix
        self._fetch(q, 300)
        
    def test04_commented250_lim(self):
        """Test dblhyphen comment with limit. """
        q = """SELECT * FROM %sbig 
               -- LIMIT 25 
               WHERE value < 300
               LIMIT 250
            """ % self.table_prefix
        self._fetch(q, 250)
        
    def test05_nestedcomment250_lim(self):
        """Tests nested comments with high limit"""
        q = """SELECT * FROM %sbig 
               /* beginning of comment that
                 /* nests once */  OFFSET 100
                 how about that. Limit 200 */
               WHERE value < 300
               LIMIT 250
            """ % self.table_prefix
        self._fetch(q, 250)
            
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
        self._fetch(q, 150)

    def test07_subsel150_lim(self):
        """Tests subselect with limit 150"""
        q = """SELECT * FROM %sbig 
               WHERE value IN (SELECT * FROM %sbig LIMIT 150)
               LIMIT 150
            """ % (self.table_prefix, self.table_prefix)
        self._fetch(q, 150)
        
    def test08_postcomment_lim(self):
        """Test -- commenting w/o newline"""
        q = """SELECT 1+1;
            --CREATE table %sdummy (); 
            """ % (self.table_prefix)
        self._fetch(q, 1)

    def test10_arg_lim(self):
        """Test -- commenting w/o newline"""
        q = """SELECT %s;
            """
        r = self._fetchOne(q, (13,))
        self.assert_(r[0] == 13, '%s token not working')

    def test11_namedParm_lim(self):
        """Test -- commenting w/o newline"""
        q = """SELECT %(one)s;
            """
        r = self._fetchOne(q, {'one': 14})
        self.assert_(int(r[0]) == 14, '%%\(one\)s token not working %s' % r[0])

    def test12_namedParm1_lim(self):
        """Test -- commenting w/o newline"""
        q = """SELECT %(two);
            """
        r = self._fetchOne(q, {'two': 15})
        self.assert_(int(r[0]) == 15, '%%\(one\) token not working %s' % r[0])


class test_Rdbhdb_sql_ws(test_Rdbhdb_sql):

    connect_kw_args = {
        'role': accounts.demo['role'],
        'authcode': accounts.demo['authcode'],
        'host': test_Rdbhdb_sql.HOST,
        'useWebsocket': True
    }


if __name__ == '__main__':
    unittest.main()
