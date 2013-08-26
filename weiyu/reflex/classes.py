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

'''
Reflex-like request handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module implements the general request handling mechanism, much like
the neurological concept *reflex arc*, hence the name. Process of requests
and responses are fully customizable via the hooking machinery, which can
be done on the subclasses.

'''

from __future__ import unicode_literals, division

import abc

import six


class ReflexRequest(dict):
    '''Class representing a protocol-independent request.'''

    def __init__(self, env, *args, **kwargs):
        self.env = env


class ReflexResponse(dict):
    '''Class describing a protocol-independent response.'''

    def __init__(self, status, content, context=None, request=None):
        self.status = status
        self.content = content
        self.context = context or {}
        self.request = request


class BaseReflex(six.with_metaclass(abc.ABCMeta)):
    '''Abstract reflex class.

    Responses are obtained by calling :meth:`stimulate`, which "excites" the
    several ``_do_*`` methods in order. Among these methods
    :meth:`_do_accept_request`, :meth:`_do_generate_response` and
    :meth:`_do_deliver_response` are abstract; they are to implement the bare
    minimum of code to parse incoming requests into protocol-agnostic form,
    to generate a response, to transform and deliver the response object,
    thus subclasses must provide implementations.

    '''

    @abc.abstractmethod
    def _do_accept_request(self, *args, **kwargs):
        '''Called to convert protocol-specific request parameters into an
        instance of a certain subclass of :class:`.ReflexRequest`, for
        further processing.

        This method is abstract.

        '''

        pass

    def _do_translate_request(self, request):
        '''Called to perform various protocol-agnostic transformations on
        ``request``, such as applying middleware parameters or recording
        session information.

        The default implementation does nothing: it just returns the object
        untouched. Subclasses are free to override this.

        '''

        return request

    @abc.abstractmethod
    def _do_generate_response(self, request):
        '''Called to generate a :class:`.ReflexResponse` (sub)class instance
        with the information present in ``request``.

        The method is abstract by nature.

        '''

        pass

    def _do_postprocess(self, response):
        '''Called to perform protocol-agnostic transformations on
        ``response``.

        Same as with :meth:`_do_translate_request`, the default
        implementation is a stub which is free to be overridden.

        '''

        return response

    @abc.abstractmethod
    def _do_deliver_response(self, response):
        '''Called to actually deliver content in ``response`` in a
        particular output protocol.

        This method is also abstract by nature. There is no restrictions
        put on its return value; after the method is called the whole
        stimulation procedure ends, and you are in total control.

        '''

        pass

    def stimulate(self, *args, **kwargs):
        '''Triggers a response upon being presented with a set of arbitrary
        parameters. Depending on implementations of the several relaying
        methods, the effects triggered can be just about anything.

        '''

        raw_request = self._do_accept_request(*args, **kwargs)
        request = self._do_translate_request(raw_request)
        raw_response = self._do_generate_response(request)
        response = self._do_postprocess(raw_response)
        return self._do_deliver_response(response)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
