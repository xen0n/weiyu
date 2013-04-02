#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / Task queue integration - Task file
#
# This file is in public domain.

from __future__ import unicode_literals, division

from weiyu.tasks import task_hub


@task_hub.task('tasktest')
def add(a, b):
    return a + b


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
