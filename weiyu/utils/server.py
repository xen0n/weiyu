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

from __future__ import unicode_literals, division, print_function

__all__ = [
        'cli_server',
        ]

import sys
import inspect
from socket import gethostname

from ..adapters import adapter_hub

DEFAULT_PORT = 9090
_SERVER_FLAVORS = {}


def expose_flavor(name):
    def _decorator_(thing):
        _SERVER_FLAVORS[name] = thing
        return thing
    return _decorator_


def get_port_number():
    if len(sys.argv) > 2:
        print(
                'usage: %s [port=%d]' % (sys.argv[0], DEFAULT_PORT),
                file=sys.stderr,
                )
        sys.exit(2)

    return int(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_PORT


def cli_server(flavor, *args, **kwargs):
    return _SERVER_FLAVORS[flavor](*args, **kwargs)


@expose_flavor('cherrypy')
def cli_server_cherrypy(application=None, port=None, hostname=None):
    try:
        from cherrypy import wsgiserver
    except ImportError:
        print(
                'no cherrypy, plz run via an external wsgi server',
                file=sys.stderr,
                )
        sys.exit(1)

    port = get_port_number() if port is None else port
    hostname = gethostname() if hostname is None else hostname

    if application is None:
        # inspect the outer frame's locals to get the application object, for
        # developer's convenience.
        outer_frame = inspect.getouterframes(inspect.currentframe())[2][0]
        app = outer_frame.f_globals['application']
    else:
        app = application

    server = wsgiserver.CherryPyWSGIServer(
            ('0.0.0.0', port),
            app,
            server_name=hostname,
            )

    server.start()


@expose_flavor('tornado')
def cli_server_tornado(server=None, port=None, hostname=None):
    try:
        from tornado import ioloop
    except ImportError:
        print(
                'import of tornado.ioloop failed, bailing',
                file=sys.stderr,
                )
        sys.exit(1)

    port = get_port_number() if port is None else port
    hostname = gethostname() if hostname is None else hostname

    if server is None:
        # NOTE: Tornado does not have the notion of "application" as WSGI.
        # The procedure to start serving requests is also different, so we
        # do not inspect the parent frame for the application object.
        # Instead, we request one from ``adapter_hub`` directly.
        server = adapter_hub.make_app('tornado')

    server.listen(port)
    ioloop.IOLoop.instance().start()


@expose_flavor('socketio')
def cli_server_socketio(listener, application=None, *args, **kwargs):
    try:
        from socketio.server import SocketIOServer
    except ImportError:
        print(
                'import of socketio.server failed, bailing',
                file=sys.stderr,
                )
        sys.exit(1)

    if application is None:
        # inspect the caller
        outer_frame = inspect.getouterframes(inspect.currentframe())[2][0]
        app = outer_frame.f_globals['application']
    else:
        app = application

    server = SocketIOServer(listener, app, *args, **kwargs)
    server.serve_forever()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
