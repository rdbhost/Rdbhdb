# test_psycop_RealDictCursor.py
# Example shows using psycopg's RealDictCursor

from rdbhdb import rdbhdb as db
from rdbhdb import extras

DictCursor = extras.DictCursor
RealDictCursor = extras.RealDictCursor
RealDictConnection = extras.RealDictConnection

authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
conn=db.connect('s000015', authcode=authcode)
rdconn=RealDictConnection('s000015', authcode=authcode)
rdc = rdconn.cursor()

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

rdc.execute(q1)
rdc.execute(q2)
rdc.execute(q3)
rdc.execute(q4)

q5 = "SELECT * FROM accounts;"

try:
    print "\n\nFetching all rows using fetchall:\n"
    s=rdc.execute(q5)
    recs = rdc.fetchall()
    print(recs) 

    print "\n\nFetching rows one by one using fetchone:\n"
    print "Row 1:"
    rdc = rdconn.cursor()
    s=rdc.execute(q5)
    rdict = rdc.fetchone()
    print(rdict) 
    print "Row 2:"
    rdict = rdc.fetchone()
    print(rdict) 
    print "Row 3:"
    rdict = rdc.fetchone()
    print(rdict)

    print "\n\nFetching several rows using fetchmany:\n"
    rdc = rdconn.cursor()
    s=rdc.execute(q5)
    recs = rdc.fetchmany(size=2)
    print (recs)
except:
    raise db.Error('Some Error')
finally:
    rdc.execute("DROP TABLE accounts;")
