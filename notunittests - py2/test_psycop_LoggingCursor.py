# test_psycop_LoggingCursor.py
# Example shows using psycopg's LoggingCursor

from rdbhdb import rdbhdb as db
from rdbhdb import extras

DictCursor = extras.DictCursor
LoggingCursor = extras.LoggingCursor
LoggingConnection = extras.LoggingConnection

role = 's000015'
authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
logconn=LoggingConnection(role, authcode=authcode)
f = open('cursor.log', 'w')
logconn.initialize(f)
logcur = logconn.cursor()

q1 = '''CREATE TABLE accounts (
            name varchar(20),
            branch_name varchar(20),
            balance real
            );'''
q2='''INSERT INTO accounts (name, branch_name, balance)
            VALUES ('Alice', 'University', 5473.0);'''
q3='''INSERT INTO accounts (name, branch_name, balance)
            VALUES ('Bob', 'Mall', 1678.0);'''
q4='''INSERT INTO accounts (name, branch_name, balance)
            VALUES ('Wally', 'Stadium', 25105.0);'''
q5 = "SELECT * FROM accounts;"
s=logcur.execute(q1)
s=logcur.execute(q2)
s=logcur.execute(q3)
s=logcur.execute(q4)
s=logcur.execute(q5)
try:
    print "\n\nFetching all rows using fetchall:\n"
    recs = logcur.fetchall()
    print(recs) 
    s=logcur.execute(q5)
    print "\n\nFetching rows one by one using fetchone:\n"
    print "Row 1:"
    #logcur = logconn.cursor()
    recs = logcur.fetchone()
    print(recs) 
    print "Row 2:"
    recs = logcur.fetchone()
    print(recs) 
    print "Row 3:"
    recs = logcur.fetchone()
    print(recs) 
    s=logcur.execute(q5)
    print "\n\nFetching several rows using fetchmany:\n"
    recs = logcur.fetchmany(size=2)
    print (recs)
#except:
#    raise db.Error('Some Error')
finally:
    logcur.execute("DROP TABLE accounts;")
    f.close()
