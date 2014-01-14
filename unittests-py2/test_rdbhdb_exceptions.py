#!/usr/bin/env python

import dbexceptions
import accounts
import unittest
import sys, os

sys.path.insert(0, '..\lib')

from rdbhdb import rdbhdb

need_version = '0.9.3'

class test_Rdbhdb_dbexc(dbexceptions.DatabaseExcTest):

    driver = rdbhdb
    
        # get choice of server from environment
    HOST = os.environ.get('RDBHOST_TEST', "dev.rdbhost.com").strip("'")
    #print >> sys.stderr, 'Using SERVER', HOST

    connect_args = ()
    connect_kw_args = {
        'role': accounts.demo['role'],
        'authcode': accounts.demo['authcode'],
        'host': HOST }

    lower_func = 'lower' # For stored procedure test

    def setUp(self):
        # Call superclass setUp In case this does something in the
        # future
        dbexceptions.DatabaseExcTest.setUp(self) 

        try:
            con = self._connect()
            con.close()
        except Exception, e:
            print 'connection not made. %s db must be created online.'%e[0]
            sys.exit(2)

    def tearDown(self):
        dbexceptions.DatabaseExcTest.tearDown(self)

    def test0_host(self):
        print 'using server', self.HOST
        
    def test1_version(self):
        """Verify correct API module version in use."""
        lVersion = rdbhdb.__version__.split('.')
        nVersion = need_version.split('.')
        self.assert_(lVersion >= nVersion, rdbhdb.__version__)


if __name__ == '__main__':
    unittest.main()
    