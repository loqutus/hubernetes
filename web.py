from flask import Flask, render_template
from docker_client import docker_client

app = Flask(__name__)


@app.route('/')
def flask_index():
    return render_template('index.html', info=docker_client.get_info())


@app.route('/containers')
def flask_containers():
    return render_template('containers.html', containers=docker_client.get_containers_info())


@app.route('/hosts')
def flask_hosts():
    return render_template('hosts.html', hosts=docker_client.get_hosts())


@app.route('/groups')
def flask_groups():
    return render_template('groups.html', groups=docker_client.get_groups())


@app.route('/images')
def flask_images():
    return render_template('images.html', images=docker_client.get_images())
