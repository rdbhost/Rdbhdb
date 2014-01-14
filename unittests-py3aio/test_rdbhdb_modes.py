#!/usr/bin/env python
''' unit test suite for autorefill features of rdbhdb, modified from the following.'''

import unittest
import time
import sys, os

import accounts
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


class BaseTest(unittest.TestCase):

    driver = rdbhdb

    # get choice of server from environment
    HOST = os.environ.get('RDBHOST_TEST', "dev.rdbhost.com").strip("'")

    connect_args = ()
    connect_kw_args = {
        'asyncio': True,
        'role': accounts.demo['role'],
        'authcode': accounts.demo['authcode'],
        'host': HOST}

    lower_func = 'lower' # For stored procedure test
        
    def setUp(self):
        # Call superclass setUp In case this does something in the
        # future
        try:
            con = self._connect()
            con.close()
        except Exception as e:
            print('connection not made. %s db must be created online.' % e.args[0])
            sys.exit(2)

    def _connect(self):
        try:
            return self.driver.connect(*self.connect_args, **self.connect_kw_args)
        except AttributeError:
            self.fail("No connect method found in self.driver module")


class Https(BaseTest):
    
    def testIdSrv(self):
        print('SERVER:', self.HOST, file=sys.stderr)

    @asyncio_meth_ruc
    def test_Https_fetchall(self):
        con = self._connect()
        con.https = True
        try:
            cur = con.cursor()
            yield from cur.execute('SELECT 1+1', ())
            results = cur.fetchall()
            self.assertTrue(cur._header)
            self.assertTrue(results)
        finally:
            con.close()


class Deferred(BaseTest):
    """verify that deferred requests return null results."""
    
    def testIdSrv(self):
        print('SERVER:', self.HOST, file=sys.stderr)

    @asyncio_meth_ruc
    def test_deferred(self):
        con = self._connect()
        try:
            cur = con.cursor()
            yield from cur.execute_deferred('SELECT 1+1', ())
            self.assertTrue(cur.rowcount <= 0, cur.rowcount)
            self.assertTrue(not cur._header, cur._header)
            self.assertTrue(not cur._records, cur._records)
            ##
        finally:
            con.close()
    
            
if __name__ == '__main__':
    unittest.main()
