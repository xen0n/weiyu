weiyu
=====

.. image:: https://pypip.in/v/weiyu/badge.png
    :target: https://pypi.python.org/pypi/weiyu/

.. image:: https://pypip.in/d/weiyu/badge.png
    :target: https://pypi.python.org/pypi/weiyu/

**weiyu** is a Web development framework for Python. Highly modular and
configurable, ``weiyu`` strives to empower developers with convenience
and productivity.


Features
========

* Configuration driven
    - YAML, JSON or Python pickles are supported
    - YAML is the default configuration format for readability
* NoSQL storage
    - MongoDB
    - Redis
    - Riak
* Flexible URL routing
    - Route with either regexes or exact ``startswith`` matches
    - Concise URLconf definition syntax
    - Support for reverse resolution
* Cache integration
* Task queue integration
* Frontend technologies
    - Sass by means of pyScss_

The framework provides integration with the following packages:

* Caches
    - python-memcached
    - redis
* Database
    - pymongo
    - redis
    - riak
* Server interfaces
    - WSGI
    - tornado
    - gevent-socketio
* Session management
    - Beaker
    - redis
* Task queue
    - celery
* Templating engine
    - Mako
    - pyScss_
* Miscellaneous
    - ultrajson

CPython 2.7 and PyPy are supported, with support for CPython 3.2 and above
considered experimental. Any help is appreciated.

.. _pyScss: https://github.com/Kronuz/pyScss


Licenses
--------

* GPLv3+
* Public domain for ``examples/``

The project contains code from other libraries; copyright notices are attached
to the respective source files.

* ``helpers/regex_helper.py``: Taken from Django_, BSD-licensed.
* ``helpers/metaprogramming.py``: Contains code from formencode_, PSF-licensed.
  Also contains user-contributed code from StackOverflow which is licensed
  under cc-by-sa 3.0 according to StackOverflow policy.

.. _Django: https://www.djangoproject.com/
.. _formencode: https://github.com/formencode/formencode


Installation
------------

``weiyu`` is registered in PyPI, but for the moment directly installing from
the official repository is recommended as the development is constantly in
flux. Also you get the full set of examples this way.

To install from the official repo::

    $ git clone https://github.com/xen0n/weiyu.git
    $ cd weiyu/
    (installing using distribute)
    $ ./setup.py develop
    (or manually setting up the link)
    $ pwd > /path/to/your/site-packages/weiyu.pth

To install via ``pip``::

    $ pip install weiyu

Both will not install most of the dependencies. While the deps can be
controlled individually using flags like ``weiyu[mako,celery,redis]``,
requirements files have been provided to allow quick install of all
possible dependencies.::

    $ pip install -r requirements.txt

.. note::

    PyPy users would have to use the other requirement file,
    ``requirements.pypy.txt``, which basically has the optional C
    accelerator modules stripped out.


Known issues
------------

* ``gevent-socketio`` integration is not directly usable on PyPy.
  However, with the latest version of PyPy and some hacks_, the
  performance can become really awesome!
* The NoSQL DB mapper is somewhat lacking in capabilities, help appreciated.

.. _hacks: https://github.com/gevent-on-pypy/pypycore/


Community
---------

* Mailing list
    - weiyu-cn at groups.google.com (Main language: Chinese)


Why the name?
-------------

The name comes from *Lin Jiang Xian* (trad: 臨江仙/simp: 临江仙) by Yan
Jidao, a poet of the Song dynasty. The referenced sentence is
``去年春恨卻來時，落花人獨立，微雨燕雙飛``. Its pronunciation is like
"WE-you", if not using the correct vowel for "yu".


Examples
--------

Some examples are provided in the ``examples/`` directory. Check them out to
get a feeling of working with ``weiyu``.


.. vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
