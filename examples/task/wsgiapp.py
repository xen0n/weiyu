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
from weiyu.shortcuts import *
from weiyu.tasks import task_hub
from weiyu.utils.server import cli_server

# load up registries
conf = JSONConfig('conf.json')
conf.populate_central_regs()

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
