#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / request service bundle / classes
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

u'''
"Reflex arc"
~~~~~~~~~~~~

This module implements the general request handling mechanism, much like
the neurological concept *reflex arc*, hence the name. Process of requests
and responses are fully customizable via the hooking machinery, which can
be done on the subclasses.

'''

from __future__ import unicode_literals, division

import abc


class BaseReflex(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def _do_accept_request(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def _do_translate_request(self, request):
        pass

    @abc.abstractmethod
    def _do_generate_response(self, request):
        pass

    def _do_postprocess(self, response):
        return response

    @abc.abstractmethod
    def _do_deliver_response(self, response):
        pass

    def stimulate(self, *args, **kwargs):
        raw_request = self._do_accept_request(*args, **kwargs)
        request = self._do_translate_request(raw_request)
        raw_response = self._do_generate_response(request)
        response = self._do_postprocess(raw_response)
        return self._do_deliver_response(response)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
