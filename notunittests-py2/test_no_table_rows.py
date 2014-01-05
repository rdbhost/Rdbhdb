# test_no_table_rows.py - Example using the API Classes with the s role
# Number of table rows
from rdbhdb import rdbhdb as db

authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
conn=db.connect('s000015', authcode=authcode)
q = "CREATE TABLE rdbhdbTest (value) AS SELECT * FROM generate_series(1, 250)"
x = "DROP TABLE rdbhdbTest"
q1 = "SELECT count(*) FROM rdbhdbTest;"
curs = conn.cursor()
s=curs.execute(q)
try:
    s=curs.execute(q1)
    row = curs.fetchone()
    print row
except:
    raise db.ProgrammingError("Some Error")
finally:
    s=curs.execute(x)
