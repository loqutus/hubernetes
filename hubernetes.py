#!/usr/bin/env python3

from threading import Thread
from scheduler import Scheduler
import etcd
import settings
import json
import sys
import logging
from web import app
from docker_client import docker_client
import etcd

logging.basicConfig(filename=settings.log_name, level=settings.log_level,
                    format=u'[%(asctime)s] %(filename)s:%(lineno)d %(levelname)-8s %(message)s', )
ch = logging.StreamHandler(sys.stdout)
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)

scheduler = Scheduler(docker_client)


def run_flask():
    app.run(host=settings.host, port=settings.port)


def run_watcher():
    scheduler.schedule()


if __name__ == '__main__':
    Thread(target=run_flask).start()
    Thread(target=run_watcher).start()
