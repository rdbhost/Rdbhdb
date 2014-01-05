# ex6 - Example using the (rudimentary)API Classes with the s role

from rdbhdb import connection as db
from xml.etree import ElementTree as et

authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
conn=db.connect('s000015', authcode=authcode)
#print conn
c = conn.cursor(conn)
c.set_result_format('xml')
#s=c.execute('SELECT version()')
s=c.execute('SELECT * FROM weather')
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
    for flds in records:
        for fld in flds:
            print fld.text
'''
result = elem[0]                 # self.result is of type et.Element
status = result.text        # self.status is of type string
print 'status = '+status
if status is 'Error':
    status_detail = elem[1].text
else:                                 # self.status_detail is of type string
    row_count = elem[1]      # self.result_detail is of type et.Element
print 'row_count = '+elem[1].text

# ex5 - Example using the (rudimentary)API Classes with the s role

from elementtree import ElementTree as et
from rdbhdb import connection as db

authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
conn=db.connect('s000015', authcode=authcode)
#print conn
c = conn.cursor(conn)
c.set_result_format('xml')
s=c.execute('SELECT * FROM weather')
elem = et.XML(s)
=======================
JSON
When retrieving data in JSON form, after deserializing to an object named data, data['status'][0] will always exist, and be 'complete', 'incomplete', or 'error'. If 'complete' or 'incomplete', data['rowcount'][0] will be the number of records affected. If 'error', then data['error'][0] will be the error code, and data['error'][1] will an error message. 
======================
1 <xml xmlns="http://rdbhost.com/xml.html"> 
2 <status value="complete">OK</status> 
3 <row_count value="1">1 Rows Affected</row_count> 
4 <records> 
5 <header> 
6 <fld type="23">sum</fld> 
7 </header> 
8 <rec> 
9 <fld>2</fld> 
10 </rec> 
11 </records> 
12 </xml> 
=======================
1 <xml xmlns="http://rdbhost.com/xml.html"> 
2 <status value="error">DatabaseNotOpened</status> 
3 <error code="None">FATAL: password authentication failed for user "r000004" 
4 </error> 
5 </xml> 
=======================
        amtd = response.read()             # amtd is the xml string response received
        elem = et.XML(amtd)
        self.result = elem[0]              # self.result is of type et.Element
        self.status = self.result.text     # self.status is of type string
        if self.status == 'FAIL':
            self.status_detail = elem[1].text
        else:                              # self.status_detail is of type string
            self.xml_log_in = elem[1]      # self.result_detail is of type et.Element
=======================
        amtd = response.read()      # amtd is the xml string response received
        elem = et.XML(amtd)
        self.result = elem[0]                 # self.result is of type et.Element
        self.status = self.result.text        # self.status is of type string
        print self.status
        if self.status == 'FAIL':
            self.status_detail = elem[1].text
        else:                                 # self.status_detail is of type string
            self.quote_list = elem[1]      # self.result_detail is of type et.Element

=======================
					element=et.XML(xmlText)
					tree=et.ElementTree(element)
					anchors=tree.findall('//a')
					num=len(anchors)
=======================
					admin=anchors[num-1].text
					if 'href' in anchors[num-1].attrib:
						adminmail=anchors[num-1].attrib['href']

							adminemail=et.SubElement(league, 'adminemail')
        lia = et.ElementTree(self.xml_log_in).find('/authorizations')
        self.LogInAuthorizations = {}
        for node in lia:
            self.LogInAuthorizations[node.tag] = node.text
=======================

'''