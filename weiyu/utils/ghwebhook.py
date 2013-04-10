#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / utilities / GitHub webhook listener
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

try:
    import ipaddress
except ImportError:
    import ipaddr as ipaddress

from ..registry.provider import request as regrequest
from ..shortcuts import *

# Valid GitHub callback IP ranges
GH_IP_WHITELIST = (
        '207.97.227.253/32',
        '50.57.128.197/32',
        '108.171.174.178/32',
        '50.57.231.61/32',
        '204.232.175.64/27',
        '192.30.252.0/22',
        )

GH_NETWORKS = [ipaddress.IPv4Network(i) for i in GH_IP_WHITELIST]


def _dummy(status):
    return (
            status,
            None,
            {
                'mimetype': 'text/plain',
                },
            )


def is_ip_whitelisted(ip):
    addr = ipaddress.IPv4Address(ip)
    return any(addr in net for net in GH_NETWORKS)


@http('gh-webhook-post-receive')
@renderable('dummy')
@view
def on_gh_post_receive(request):
    conf = regrequest('site')['github']['post-receive']

    if not is_ip_whitelisted(request.remote_addr):
        return _dummy(403)

    if request.method != 'POST':
        # TODO: a limit method decorator would be better
        return _dummy(400)

    try:
        payload_json = request.form['payload']
    except KeyError:
        return _dummy(400)

    try:
        payload = json.loads(payload_json)
    except ValueError:
        return _dummy(400)

    repo_name, ref = payload['repository']['name'], payload['ref']
    if repo_name != conf['name'] or ref not in conf['refs']:
        return _dummy(403)

    # Push accepted, execute the command given in configuration
    # Write the payload into the configured file, in effect also touching
    # it
    # FIXME: This is best done via some established deferred mechanism
    with open(conf['refs'][ref], 'wb') as fp:
        fp.write(payload_json)

    return _dummy(204)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
