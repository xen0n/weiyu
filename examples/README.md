# Example apps

Here you can find example(s) on how to make use of the weiyu framework.
Most of them are meant for use inside a virtualenv. You should first copy
the directory out of weiyu's repository if you decide to try out the
example, as during experiment I found out that sometimes Python won't be
able to locate ``weiyu`` if the library is put on the Python path by use of
``.pth`` files.

The examples are now put in public domain, so you can use them in whatever
way you want to, without any limitation.


## hello

This example provides a nice overview of ``weiyu``'s inner workings, testing
various pieces of ``weiyu`` infrastructure.


## github-webhook

This is an implementation of GitHub's post-receive hook listener.


## tasks

This example shows how to integrate Celery into your ``weiyu`` app. It boils
down to just loading the config *after* creating the ``celery`` object!


## cache

This example demonstrates ``weiyu``'s caching capability.


<!-- vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8: -->
