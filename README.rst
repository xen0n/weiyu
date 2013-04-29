weiyu
=====

**weiyu** is a Web development framework for Python. Highly modular and
configurable, ``weiyu`` tries hard to integrate common functionalities
for the developer's convenience. It features integration with the following
popular packages:

* Caches
    - python-memcached
    - redis
* Database
    - pymongo
* Server interfaces
    - WSGI
    - tornado
    - gevent-socketio
* Session management
    - Beaker
* Task queue
    - celery
* Templating engine
    - Mako
* Miscellaneous
    - ultrajson

CPython 2.7 and PyPy are supported, and Python 3 compliance is on the way.


Licenses
--------

* GPLv3+
* Public domain for ``examples/``


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

* ``gevent-socketio`` integration is broken under PyPy 2.0b2 with the
  experimental hacks_.
* The NoSQL DB mapper is rather weak, may need a complete overhaul.

.. _hacks: https://github.com/gevent-on-pypy/pypycore/


Community
---------

* Mailing list
    - weiyu-cn at groups.google.com (Main language: Chinese)


Why the name?
-------------

The two names come from *Lin Jiang Xian* (trad: 臨江仙/simp: 临江仙) by Yan
Jidao, a poet of the Song dynasty. The referenced sentence is
``去年春恨卻來時，落花人獨立，微雨燕雙飛``.


Examples
--------

Some examples are provided in the ``examples/`` directory. Check them out to
get a feeling of working with ``weiyu``.


.. vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
