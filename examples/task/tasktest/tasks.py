#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / Working with Celery - Task file
#
# This file is in public domain.

from __future__ import unicode_literals, division

from .celery import celery


@celery.task(serializer='json')
def add(a, b):
    return a + b


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
