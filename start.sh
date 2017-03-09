#!/bin/bash
set -e
set -x

mkdir -p /home/docker/code/config
touch /home/docker/code/config/__init__.py
# SSL certs are invalid on S3?
wget --no-check-certificate -O /home/docker/code/config/production_settings.py "$CONFIG_URL"
#supervisord -n
uwsgi --http-socket 0.0.0.0:8000 --wsgi-file trivia_stats/wsgi.py --master --processes 4 --threads 0
