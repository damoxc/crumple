#
# crumple/main.py
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
import optparse

def main():
    from crumple import common

    parser = optparse.OptionParser(version=common.get_version())
    parser.add_option('-b', '--base', dest='base', action='store',
        help='Set the base path that crumpled is running on (proxying)')
    parser.add_option('-f', '--fork', dest='fork', action='store_true',
        help='Fork the web interface process into the background')
    parser.add_option('-p', '--pork', dest='port', action='store',
        help='Sets the port to be used for the webserver', type=int)
    parser.add_option('--profile', dest='profile', action='store_true',
        help='Profile the web server code')
    (options, args) = parser.parse_args()

    
    if options.fork and not common.windows_check():

        if os.fork():
            os._exit(0)

        os.setsid()

        if os.fork():
            os._exit(0)

        os.chdir('/')

    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s %(levelname)-5s [%(module)s:%(lineno)d] %(message)s'
    )

    from crumple import server
    _server = server.CrumpleServer()

    if options.base:
        _server.base = options.base

    if options.port:
        _server.port = options.port

    if options.profile:
        import hotshot
        import tempfile

        stats_path = os.path.join(tempfile.tempdir, 'crumpled.profile')
        hsp = hotshot.Profile(os.path.join(stats_path))
        hsp.start()

    _server.install_signal_handlers()
    _server.start()

    if options.profile:
        hsp.stop()
        hsp.close()

        import hotshot.stats
        stats = hotshot.stats.load(stats_path)
        stats.strip_dirs()
        stats.sort_stats("time", "calls")
        stats.print_stats(400)
