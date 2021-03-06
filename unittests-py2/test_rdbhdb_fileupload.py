#!/usr/bin/env python
''' unit test suite for file upload features of rdbhdb'''

import unittest
import time
import os, sys
import accounts

sys.path.insert(0, '..\lib')

from rdbhdb import rdbhdb

need_version = '0.11.0'

class test_Rdbhdb_fileupload(unittest.TestCase):

    driver = rdbhdb

    # get choice of server from environment
    HOST = os.environ.get('RDBHOST_TEST', "dev.rdbhost.com").strip("'")

    connect_args = ()
    connect_kw_args = {
        'role': accounts.demo['role'],
        'authcode': accounts.demo['authcode'],
        'host': HOST }

    table_prefix = 'fileupload_'  # If you need to specify a prefix for tables

    ddl1 = '''CREATE TABLE %spics (nm varchar(12), img bytea);''' % table_prefix
    xddl1 = 'DROP TABLE %spics;' % table_prefix

    imgSrc = 'datafiles/sunset.JPG'

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
            print 'connection not made. %s db must be created online.' % e[0]
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
            return self.driver.connect(*self.connect_args, **self.connect_kw_args)
        except AttributeError:
            self.fail("No connect method found in self.driver module")

    def test0_host(self):
        print >> sys.stderr, 'using server', self.HOST
        
    def test1_version(self):
        """Verify correct API module version in use."""
        lVersion = rdbhdb.__version__.split('.')
        nVersion = need_version.split('.')
        self.assert_(lVersion >= nVersion, rdbhdb.__version__)

    def test_Fileupload(self):
        con = self._connect()
        try:
            cur = con.cursor()

            # cursor.fetchone should raise an Error if called after
            # executing a query that cannnot return rows
            self.executeDDL1(cur)

            cur.execute('select nm from %spics' % self.table_prefix)
            self.assertEqual(cur.fetchone(), None,
                'cursor.fetchone should return None if a query retrieves '
                'no rows'
                )
            self.failUnless(cur.rowcount in (-1, 0))

            # load binary source
            img = buffer(open(self.imgSrc, 'rb').read())
            self.assert_(len(img)>1000, len(img))
            cur.execute("insert into %spics (nm, img) values ('Victoria', %%s)" % self.table_prefix, (img, ))
            self.assertRaises(self.driver.Error, cur.fetchone)

            cur.execute('select nm from %spics' % self.table_prefix)
            r = cur.fetchone()
            self.assertEqual(len(r), 1, 'cursor.fetchone should have retrieved a single row')
            self.assertEqual(r[0], 'Victoria', 'cursor.fetchone retrieved incorrect data')
            self.failUnless(cur.rowcount in (-1, 1))
        finally:
            con.close()

            
class test_Rdbhdb_fileupload_ws(test_Rdbhdb_fileupload):

    connect_kw_args = {
        'role': accounts.demo['role'],
        'authcode': accounts.demo['authcode'],
        'host': test_Rdbhdb_fileupload.HOST,
        'useWebsocket': True
    }




if __name__ == '__main__':
    unittest.main()
