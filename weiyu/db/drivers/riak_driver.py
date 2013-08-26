#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / db drivers / riak driver
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

'''
Riak Driver
~~~~~~~~~~~

This is the Riak driver for ``weiyu``.

'''

from __future__ import unicode_literals, division

import riak

from .. import db_hub
from .baseclass import BaseDriver


class RiakDriver(BaseDriver):
    def __init__(self, protocol, host, http_port, pb_port, nodes):
        super(RiakDriver, self).__init__()

        self.host, self.http_port, self.pb_port, self.nodes = (
                host,
                http_port,
                pb_port,
                nodes,
                )

        if nodes is None:
            # Let Riak client create a node for us
            # Parameters end up in RiakClient.__init__'s **unused_args,
            # which in turn are passed on to RiakNode's ctor.
            client = riak.RiakClient(
                    protocol=protocol,
                    host=host,
                    http_port=http_port,
                    pb_port=pb_port,
                    )
        else:
            # host, http_port and pb_port are ignored if a list of node
            # configurations is specified
            # TODO: provide way to config transport_options?
            client = riak.RiakClient(
                    protocol=protocol,
                    nodes=nodes,
                    )

        self.conn = client
        self._buckets = {}

    def start(self):
        # No-op.
        pass

    def finish(self):
        # No-op.
        pass

    def get_bucket(self, bucket):
        try:
            return self._buckets[bucket]
        except KeyError:
            b = self.conn.bucket(bucket)
            self._buckets[bucket] = b

        return self._buckets[bucket]

    def __repr__(self):
        return b'<weiyu.db/riak: %s:%d, prefix=%s, mapred_prefix=%s>' % (
                self.host,
                self.port,
                self.prefix,
                self.mapred_prefix,
                )


@db_hub.register_handler('riak')
def riak_handler(
        hub,
        protocol='http',
        host='127.0.0.1',
        http_port=8098,
        pb_port=8087,
        nodes=None,
        ):
    return RiakDriver(protocol, host, http_port, pb_port, nodes)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
