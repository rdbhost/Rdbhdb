# ex7 - Example using the (rudimentary)API Classes with the s role
# Shows how to extract rows from result

from rdbhdb import connection as db
from xml.etree import ElementTree as et

authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
conn=db.connect('s000015', authcode=authcode)
#print conn
c = conn.cursor(conn)
c.set_result_format('xml')
#s=c.execute('SELECT version()')
s=c.execute('SELECT * FROM weather')
print s
elem = et.XML(s)
descrip = elem[0].text            # this contains 'OK' or 'Error description'
status = elem[0].attrib['value']  # this contains 'complete', incomplete', or, 'error'
if status is 'error':
    print 'Error: '+ descrip
    print elem[1].text
else:
    print 'Status: '+ status
    nrows = elem[1].attrib['value']
    print 'Number of rows affected = ' + nrows
    numrows = int(nrows)
    records = elem[2]
    for record in records:
        for fld in record:
            print fld.text
