import socket
import sys
import pickle
import threading
import socketserver


DOCKER_NETWORK_CONNECTION_PORT = 12345
DOCKER_CONTAINER_NAME_PREFIX = 'aenode.'
DOCKER_NETWORK_NAME = 'alifeengine_network'

def send(node_name, dict_data):
    try:
        host = DOCKER_CONTAINER_NAME_PREFIX + node_name
        data = pickle.dumps(dict_data)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (host, DOCKER_NETWORK_CONNECTION_PORT))
    except socket.gaierror as e:
        print(f'Error: Node name "{node_name}" does not resolve. Please check connection.', file=sys.stderr)


listener_list = {}

def add_listener(node_name, func):
    if not node_name in listener_list:
        listener_list[node_name] = []
    listener_list[node_name].append(func)



class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = pickle.loads(self.request[0])
        host_name = socket.gethostbyaddr(self.client_address[0])[0]
        node_name = host_name.replace(DOCKER_CONTAINER_NAME_PREFIX, '').replace('.' + DOCKER_NETWORK_NAME, '')
        if node_name in listener_list:
            for l in listener_list[node_name]:
                l(data)

server = socketserver.ThreadingUDPServer(('0.0.0.0', DOCKER_NETWORK_CONNECTION_PORT), ThreadedUDPRequestHandler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()

#server.shutdown()
#server.server_close()
