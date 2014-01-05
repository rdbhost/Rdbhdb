# Direct connection; Not through API; Creates table test and then deletes it.

from urllib import urlencode
from urllib2 import Request, urlopen

url = 'http://rdbhost.com/db/'+'s000015'
authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
req = Request(url)
flds0 = [('authcode', authcode)]
postdata = urlencode(flds0)
headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': str(len(postdata))}
req.add_data(postdata)
q1 = '''CREATE TABLE test (
city varchar(80),
temp_lo int, -- low temperature
temp_hi int, -- high temperature
prcp real, -- precipitation
date date
);'''
q2 = "DROP TABLE test;"
flds1 = [ ('q', q1), ('format', 'xml'), ('authcode', authcode)]
postdata = urlencode(flds1)
req.add_data(postdata)
pg=urlopen(req)
text=pg.read()
print text
flds2 = [ ('q', q2), ('format', 'xml'), ('authcode', authcode)]
postdata = urlencode(flds2)
req.add_data(postdata)
pg=urlopen(req)
text=pg.read()
print text
