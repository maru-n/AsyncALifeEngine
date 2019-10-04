import os
import socket
import sys
import pickle
import threading
import socketserver
from bottle import get, post, request, run
import pickle
from .constants import *


class MessageHandler(socketserver.BaseRequestHandler):
    def handle(self):
        req_data = pickle.loads(self.request[0])
        try:
            src_node = req_data['node_name']
            src_vname = req_data['variable_name']
            data = req_data['data']
        except KeyError as e:
            print(f'invalid message: {req_data}')
            return

        if (src_node, src_vname) in connection_map:
            for tgt_node, tgt_vname, p in connection_map[(src_node, src_vname)]:
                payload = {'variable_name':tgt_vname, 'data':data}
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(pickle.dumps(payload), ('localhost', p))
                print(f'MSG:{data}({type(data)}) : {src_node}:{src_vname} => {tgt_node}:{tgt_vname}')


connection_map = dict()

@post('/connect/')
def index():
    src_n = request.query['source_node']
    src_v = request.query['source_var_name']
    s = (src_n, src_v)
    tgt_n = request.query['target_node_name']
    tgt_v = request.query['target_var_name']
    local_port = int(request.query['local_port'])
    t = (tgt_n, tgt_v, local_port)
    if not s in connection_map:
        connection_map[s] = set()
    connection_map[s].add(t)

    print(connection_map)
    return 'OK'

def start_server():
    server = socketserver.ThreadingUDPServer((AE_SERVER_HOST, AE_SERVER_MESSAGE_PORT), MessageHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    run(host=AE_SERVER_HOST, port=AE_SERVER_COMMAND_PORT)


def stop_server():
    print('!!!not implemented!!!')

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
