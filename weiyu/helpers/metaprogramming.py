#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / helpers / metaprogramming structures

from __future__ import unicode_literals, division

__all__ = [
        'classproperty',
        'classinstancemethod',
        ]


# The following class is taken from an answer to StackOverflow question
# 3203286/how-to-create-a-read-only-class-property-in-python,
# answered by StackOverflow user bobince.
# According to SO policy, the content is licensed under cc-by-sa 3.0.
class classproperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


# The following code is part of the formencode library, which is licensed under
# the PSF license.
# START OF formencode CODE
class classinstancemethod(object):
    """
    Acts like a class method when called from a class, like an
    instance method when called by an instance.  The method should
    take two arguments, 'self' and 'cls'; one of these will be None
    depending on how the method was called.
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, type=None):
        return _methodwrapper(self.func, obj=obj, type=type)


class _methodwrapper(object):

    def __init__(self, func, obj, type):
        self.func = func
        self.obj = obj
        self.type = type

    def __call__(self, *args, **kw):
        assert 'self' not in kw and 'cls' not in kw, (
            "You cannot use 'self' or 'cls' arguments to a "
            "classinstancemethod")
        return self.func(*((self.obj, self.type) + args), **kw)

    def __repr__(self):
        if self.obj is None:
            return ('<bound class method %s.%s>'
                    % (self.type.__name__, self.func.__name__))
        else:
            return ('<bound method %s.%s of %r>'
                    % (self.type.__name__, self.func.__name__, self.obj))


# END OF formencode CODE


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
