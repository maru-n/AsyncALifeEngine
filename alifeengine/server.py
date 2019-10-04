import threading
import socketserver
import socket
import pickle
import bottle
from .constants import *

class AsyncALifeEngineServer(object):
    """docstring for AsyncALifeEngineServer."""

    def __init__(self):
        message_server = socketserver.ThreadingUDPServer((AE_SERVER_HOST, AE_SERVER_MESSAGE_PORT), MessageHandler)
        self.message_server_thread = threading.Thread(target=message_server.serve_forever)
        self.message_server_thread.daemon = True

    def run(self):
        self.message_server_thread.start()
        bottle.run(host=AE_SERVER_HOST, port=AE_SERVER_COMMAND_PORT)

    def stop(self):
        print('not implemented')


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

@bottle.post('/connect/')
def connect():
    src_n = bottle.request.query['source_node']
    src_v = bottle.request.query['source_var_name']
    s = (src_n, src_v)
    tgt_n = bottle.request.query['target_node_name']
    tgt_v = bottle.request.query['target_var_name']
    local_port = int(bottle.request.query['local_port'])
    t = (tgt_n, tgt_v, local_port)
    if not s in connection_map:
        connection_map[s] = set()
    connection_map[s].add(t)

    print(connection_map)
    return 'OK'
