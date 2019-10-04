import os
import socket
import sys
import pickle
import threading
import socketserver
from os import path
import time
import docker
import pickle
from .constants import *


def exec_command(node_name, command):
    container = client.containers.get(DOCKER_CONTAINER_NAME_PREFIX + node_name)
    result = container.exec_run(command)
    return result.output.decode()

def run_node(node_name):
    if node_name[0] == 'all':
        node_list = find_all_nodes()
    else:
        node_list = node_name

    for n in node_list:
        exec_command(n, f'cp /dev/null {DOCKER_CONTAINER_LOG_PATH}')
        result = exec_command(n, 'supervisorctl start aenode')
        print(result)


def stop_node(node_name):
    if node_name[0] == 'all':
        node_list = find_all_nodes()
    else:
        node_list = node_name

    for n in node_list:
        result = exec_command(n, 'supervisorctl stop aenode')
        print(result)


def restart_node(node_name):
    if node_name[0] == 'all':
        node_list = find_all_nodes()
    else:
        node_list = node_name

    for n in node_list:
        result = exec_command(n, 'supervisorctl stop aenode')
        print(result)
    for n in node_list:
        exec_command(n, f'cp /dev/null {DOCKER_CONTAINER_LOG_PATH}')
        result = exec_command(n, 'supervisorctl start aenode')
        print(result)


def log_node(node_name, follow=False):
    result = exec_command(node_name , f'cat {DOCKER_CONTAINER_LOG_PATH}')
    print(result, end='', flush=True)
    if follow:
        while True:
            new_result = exec_command(node_name , f'cat {DOCKER_CONTAINER_LOG_PATH}')
            if len(new_result) < len(result):
                print('---- restarted ----')
                print(new_result, end='', flush=True)
            else:
                print(new_result[len(result):], end='', flush=True)
            result = new_result
            time.sleep(0.1)

def send(variable_name, var):
    host_name = os.uname()[1]
    node_name = host_name.replace(DOCKER_CONTAINER_NAME_PREFIX, '').replace('.' + DOCKER_NETWORK_NAME, '')
    data = {
        'node_name': node_name,
        'variable_name': variable_name,
        'data': var
    }
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(pickle.dumps(data), (AE_SERVER_HOSTNAME, AE_SERVER_MESSAGE_PORT))
    except socket.gaierror as e:
        print(e)

default_listener_list = []
listener_list = {}
server = None

def add_listener(func, variable_name=None):
    host_name = os.uname()[1]
    node_name = host_name.replace(DOCKER_CONTAINER_NAME_PREFIX, '').replace('.' + DOCKER_NETWORK_NAME, '')
    global server
    if server is None:
        server = socketserver.ThreadingUDPServer(('0.0.0.0', DOCKER_CONTAINER_MESSAGE_PORT), ThreadedUDPRequestHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

    if variable_name is None:
        default_listener_list.append(func)
    else:
        if not variable_name in listener_list:
            listener_list[variable_name] = []
        listener_list[variable_name].append(func)


import requests

client = docker.from_env()

def find_all_containers(include_stopped=False):
    nodes = []
    for c in client.containers.list(all=include_stopped):
        if c.name.startswith(DOCKER_CONTAINER_NAME_PREFIX):
            nodes.append(c.name)
    return nodes


def find_all_nodes():
    nodes = [n.replace(DOCKER_CONTAINER_NAME_PREFIX, '') for n in find_all_containers()]
    return nodes


def search_next_node_index():
    nodes = find_all_nodes()
    used_idxs = [int(n.replace(DEFAULT_NODE_NAME, '')) for n in nodes if n.replace(DEFAULT_NODE_NAME, '').isdecimal()]
    idx = 0
    while True:
        if not idx in used_idxs:
            break
        idx += 1
    return idx


def print_node_list():
    for n in find_all_nodes():
        print(n)

def create_node(script, node_name=None):
    if node_name is None:
        idx = search_next_node_index()
        node_name = DEFAULT_NODE_NAME + str(idx)
    else:
        node_name = node_name
    container_name = DOCKER_CONTAINER_NAME_PREFIX + node_name

    script_file = path.basename(script)
    script_dir = path.dirname(path.abspath(script))
    library_dir = path.dirname(__file__)

    container = client.containers.run(image=DOCKER_IMAGE_NAME,
                                      name=container_name,
                                      hostname=container_name,
                                      detach=True,
                                      auto_remove=True,
                                      privileged=True,
                                      ports={f'{DOCKER_CONTAINER_MESSAGE_PORT}/udp': None},
                                      volumes = {script_dir: {'bind': DOCKER_CONTAINER_SCRIPT_DIR, 'mode': 'ro'},
                                                 library_dir: {'bind': '/usr/local/lib/python3.7/site-packages/alifeengine', 'mode': 'ro'}})

    container.exec_run(f'pip install -e {DOCKER_CONTAINER_LIBRARY_DIR}')
    for lib in LIBRARY_REQUIPMENTS:
        container.exec_run(f'pip install {lib}')
    container.exec_run(f'ln -s {path.join(DOCKER_CONTAINER_SCRIPT_DIR, script_file)} /app/main.py')

def remove_node(node_name):
    if node_name[0] == 'all':
        node_list = find_all_nodes()
    else:
        node_list = node_name

    for n in node_list:
        try:
            c = client.containers.get(DOCKER_CONTAINER_NAME_PREFIX + n)
            c.stop()
            print(f'ALife Engine: {n} is removed.')
        except docker.errors.NotFound as e:
            print(f'ALife Engine: {n} not found.')


def connect_node(src_node, src_vname, tgt_node, tgt_vname):
    container = client.containers.get(DOCKER_CONTAINER_NAME_PREFIX + tgt_node)
    port = int(container.ports[f'{DOCKER_CONTAINER_MESSAGE_PORT}/udp'][0]['HostPort'])

    url = f'http://{AE_SERVER_HOST}:{AE_SERVER_COMMAND_PORT}/connect/'
    params = {
        'source_node': src_node,
        'source_var_name': src_vname,
        'target_node_name': tgt_node,
        'target_var_name': tgt_vname,
        'local_port': port
    }
    res = requests.post(url, params=params)
    if res.text == 'OK':
        print(f'ALifeEngine: connectted {src_node}:{src_vname} => {tgt_node}:{tgt_vname}')
    else:
        print(f'ALifeEngine: connection error.')
        print(res)




class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        payload = pickle.loads(self.request[0])
        variable_name = payload['variable_name']
        data = payload['data']


        host_name = socket.gethostbyaddr(self.client_address[0])[0]
        node_name = host_name.replace(DOCKER_CONTAINER_NAME_PREFIX, '').replace('.' + DOCKER_NETWORK_NAME, '')
        if variable_name in listener_list:
            for l in listener_list[variable_name]:
                l(data)
        for l in default_listener_list:
            l(data, variable_name)


def test():
    unittest.main()

import unittest

class Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_find_all_containers(self):
        pass

    def tearDown(self):
        pass
