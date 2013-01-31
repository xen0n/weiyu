#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / GitHub webhook listener
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

try:
    import ujson as json
except ImportError:
    import json

import subprocess

from weiyu.reflex.classes import ReflexResponse

from weiyu.registry.provider import request as regrequest
from weiyu.rendering.decorator import renderable
from weiyu.router import router_hub

# Valid GitHub callback IPs
GH_IP_WHITELIST = (
        '207.97.227.253',
        '50.57.128.197',
        '108.171.174.178',
        '50.57.231.61',
        )


def dummy_response(status, request):
    return ReflexResponse(
            status,
            None,
            {
                'mimetpe': 'text/plain',
                },
            request,
            )


@router_hub.endpoint('http', 'gh-webhook-post-receive')
@renderable('dummy')
def on_gh_post_receive(request):
    conf = regrequest('site')['github']['post-receive']
    dummy = lambda status: dummy_response(status, request)

    if request.remote_addr not in GH_IP_WHITELIST:
        return dummy(403)

    if request.method != 'POST':
        # TODO: a limit method decorator would be better
        return dummy(400)

    try:
        payload_json = request.form['payload']
    except KeyError:
        return dummy(400)

    try:
        payload = json.loads(payload_json)
    except ValueError:
        return dummy(400)

    repo_name, ref = payload['repository']['name'], payload['ref']
    if repo_name != conf['name'] or ref != conf['ref']:
        return dummy(403)

    # Push accepted, execute the command given in configuration
    # FIXME: This is best done via some established deferred mechanism
    # For now touching a file should be a sign of success
    # Wait... you're deploying this on Windows? Are you serious?
    touch = subprocess.Popen(
            ['touch', conf['touch'], ],
            shell=False,
            )
    touch.communicate()

    return dummy(204)


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
