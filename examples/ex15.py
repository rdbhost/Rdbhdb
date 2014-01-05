# Example shows use of AutoFill Cursor to break RdbHost record limit.
# modified from pgoids.py -- Example using the API Classes (ver 2.0.2) with the s role

from rdbhdb import rdbhdb as db
authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
conn=db.connect('s000015', authcode=authcode)
conn.set_autorefill()
dc = conn.cursor()
q = "SELECT oid, typname, typelem FROM pg_type WHERE typtype = \'b\' ORDER BY oid"
for i in range(124):
    row = dc.fetchone()
    print row
