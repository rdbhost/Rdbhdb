# test_psycop_MinTimeLoggingCursor
# Example shows using psycopg's MinTimeLoggingCursor

from rdbhdb import rdbhdb as db
from rdbhdb import extras

DictCursor = extras.DictCursor
MinTimeLoggingCursor = extras.MinTimeLoggingCursor
MinTimeLoggingConnection = extras.MinTimeLoggingConnection

authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
mtlconn=MinTimeLoggingConnection('s000015', authcode=authcode)
f = open('cursor.log', 'w')
mtlconn.initialize(f, mintime=0)
mtlcur = mtlconn.cursor()

q1 = "SELECT * FROM accounts;"

print "\n\nFetching all rows using fetchall:\n"

s=mtlcur.execute(q1)
recs = mtlcur.fetchall()
print(recs) 

print "\n\nFetching rows one by one using fetchone:\n"
print "Row 1:"
mtlcur = mtlconn.cursor()
s=mtlcur.execute(q1)
recs = mtlcur.fetchone()
print(recs) 
print "Row 2:"
recs = mtlcur.fetchone()
print(recs) 
print "Row 3:"
recs = mtlcur.fetchone()
print(recs) 

print "\n\nFetching several rows using fetchmany:\n"
mtlcur = mtlconn.cursor()
s=mtlcur.execute(q1)
recs = mtlcur.fetchmany(size=2)
print (recs)
f.close()