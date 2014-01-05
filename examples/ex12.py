# ex12 - Example using the rdbhdb API Classes with the s role

from rdbhdb import rdbhdb as db

authcode = 'KF7IUQPlwfSth4sBvjdqqanHkojAZzEjMshrkfEV0O53yz6w6v'
conn=db.connect('s000015', authcode=authcode)
#q = "GRANT ALL ON weather to s000015"
q = "COPY weather FROM 'xxx'"
#q1 = "DROP TABLE weather;DROP TABLE cities;"

q2 = '''CREATE TABLE weather (
city varchar(80),
temp_lo int, -- low temperature
temp_hi int, -- high temperature
prcp real, -- precipitation
date date
);'''

q3='''CREATE TABLE cities (
name varchar(80),
location point
);'''

q4="INSERT INTO weather VALUES ('San Francisco', 46, 50, 0.25, '1994-11-27');"

q5="INSERT INTO cities VALUES ('San Francisco', '(-194.0, 53.0)');"

q6='''INSERT INTO weather (city, temp_lo, temp_hi, prcp, date)
VALUES ('San Francisco', 43, 57, 0.0, '1994-11-29');'''

q7='''INSERT INTO weather (date, city, temp_hi, temp_lo)
VALUES ('1994-11-29', 'Hayward', 54, 37);'''


c = conn.cursor()
#s=c.execute(q1)
#s=c.execute(q2)
s=c.execute(q)
#s=c.execute(q3)
#s=c.execute(q4)
#s=c.execute(q5)
#s=c.execute(q6)
#s=c.execute(q7)
print "Done"

