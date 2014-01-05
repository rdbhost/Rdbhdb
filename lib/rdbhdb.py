# rdbhdb.py - PEP-249 conformant python db API for RdbHost database web service
#
# Copyright (C) 2009-2014 David Keeney<dkeeney@rdbhost.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# Developed by - 
# David Keeney<dkeeney@rdbhost.com> and Kris Sundaram<sundram@hotmail.com>
# Maintained by - David Keeney<dkeeney@rdbhost.com>

"""PEP-249 conformant python db API for RdbHost database web service"""


import sys
import time
import datetime
import re
import threading
import types
from decimal import Decimal
import zlib

try:
    from rdbhdb import pgoid
    from rdbhdb import six
except ImportError as e:
    import pgoid
    import six
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        from django.utils import simplejson as json
import urllib3

__version__ = '0.9.5'


threadsafety = 2
paramstyle = 'pyformat' # format
apilevel = '2.0'

MAX_UNCOMPRESSED_SIZE = 1024


def connect(role, authcode, host='www.rdbhost.com'):
    """Connect to the remote database. Return Connection object. """
    return Connection(host, role, authcode)


class DBAPITypeObject:
    """Type object.  One instance can compare positive to multiple 
    Postgres field types.  This class taken from API PEP-249 doc.
    """
    def __init__(self, *values):
        self.values = values
    def __cmp__(self, other):
        if other in self.values:
            return 0
        if other < self.values:
            return 1

# implements type object instances for the API mandated types.  
#
STRING = DBAPITypeObject(
    pgoid.bpchar, 
    pgoid.char, 
    pgoid.name, 
    pgoid.text, 
    pgoid.varchar,
)
BINARY = DBAPITypeObject(
    pgoid.bytea
)
NUMBER = DBAPITypeObject(
    pgoid.float4, 
    pgoid.float8, 
    pgoid.int2, 
    pgoid.int4, 
    pgoid.int8, 
    pgoid.numeric,
)
DATETIME = DBAPITypeObject(
    pgoid.interval, 
    pgoid.timestamp, 
    pgoid.timestamptz, 
    pgoid.tinterval,
)
ROWID = DBAPITypeObject(
    pgoid.oid,
)
# define API types as stdlib types
if six.PY3:
    Binary = lambda s: s.encode('utf-8')
    binTest = bytes
else:
    Binary = buffer
    binTest = buffer
Date = datetime.date
Time = datetime.time
Timestamp = datetime.datetime

# simple conversion functions
def DateFromTicks(ticks):
    return Date(*time.localtime(ticks)[:3])
def TimeFromTicks(ticks):
    return Time(*time.localtime(ticks)[3:6])
def TimestampFromTicks(ticks):
    return Timestamp(*time.localtime(ticks)[:6])

# define the heirarchy of API exceptions
class RdbhostError(Exception): pass
class Warning(RdbhostError): pass
class Error(RdbhostError): pass
class InterfaceError(Error): pass
class DatabaseError(Error): pass
class DataError(DatabaseError): pass
class OperationalError(DatabaseError): pass
class IntegrityError(DatabaseError): pass
class InternalError(DatabaseError): pass
class ProgrammingError(DatabaseError): pass
class NotSupportedError(DatabaseError): pass

def getTypeOf(p):
    """Returns string with DB API data type for p"""
    if type(p) in (type(1.0), ) or isinstance(p, six.integer_types):
        return 'NUMBER'
    if isinstance(p, binTest):
        return 'BINARY'
    if p is None:
        return 'NONE'
    if isinstance(p, datetime.datetime):
        return 'DATETIME'
    if isinstance(p, datetime.date):
        return 'DATE'
    if isinstance(p, datetime.time):
        return 'TIME'
    return 'STRING'

def toDate(datestring):
    #YYYY-MM-DDTHH:MM:SS.mmmmmm+tz
    if datestring is None:
        return None
    datestring = datestring.split(' ', 1)[0]
    y, m, d = datestring.split('-')
    return datetime.date(int(y), int(m), int(d))
    
def toTime(timestring):
    if timestring is None:
        return None
    if ' ' in timestring:
        timestring = timestring.split(' ', 1)[1]
    timestring = timestring.split('+', 1)[0]
    h, mi, s = timestring.split(':')
    if '.' in s:
        s, u = s.split('.', 1)
        u = ('000000'+u)[-6:]
    else:
        u = 0
    return datetime.time(int(h), int(mi), int(s), int(u))

def toDateTime(timedatestring):
    if timedatestring is None:
        return None
    if ' ' in timedatestring:
        datestring, timestring = timedatestring.split(' ', 1)
        timestring = timestring.split('+', 1)[0]
    else:
        datestring = timedatestring
        timestring = '0:0:0'
    y, m, d = datestring.split('-')
    h, mi, s = timestring.split(':')
    if '.' in s:
        s, u = s.split('.', 1)
        u = ('000000'+u)[-6:]
    else:
        u = 0
    return datetime.datetime(int(y), int(m), int(d), int(h), int(mi), int(s), int(u))

TIMEDATEDEC_FIELD_CODES = [1082, 1083, 1266, 1184, 1114, 1700]
def replaceDateTimeDec(header, rows):

    tochange = []
    for i, h in enumerate(header):
        if h[0] in TIMEDATEDEC_FIELD_CODES:
            tochange.append((i, h[0]))

    if not tochange:
        return

    for i, r in enumerate(rows):
        row = list(r)
        for tdflds in tochange:
            new = None
            idx, code = tdflds
            orig = row[idx]
            if code == 1082:
                new = toDate(orig)
            elif code in (1083, 1266):
                new = toTime(orig)
            elif code in (1184, 1114):
                new = toDateTime(orig)
            elif code == 1700:
                if orig is None: new = None
                else: new = Decimal(orig)
            else:
                assert code not in TIMEDATEDEC_FIELD_CODES, code
            row[idx] = new

        rows[i] = tuple(row)

class Connection(object):
    """Connection object.  Generates cursors for database operations.  
    Most specific ops handled by cursors themselves.
    Note that this is an rdbhost connection, not a postgresql connection. 
    """
    
    # set this to True, if you want cursors to work around the 100 records
    #  per execute limit.
    autorefill = False

    # data is compressed/decompressed by default
    compression = True

    # is tls/ssl needed
    https = True # False

    def __init__(self, host, role, authcode):
        """Obtain a connection to RdbHost database web service"""
        self.host = host
        self.role = role
        self.authcode = authcode
        self._lock = threading.Lock()
    
    def close(self):
        """Close the connection.  Further operations on closed connection
        will raise exceptions.
        """
        self._lock.acquire()
        try:
            if not self.role:
                raise ProgrammingError('-', 'Connection already closed')
            self.role = self.authcode = None
        finally:
            self._lock.release()

    def cursor(self, cursor_factory=None):
        """Create cursor.  If autorefill is set to true, will create
        an autorefilling cursor.  Otherwise not.  Passing a cursor class
        as the 'cursor_factory' will create that type of cursor.
        """
        self._lock.acquire()
        try:
            if not cursor_factory:
                cur = Cursor(self)
            else:
                cur = cursor_factory(self)
            if self.autorefill:
                cur = AutoRefill(self, cur)
        finally:
            self._lock.release()
        return cur

    def commit(self):
        """Phony commit.  Does nothing. """
        self._lock.acquire()
        try:
            if not self.role:
                raise ProgrammingError('-', 'Connection closed before commit')
        finally:
            self._lock.release()

    def rollback(self):
        """Rollback not supported.  Raise exception. """
        raise NotSupportedError('This module does not support rollback.')


class Cursor(object):
    """Cursor object handles all database operations. """
    
    def __init__(self, conn):
        """Create cursor object."""
        self.conn = conn
        self.arraysize = 1
        self.rowcount = -1
        self.description = None
        self._complete = None
        self._header = None
        self._records = None
        self._rawbodysize = None
        
    def close(self):
        """Close the cursor. Render it unable to act further. """
        self = None

    def setoutputsize(self, size, o=None):
        """Ignored. Optional in API """
        pass
    
    def setinputsizes(self, size, o=None):
        """Ignored.  Optional in API """
        pass
    
    def describe(self, header):
        """Return description fields. """
        d = []
        for f in header:
            typ, nm = f
            d.append((nm, typ, None, None, None, None, None))
        return d
    
    def raw(self):  
        """return info about raw data recieved from server. """
        return 'json', self._rawbodysize
    
    def _convert_to_tuple_form(self, query, dictargs):
        """Convert dictionary type args to tuple form"""
        assert isinstance(dictargs, dict)
        #Preprocessing to convert pyformatted query to formatted query
        p = re.compile('\%\((\w+)\)s')
        L = re.findall(p, query)
        parms = []
        assert len(L) <= 100000, len(L)
        for i in range(len(L)):
           key = L[i]
           # create tuple and add to new args list
           tup = 'arg%05d' % i, dictargs[key]
           parms.append(tup)
           ttup = tup[0]+'type', getTypeOf(dictargs[key])
           parms.append(ttup)
           # remove name from named parm in query
           old = ''.join(['%(', key, ')'])
           query=query.replace(old, '%', 1)
        return query, tuple(parms)

    def execute(self, query, args=()):
        """Execute query with optional args """
        assert type(args) in (type((1, 2)), type([]), type({}), type(None)), (type(args), args)
        self.conn._lock.acquire()
        try:
            self._execute(query, args, (), ())
        finally:
            self.conn._lock.release()
    
    def executemany(self, query, argslist):
        """Execute query multiple times, once per arg set."""
        self.conn._lock.acquire()
        try:
            for a in argslist:
                self._execute(query, a, (), ())
            self.rowcount = -1
            return None
        finally:
            self.conn._lock.release()
    
    def execute_deferred(self, query, args=()):
        """Execute query with optional args, so that execution is deferred
        until after method returns.
        """
        self.conn._lock.acquire()
        try:
            addparms = (('deferred', 'yes'), )
            self._execute(query, args, addparms, ())
        finally:
            self.conn._lock.release()
    
    def _execute(self, query, args, otherparms, addhdrs):
        """Private method to handle core of execute and executemany """

        parms = []
        if not self.conn.role:
            raise ProgrammingError('-', 'Connection closed before execute')

        if args:

            if isinstance(args, dict):

                query, parms = self._convert_to_tuple_form(query, args)

            else:
                for i, val in enumerate(args):
                    key = 'arg%05d' % i
                    typ = getTypeOf(val)
                    tkey = 'argtype' + key[3:]
                    #print >> sys.stderr, 'type: ', typ
                    if typ == 'BINARY':
                        parms.append((key, ('file', val)))
                    else:
                        parms.append((key, val))
                    parms.append((tkey, typ))

        if otherparms:
            for ap in otherparms:
                assert type(ap) == type((1, 2)), type(ap)
                parms.append(ap)

        datareceived = stuff = False

        for _i in range(3):
            txt = None
            try:
                hdrs, txt = post_it(self.conn.role, self.conn.authcode, self.conn.host, 'json', query, parms, addhdrs)
                self._rawbodysize = len(txt)
                stuff = json.loads(txt)
                if stuff['status'][0] != 'error' or stuff['error'][0] != 'rdb03':  # if query timeout, retry
                    datareceived = True
                    break
                else:
                    time.sleep(0.25)
                    continue

            except ValueError as e:
                raise InterfaceError('??', 'JSON not converted [%s]' % txt)

            except urllib3.exceptions.ConnectTimeoutError as e:
                continue

            except urllib3.exceptions.HTTPError as e:
                break

        if not datareceived:
            raise InterfaceError('rdbhdb09', 'Http connection failed -> received %s' % txt)

        if stuff and 'status' in stuff and stuff['status'][0] == 'error':
            excName = stuff['status'][1]
            code, msg = stuff['error'][0], stuff['error'][1]
            rdbex = sys.modules['rdbhdb.rdbhdb']
            exc = rdbex.__dict__[excName](code, msg)
            raise exc

        elif stuff['status'][0] == 'delayed':
            self._records = None
            self._header = None
            self.description = None
            self.rowcount = -1
            self._complete = False

        else:
            self._complete = stuff['status'][0] == 'complete'
            if 'result_sets' in stuff:
                self._resultsets = stuff['result_sets']
                self._nextset(stuff)

            else:
                if 'records' in stuff:
                    self.description = self.describe(stuff['records']['header'])
                    self.rowcount = stuff['row_count'][0]
                    self._header = stuff['records']['header']
                    if self._header:
                        if 'rows' in stuff['records']:
                            self._records = stuff['records']['rows']
                            replaceDateTimeDec(self._header, self._records)
                        else:
                            self._records = []
                    else:
                        self._records = None

                else:
                    self._header = None
                    self._records = None
                    self.rowcount = stuff['row_count'][0]
                    if self.rowcount == -1:
                        self.description = None
                    else:
                        self.description = []

        return stuff['status']
        
    def _nextset(self, stuff):
        """Advances to next result set.  Returns None if no more. """
        if not self._resultsets:
            return None
        resultset = self._resultsets.pop(0)
        if 'records' in resultset:
            stuff['records'] = resultset['records']
        if resultset['row_count']:
            stuff['row_count'] = resultset['row_count']
        else:
            stuff['row_count'] = None
        self._complete = resultset['status'][0] == 'complete'
        if 'records' in stuff:
            self.description = self.describe(stuff['records']['header'])
            self.rowcount = stuff['row_count'][0]
            self._header = stuff['records']['header']
            if self._header:
                if 'rows' in stuff['records']:
                    self._records = stuff['records']['rows']
                    replaceDateTimeDec(self._header, self._records)
                else:
                    self._records = []
            else:
                self._records = None
        else:
            self._header = None
            self._records = None
            self.rowcount = stuff['row_count'][0]
            if self.rowcount == -1:
                self.description = None
            else:
                self.description = []
        return True

    def fetchone(self):
        """Fetch one record."""
        self.conn._lock.acquire()
        try:
            if not self._header:
                raise ProgrammingError('rdbhdb10', 'No data available')
            if not self._records:
                if not self._complete:
                    raise Warning('rdbhdb11', 'Rdbhost recordset limit exceeded')
                return None
            rec = self._records.pop(0)
            return tuple(rec)
        finally:
            self.conn._lock.release()
    
    def fetchall(self):
        """Fetch all available records."""
        self.conn._lock.acquire()
        try:
            if not self._header:
                raise ProgrammingError('rdbhdb10', 'No data available')
            recs = []
            if not self._complete:
                raise Warning('rdbhdb11', 'Rdbhost recordset limit exceeded')
            while self._records:
                r = self._records.pop(0)
                recs.append(tuple(r))
            return recs
        finally:
            self.conn._lock.release()
    
    def fetchmany(self, size=None):
        """Fetch multiple (default 1) records. """
        self.conn._lock.acquire()
        try:
            if not size:
                size = self.arraysize
            if not self._header:
                raise ProgrammingError('rdbhdb10', 'No data available')
            recs = []
            if len(self._records) < size and not self._complete:
                raise Warning('rdbhdb11', 'Rdbhost recordset limit exceeded')
            while self._records and len(recs)<size:
                r = self._records.pop(0)
                recs.append(tuple(r))
            return recs
        finally:
            self.conn._lock.release()

    def nextset(self):
        """Get next set of results. """
        if not self._resultsets:
            self._header = None
            self._records = None
            self.rowcount = -1
            return None
        stuff = {}
        return self._nextset(stuff)
 
           
# sql rewriter, to add/modify OFFSET, and if apropos, modify LIMIT
def modify_query(query, offset):
    q = r'SELECT * FROM (%s) AS "rdbhdbsqlrewriter" OFFSET %s' % (query, offset)
    return q

    
class AutoRefill(Cursor):
    """Autorefilling Cursor, that works around rdbhost 100 records
    per request limit.  Modifies query, and transparently resubmits query 
    to gather additional records when a fetch*() method attempts to reach 
    beyond the 100 record limit of RdbHost
    Delegates all cursor-specific operations to delegate cursor, passed
    as constructor param.
    """
    def __init__(self, conn, cur):
        """Init
        cur param is an instantiated cursor of another class.
        """
        self.conn = conn
        self._cursor = cur
        self._offset = 0
        self._limit = 0
        self._args = None
        self._query = None

    def execute(self, query, args=()):
        self._args = args
        self._query = query
        return self._cursor.execute(query, args)
            
    def executemany(self, query, argslist):
        """Execute query multiple times, once per arg set."""
        for a in argslist:
            self.execute(query, a)
        self._cursor.rowcount = -1
        return None
    
    def fetchone(self):
        try:
            rec = self._cursor.fetchone()
            return rec
        except Warning as w:
            if w.args[0] == 'rdbhdb11':
                self._refill_records()
                return self.fetchone()
            else:
                raise

    def fetchmany(self, size=None):
        try:
            recs = self._cursor.fetchmany(size)
            return recs
        except Warning as w:
            if w.args[0] == 'rdbhdb11':
                self._refill_records()
                return self.fetchmany(size)
            else:
                raise

    def fetchall(self):
        try:
            recs = self._cursor.fetchall()
            return recs    
        except Warning as w:
            if w.args[0] == 'rdbhdb11':
                self._refill_records()
                return self.fetchall()
            else:
                raise

    def _refill_records(self):
        """Resubmit query to retrieve additional records beyond
        the previous truncation point using SQL's OFFSET modifier.
        """
        self._offset += 100
        query = modify_query(self._query, self._offset)
        rows = self._cursor._records
        self._cursor._records = []
        self._cursor.execute(query, self._args)
        rows.extend(self._cursor._records)
        self._cursor._records = rows

    # various attributes of cursor implemented here as 'pass-throughs'
    def _getrc(self):
        return self._cursor.rowcount

    rowcount = property(_getrc, None, None)

    def _getary(self): 
        return self._cursor.arraysize

    def _setary(self, v):
        self._cursor.arraysize = v

    arraysize = property(_getary, _setary, None)

    def _getdesc(self):
        return self._cursor.description

    description = property(_getdesc, None, None)


def post_it_sync(role, authcode, host, fmt, q, flds, addhdrs):
    """post fields to url via POST, return result page. """

    fields = {'q': q,
              'format': fmt,
              'authcode': authcode}
    for f in flds:
        fields[f[0]] = f[1]

    body, content_type = urllib3.filepost.encode_multipart_formdata(fields or {})

    headers = {'Accept-Encoding': 'gzip',
               'Content-Type': content_type}
    for h in addhdrs:
        headers[h[0]] = h[1]

    if len(body) > MAX_UNCOMPRESSED_SIZE:
        body = zlib.compress(body, 6)
        headers['Content-Encoding'] = 'gzip'

    conn = urllib3.HTTPSConnectionPool(host, timeout=20)

    r = conn.urlopen('POST', '/db/'+role, body=body, headers=headers, retries=5, assert_same_host=True)

    # return headers and body
    headers = r.headers
    text = r.data.decode('utf-8')

    return headers, text

    
post_it = post_it_sync

##