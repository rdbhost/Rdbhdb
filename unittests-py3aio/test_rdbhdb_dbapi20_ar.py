#!/usr/bin/env python

import dbapi20
import unittest
import sys
import accounts

from rdbhdb import rdbhdb
import asyncio

sys.path.insert(0, '..\lib')

from rdbhdb import rdbhdb

def asyncio_meth_ruc(f):
    def asy(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(f(self))
    return asy
def asyncio_ruc(f):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(f())

need_version = '0.9.6'

class test_Rdbhdb_ar(dbapi20.DatabaseAPI20Test):
    driver = rdbhdb
    connect_args = ()
    connect_kw_args = {
        'asyncio': True,
        'role': accounts.demo['role'],
        'authcode': accounts.demo['authcode'] }

    lower_func = 'lower' # For stored procedure test

    def _connect(self):
        try:
            conn = self.driver.connect(
                *self.connect_args, **self.connect_kw_args )
            conn.autorefill = True
            return conn
        except AttributeError:
            self.fail("No connect method found in self.driver module")
    
    def setUp(self):
        # Call superclass setUp In case this does something in the
        # future
        dbapi20.DatabaseAPI20Test.setUp(self) 

        try:
            con = self._connect()
            con.close()
        except Exception as e:
            print('connection not made. %s db must be created online.'%e.args[0])
            sys.exit(2)

    def tearDown(self):
        dbapi20.DatabaseAPI20Test.tearDown(self)

    def test_nextset(self): pass
    def test_setoutputsize(self): pass
    def test_ExceptionsAsConnectionAttributes(self): pass  # override

if __name__ == '__main__':
    unittest.main()
    
