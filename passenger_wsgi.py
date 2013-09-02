# From: http://wiki.dreamhost.com/Passenger_WSGI

import os, sys, jonprovolone

INTERP = "/path/to/interpreter"
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

application = jonprovolone.site.app
