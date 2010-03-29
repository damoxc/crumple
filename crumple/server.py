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
import fnmatch
import logging
import mimetypes

from twisted.internet import reactor, defer, error
from twisted.web import http, resource, server, static

from crumple.common import Template, compress, get_version, windows_check

log = logging.getLogger(__name__)

MY_DIR = os.path.dirname(__file__)

def rpath(*paths):
    """Convert a relative path into an absolute path relative to the location
    of this script.
    """
    return os.path.join(MY_DIR, *paths)

class GetText(resource.Resource):

    def render(self, request):
        request.setHeader('content-type', 'text/javascript; encoding=utf-8')
        template = Template(filename=rpath("gettext.js"))
        return compress(template.render(), request)

class StaticResources(resource.Resource):

    def __init__(self, prefix=''):
        resource.Resource.__init__(self)
        self.__resources = {
            'normal': {
                'filemap': {},
                'order': []
            },
            'debug': {
                'filemap': {},
                'order': []
            },
            'dev': {
                'filemap': {},
                'order': []
            }
        }
        self.__prefix = prefix

    def _get_script_dicts(self, type):
        """
        Return the order list and the filemap dict for the specified
        type.

        :param type: The type to return for (dev, debug, normal)
        :type type: string
        """
        if type not in ('dev', 'debug', 'normal'):
            type = 'normal'
        type = type.lower()
        return (self.__resources[type]['filemap'],
            self.__resources[type]['order'])

    def _get_files(self, dirpath, urlpath, base):
        """
        Returns all the files within a directory in the correct order.

        :param dirpath: The physical directory the files are in
        :type dirpath: string
        """
        files = self._adjust_order(dirpath, fnmatch.filter(os.listdir(dirpath), "*.js"))
        dirpath = dirpath[len(base) + 1:]
        if dirpath:
            return [self.__prefix + '/%s/%s/%s' % (urlpath, dirpath, f) for f in files]
        else:
            return [self.__prefix + '/%s/%s' % (urlpath, f) for f in files]

    def _adjust_order(self, dirpath, files):
        """
        Fix the order of a files list by doing a .sort() and checking
        for a .order file in the dirpath.

        :param dirpath: The physical directory the files are in
        :type dirpath: string
        :param files: The list of files to adjust the order for
        :type files: list
        """
        order_file = os.path.join(dirpath, '.order')

        if os.path.isfile(order_file):

            files.sort()
            for line in open(order_file, 'rb'):
                line = line.strip()
                if not line or line[0] == '#':
                    continue
                try:
                    pos, filename = line.split()
                    files.pop(files.index(filename))
                    if pos == '+':
                        files.insert(0, filename)
                    else:
                        files.append(filename)
                except:
                    pass
        else:
            files.sort()

        return files

    def add_file(self, path, filepath, type=None):
        """
        Adds a file to the resource.

        :param path: The path of the resource
        :type path: string
        :param filepath: The physical location of the resource
        :type filepath: string
        :keyword type: The type of script to add (normal, debug, dev)
        :type type: string
        """

        (filemap, order) = self._get_script_dicts(type)
        filemap[path] = filepath
        order.append(path)

    def add_folder(self, path, filepath, type=None, recurse=True):
        """
        Adds a folder to the resource.

        :param path: The path of the resource
        :type path: string
        :param filepath: The physical location of the resource
        :type filepath: string
        :keyword type: The type of script to add (normal, debug, dev)
        :type type: string
        :keyword recurse: Whether or not to recurse into subfolders
        :type recurse: bool
        """

        (filemap, order) = self._get_script_dicts(type)
        filemap[path] = (filepath, recurse)
        order.append(path)

    def get_resources(self, type=None):
        """
        Returns a list of the resources that can be used for producing
        script/link tags.

        :keyword type: The type of resources to get (normal, debug, dev)
        :param type: string
        """
        files = []
        (filemap, order) = self._get_script_dicts(type)

        for urlpath in order:
            filepath = filemap[urlpath]

            # this is a folder
            if isinstance(filepath, tuple):
                (filepath, recurse) = filepath

                if recurse:
                    for dirpath, dirnames, filenames in os.walk(filepath, False):
                        files.extend(self._get_files(dirpath, urlpath, filepath))
                else:
                    files.extend(self._get_files(filepath, urlpath, None))

            else:
                files.append(self.__prefix + '/' + urlpath)

        return files

    def getChild(self, path, request):
        if hasattr(request, 'lookup_path'):
            request.lookup_path = os.path.join(request.lookup_path, path)
        else:
            request.lookup_path = path
        return self

    def render(self, request):
        log.debug('requested path: %s', request.lookup_path)

        for type in ('dev', 'debug', 'normal'):
            filemap = self.__resources[type]['filemap']
            for urlpath in filemap:
                if not request.lookup_path.startswith(urlpath):
                    continue

                filepath = filemap[urlpath]
                if isinstance(filepath, tuple):
                    filepath = filepath[0]

                path = filepath + request.lookup_path[len(urlpath):]
                if not os.path.isfile(path):
                    continue

                log.debug('serving path: %s', path)
                mime_type = mimetypes.guess_type(path)
                request.setHeader('content-type', mime_type[0])
                return compress(open(path, 'rb').read(), request)
        
        request.setResponseCode(http.NOT_FOUND)
        return '<h1>404 - Not Found</h1>'

class TopLevel(resource.Resource):

    addSlash = True

    def __init__(self):
        resource.Resource.__init__(self)

        css = StaticResources('css')

        css.add_file('ext-all-notheme.css',
            rpath('public', 'css', 'ext-all-notheme.css'), 'dev')
        css.add_folder('ext-extensions',
            rpath('public', 'css', 'ext-extensions'), 'dev')
        
        css.add_file('ext-all-notheme.css',
            rpath('public', 'css', 'ext-all-notheme.css'), 'debug')
        css.add_file('ext-extensions-debug.css',
            rpath('public', 'css', 'ext-extensions-debug.css'), 'debug')

        
        css.add_file('ext-all-notheme.css', rpath('public', 'css', 'ext-all-notheme.css'))
        css.add_file('ext-extensions.css', rpath('public', 'css', 'ext-extensions.css'))

        self.__css = css

        self.__icons = StaticResources()
        self.__images = StaticResources()
        
        js = StaticResources('js')

        # configure the dev scripts
        js.add_file('ext-base-debug.js', rpath('public', 'js', 'ext-base-debug.js'), 'dev')
        js.add_file('ext-all-debug.js', rpath('public', 'js', 'ext-all-debug.js'), 'dev')
        js.add_folder('ext-extensions', rpath('public', 'js', 'ext-extensions'), 'dev')
        js.add_folder('crumple-all', rpath('public', 'js', 'crumple-all'), 'dev')

        # configure the debug scripts
        js.add_file('ext-base-debug.js', rpath('public', 'js', 'ext-base-debug.js'), 'debug')
        js.add_file('ext-all-debug.js', rpath('public', 'js', 'ext-all-debug.js'), 'debug')
        js.add_file('ext-extensions-debug.js',
            rpath('public', 'js', 'ext-extensions-debug.js'), 'debug')
        js.add_file('crumple-all.js', rpath('public', 'js', 'crumple-all-debug.js'), 'debug')

        # configure the normal scripts
        js.add_file('ext-base.js', rpath('public', 'js', 'ext-base.js'))
        js.add_file('ext-all.js', rpath('public', 'js', 'ext-all.js'))
        js.add_file('ext-extensions.js', rpath('public', 'js', 'ext-extensions.js'))
        js.add_file('crumple-all.js', rpath('public', 'js', 'crumple-all.js'))

        self.__js = js

        self.putChild('css', self.__css)
        self.putChild('gettext.js', GetText())
        self.putChild('icons', self.__icons)
        self.putChild('images', self.__images)
        self.putChild('js', self.__js)
        self.putChild('themes', static.File(rpath('public', 'themes')))

    def getChild(self, path, request):
        if path == '':
            return self
        else:
            return resource.Resource.getChild(self, path, request)

    def render(self, request):
        debug = False
        if 'debug' in request.args:
            debug_arg = request.args.get('debug')[-1]
            if debug_arg in ('true', 'yes', '1'):
                debug = True
            else:
                debug = False

        dev = 'dev' in get_version()
        if 'dev' in request.args:
            dev_arg = request.args.get('dev')[-1]
            if dev_arg in ('true', 'yes' '1'):
                dev = True
            else:
                dev = False

        if dev:
            mode = 'dev'
        elif debug:
            mode = 'debug'
        else:
            mode = None

        scripts = self.__js.get_resources( mode)
        scripts.insert(0, "gettext.js")

        stylesheets = self.__css.get_resources(mode)
        stylesheets.append('themes/css/xtheme-gray.css')

        template = Template(filename=rpath("index.html"))
        request.setHeader("content-type", "text/html; charset=utf-8")

        if request.requestHeaders.hasHeader('x-deluge-base'):
            base = request.requestHeaders.getRawHeaders('x-deluge-base')[-1]
        else:
            base = CrumpleServer.instance.base

        # validate the base parameter
        if not base:
            base = '/'

        if base[0] != '/':
            base = '/' + base

        if base[-1] != '/':
            base += '/'

        #web_config = component.get("Web").get_config()
        #web_config["base"] = base
        #config = dict([(key, web_config[key]) for key in UI_CONFIG_KEYS])
        #js_config = common.json.dumps(config)
        js_config = '{}'
        return template.render(scripts=scripts, stylesheets=stylesheets,
            debug=debug, base=base, js_config=js_config)

class CrumpleServer(object):
    
    def __init__(self):

        self.socket = None
        self.top_level = TopLevel()
        self.site = server.Site(self.top_level)
        self.port = 9022
        self.https = False
        self.base = '/'
        CrumpleServer.instance = self

    def install_signal_handlers(self):
        # Since twisted assigns itself all the signals may as well make
        # use of it.
        reactor.addSystemEventTrigger("after", "shutdown", self.shutdown)

        # Twisted doesn't handle windows specific signals so we still
        # need to attach to those to handle the close correctly.
        if windows_check():
            from win32api import SetConsoleCtrlHandler
            from win32con import CTRL_CLOSE_EVENT, CTRL_SHUTDOWN_EVENT
            def win_handler(ctrl_type):
                log.debug('ctrl type: %s', ctrl_type)
                if ctrl_type == CTRL_CLOSE_EVENT or \
                    ctrl_type == CTRL_SHUTDOWN_EVENT:
                    self.shutdown()
                    return 1
            SetConsoleCtrlHandler(win_handler)

    def start(self, start_reactor=True):
        log.info('%s %s.', 'Starting server in PID', os.getpid())
        if self.https:
            self.start_ssl()
        else:
            self.start_normal()

        if start_reactor:
            reactor.run()
    
    def start_normal(self):
        self.socket = reactor.listenTCP(self.port, self.site)
        log.info('serving on %s:%s view at http://127.0.0.1:%s', '0.0.0.0',
            self.port, self.port)

    def start_ssl(self):
        check_ssl_keys()
        self.socket = reactor.listenSSL(self.port, self.site, ServerContextFactory())
        log.info('serving on %s:%s view at https://127.0.0.1:%s', '0.0.0.0',
            self.port, self.port)

    def stop(self):
        log.info('Shutting down webserver')
        log.debug('Saving configuration file')

        if self.socket:
            d = self.socket.stopListening()
            self.socket = None
        else:
            d = defer.Deferred()
            d.callback(False)
        return d

    def shutdown(self, *args):
        self.stop()
        try:
             reactor.stop()
        except:
            log.debug('Reactor not running')
