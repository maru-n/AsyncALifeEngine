#!/usr/bin/env python

import docker
import argparse
from os import path
import sys
import time


client = docker.from_env()

# Default node name is {DEFAULT_NODE_NAME}{INDEX}
DEFAULT_NODE_NAME = 'node_'

# Docker container name is {DOCKER_CONTAINER_NAME_PREFIX}{NODE_NAME}
DOCKER_CONTAINER_NAME_PREFIX = 'aenode.'
DOCKER_CONTAINER_SCRIPT_DIR = '/app/scripts'
DOCKER_IMAGE_NAME = 'marun/alifeengine_node:latest'
DOCKER_NETWORK_NAME = 'alifeengine_network'
DOCKER_CONTAINER_LOG_PATH = '/var/log/aenode.log'

import unittest

class Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_find_all_containers(self):
        pass

    def tearDown(self):
        pass


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

    container = client.containers.run(image=DOCKER_IMAGE_NAME,
                                      name=container_name,
                                      hostname=container_name,
                                      detach=True,
                                      auto_remove=True,
                                      privileged=True,
                                      volumes = {script_dir: {'bind': DOCKER_CONTAINER_SCRIPT_DIR, 'mode': 'ro'}})
    container.exec_run(f'ln -s {path.join(DOCKER_CONTAINER_SCRIPT_DIR, script_file)} /app/main.py')

    print(f'ALife Engine: {node_name} is lauched.')


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
    parser.add_argument('node1', help="node name.")
    parser.add_argument('node2', help="node name.")
    args = parser.parse_args(argv)

    # create network if not exist
    network_list = [n.name for n in client.networks.list()]
    if not DOCKER_NETWORK_NAME in network_list:
        client.networks.create(DOCKER_NETWORK_NAME)

    # connect nodes to the network
    net = client.networks.get(DOCKER_NETWORK_NAME)
    net.connect(DOCKER_CONTAINER_NAME_PREFIX + args.node1)
    net.connect(DOCKER_CONTAINER_NAME_PREFIX + args.node2)


def command_test(argv):
    unittest.main()



COMMAND_MAP = {
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
