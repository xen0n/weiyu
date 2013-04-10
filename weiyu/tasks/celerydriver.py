#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / tasks / Celery integration
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

import celery

from . import task_hub


class CeleryHubHandler(object):
    def build_app(self, conf, extras):
        obj = celery.Celery(**conf)
        obj.conf.update(**extras)
        return obj

    def get_task(self, appobj):
        return appobj.task


_handler = CeleryHubHandler()


@task_hub.register_handler('celery')
def _celery_handler_stub(hub):
    return _handler


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
