# Testing rdbhdb for Level-2 Thread Safety - i.e. threads can share connection

import sys, threading, random
from rdbhdb import rdbhdb as db

def insert(conn, table_suffix):
    cur = conn.cursor()
    rows_added = []
    for cycle in range(5):
        n = random.randint(0, 9)
        rows_added = rows_added + [n]
        for i in range(n):
            q =  "INSERT INTO thread%s VALUES (%s, %s, %s, %s)" %(table_suffix, cycle, str(i), i, float(i))
            try:
                cur.execute(q)
            except:
                raise DatabaseError('while inserting rows into table thread%s'%table_suffix)
    cur.close()
    ROWS_ADDED[table_suffix] = rows_added
    return
                
role = 's000015'
authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
conn=db.connect(role, authcode=authcode)
ROWS_ADDED = {}
THREADS = ('I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X')

qsetup = "CREATE TABLE thread%s (cycle int4, name text, value1 int4, value2 float)"

qteardown = "DROP TABLE IF EXISTS thread%s"

cur = conn.cursor()
for name in THREADS:
    #cur.execute(qsetup + '%' + name)
    cur.execute(qteardown%name)
    cur.execute(qsetup%name)
cur.close()

threads = []

print "Creating threads:"
for name in THREADS:
    t = threading.Thread(None, insert, 'thread'+name,
                         (conn, name))
    t.setDaemon(0)
    threads.append(t)

## Start the threads now
for t in threads:
    t.start()

# and wait for them to finish
for t in threads:
    t.join()
    print t.getName(), "exited OK"

cur = conn.cursor()
for name in THREADS:
    rows_added = ROWS_ADDED[name]
    print rows_added
    for cycle in range(5):
        rows = rows_added[cycle]
        q = "SELECT COUNT(*) FROM thread%s WHERE cycle = %s" %(name, cycle)
        s=cur.execute(q)
        recs = cur.fetchall()
        nrows = recs[0][0]
        print nrows
        if rows == nrows:
            continue
        else:
            raise db.DataError('Thread ' + name + ' Cycle ' + str(cycle))

print "Thread safety level 2 verified"

for name in THREADS:
    #cur.execute(qteardown + '%' + name)
    cur.execute(qteardown%name)
cur.close()
