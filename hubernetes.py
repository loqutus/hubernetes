#!/usr/bin/env python3

import docker
from threading import Thread
from flask import Flask, render_template
from time import sleep
import logging
import settings

app = Flask(__name__)


@app.route('/')
def flask_index():
    return render_template('index.html', name='hubernetes')


def set_log(log=settings.log_name, level=settings.log_level, format=settings.log_format):
    logging.basicConfig(filename=log, level=level, format=format)


class docker_client():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client=docker.DockerClient


class watcher():
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port

    def watch(self):
        while True:
            sleep(settings.sleep)


def run_flask():
    app.run(host=settings.host, port=settings.port, debug=settings.debug)


def run_watcher():
    watch = watcher(host=settings.host, port=settings.port)
    watch.watch()


if __name__ == '__main__':
    flask_thread = Thread(target=run_flask())
    watcher_thread = Thread(target=run_watcher())
    flask_thread.start()
    watcher_thread.start()
    flask_thread.join()
    watcher_thread.join()
