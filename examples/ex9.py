# Testing Exception Raising. Direct connection (not through API)
from urllib import urlencode
from urllib2 import Request, urlopen
import json
 
def postit(url, fields):
    postdata = urlencode(fields)
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Content-Length': str(len(postdata))}
    r = Request(url, postdata, headers)

    pg = urlopen(r)
    text = pg.read()
    return text

if __name__ == '__main__':
    role = 's000015'
    authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
    url = 'http://www.rdbhost.com/db/'+role

    q1 = '''CREATE TABLE accounts (
            name varchar(20),
            branch_name varchar(20),
            balance real
            );'''
    q2 = '''CREATE TABLE branches (
            name varchar(20),
            balance real
            );'''

    q3='''INSERT INTO accounts (name, branch_name, balance)
            VALUES ('Alice', 'University', 5473.0);'''

    q4='''INSERT INTO accounts (name, branch_name, balance)
            VALUES ('Bob', 'Mall', 1678.0);'''

    q5='''INSERT INTO accounts (name, branch_name, balance)
            VALUES ('Wally', 'Stadium', 25105.0);'''

    q6='''INSERT INTO branches (name, balance)
            VALUES ('University', 1000000.0);'''

    q7='''INSERT INTO branches (name, balance)
            VALUES ('Stadium', 1500000.0);'''

    q8='''INSERT INTO branches (name, balance)
            VALUES ('Mall', 2000000.0);'''

    # Create tables accounts and branches and enter values

    # Drop the tables created for this test

    qs = [q1, q2, q3, q4, q5, q6, q7, q8]
    for q in qs:
        flds = [ ('q', q),
                 ('format', 'xml'),
                 ('authcode', authcode) ]
        res = postit(url, flds)
        print res

    qa = '''BEGIN;'''
    qb = '''UPDATE accounts SET balance = balance - 100.00 WHERE name = 'Alice';'''
    qc = '''SAVEPOINT my_savepoint;'''
    qd = '''UPDATE accounts SET balance = balance + 100.00 WHERE name = 'Bob';'''
    qe = '''-- oops ... forget that and use Wally's account'''
    qf = '''ROLLBACK TO my_savepoint;'''
    qg = '''UPDATE accounts SET balance = balance + 100.00 WHERE name = 'Wally';'''
    qh = '''COMMIT;'''

    # Send multiple queries constituting a transaction with roll back
    # in a single access

    q = qa + qb + qc + qd + qe + qf + qg + qh
    flds = [ ('q', q),
             ('format', 'xml'),
             ('authcode', authcode) ]
    res = postit(url, flds)
    print res

    x1 = '''DROP TABLE accounts'''
    x2 = '''DROP TABLE branches'''

    # Drop the tables created for this test

    qs = [x1, x2]
    for q in qs:
        flds = [ ('q', q),
                 ('format', 'xml'),
                 ('authcode', authcode) ]
        res = postit(url, flds)
        print res
