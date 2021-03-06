#!/usr/bin/env python
''' unit test suite for file upload features of rdbhdb'''

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

need_version = '0.11.0'

class test_Rdbhdb_compressedRequest(unittest.TestCase):

    driver = rdbhdb

    # get choice of server from environment
    HOST = os.environ.get('RDBHOST_TEST', "dev.rdbhost.com").strip("'")

    connect_args = ()
    connect_kw_args = {
        'role': accounts.demo['role'],
        'authcode': accounts.demo['authcode'],
        'host': HOST,
        'asyncio': True}

    table_prefix = 'compressed_' # If you need to specify a prefix for tables

    ddl1 = '''CREATE TABLE %sbig (descr VARCHAR(300), idx INTEGER);''' % table_prefix
    xddl1 = 'DROP TABLE %sbig;' % table_prefix

    # Some drivers may need to override these helpers, for example adding
    # a 'commit' after the execute.
    def executeDDL1(self, cur):
        yield from cur.execute(self.ddl1)

    def setUp(self):
        # Call superclass setUp In case this does something in the
        # future
        try:
            con = self._connect()
            con.close()
        except Exception as e:
            print('connection not made. %s db must be created online.' % e.args[0])
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

    def test0_host(self):
        print('using server ' + self.HOST, end=" ")
        
    def test1_version(self):
        """Verify correct API module version in use."""
        lVersion = rdbhdb.__version__.split('.')
        nVersion = need_version.split('.')
        self.assertTrue(lVersion >= nVersion, rdbhdb.__version__)

    def test_Compressed(self):
        con = self._connect()
        try:
            cur = con.cursor()

            # cursor.fetchone should raise an Error if called after
            # executing a query that cannnot return rows
            yield from self.executeDDL1(cur)

            yield from cur.execute('select idx from %sbig' % self.table_prefix)
            self.assertEqual(cur.fetchone(), None, 'cursor.fetchone should return None if a query retrieves no rows')
            self.failUnless(cur.rowcount in (-1, 0))

            stuff = "asjdfasdl;kfjasdkl;fj asdklfh asdlkfj asdklfj asdklfj asdklf adddsdklfasdfas f" + \
                    "asjkdf askldfjasdlkfjasdlkfj asdklfjasdlkfj asdklfjasdlkfj asdlfj asdlfjasdlkf" + \
                    "asldkjfasdl;kfjaskldfjasdklfjasdklfjasdklfjasdfasdfkljasdklfjasdklfjasdlkfjsdl"
            assert 235 > len(stuff) > 230, len(stuff)

            qs = []
            args = []
            for i in range(15):
                qs.append('INSERT INTO %sbig (idx, descr) VALUES(%%s, %%s);' % self.table_prefix)
                args.extend([i, stuff])
            q = '\n'.join(qs)

            self.assertTrue(len(q)>150, len(q))
            self.assertTrue(sum([len(a) for a in args if type(a) == type('')]) > 2000)
            yield from cur.execute(q, args)
            self.assertRaises(self.driver.Error, cur.fetchone)

            yield from cur.execute('select count(*) from %sbig' % self.table_prefix)
            r = cur.fetchone()
            self.assertEqual(len(r), 1, 'cursor.fetchone should have retrieved a single row')
            self.assertEqual(r[0], 15, 'cursor.fetchone retrieved incorrect data %s' % r[0])
            self.failUnless(cur.rowcount in (-1, 1))
        finally:
            con.close()


class test_Rdbhdb_compressedRequest_ws(test_Rdbhdb_compressedRequest):

    connect_kw_args = {
        'role': accounts.demo['role'],
        'asyncio': True,
        'authcode': accounts.demo['authcode'],
        'host': test_Rdbhdb_compressedRequest.HOST,
        'useWebsocket': True
    }



if __name__ == '__main__':
    unittest.main()
