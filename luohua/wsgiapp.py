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
from collections import OrderedDict

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
@renderable('json')
def section_list_view(request):
    result = OrderedDict([
            (u'0', {u'name': u'站务系统', u'topics': [u'公告', u'意见', ], }),
            (u'1', {u'name': u'江南大学', u'topics': [u'学院', u'院系', ], }),
            (u'2', {u'name': u'文化艺术', u'topics': [u'艺术', u'音乐', ], }),
            (u'3', {u'name': u'电脑技术', u'topics': [u'电脑', u'程序', ], }),
            (u'4', {u'name': u'学术科学', u'topics': [u'学术', u'设计', ], }),
            (u'5', {u'name': u'菁菁校园', u'topics': [u'校园', u'资讯', ], }),
            (u'6', {u'name': u'知性感性', u'topics': [u'生活', u'感受', ], }),
            (u'7', {u'name': u'休闲娱乐', u'topics': [u'游戏', u'健身', ], }),
            (u'8', {u'name': u'社团群体', u'topics': [u'社团', u'群体', ], }),
            (u'9', {u'name': u'校务信箱', u'topics': [u'建议', u'反馈', ], }),
            (u'A', {u'name': u'服务专区', u'topics': [u'交易', u'服务', ], }),
            ])
    return ReflexResponse(
            200,
            {'sections': result, },
            {
                'mimetype': 'text/html',
                'enc': OUTPUT_ENC,
                },
            request,
            )


@router_hub.endpoint('wsgi', 'section')
@renderable('mako', 'section.html')
def section_view(request, sec_id):
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
