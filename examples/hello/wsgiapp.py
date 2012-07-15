#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / hello world app
# NOTE: the recommended way to run this example is to copy the example
# directory into a virtualenv. symlinks can prevent Python from locating
# weiyu's libraries!
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
from weiyu.reflex.classes import ReflexResponse
from weiyu.adapters.wsgi import WeiyuWSGIAdapter, WSGISession

from weiyu.__version__ import VERSION_STR
from weiyu.registry.provider import request, _registries as REGS
from weiyu.rendering.decorator import renderable

OUTPUT_ENC = 'utf-8'

# load up registries
conf = JSONConfig('conf.json')
conf.populate_central_regs()

# DEBUG: db
from weiyu.db.drivers.pymongo_driver import PymongoDriver
from weiyu.db import db_hub

# DEBUG: session
from weiyu.session.beakerbackend import BeakerSession
from weiyu.session import session_hub

# DEBUG: hooks
from weiyu.hooks.decorator import *

# DEBUG: router
from weiyu.router import router_hub
from weiyu.router.regexrouter import RegexRouter


# funny thing: add color representing commit revision!
def get_git_rev_color(_re_pat=re.compile(r'Git-([0-9A-Fa-f]{6,})$')):
    result = _re_pat.findall(VERSION_STR)
    if result:
        return True, '#%s' % (result[0][:6], )
    return False, None


HAVE_GIT_COLOR, GIT_COLOR_VAL = get_git_rev_color()


def get_response(request):
    env, conf, session = request.env, request.site, request.session

    ## DEBUG: db
    #connstr = None
    #dbresult = None
    #with db_hub.get_database('test') as conn:
    #    # dummy things
    #    connstr = repr(conn)
    #    cursor = conn.ops.find(conn.storage.test, {})
    #    dbresult = ' '.join(repr(i) for i in cursor)

    # DEBUG: session
    try:
        if 'visited' in session:
            session['visited'] += 1
        else:
            session['visited'] = 1
    finally:
        session.save()

    result = dict(
            request=request,
            env=env,
            regs=REGS,
            sitename=conf['name'],
            version=VERSION_STR,
#            connstr=connstr,
#            dbresult=repr(dbresult),
            session=session,
            HAVE_GIT_COLOR=HAVE_GIT_COLOR,
            git_color=GIT_COLOR_VAL,
            )

    return result


@router_hub.endpoint('wsgi', 'index')
@renderable('mako', 'env.html')
@hookable('test-app')
def env_test_worker(request):
    return ReflexResponse(
            200,
            get_response(request),
            {
                'mimetype': 'text/html',
                'enc': OUTPUT_ENC,
            },
            request,
            )


@router_hub.endpoint('wsgi', 'multiformat-test')
@renderable('mako', 'multifmt.txt')
@renderable('json')
def multiformat_test_view(request, val):
    try:
        val = int(val)
    except ValueError:
        val = 0

    return ReflexResponse(
            200,
            {'value': val, 'results': [val + 2, val * 2, val ** 2, ], },
            {'mimetype': 'text/plain', 'enc': OUTPUT_ENC, },
            request,
            )


# DEBUG: hook & session
session_backend = BeakerSession(request('site')['session'])
session_obj = WSGISession(session_backend)

hook_before('test-app')(session_obj.pre_hook)
hook_after('test-app')(session_obj.post_hook)


# DEBUG: router
wsgi_router = router_hub.init_router(
        'wsgi',
        request('site')['routing'],
        RegexRouter,
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
