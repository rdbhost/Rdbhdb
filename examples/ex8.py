# ex8 - Example using the (rudimentary)API Classes with the s role
# testing multiple queries
from rdbhdb import connection as db
authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
conn=db.connect('s000015', authcode=authcode)
q = "DROP TABLE cities;DROP TABLE weather;"
c = conn.cursor(conn)
c.set_result_format('xml')
s=c.execute(q)
print "Done"

