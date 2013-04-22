#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / async / views
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

from socketio import socketio_manage

from . import async_hub
from ..shortcuts import http, view


@http('socketio-handler')
@view
def socketio_bridge_view(request):
    socketio_manage(
            request.env,
            async_hub.get_namespaces('socketio'),
            request,
            )

    # XXX does this ever return?
    return (
            204,
            {},
            {},
            )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
