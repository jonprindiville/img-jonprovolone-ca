# Based on: http://wiki.dreamhost.com/Passenger_WSGI

import os, sys

# append current dir to module path
sys.path.append(os.getcwd())

# exec virtualenv interpreter if needed
INTERP = "/home/jprind/img.jonprovolone.ca/ve/bin/python"
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# this module is in the same directory as passenger_wsgi
import ijpca
application = ijpca.site.app
