#!/usr/bin/env python

from rdbhdb.rdbhdb import connect

authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'

conn = connect('s000015', authcode=authcode)

curs = conn.cursor()
curs.execute("""DROP TABLE atable""")
curs.execute("""CREATE TABLE atable (
                name char(8),
                value float)""" )
curs.execute("INSERT INTO atable VALUES ('one', 1.0)")
curs.execute("INSERT INTO atable VALUES ('two', 2.0)")

conn.commit()
