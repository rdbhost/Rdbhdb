# test_psycop_DictCursor.py
# Example shows using psycopg's DictCursor

from rdbhdb import rdbhdb as db
#from rdbhdb import extensions
from rdbhdb import extras

#DictCursor = extensions.DictCursor
DictCursor = extras.DictCursor

authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
conn=db.connect('s000015', authcode=authcode)
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


dc = conn.cursor(cursor_factory=DictCursor)
s=dc.execute(q1)
s=dc.execute(q2)
s=dc.execute(q3)
s=dc.execute(q4)
s=dc.execute(q5)
try:
    print "\n\nFetching all rows using fetchall:\n"
    recs = dc.fetchall()
    print(recs) 

    s=dc.execute(q5)
    print "\n\nFetching rows one by one using fetchone:\n"
    print "Row 1:"
    rdict = dc.fetchone()
    print(rdict) 
    print "Row 2:"
    rdict = dc.fetchone()
    print(rdict) 
    print "Row 3:"
    rdict = dc.fetchone()
    print(rdict) 
    print "\n\nFetching several rows using fetchmany:\n"
    s=dc.execute(q5)
    recs = dc.fetchmany(size=2)
    print (recs)
except:
    raise db.Error('Some Error')
finally:
    dc.execute("DROP TABLE accounts;")