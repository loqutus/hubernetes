from logging import debug
import settings
from time import sleep


class Scheduler:
    def __init__(self, docker_client):
        self.docker_client = docker_client

    def schedule(self):
        sleep(1)
        while True:
            running_containers_by_groups = self.docker_client.get_running_containers_by_groups()
            if running_containers_by_groups:
                for group_name, group_running_containers in running_containers_by_groups.items():
                    running_containers_count = len(group_running_containers)
                    required_containers_count = int(self.docker_client.groups[group_name]['instances'])
                    if running_containers_count < required_containers_count:
                        containers_delta = required_containers_count - running_containers_count
                        i = 0
                        while i < containers_delta:
                            for docker_host_name, docker_client in self.docker_client.docker_clients.items():
                                if i < containers_delta:
                                    new_container = self.docker_client.run_container(docker_client,
                                                                                     self.docker_client.groups[group_name]['image'],
                                                                                     self.docker_client.groups[group_name]['command'],
                                                                                     group_name)
                                    debug('new ' + new_container.name + ' on ' + docker_host_name)
                                    i += 1
                                else:
                                    break
            debug('sleep ' + str(settings.sleep))
            sleep(settings.sleep)
