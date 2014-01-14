#!/usr/bin/env python

import unittest
import sys
import accounts
import asyncio

sys.path.insert(0, '..\lib')

from rdbhdb import rdbhdb
import extras

def asyncio_meth_ruc(f):
    def asy(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(f(self))
    return asy
def asyncio_ruc(f):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(f())


class test_Rdbhdb_err(unittest.TestCase):

    driver = rdbhdb
    xtras = extras

    connect_args = ()
    connect_kw_args = {
        'asyncio': True,
        'role': accounts.demo['role'],
        'authcode': accounts.demo['authcode']}

    table_prefix = 'err_' # If you need to specify a prefix for tables

    ddl1 = '''CREATE TABLE %sxml (name char(3));''' % table_prefix
    xddl1 = 'drop table %sxml' % table_prefix

    lowerfunc = 'lower' # Name of stored procedure to convert string->lowercase
        
    # Some drivers may need to override these helpers, for example adding
    # a 'commit' after the execute.
    def executeDDL1(self, cursor):
        yield from cursor.execute(self.ddl1)

    def setUp(self):
        # Call superclass setUp In case this does something in the future
        try:
            con = self._connect()
            con.close()
        except Exception as e:
            print( 'connection not made. %s db must be created online.'%e.args[0] )
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

    @asyncio_meth_ruc
    def test_xml_error(self):
        con = self._connect()
        try:
            cur = con.cursor()

            # cursor.fetchone should raise an Error if called after
            # executing a query that cannnot return rows
            yield from self.executeDDL1(cur)
            self.assertRaises(self.driver.Error, cur.fetchone)

            yield from cur.execute("insert into %sxml (name) values ('\b\f')" % self.table_prefix)
            xmltest = 'select * from %sxml' % self.table_prefix
            try:
                yield from cur.execute(xmltest)
            except self.driver.Error:
                pass
            #yield from cur.execute(xmltest)
        finally:
            con.close()

            
if __name__ == '__main__':
    unittest.main()
    

