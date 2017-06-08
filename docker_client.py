import docker
import json
import settings
import etcd
import math
from logging import debug,info,error,warning
import requests


class DockerClient:
    def __init__(self, etcd_client, etcd_dir):
        debug('docker_client init')
        self.docker_clients = {}
        self.running_containers_by_groups = {}
        self.etcd_client = etcd_client
        self.hosts = json.loads(self.etcd_client.read(etcd_dir + '/' + 'hosts').value)
        self.images = json.loads(self.etcd_client.read(etcd_dir + '/' + 'images').value)
        self.groups = json.loads(self.etcd_client.read(etcd_dir + '/' + 'groups').value)
        self.running_containers = {}
        for host_name, host_address in self.hosts.items():
            self.docker_clients[host_name] = docker.DockerClient(base_url=host_address, version=settings.docker_version, timeout=settings.docker_timeout)

    def kmg(self, number):
        n_str = str(number)
        if number >= 10**9:
            return n_str[:-9] + 'G'

    def get_running_containers(self):
        debug('get_running_containeres')
        for docker_host_name, docker_host_client in self.docker_clients.items():
            self.running_containers[docker_host_name] = []
            for docker_container in docker_host_client.containers.list():
                for retry in range(settings.docker_retry):
                    try:
                        stats = docker_container.stats(decode=True, stream=False)
                        if stats:
                            break
                    except requests.exceptions.ReadTimeout:
                        self.docker_clients[docker_host_name] = docker.DockerClient(base_url=self.hosts[docker_host_name], version=settings.docker_version, timeout=settings.docker_timeout)
                        warning('connection timeout to ' + docker_host_name) 
                        continue
                memory_usage = 0
                memory_limit = 0
                memory_max_usage = 0
                cpu_usage = 0
                cpus = 0
                net_rx = 0
                net_tx = 0
                memory_stats = stats.get('memory_stats')
                cpu_stats = stats.get('cpu_stats')
                net_stats = stats.get('networks')
                if memory_stats:
                    memory_usage = memory_stats.get('usage')
                    memory_limit = memory_stats.get('limit')
                    memory_max_usage = memory_stats.get('max_usage')
                if cpu_stats:
                    cpu_usage = cpu_stats.get('cpu_usage').get('total_usage')
                    cpus = len(cpu_stats.get('cpu_usage').get('percpu_usage'))
                if net_stats:
                    net_rx = net_stats.get('eth0').get('rx_bytes')
                    net_tx = net_stats.get('eth0').get('tx_bytes')
                self.running_containers[docker_host_name].append(
                    {'name': docker_container.name, 'group': docker_container.attrs['Config']['Labels']['group'],
                     'id': docker_container.id,
                     'memory_used': memory_usage,
                     'memory_limit': memory_limit,
                     'memory_max_usage': memory_max_usage,
                     'cpu_usage': cpu_usage,
                     'cpus': cpus,
                     'rx': net_rx,
                     'tx': net_tx})
        #debug(self.running_containers)
        return self.running_containers

    def get_running_containers_by_groups(self):
        debug('get_running_containers_by_groups')
        self.get_running_containers()
        for group, group_params in self.groups.items():
            self.running_containers_by_groups[group] = []
            for docker_host_name, containers in self.running_containers.items():
                for container in containers:
                    if container['group'] == group:
                        self.running_containers_by_groups[group].append(container)
        return self.running_containers_by_groups

    def get_containers_info(self):
        debug('get_containers_info')
        debug(self.running_containers)
        return self.running_containers

    def run_container(self, docker_client, image, command, group):
        debug('run_contaiener')
        return docker_client.containers.run(image, command, labels={'group': group}, detach=True)

    def get_hosts(self):
        debug('get_hosts')
        hosts = []
        for host in self.hosts:
            for host_name, host_url in host.items():
                hosts.append(host_name)
        return hosts

    def get_images(self):
        debug('get_images')
        return self.images

    def get_groups(self):
        return self.groups

    def get_info(self):
        containers_count = 0
        for host, containers in self.running_containers.items():
            containers_count += len(containers)
        return {'hosts': len(self.hosts), 'groups': len(self.groups), 'images': len(self.images),
                'containers': containers_count}


docker_client = DockerClient(etcd_client=etcd.Client(host=settings.etcd_host, port=settings.etcd_port),
                             etcd_dir=settings.etcd_dir)
