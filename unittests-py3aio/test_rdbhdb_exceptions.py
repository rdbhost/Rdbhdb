#!/usr/bin/env python

import unittest
import os, sys

import dbexceptions
import accounts
import asyncio

sys.path.insert(0, '..\lib')

from rdbhdb import rdbhdb

need_version = '0.9.6'

class test_Rdbhdb(dbexceptions.DatabaseExcTest):
    driver = rdbhdb
    
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

    def setUp(self):
        # Call superclass setUp In case this does something in the
        # future
        dbexceptions.DatabaseExcTest.setUp(self)

        try:
            con = self._connect()
            con.close()
        except Exception as e:
            print('connection not made. %s db must be created online.' % e.args[0])
            sys.exit(2)

    def tearDown(self):
        dbexceptions.DatabaseExcTest.tearDown(self)

    def test0_host(self):
        print('using server', self.HOST, end=" ")
        
    def test1_version(self):
        self.assertTrue(rdbhdb.__version__ >= need_version, rdbhdb.__version__)


if __name__ == '__main__':
    unittest.main()



#