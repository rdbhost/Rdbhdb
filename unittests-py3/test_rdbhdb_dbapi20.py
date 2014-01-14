#!/usr/bin/env python

import dbapi20
import unittest
import sys, os
import accounts

sys.path.insert(0, '..\lib')

from rdbhdb import rdbhdb

need_version = '0.9.3'

class test_Rdbhdb(dbapi20.DatabaseAPI20Test):
    driver = rdbhdb

    # get choice of server from environment
    HOST = os.environ.get('RDBHOST_TEST', "dev.rdbhost.com").strip("'")
    #print >> sys.stderr, 'Using SERVER', HOST

    connect_args = ()
    connect_kw_args = {
        'role': accounts.demo['role'],
        'authcode': accounts.demo['authcode'],
        'host': HOST}

    lower_func = 'lower' # For stored procedure test

    def setUp(self):
        # Call superclass setUp In case this does something in the
        # future
        dbapi20.DatabaseAPI20Test.setUp(self) 

        try:
            con = self._connect()
            con.compression = False
            con.close()
        except Exception as e:
            print ('connection not made. %s db must be created online.'%e.args[0])
            sys.exit(2)

    def tearDown(self):
        dbapi20.DatabaseAPI20Test.tearDown(self)

    def test0_host(self):
        print('using SERVER', self.HOST, file=sys.stderr, end=" ")
        
    def test1_version(self):
        self.assertTrue(rdbhdb.__version__ >= need_version, rdbhdb.__version__)

    def test_setoutputsize(self): pass
    def test_ExceptionsAsConnectionAttributes(self): pass  # override

    def test_nextset(self): 
        """tested in another module. """

if __name__ == '__main__':
    unittest.main()
    
