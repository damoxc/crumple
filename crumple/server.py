#
# crumple/server.py
#
# Copyright (C) 2010 Damien Churchill <damoxc@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.    If not, write to:
#   The Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor
#   Boston, MA    02110-1301, USA.
#

import os
import logging
from corkscrew.server import CorkscrewServer, ExtJSTopLevel
from crumple.common import get_version

log = logging.getLogger(__name__)

def rpath(*paths):
    """Convert a relative path into an absolute path relative to the location
    of this script.
    """
    return os.path.join(os.path.dirname(__file__), *paths)

class TopLevel(ExtJSTopLevel):

    jsonrpc = 'json'

    def __init__(self):
        ExtJSTopLevel.__init__(self, rpath('public'), rpath('templates'), '/', 'dev' in get_version(), rpath('gettext.js'))
        # configure the scripts
        self.js.add_folder('crumple-all',
            rpath('public', 'js', 'crumple-all'), 'dev')
        
        self.js.add_file('crumple-all-debug.js',
            rpath('public', 'js', 'crumple-all-debug.js'), 'debug')
        self.js.add_file('crumple-all.js',
            rpath('public', 'js', 'crumple-all.js'))

class CrumpleServer(CorkscrewServer):
    
    def __init__(self):
        super(CrumpleServer, self).__init__(TopLevel(), 9022)
