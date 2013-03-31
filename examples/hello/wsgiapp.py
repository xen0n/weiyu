#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / hello world app - WSGI file
# NOTE: the recommended way to run this example is to copy the example
# directory into a virtualenv. symlinks can prevent Python from locating
# weiyu's libraries!
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

from weiyu.shortcuts import *
from weiyu.utils.server import cli_server

# load up registries
load_config('conf.json')

# DEBUG: static file
from weiyu.utils.views import staticfile_view

# app views
import hello_views

# init router and app
load_router('http', 'urls.txt')
application = make_app('wsgi')


if __name__ == '__main__':
    cli_server('cherrypy')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
