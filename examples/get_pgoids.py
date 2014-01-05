# pgoids.py -- Example using the API Classes (ver 2.0.2) with the s role
# Example shows extracting Postgress oids using RdbHost accessed through rdbhdb API.

import rdbhdb as db
authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
conn=db.connect('s000015', authcode=authcode)
#dc = conn.cursor(type='dict')
dc = conn.cursor()
recs = []
q = "SELECT COUNT(*) FROM pg_type WHERE typtype = \'b\' "
s=dc.execute(q)
recs = recs + dc.fetchall()
nrows = recs[0][0]
#print "No. of rows = " + str(nrows)
#print "\n\nFetching all oid's their type name and type element:\n"
offset = 0
recs = []
while offset < nrows :
    q = "SELECT oid, typname, typelem FROM pg_type WHERE typtype = \'b\' ORDER BY oid LIMIT 100 OFFSET %d"%offset
    #print q
    s=dc.execute(q)
    recs = recs + dc.fetchall()
    #print "\n\n"
    #print recs
    offset += 100
name_to_oid = {}
names = []
for rec in recs:
    oid, name, typelem = rec[0:3]
    oid = int(oid)
    name_to_oid[name] = oid
    names.append(name)
    typelem = int(typelem)
    print '%s = %d' % (name, oid)

print
print 'data_to_array = {'
for name in names:
    _name = '_' + name
    if not name.startswith('_') and _name in name_to_oid:
        print '    %d: %d, ' % (name_to_oid[name], name_to_oid[_name])
print '}'

print
print 'array_to_data = {'
for name in names:
    _name = '_' + name
    if not name.startswith('_') and _name in name_to_oid:
        print '    %d: %d, ' % (name_to_oid[_name], name_to_oid[name])
print '}'
