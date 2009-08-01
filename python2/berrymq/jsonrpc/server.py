# -*- coding: utf-8 -*-

# Almost all code comes from http://code.activestate.com/recipes/552751/

import sys


if sys.version_info[:2] == (2, 5) or sys.version_info[:2] == (2, 4):
    from server25 import SimpleJSONRPCServer
elif sys.version_info[:2] == (2, 6):
    from server26 import SimpleJSONRPCServer




