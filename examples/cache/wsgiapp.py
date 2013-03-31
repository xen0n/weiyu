#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / Cache integration - WSGI file
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

import time

from weiyu.shortcuts import *
from weiyu.cache import cache_hub
from weiyu.utils.server import cli_server

# load up registries
load_config('conf.json')


def gen_cache_key(a, b):
    return b'add_%s_%s' % (a, b, )


@http('cached-add-redis')
@renderable('json')
@view
def redis_add(request, r_a, r_b):
    return do_add(request, r_a, r_b, 'main-redis')


@http('cached-add-memcached')
@renderable('json')
@view
def mc_add(request, r_a, r_b):
    return do_add(request, r_a, r_b, 'main-mc')


def do_add(request, r_a, r_b, cache_name):
    a, b = int(r_a), int(r_b)

    # prepare cache key
    c_key = gen_cache_key(*((a, b) if a < b else (b, a)))

    cache = cache_hub.get_cache(cache_name)
    r = cache.get(c_key)

    r_stat = 'MISS' if r is None else 'HIT'
    if r is None:
        # simulate some expensive processing
        r = a + b
        time.sleep(0.01 * r)

        # update cache
        cache.set(c_key, r)

    return (
            200,
            {
                'a': a,
                'b': b,
                'key': c_key,
                'status': r_stat,
                'result': r,
                },
            {
                'mimetype': 'text/plain',
                'enc': 'utf-8',
                },
            )


# init router and app
load_router('http', 'urls.txt')
application = make_app('wsgi')


if __name__ == '__main__':
    cli_server('cherrypy')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
