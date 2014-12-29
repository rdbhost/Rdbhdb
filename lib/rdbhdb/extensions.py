# extensions.py - Dictionary Cursor class for rdbhdb - A PEP-249 Extension
#
# Copyright (C) 2009 David Keeney<dkeeney@rdbhost.com>
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


try:
    from rdbhdb import rdbhdb
    from rdbhdb import six
except ImportError:
    import rdbhdb
    import six

class DictCursor(rdbhdb.Cursor):

    def __init__(self, parent):
        rdbhdb.Cursor.__init__(self, parent)

    def fetchone(self):
        if not self._header:
            raise rdbhdb.ProgrammingError('rdbh10', 'No data available')
        if not self._records:
            if not self._complete:
                raise rdbhdb.Warning('rdbh11', 'Rdbhost recordset limit exceeded')
            return None
        recdict = {}
        rec = self._records.pop(0)
        for i, k in enumerate(self._header):
            recdict[k[1]] = rec[i]
        return recdict
 
    def fetchall(self):
        """Fetch all available records."""
        if not self._header:
            raise rdbhdb.ProgrammingError('rdbh10', 'No data available')
        if not self._complete:
            raise rdbhdb.Warning('rdbh11', 'Rdbhost recordset limit exceeded')
        recs = []
        while self._records:
            recdict = {}
            rec = self._records.pop(0)
            for i, k in enumerate(self._header):
                recdict[k[1]] = rec[i]
            recs.append(recdict)
        return recs
    
    def fetchmany(self, size=None):
        """Fetch multiple (default 1) records. """
        if not size:
            size = self.arraysize
        if not self._header:
            raise rdbhdb.ProgrammingError('rdbh10', 'No data available')
        recs = []
        while self._records and len(recs)<size:
            recdict = {}
            rec = self._records.pop(0)
            for i, k in enumerate(self._header):
                recdict[k[1]] = rec[i]
            recs.append(recdict)
        if len(recs) == 0 and not self._complete:
            raise rdbhdb.Warning('rdbh11', 'Rdbhost recordset limit exceeded')
        return recs

try:
    from rdbhdb.extensions_asyncio import *
except:
    pass

