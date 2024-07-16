#!/usr/bin/env bash
set -e

python ./manage.py collectstatic --noinput
# TODO: fix
while ! nc -z "$DB_HOST" "$DB_PORT"; do sleep 1; done;
while ! nc -z "$SUBSCRIPTIONS_DB_HOST" "$SUBSCRIPTIONS_DB_PORT"; do sleep 1; done;
while ! nc -z "$PAYMENTS_DB_HOST" "$PAYMENTS_DB_PORT"; do sleep 1; done;
python ./manage.py migrate

uwsgi --strict --ini uwsgi.ini
