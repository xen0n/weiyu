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


def to_response(request, status=200, mimetype='text/html', **kwargs):
    return ReflexResponse(
            status,
            kwargs,
            {
                'mimetype': mimetype,
                'enc': OUTPUT_ENC,
                'request': request,
                'env': request.env,
                'session': request.session,
                'version': VERSION_STR,
                'HAVE_GIT_COLOR': HAVE_GIT_COLOR,
                'git_color': GIT_COLOR_VAL,
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
    result = [
            {u'ord': u'0', u'name': u'站务系统', u'topics': [u'公告', u'意见', ], },
            {u'ord': u'1', u'name': u'江南大学', u'topics': [u'学院', u'院系', ], },
            {u'ord': u'2', u'name': u'文化艺术', u'topics': [u'艺术', u'音乐', ], },
            {u'ord': u'3', u'name': u'电脑技术', u'topics': [u'电脑', u'程序', ], },
            {u'ord': u'4', u'name': u'学术科学', u'topics': [u'学术', u'设计', ], },
            {u'ord': u'5', u'name': u'菁菁校园', u'topics': [u'校园', u'资讯', ], },
            {u'ord': u'6', u'name': u'知性感性', u'topics': [u'生活', u'感受', ], },
            {u'ord': u'7', u'name': u'休闲娱乐', u'topics': [u'游戏', u'健身', ], },
            {u'ord': u'8', u'name': u'社团群体', u'topics': [u'社团', u'群体', ], },
            {u'ord': u'9', u'name': u'校务信箱', u'topics': [u'建议', u'反馈', ], },
            {u'ord': u'A', u'name': u'服务专区', u'topics': [u'交易', u'服务', ], },
            ]
    return to_response(request, sections=result)


@router_hub.endpoint('wsgi', 'section')
@renderable('mako', 'section.html')
@renderable('json')
def section_view(request, sec_id):
    result = [
            {u'id': u'Android', u'name': u'Android世界', u'topics': [u'待定', ], u'bm': [], },
            {u'id': u'Apple', u'name': u'Apple', u'topics': [u'苹果', ], u'bm': [u'wangshuang', ], },
            {u'id': u'ComputerPark', u'name': u'电脑天地', u'topics': [u'电脑', ], u'bm': [u'liqu1d', ], },
            {u'id': u'JNRainerds', u'name': u'技术沙龙', u'topics': [u'交流', ], u'bm': [], },
            {u'id': u'Linux', u'name': u'Linux', u'topics': [u'学术', ], u'bm': [u'akira', ], },
            {u'id': u'MobileDigit', u'name': u'玩转数码', u'topics': [u'电脑', ], u'bm': [], },
            {u'id': u'Program', u'name': u'程序语言', u'topics': [u'编程', ], u'bm': [], },
            {u'id': u'Resources', u'name': u'听雨资源', u'topics': [u'资源', ], u'bm': [u'pin', ], },
            {u'id': u'Vista', u'name': u'Windows', u'topics': [u'电脑', ], u'bm': [], },
            {u'id': u'website', u'name': u'网站建设', u'topics': [u'待定', ], u'bm': [], },
            ]
    return to_response(request, sec_id=sec_id, boards=result)


@router_hub.endpoint('wsgi', 'hot-global')
@renderable('json')
def global_hot_view(request):
    result = [
            {
                u'id': 123 + i,
                u'board': u'A.JNRainClub',
                u'title': u'测试1_%d' % i,
                u'author': u'xenon',
                }
            for i in range(10)
            ]
    return to_response(request, type=u'global', posts=result)


@router_hub.endpoint('wsgi', 'hot-section')
@renderable('json')
def section_hot_view(request, sec_id):
    result = [
            {
                u'id': 234 + i,
                u'board': u'ComputerPark',
                u'title': u'测试2_%d' % i,
                u'author': u'xenon',
                }
            for i in range(10)
            ]
    return to_response(request, type=u'sec', sec_id=sec_id, posts=result)


@router_hub.endpoint('wsgi', 'hot-board')
@renderable('json')
def board_hot_view(request, board):
    result = [
            {
                u'id': 345 + i,
                u'board': board,
                u'title': u'测试3_%d' % i,
                u'author': u'xenon',
                }
            for i in range(10)
            ]
    return to_response(request, type=u'board', board=board, posts=result)



# router
wsgi_router = router_hub.init_router_from_config('wsgi', 'urls.txt')
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
