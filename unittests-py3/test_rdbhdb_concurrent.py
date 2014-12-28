#!/usr/bin/env python
''' unit test suite for file upload features of rdbhdb'''

import unittest
import time
import sys, os
import accounts
import threading

sys.path.insert(0, '..\lib')

from rdbhdb import rdbhdb

need_version = '0.10.0'

class test_Rdbhdb_concurrentRequest(unittest.TestCase):

    driver = rdbhdb

    # get choice of server from environment
    HOST = os.environ.get('RDBHOST_TEST', "dev.rdbhost.com").strip("'")

    connect_args = ()
    connect_kw_args = {
        'role': accounts.demo['role'],
        'authcode': accounts.demo['authcode'],
        'host': HOST}

    table_prefix = 'compressed_' # If you need to specify a prefix for tables

    ddl1 = '''CREATE TABLE %sbig (descr VARCHAR(300), idx INTEGER);''' % table_prefix
    xddl1 = 'DROP TABLE %sbig;' % table_prefix

    # Some drivers may need to override these helpers, for example adding
    # a 'commit' after the execute.
    def executeDDL1(self, cur):
        cur.execute(self.ddl1)

    def setUp(self):
        # Call superclass setUp In case this does something in the
        # future
        try:
            con = self._connect()
            con.close()
        except Exception as e:
            print('connection not made. %s db must be created online.' % e.args[0])
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
        print('using server ' + self.HOST, end=" ")
        
    def test1_version(self):
        """Verify correct API module version in use."""
        lVersion = rdbhdb.__version__.split('.')
        nVersion = need_version.split('.')
        self.assert_(lVersion >= nVersion, rdbhdb.__version__)

    def test_Twin(self):
        con = self._connect()
        try:
            cur0 = con.cursor()
            cur1 = con.cursor()

            thd0 = threading.Thread(target=cur0.execute, args=('SELECT 1',))
            thd1 = threading.Thread(target=cur1.execute, args=('SELECT 2',))

            thd0.start()
            thd0.join()

            thd1.start()
            thd1.join()

            row0 = cur0.fetchone()
            self.assert_(row0[0] == 1)

            row1 = cur1.fetchone()
            self.assert_(row1[0] == 2)
            pass

        finally:
            con.close()



if __name__ == '__main__':
    unittest.main()
