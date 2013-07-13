#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / Cache integration - view
#
# This file is in public domain.

from __future__ import unicode_literals, division

import time

from weiyu.shortcuts import *
from weiyu.cache import cache_hub


def gen_cache_key(a, b):
    return b'add_%s_%s' % (a, b, )


@http('cached-add-redis')
@jsonview
def redis_add(request, r_a, r_b):
    return do_add(request, r_a, r_b, 'main-redis')


@http('cached-add-memcached')
@jsonview
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


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
