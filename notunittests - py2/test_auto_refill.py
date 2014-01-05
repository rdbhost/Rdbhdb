# Example shows use of AutoFill Cursor to break RdbHost record limit.

from rdbhdb import rdbhdb as db
authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
conn=db.connect('s000015', authcode=authcode)
conn.set_autorefill()
dc = conn.cursor()
q = "CREATE TABLE rdbhdbTest (value) AS SELECT * FROM generate_series(0, 509)"
#q2 = "SELECT * FROM rdbhdbTest LIMIT 60 OFFSET 150"
q1 = "SELECT * FROM rdbhdbTest"
x = "DROP TABLE rdbhdbTest"
dc.execute(q)
dc.execute(q1)
try:
    print "*******************  Fetching 95 rows using fetchmany  ************************"
    rows = []
    rows=dc.fetchmany(95)
    for row in rows[:10]:
        print row
    print '   :   '
    print '   :   '
    for row in rows[-10:]:
        print row
    print "*******************  Fetching 10 rows using fetchone  *************************"
    for i in range(10):
        print dc.fetchone()
    print "*******************  Fetching 105 rows using fetchmany  ************************"
    rows = []
    rows=dc.fetchmany(105)
    for row in rows[:10]:
        print row
    print '   :   '
    print '   :   '
    for row in rows[-10:]:
        print row
    print "*************  Fetching all remaining rows (300) using fetchall  ***************"
    rows = []
    rows=dc.fetchall()
    for row in rows[:10]:
        print row
    print '   :   '
    print '   :   '
    for row in rows[-10:]:
        print row
except:
    pass
finally:
    dc.execute(x)
