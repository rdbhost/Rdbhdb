#!/usr/bin/env python

import unittest
import sys

sys.path.insert(0, '..\lib')

from rdbhdb import rdbhdb
from rdbhdb import extras


class test_Rdbhdb_err(unittest.TestCase):
    driver = rdbhdb
    xtras = extras

    connect_args = ()
    connect_kw_args = {
        'role': accounts.demo['role'],
        'authcode': accounts.demo['authcode'] }

    table_prefix = 'err_' # If you need to specify a prefix for tables

    ddl1 = '''CREATE TABLE %sxml (name char(3));''' % table_prefix
    xddl1 = 'drop table %sxml' % table_prefix

    lowerfunc = 'lower' # Name of stored procedure to convert string->lowercase
        
    # Some drivers may need to override these helpers, for example adding
    # a 'commit' after the execute.
    def executeDDL1(self, cursor):
        cursor.execute(self.ddl1)

    def setUp(self):
        # Call superclass setUp In case this does something in the future
        try:
            con = self._connect()
            con.close()
        except Exception as e:
            print( 'connection not made. %s db must be created online.'%e.args[0] )
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

    def test_xml_error(self):
        con = self._connect()
        try:
            cur = con.cursor()

            # cursor.fetchone should raise an Error if called after
            # executing a query that cannnot return rows
            self.executeDDL1(cur)
            self.assertRaises(self.driver.Error, cur.fetchone)

            # cursor.fetchone should raise an Error if called after
            # executing a query that cannnot return rows
            cur.execute("insert into %sxml (name) values ('\b\f')" % (
                self.table_prefix
                ))
            xmltest = 'select * from %sxml' % self.table_prefix
            self.assertRaises(self.driver.Error, cur.execute, xmltest)
            cur.execute(xmltest)
        finally:
            con.close()

            
if __name__ == '__main__':
    unittest.main()
    

