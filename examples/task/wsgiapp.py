#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / Task queue integration - WSGI file
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

from weiyu.registry.loader import JSONConfig
from weiyu.adapters.http.wsgi import WeiyuWSGIAdapter
from weiyu.router import router_hub
from weiyu.rendering.decorator import renderable
from weiyu.reflex.classes import ReflexResponse
from weiyu.tasks import task_hub

# load up registries
conf = JSONConfig('conf.json')
conf.populate_central_regs()

from tasktest.tasks import add


@router_hub.endpoint('http', 'delayed-add')
@renderable('json')
def add_view(request, r_a, r_b):
    a, b = int(r_a), int(r_b)
    r = add.delay(a, b)

    r_repr = repr(r)
    r.wait()
    r_stat, r_result = r.status, r.result

    return ReflexResponse(
            200,
            {
                'a': a,
                'b': b,
                'r': r_repr,
                'status': r_stat,
                'result': r_result,
                },
            {
                'mimetype': 'text/plain',
                'enc': 'utf-8',
                },
            request,
            )


# router
wsgi_router = router_hub.init_router_from_config('http', 'urls.txt')
router_hub.register_router(wsgi_router)


# WSGI callable
application = WeiyuWSGIAdapter()


if __name__ == '__main__':
    import sys
    from socket import gethostname

    DEFAULT_PORT = 9090

    try:
        from cherrypy import wsgiserver
    except ImportError:
        print >>sys.stderr, 'no cherrypy, plz run via an external wsgi server'
        sys.exit(1)

    if len(sys.argv) > 2:
        print >>sys.stderr, 'usage: %s [port=%d]' % (sys.argv[0], DEFAULT_PORT)
        sys.exit(2)

    port = int(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_PORT

    server = wsgiserver.CherryPyWSGIServer(
            ('0.0.0.0', port),
            application,
            server_name=gethostname(),
            )

    server.start()


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
