#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / luohua / WSGI application
#
# Copyright (C) 2012 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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

import re

from weiyu.registry.loader import JSONConfig
from weiyu.registry.provider import request
from weiyu.reflex.classes import ReflexResponse
from weiyu.adapters.wsgi import WeiyuWSGIAdapter
from weiyu.router import router_hub

from weiyu.__version__ import VERSION_STR
from weiyu.rendering.decorator import renderable
from weiyu.utils.views import staticfile_view
from weiyu.session import beakerbackend
OUTPUT_ENC = 'utf-8'

# load up registries
conf = JSONConfig('conf.json')
conf.populate_central_regs()


# Git commit coloring
def get_git_rev_color(_re_pat=re.compile(r'Git-([0-9A-Fa-f]{6,})$')):
    result = _re_pat.findall(VERSION_STR)
    if result:
        return True, '#%s' % (result[0][:6], )
    return False, None


HAVE_GIT_COLOR, GIT_COLOR_VAL = get_git_rev_color()


def get_response(request, **kwargs):
    env, conf, session = request.env, request.site, request.session

    result = dict(
            request=request,
            env=env,
            version=VERSION_STR,
            session=session,
            HAVE_GIT_COLOR=HAVE_GIT_COLOR,
            git_color=GIT_COLOR_VAL,
            **kwargs
            )

    return result


def to_response(request, status=200, mimetype='text/html', **kwargs):
    return ReflexResponse(
            status,
            get_response(request, **kwargs),
            {
                'mimetype': mimetype,
                'enc': OUTPUT_ENC,
                },
            request,
            )


@router_hub.endpoint('wsgi', 'index')
@renderable('mako', 'index.html')
def index_view(request):
    return to_response(request)


@router_hub.endpoint('wsgi', 'section_list')
@renderable('mako', 'section-list.html')
def section_list_view(request):
    return to_response(request)


# router
wsgi_router = router_hub.init_router(
        'wsgi',
        request('site')['routing'],
        )
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
