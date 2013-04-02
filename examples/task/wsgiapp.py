#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / Task queue integration - WSGI file
#
# This file is in public domain.

from __future__ import unicode_literals, division

from weiyu.shortcuts import *
from weiyu.tasks import task_hub
from weiyu.utils.server import cli_server

# load up registries
load_config('conf.json')

from tasktest.tasks import add


@http('delayed-add')
@renderable('json')
@view
def add_view(request, r_a, r_b):
    a, b = int(r_a), int(r_b)
    r = add.delay(a, b)

    r_repr = repr(r)
    r.wait()
    r_stat, r_result = r.status, r.result

    return (
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
            )


# init router and app
load_router('http', 'urls.txt')
application = make_app('wsgi')


if __name__ == '__main__':
    cli_server('cherrypy')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
