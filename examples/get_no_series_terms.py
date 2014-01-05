# Direct connection; Not through API; Prints rows of tables accounts and branches

from urllib import urlencode
from urllib2 import Request, urlopen

url = 'http://rdbhost.com/db/'+'s000015'
authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
req = Request(url)
flds0 = [('authcode', authcode)]
postdata = urlencode(flds0)
headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': str(len(postdata))}
req.add_data(postdata)
q1 = "CREATE TABLE rdbhdbTest (value) AS SELECT * FROM generate_series(1, 250)"
q = "SELECT count(*) FROM rdbhdbTest"
x1 = "DROP TABLE IF EXISTS rdbhdbTest"
try:
    flds1 = [ ('q', x1), ('format', 'xml'), ('authcode', authcode)]
    postdata = urlencode(flds1)
    req.add_data(postdata)
    pg=urlopen(req)
    text=pg.read()
    print text
    '''
    flds1 = [ ('q', x1), ('format', 'xml'), ('authcode', authcode)]
    postdata = urlencode(flds1)
    req.add_data(postdata)
    pg=urlopen(req)
    text=pg.read()
    print text
    '''
except:
    pass
finally:
    flds1 = [ ('q', x1), ('format', 'xml'), ('authcode', authcode)]
    postdata = urlencode(flds1)
    req.add_data(postdata)
    pg=urlopen(req)
    text=pg.read()
    print text
