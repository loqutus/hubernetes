#!/usr/bin/env python3

import docker
from threading import Thread
from flask import Flask, render_template
from time import sleep
import etcd
import settings
import json
import sys
import logging

app = Flask(__name__)

logging.basicConfig(filename=settings.log_name, level=30,
                    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', )
ch = logging.StreamHandler(sys.stdout)

class docker_client():
    def __init__(self):
        self.docker_clients = {}
        self.running_containers_by_groups = {}
        self.etcd_client = etcd.Client(host=settings.etcd_host, port=settings.etcd_port)
        self.hosts = json.loads(self.etcd_client.read(settings.etcd_dir + '/' + 'hosts').value)
        self.images = json.loads(self.etcd_client.read(settings.etcd_dir + '/' + 'images').value)
        self.groups = json.loads(self.etcd_client.read(settings.etcd_dir + '/' + 'groups').value)
        self.running_containers = {}
        for host_name, host_url in self.hosts.items():
            self.docker_clients[host_name] = docker.DockerClient(base_url=host_url)

    def get_running_containers(self):
        for docker_host_name, docker_host_client in self.docker_clients.items():
            self.running_containers[docker_host_name] = []
            for docker_container in docker_host_client.containers.list():
                stats = docker_container.stats(decode=True, stream=False)
                self.running_containers[docker_host_name].append(
                    {'name': docker_container.name, 'group': docker_container.attrs['Config']['Labels']['group'],
                     'id': docker_container.id,
                     'memory_used': stats['memory_stats']['usage'], 'memory_limit': stats['memory_stats']['limit'],
                     'memory_max_usage': stats['memory_stats']['max_usage'],
                     'cpu_usage': stats['cpu_stats']['cpu_usage']['total_usage'],
                     'cpus': stats['cpu_stats']['online_cpus'],
                     'rx': stats['networks']['eth0']['rx_bytes'], 'tx': stats['networks']['eth0']['tx_bytes']})
        return self.running_containers

    def get_running_containers_by_groups(self):
        self.get_running_containers()
        for group, group_params in self.groups.items():
            self.running_containers_by_groups[group] = []
            for docker_host_name, containers in self.running_containers.items():
                for container in containers:
                    if container['group'] == group:
                        self.running_containers_by_groups[group].append(container)
        return self.running_containers_by_groups

    def run_container(self, docker_client, image, command, group):
        return docker_client.containers.run(image, command, labels={'group': group}, detach=True)

    def get_hosts(self):
        hosts = []
        for host_name, host_url in self.hosts.items():
            hosts.append(host_name)
        return hosts

    def get_images(self):
        return self.images

    def get_groups(self):
        return self.groups

    def get_info(self):
        containers_count = 0
        for host, containers in self.running_containers.items():
            containers_count += len(containers)
        return {'hosts': len(self.hosts), 'groups': len(self.groups), 'images': len(self.images),
                'containers': containers_count}


class watcher():
    def watch(self):
        sleep(1)
        logging.info('1')
        while True:
            logging.info('2')
            running_containers_by_groups=dock.get_running_containers_by_groups()
            if running_containers_by_groups:
                for group_name, group_running_containers in running_containers_by_groups.items():
                    logging.info('3')
                    running_containers_count = len(group_running_containers)
                    required_containers_count = int(dock.groups[group_name]['instances'])
                    if running_containers_count < required_containers_count:
                        logging.info('4')
                        delta = required_containers_count - running_containers_count
                        for i in range(delta):
                            logging.info('5')
                            for docker_client in dock.docker_clients:
                                logging.info('6')
                                dock.run_container(docker_client, dock.groups[group_name]['image'],
                                                   dock.groups[group_name]['command'], group_name)

            sleep(settings.sleep)


dock = docker_client()


@app.route('/')
def flask_index():
    return render_template('index.html', info=dock.get_info())


@app.route('/containers')
def flask_containers():
    return render_template('containers.html', containers=dock.get_running_containers())


@app.route('/hosts')
def flask_hosts():
    return render_template('hosts.html', hosts=dock.get_hosts())


@app.route('/groups')
def flask_groups():
    return render_template('groups.html', groups=dock.get_groups())


@app.route('/images')
def flask_images():
    return render_template('images.html', images=dock.get_images())


def run_flask():
    app.run(host=settings.host, port=settings.port)


def run_watcher():
    watch = watcher()
    watch.watch()


if __name__ == '__main__':
    Thread(target=run_flask).start()
    Thread(target=run_watcher).start()
