#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / tasks / package
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

__all__ = [
        'task_hub',
        ]

from ..helpers.hub import BaseHub
from ..helpers.modprober import ModProber
from ..registry.classes import UnicodeRegistry

TASK_DRIVERS_KEY = 'drivers'
APP_OBJECTS_KEY = 'app_objects'
APP_CONF_KEY = 'conf'

PROBER = ModProber('weiyu.tasks', '%sdriver')


class TaskHub(BaseHub):
    registry_name = 'weiyu.tasks'
    registry_class = UnicodeRegistry
    handlers_key = TASK_DRIVERS_KEY

    def __init__(self):
        super(TaskHub, self).__init__()
        self._apps = self._reg[APP_OBJECTS_KEY] = {}

    def ensure_app(self, name):
        if name in self._apps:
            return

        # Read app configuration.
        dct = self._reg[APP_CONF_KEY][name]
        drv, conf, extras = dct['driver'], dct['conf'], dct['extras']

        # Load driver.
        PROBER.modprobe(drv)

        # Build app object.
        app_obj = self.do_handling(drv).build_app(conf, extras)

        # Save a reference, along with the driver type
        self._apps[name] = {
                'drv': drv,
                'obj': app_obj,
                }

    def get_app(self, name):
        try:
            return self._apps[name]['obj']
        except KeyError:
            self.ensure_app(name)
            return self._apps[name]['obj']

    def task(self, app):
        # Callback into driver layer for high-level API consistence
        try:
            appreg = self._apps[app]
        except KeyError:
            self.ensure_app(app)
            appreg = self._apps[app]

        return self.do_handling(appreg['drv']).get_task(appreg['obj'])


task_hub = TaskHub()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
