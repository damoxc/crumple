#
# crumple/imap.py
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

from twisted.internet import defer, protocol, ssl, stdio
from twisted.mail import imap4
from twisted.protocols import basic
from twisted.python import log, util

class IMAP4Client(imap4.IMAP4Client):

    def serverGreeting(self, caps):
        if self.greetDeferred is not None:
            d, self.greetDeferred = self.greetDeferred, None
            d.callback(self)

    def response_IDLE(self, tag, rest):
        print tag, rest
        if tag == '*':
            cmd = self.tags[self.waiting]
            cmd.continuation(rest)

    def finishIdle(self):
        self.state = self.idle_state
        self.idle_state = None
        return self.sendLine('DONE')
    
    def startIdle(self):
        """
        Causing the client to wait for new mail changes to occur.
        """
        if 'IDLE' not in self._capCache:
            raise imap4.IllegalOperation('IDLE not supported')

        cmd = 'IDLE'
        resp = ('EXISTS', 'EXPUNGE', 'RECENT')
        d = self.sendCommand(imap4.Command(cmd, wantResponse=resp,
            continuation=self.__conIdle))
        d.addCallback(self.__cbIdle)
        self.idle_state = self.state
        self.state = 'idle'
        return d

    def __cbIdle(self, (lines, tagline)):
        return (lines, tagline)

    def __conIdle(self, *args, **kwargs):
        print args
        

class IMAP4ClientFactory(protocol.ClientFactory):
    usedUp = False

    protocol = IMAP4Client

    def __init__(self, username, onConn):
        self.ctx = ssl.ClientContextFactory()

        self.username = username
        self.onConn = onConn

    def buildProtocol(self, addr):
        assert not self.usedUp
        self.usedUp = True

        p = self.protocol(self.ctx)
        p.factory = self
        p.greetDeferred = self.onConn

        auth = imap4.CramMD5ClientAuthenticator(self.username)
        p.registerAuthenticator(auth)

        return p

    def clientConnectionFailed(self, connector, reason):
        d, self.onConn = self.onConn, None
        d.errback(reason)
