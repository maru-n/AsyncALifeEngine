#!/usr/bin/env python

import docker
import argparse
from os import path
import sys
import time
from .core import start_server, stop_server, test
from .constants import *

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


def command_list_node(argv):
    parser = argparse.ArgumentParser(description='list all node.')
    parser.prog += f' {sys.argv[1]}'
    for n in find_all_nodes():
        print(n)


def command_create(argv):
    parser = argparse.ArgumentParser(description='create node.')
    parser.prog += f' {sys.argv[1]}'
    parser.add_argument('script', help="python script for runnning in the node.")
    parser.add_argument('--name', type=str,
                        help='unique name of the node.')
    args = parser.parse_args(argv)

    if args.name is None:
        idx = search_next_node_index()
        node_name = DEFAULT_NODE_NAME + str(idx)
    else:
        node_name = args.name
    container_name = DOCKER_CONTAINER_NAME_PREFIX + node_name

    script_file = path.basename(args.script)
    script_dir = path.dirname(path.abspath(args.script))
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
    for l in LIBRARY_REQUIPMENTS:
        container.exec_run(f'pip install {l}')
    container.exec_run(f'ln -s {path.join(DOCKER_CONTAINER_SCRIPT_DIR, script_file)} /app/main.py')



def command_remove(argv):
    parser = argparse.ArgumentParser(description='run node process.')
    parser.prog += f' {sys.argv[1]}'
    parser.add_argument('node_name', nargs='+', help="node name or 'all'.")
    args = parser.parse_args(argv)

    if args.node_name[0] == 'all':
        node_list = find_all_nodes()
    else:
        node_list = args.node_name

    for n in node_list:
        try:
            c = client.containers.get(DOCKER_CONTAINER_NAME_PREFIX + n)
            c.stop()
            print(f'ALife Engine: {n} is removed.')
        except docker.errors.NotFound as e:
            print(f'ALife Engine: {n} not found.')


def exec_command(node_name, command):
    container = client.containers.get(DOCKER_CONTAINER_NAME_PREFIX + node_name)
    result = container.exec_run(command)
    return result.output.decode()


def command_run(argv):
    parser = argparse.ArgumentParser(description='run node process.')
    parser.prog += f' {sys.argv[1]}'
    parser.add_argument('node_name', nargs='+', help="node name or 'all'.")
    args = parser.parse_args(argv)

    if args.node_name[0] == 'all':
        node_list = find_all_nodes()
    else:
        node_list = args.node_name

    for n in node_list:
        exec_command(n, f'cp /dev/null {DOCKER_CONTAINER_LOG_PATH}')
        result = exec_command(n, 'supervisorctl start aenode')
        print(result)


def command_stop(argv):
    parser = argparse.ArgumentParser(description='run node process.')
    parser.prog += f' {sys.argv[1]}'
    parser.add_argument('node_name', nargs='+', help="node name or 'all'.")
    args = parser.parse_args(argv)

    if args.node_name[0] == 'all':
        node_list = find_all_nodes()
    else:
        node_list = args.node_name

    for n in node_list:
        result = exec_command(n, 'supervisorctl stop aenode')
        print(result)

def command_restart(argv):
    parser = argparse.ArgumentParser(description='run node process.')
    parser.prog += f' {sys.argv[1]}'
    parser.add_argument('node_name', nargs='+', help="node name or 'all'.")
    args = parser.parse_args(argv)

    if args.node_name[0] == 'all':
        node_list = find_all_nodes()
    else:
        node_list = args.node_name

    for n in node_list:
        result = exec_command(n, 'supervisorctl stop aenode')
        print(result)
    for n in node_list:
        exec_command(n, f'cp /dev/null {DOCKER_CONTAINER_LOG_PATH}')
        result = exec_command(n, 'supervisorctl start aenode')
        print(result)


def command_log(argv):
    parser = argparse.ArgumentParser(description='peint log.')
    parser.prog += f' {sys.argv[1]}'
    parser.add_argument('node_name', help="node name.")
    parser.add_argument("-f", "--follow", help="Follow log output", action="store_true")
    args = parser.parse_args(argv)
    result = exec_command(args.node_name , f'cat {DOCKER_CONTAINER_LOG_PATH}')
    print(result, end='', flush=True)
    if args.follow:
        while True:
            new_result = exec_command(args.node_name , f'cat {DOCKER_CONTAINER_LOG_PATH}')
            if len(new_result) < len(result):
                print('---- restarted ----')
                print(new_result, end='', flush=True)
            else:
                print(new_result[len(result):], end='', flush=True)
            result = new_result
            time.sleep(0.1)


def command_connect(argv):
    parser = argparse.ArgumentParser(description='connect node.')
    parser.prog += f' {sys.argv[1]}'
    parser.add_argument('source', help='source_node:source_var_name')
    parser.add_argument('target', help='target_node_name:target_var_name')
    args = parser.parse_args(argv)

    src_node = args.source.split(':')[0]
    src_vname = args.source.split(':')[1]
    tgt_node = args.target.split(':')[0]
    tgt_vname = args.target.split(':')[1]

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


def command_test(argv):
    test()


def command_server(argv):
    parser = argparse.ArgumentParser(description='controll server.')
    parser.prog += f' {sys.argv[1]}'
    parser.add_argument('command', choices=['start', 'stop'], help="command")
    args = parser.parse_args(argv)
    if args.command == 'start':
        start_server()
    elif args.command == 'stop':
        stop_server()


COMMAND_MAP = {
    'server': command_server,
    'ls': command_list_node,
    'create': command_create,
    'remove': command_remove,
    'rm': command_remove,
    'run': command_run,
    'start': command_run,
    'stop': command_stop,
    'restart': command_restart,
    'log': command_log,
    'connect': command_connect,
    'test': command_test
}


def main():
    parser = argparse.ArgumentParser(description='ALifeEngine CLI Interface')
    parser.add_argument('command', choices=COMMAND_MAP.keys(), help='command')

    args = parser.parse_args(sys.argv[1:2])

    COMMAND_MAP[args.command](sys.argv[2:])
