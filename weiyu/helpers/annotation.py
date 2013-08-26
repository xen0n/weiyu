#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / helpers / metadata annotation
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
Object annotation
~~~~~~~~~~~~~~~~~

This module provides managed storage of arbitrary annotations on Python
objects (mainly functions).

The annotations are stored in a ``dict`` injected into the object's
``__dict__`` by the key ``'_weiyu_data_'``. You can of course operate on
the dict yourself, but by using this module's code paths compatibility is
realized in case of renaming of the annotation dictionary.

Functions
---------

'''

from __future__ import unicode_literals, division

__all__ = [
        'is_annotated',
        'ensure_annotation',
        'annotate',
        'get_annotation',
        'remove_annotations',
        ]

ANNOTATE_KEY = '_weiyu_data_'


def is_annotated(obj):
    '''Returns if an object has been annotated by this module;
    that is, have a ``_weiyu_data_`` dict implanted into its ``__dict__``.

    '''

    return ANNOTATE_KEY in obj.__dict__


def ensure_annotation(obj):
    '''Ensures the presence of ``_weiyu_data_`` dict inside the object's
    ``__dict__``. Does nothing if the object has already been annotated
    somehow.

    '''

    if not is_annotated(obj):
        obj.__dict__[ANNOTATE_KEY] = {}


def annotate(obj, **kwargs):
    '''Annotates ``obj`` with keyword arguments supplied.

    This is implemented by calling the underlying ``dict``\ 's ``update``
    method.

    '''

    ensure_annotation(obj)
    obj.__dict__[ANNOTATE_KEY].update(kwargs)


def remove_annotations(obj, keys):
    '''Removes annotation keys ``keys`` from ``obj``.

    Raises :exc:`AttributeError` if ``obj`` is considered not previously
    annotated by :func:`.is_annotated`. Keys that do not exist in the
    annotation dictionary are silently ignored.

    .. note::
        This function does not purge the annotation dictionary from the
        object's ``__dict__``, even if that dict becomes empty after
        removal.

    '''

    if not is_annotated(obj):
        raise AttributeError(
        'object %s is not annotated' % (
            repr(obj),
            )
        )

    data = obj.__dict__[ANNOTATE_KEY]
    for key in keys:
        if key in data:
            del data[key]


def get_annotation(obj, key=None):
    '''Retrieves annotation from ``obj``.

    Raises :exc:`AttributeError` if ``obj`` is not previously annotated
    by this module.

    If ``key`` is ``None``, returns a copy of the object's annotation
    dictionary; returns the data associated with ``key`` otherwise. If
    ``key`` is not found, :exc:`KeyError` is ``raise``\ d.

    '''

    if not is_annotated(obj):
        raise AttributeError(
                'object %s is not annotated' % (
                    repr(obj),
                    )
                )

    data = obj.__dict__[ANNOTATE_KEY]
    return data.copy() if key is None else data[key]


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
