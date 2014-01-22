# Working with Celery

## Launch directions

*   Prepare a RabbitMQ instance with username `test` and password `test`
*   Start RabbitMQ
*   Inside your virtual env (you are working inside one, aren't you?), start a
    Celery instance like this:

        $ celery -A tasktest --config=tasktest.celeryconfig worker

*   Fire up `wsgiapp.py`


<!-- vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8: -->
