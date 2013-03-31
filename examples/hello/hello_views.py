#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / hello world app - view
#
# Copyright (C) 2012-2013 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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
from weiyu.shortcuts import *

from weiyu.__version__ import VERSION_STR
from weiyu.registry.provider import request, _registries as REGS

OUTPUT_ENC = 'utf-8'

# DEBUG: db & mapper
from weiyu.db.drivers.pymongo_driver import PymongoDriver
from weiyu.db import db_hub, mapper_hub
from weiyu.db.mapper.base import Document

# DEBUG: session
from weiyu.session.beakerbackend import BeakerSession
from weiyu.session import session_hub

# DEBUG: hooks
from weiyu.hooks.decorator import *

# DEBUG: static file
from weiyu.utils.views import staticfile_view


# funny thing: add color representing commit revision!
def get_git_rev_color(_re_pat=re.compile(r'Git-([0-9A-Fa-f]{6,})$')):
    result = _re_pat.findall(VERSION_STR)
    if result:
        return True, '#%s' % (result[0][:6], )
    return False, None


HAVE_GIT_COLOR, GIT_COLOR_VAL = get_git_rev_color()


# DEBUG: mapper
# Test case:
# original data {'val': x, }
# ver 1. {'v1': x + 2, }
# ver 2. {'v2': x * 2, }
_STRUCT_NAME = 'teststruct'
mapper_hub.register_struct(_STRUCT_NAME)


class TestStruct(Document):
    struct_id = _STRUCT_NAME

    def __init__(self, *args, **kwargs):
        super(TestStruct, self).__init__(*args, **kwargs)

        try:
            self.pop('_id')
        except KeyError:
            pass


@mapper_hub.decoder_for(_STRUCT_NAME, 1)
def decode1(obj):
    _id = obj.get('_id', None)
    return TestStruct(val=obj['v1'] - 2, _id=_id)


@mapper_hub.decoder_for(_STRUCT_NAME, 2)
def decode2(obj):
    _id = obj.get('_id', None)
    return TestStruct(val=obj['v2'] >> 1, _id=_id)


@mapper_hub.encoder_for(_STRUCT_NAME, 1)
def encode1(obj):
    return {'v1': obj['val'] + 2, }


@mapper_hub.encoder_for(_STRUCT_NAME, 2)
def encode2(obj):
    return {'v2': obj['val'] << 1, }


# DEBUG: session
def session_test(session):
    if 'visited' in session:
        session['visited'] += 1
    else:
        session['visited'] = 1
    session.save()


def get_response(request):
    env, conf, session = request.env, request.site, request.session

    result = dict(
            request=request,
            env=env,
            regs=REGS,
            sitename=conf['name'],
            version=VERSION_STR,
            session=session,
            HAVE_GIT_COLOR=HAVE_GIT_COLOR,
            git_color=GIT_COLOR_VAL,
            )

    return result


@http('index')
@renderable('mako', 'env.html')
@hookable('test-app')
@view
def env_test_worker(request):
    session_test(request.session)

    return (
            200,
            get_response(request),
            {
                'mimetype': 'text/html',
                'enc': OUTPUT_ENC,
            },
            )


@http('multiformat-test')
@renderable('mako', 'multifmt.txt')
@renderable('json')
@view
def multiformat_test_view(request, val):
    session_test(request.session)

    try:
        val = int(val)
    except ValueError:
        val = 0

    return (
            200,
            {
                'visits': request.session['visited'],
                'value': val,
                'results': [val + 2, val * 2, val ** 2, ],
                },
            {'mimetype': 'text/plain', 'enc': OUTPUT_ENC, },
            )


# a simple Ajax servicing routine
@http('ajax-doubler')
@renderable('json')
@view
def ajax_doubler(request, number):
    num = None
    try:
        num = int(number)
    except ValueError:
        pass

    if num is not None:
        num *= 2

    return (
            200,
            {'result': num, },
            {'mimetype': 'application/json', },
            )


# benchmark purpose: json w/ db access
@http('ajax-dbtest')
@renderable('json')
@view
def ajax_dbtest(request):
    result = TestStruct().findall()

    return (
            200,
            {'result': list(result), },
            {'mimetype': 'application/json', },
            )


## DEBUG: hook & session
#session_backend = BeakerSession(request('site')['session'])
#session_obj = WSGISession(session_backend)
#
#hook_before('test-app')(session_obj.pre_hook)
#hook_after('test-app')(session_obj.post_hook)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
