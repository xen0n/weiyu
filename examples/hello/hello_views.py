#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / hello world app - view
#
# This file is in public domain.

from __future__ import unicode_literals, division

import re

from weiyu.shortcuts import *

from weiyu.__version__ import VERSION_STR
from weiyu.registry.provider import request, _registries as REGS

OUTPUT_ENC = 'utf-8'

# DEBUG: db & mapper
from weiyu.db import db_hub, mapper_hub
from weiyu.db.mapper.base import Document

# DEBUG: session
from weiyu.session import session_hub

# DEBUG: signal
from weiyu.signals import signal_hub

from weiyu.utils.decorators import only_methods


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


@mapper_hub.decoder_for(_STRUCT_NAME, 1)
def decode1(obj):
    return {'val': obj['v1'] - 2, }


@mapper_hub.decoder_for(_STRUCT_NAME, 2)
def decode2(obj):
    return {'val': obj['v2'] >> 1, }


@mapper_hub.encoder_for(_STRUCT_NAME, 1)
def encode1(obj):
    return {'v1': obj['val'] + 2, }


@mapper_hub.encoder_for(_STRUCT_NAME, 2)
def encode2(obj):
    return {'v2': obj['val'] << 1, }


# DEBUG: session
@signal_hub.append_listener_to('signal-test')
def session_test(request):
    session = request.session

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
@view
@only_methods(['GET', 'POST', ])
def env_test_worker(request):
    signal_hub.fire('signal-test', request)

    return (
            200,
            get_response(request),
            {
                'mimetype': 'text/html',
                'enc': OUTPUT_ENC,
            },
            )


@http
@renderable('mako', 'multifmt.txt')
@renderable('json')
@view
def multiformat_test_view(request, val):
    signal_hub.fire('signal-test', request)

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
@http
@jsonview
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
@http
@jsonview
def ajax_dbtest(request):
    result = TestStruct.findall()

    return (
            200,
            {'result': list(result), },
            {'mimetype': 'application/json', },
            )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
