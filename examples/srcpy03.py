
from rdbhdb import rdbhdb as db
import rdbhdb.extensions

# connect to the RdbHost server
role = 'r0000000004'
authcode = '-'
conn = db.connect (role, authcode=authcode)

# create a dictionary cursor
cur = conn.cursor(rdbhdb.extensions.DictCursor)

# execute the addition query
cur.execute ("SELECT 1+1 AS sum")

# get the result record
rec = cur.fetchone()

# print results
print 'The sum of 1 and 1 is: ', rec['sum']	

