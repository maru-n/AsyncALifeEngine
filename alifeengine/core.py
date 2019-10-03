import os
import socket
import sys
import pickle
import threading
import socketserver


DOCKER_NETWORK_CONNECTION_PORT = 12345
DOCKER_CONTAINER_NAME_PREFIX = 'aenode.'
DOCKER_NETWORK_NAME = 'alifeengine_network'
AE_SERVER_HOSTNAME = 'host.docker.internal'
AE_SERVER_MESSAGE_PORT = 8889
DOCKER_CONTAINER_MESSAGE_PORT = 8889

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
        #server = socketserver.ThreadingUDPServer(('0.0.0.0', DOCKER_NETWORK_CONNECTION_PORT), ThreadedUDPRequestHandler)
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


#server.shutdown()
#server.server_close()
