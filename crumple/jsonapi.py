#
# crumple/jsonapi.py
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

from twisted.internet import defer, reactor
from corkscrew.jsonrpc import export

from crumple.imap import IMAP4ClientFactory

class UserSession(object):

    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password

        onConn = defer.Deferred(
            ).addCallback(self.on_server_greeting, username, password
            ).addErrback(self.on_connection_error)

        self.factory = IMAP4ClientFactory(username, onConn)
        self.connection = reactor.connectTCP(hostname, 143, self.factory)

    def on_server_greeting(self, *args):
        pass

    def on_connection_error(self, *args):
        pass

class Core(object):

    def __init__(self):
        self.sessions = {}

    @export
    def login(self, username, password, server='localhost'):
        username = username.lower()
        session = self.sessions.setdefault(username, UserSession(
            username, password))

