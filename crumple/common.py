#
# crumple/common.py
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
import sys
import time
import zlib
import platform
import subprocess
import pkg_resources

from mako.template import Template as MakoTemplate

try:
    import json
except ImportError:
    import simplejson as json

def get_version():
    """
    Returns the program version from the egg metadata

    :returns: the version of Deluge
    :rtype: string

    """
    return pkg_resources.require("crumple")[0].version

def windows_check():
    """
    Checks if the current platform is Windows

    :returns: True or False
    :rtype: bool

    """
    return platform.system() in ('Windows', 'Microsoft')

def escape(text):
    """
    Used by the gettext.js template to escape translated strings
    so they don't break the script.
    """
    text = text.replace("'", "\\'")
    text = text.replace('\r\n', '\\n')
    text = text.replace('\r', '\\n')
    text = text.replace('\n', '\\n')
    return text

def compress(contents, request):
    request.setHeader('content-encoding', 'gzip')
    compress = zlib.compressobj(6, zlib.DEFLATED, zlib.MAX_WBITS + 16,
        zlib.DEF_MEM_LEVEL,0)
    contents = compress.compress(contents)
    return contents + compress.flush()

class Template(MakoTemplate):
    """
    A template that adds some built-ins to the rendering
    """
    
    builtins = {
        "_": lambda x: x.decode('utf-8'),
        "escape": escape,
        "version": get_version()
    }
    
    def render(self, *args, **data):
        data.update(self.builtins)
        rendered = MakoTemplate.render_unicode(self, *args, **data)
        return rendered.encode('utf-8', 'replace')
