# ex11 - Example using the API Classes with the s role

from rdbhdb import connection as db

authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
conn=db.connect('s000015', authcode=authcode)
q1 = "SELECT * FROM accounts;"

curs = conn.cursor(conn)
#curs.set_result_format('xml')
s=curs.execute(q1)
rows = curs.fetchall()
print rows

