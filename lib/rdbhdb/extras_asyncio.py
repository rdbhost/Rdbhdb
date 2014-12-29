
"""
  Python 3.3 dependent features are in this module, so that py2 and py3.2- apps do not choke on them.
  The import for py2 will fail, on ImportError or SyntaxError, but importing module will function.

  If import succeeds (py3.3+), these symbols are added to importing module, so this module name is not used by
    client.
"""


from rdbhdb import rdbhdb
from rdbhdb.extras import *

src = '''
class AsyncLoggingCursor(rdbhdb.AsyncCursor, LoggingCursor):

    def _execute(self, query, vars=(), otherParms=(), addHdrs=()):
        try:
            yield from rdbhdb.AsyncCursor._execute(self, query, vars, otherParms, addHdrs)
        finally:
            self.conn.log(query, self)

class AsyncLoggingConnection(LoggingConnection):

    def cursor(self, name=None):
        self._check()
        if name is None:
            return rdbhdb.Connection.cursor(self, cursor_factory=AsyncLoggingCursor)
        else:
            return rdbhdb.Connection.cursor(self, name, cursor_factory=AsyncLoggingCursor)

'''
try:
    _c = compile(src, __name__, 'exec')
    exec(_c)
except SyntaxError as e:
    pass



