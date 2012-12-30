#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / luohua / Tornado test
#
# Copyright (C) 2012 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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
from weiyu.adapters.http.tornado_ import WeiyuTornadoAdapter
from weiyu.router import router_hub

from weiyu.utils.views import staticfile_view
from weiyu.session import beakerbackend

# load up registries
conf = JSONConfig('conf.json')
conf.populate_central_regs()

# view functions
from luohua import views


# router
http_router = router_hub.init_router_from_config('http', 'urls.txt')
router_hub.register_router(http_router)


if __name__ == '__main__':
    import sys
    from tornado import ioloop

    DEFAULT_PORT = 9090

    if len(sys.argv) > 2:
        print >>sys.stderr, 'usage: %s [port=%d]' % (sys.argv[0], DEFAULT_PORT)
        sys.exit(2)

    port = int(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_PORT

    server = WeiyuTornadoAdapter()
    server.listen(port)
    ioloop.IOLoop.instance().start()


# vim:ai:et:ts=4:sw=4:sts=4:ff=unix:fenc=utf-8:
