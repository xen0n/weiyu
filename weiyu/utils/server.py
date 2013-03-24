#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / utilities / server
#
# Copyright (C) 2013 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals, division

import sys
import inspect
from socket import gethostname

DEFAULT_PORT = 9090


def cli_server(application=None, port=None, hostname=None):
    try:
        from cherrypy import wsgiserver
    except ImportError:
        print >>sys.stderr, 'no cherrypy, plz run via an external wsgi server'
        sys.exit(1)

    if len(sys.argv) > 2:
        print >>sys.stderr, 'usage: %s [port=%d]' % (sys.argv[0], DEFAULT_PORT)
        sys.exit(2)

    if port is None:
        port = int(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_PORT

    if hostname is None:
        hostname = gethostname()

    if application is None:
        # inspect the outer frame's locals to get the application object, for
        # developer's convenience.
        outer_frame = inspect.getouterframes(inspect.currentframe())[1][0]
        app = outer_frame.f_globals['application']
    else:
        app = application

    server = wsgiserver.CherryPyWSGIServer(
            ('0.0.0.0', port),
            app,
            server_name=hostname,
            )

    server.start()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
