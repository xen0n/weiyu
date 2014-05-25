#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / utilities / HTTP (RFC2616) date parsing and generation
#
# Copyright (C) 2014 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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
        'parse_http_date',
        'make_http_date',
        ]

import calendar
import re

from wsgiref.handlers import format_date_time

# XXX TODO: This module currently accepts things like 25:61:99 for time and
# Feb 30 for date, which may not be desirable. Properly dealing with this
# may be done with datetime objects, but at the moment it seems too much of
# a hassle...
#
# Also, weekday is completely ignored in parsing, not sure if including
# validation for that would be beneficial.
WKDAY = r'(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)'
WEEKDAY = (
        r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday'
        r'|Sunday)'
        )

MONTH_LIST_STR = 'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec'
MONTH = r'(?P<month>%s)' % (MONTH_LIST_STR, )
MONTH_MAP = {i: idx + 1 for idx, i in enumerate(MONTH_LIST_STR.split('|'))}

DATE1 = r'(?P<day>\d{2}) %s (?P<year>\d{4})' % (MONTH, )
DATE2 = r'(?P<day>\d{2})-%s-(?P<year>\d{2})' % (MONTH, )
DATE3 = r'%s (?P<day>\d{2}| \d)' % (MONTH, )
TIME = r'(?P<H>\d{2}):(?P<M>\d{2}):(?P<s>\d{2})'

RFC1123_DATE = r'^%s, %s %s GMT$' % (WKDAY, DATE1, TIME, )
RFC850_DATE = r'^%s, %s %s GMT$' % (WEEKDAY, DATE2, TIME, )
ASCTIME_DATE = r'^%s %s %s (?P<year>\d{4})$' % (WKDAY, DATE3, TIME, )

RFC1123_RE = re.compile(RFC1123_DATE)
RFC850_RE = re.compile(RFC850_DATE)
ASCTIME_RE = re.compile(ASCTIME_DATE)


def timetuple_from_rfc1123(s):
    '''Parse RFC1123-formatted string into time tuple.

    >>> from __future__ import unicode_literals
    >>> timetuple_from_rfc1123('Sun, 06 Nov 1994 08:49:37 GMT')
    (1994, 11, 6, 8, 49, 37)
    >>> timetuple_from_rfc1123('Sun, 25 May 2014 07:14:36 GMT')
    (2014, 5, 25, 7, 14, 36)
    >>> timetuple_from_rfc1123('Sun,  06 Nov 1994 08:49:37 GMT')
    Traceback (most recent call last):
        ...
    ValueError: malformed RFC1123 datetime string
    >>> timetuple_from_rfc1123(' Sun, 06 Nov 1994 08:49:37 GMT')
    Traceback (most recent call last):
        ...
    ValueError: malformed RFC1123 datetime string

    '''

    match = RFC1123_RE.match(s)
    if match is None:
        raise ValueError('malformed RFC1123 datetime string')

    Y = int(match.group('year'))
    m = MONTH_MAP[match.group('month')]
    d = int(match.group('day'))
    H = int(match.group('H'))
    M = int(match.group('M'))
    s = int(match.group('s'))

    return (Y, m, d, H, M, s, )


def timetuple_from_rfc850(s):
    '''Parse RFC850-formatted string into time tuple.

    >>> from __future__ import unicode_literals
    >>> timetuple_from_rfc850('Sunday, 06-Nov-94 08:49:37 GMT')
    (1994, 11, 6, 8, 49, 37)
    >>> timetuple_from_rfc850('Sunday, 25-May-14 07:14:36 GMT')
    (2014, 5, 25, 7, 14, 36)
    >>> timetuple_from_rfc850('Sunday, 06-Nov-94  08:49:37 GMT')
    Traceback (most recent call last):
        ...
    ValueError: malformed RFC850 datetime string

    '''

    match = RFC850_RE.match(s)
    if match is None:
        raise ValueError('malformed RFC850 datetime string')

    Y_2digit = int(match.group('year'))
    Y = 1900 + Y_2digit if Y_2digit > 50 else 2000 + Y_2digit

    m = MONTH_MAP[match.group('month')]
    d = int(match.group('day'))
    H = int(match.group('H'))
    M = int(match.group('M'))
    s = int(match.group('s'))

    return (Y, m, d, H, M, s, )


def timetuple_from_asctime(s):
    '''Parse asctime-formatted string into time tuple.

    >>> from __future__ import unicode_literals
    >>> timetuple_from_asctime('Sun Nov  6 08:49:37 1994')
    (1994, 11, 6, 8, 49, 37)
    >>> timetuple_from_asctime('Sun May 25 07:14:36 2014')
    (2014, 5, 25, 7, 14, 36)
    >>> timetuple_from_asctime('Sun Nov 6 08:49:37 1994')
    Traceback (most recent call last):
        ...
    ValueError: malformed asctime datetime string
    >>> timetuple_from_asctime('Sun Nov 06 08:49:37 1994')
    Traceback (most recent call last):
        ...
    ValueError: malformed asctime datetime string

    '''

    match = ASCTIME_RE.match(s)
    if match is None:
        raise ValueError('malformed asctime datetime string')

    Y = int(match.group('year'))
    m = MONTH_MAP[match.group('month')]

    d_str = match.group('day')
    if d_str[0] == ' ':
        d = int(d_str[1])
    else:
        if d_str[0] not in '12':
            raise ValueError('malformed asctime datetime string')
        d = int(d_str)

    H = int(match.group('H'))
    M = int(match.group('M'))
    s = int(match.group('s'))

    return (Y, m, d, H, M, s, )


def parse_http_date(s):
    '''Parse HTTP date string into UTC timestamp.

    >>> from __future__ import unicode_literals
    >>> parse_http_date('Sun, 06 Nov 1994 08:49:37 GMT')
    784111777
    >>> parse_http_date('Sunday, 06-Nov-94 08:49:37 GMT')
    784111777
    >>> parse_http_date('Sun Nov  6 08:49:37 1994')
    784111777
    >>> parse_http_date('Sun Nov 6 08:49:37 1994')
    Traceback (most recent call last):
        ...
    ValueError: unrecognized HTTP date string

    '''

    try:
        return calendar.timegm(timetuple_from_rfc1123(s))
    except ValueError:
        pass

    try:
        return calendar.timegm(timetuple_from_rfc850(s))
    except ValueError:
        pass

    try:
        return calendar.timegm(timetuple_from_asctime(s))
    except ValueError:
        pass

    raise ValueError('unrecognized HTTP date string')


def make_http_date(ts):
    '''Make a HTTP date string from a UTC timestamp.

    >>> make_http_date(784111777)
    'Sun, 06 Nov 1994 08:49:37 GMT'

    '''

    return format_date_time(ts)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
