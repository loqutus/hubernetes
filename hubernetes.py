#!/usr/bin/env python3

import docker
from threading import Thread
from flask import Flask, render_template
from time import sleep
import etcd
import logging
import settings
import json
import sys

app = Flask(__name__)


# logging.basicConfig(filename=settings.log_name, level=settings.log_level, format=settings.log_format)
# ch1 = logging.StreamHandler(sys.stdout)
# ch2 = logging.StreamHandler(sys.stderr)


class docker_client():
    def __init__(self):
        self.docker_clients = {}
        self.etcd_client = etcd.Client(host=settings.etcd_host, port=settings.etcd_port)
        docker_hosts_json = self.etcd_client.read(settings.etcd_dir + '/' + 'docker_hosts').value
        self.docker_hosts = json.loads(docker_hosts_json)
        for host_name, host_url in self.docker_hosts.items():
            self.docker_clients[host_name] = docker.DockerClient(base_url=host_url)

    def get_running_containers(self):
        running_containers = {}
        for docker_host_name, docker_host_client in self.docker_clients.items():
            running_containers[docker_host_name] = []
            for docker_container in docker_host_client.containers.list():
                stats = docker_container.stats(decode=True, stream=False)
                running_containers[docker_host_name].append(
                    {'name': docker_container.name, 'id': docker_container.id,
                     'memory_used': stats['memory_stats']['usage'], 'memory_limit': stats['memory_stats']['limit'],
                     'memory_max_usage': stats['memory_stats']['max_usage'],
                     'cpu_usage': stats['cpu_stats']['cpu_usage']['total_usage'],
                     'cpus': stats['cpu_stats']['online_cpus'],
                     'rx': stats['networks']['eth0']['rx_bytes'], 'tx': stats['networks']['eth0']['tx_bytes']})
        print(running_containers)
        return running_containers

    def get_hosts(self):
        docker_hosts = {}
        for docker_host_name, docker_host_client in self.docker_clients.items():
            docker_hosts[docker_host_name] = {}


class watcher():
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port

    def watch(self):
        while True:
            sleep(settings.sleep)


dock = docker_client()


@app.route('/')
def flask_index():
    return render_template('index.html', containers=dock.get_running_containers())


@app.route('/hosts')
def flask_hosts():
    return render_template('hosts.html', hosts=dock.get_hosts())


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
