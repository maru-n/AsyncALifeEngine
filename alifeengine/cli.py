#!/usr/bin/env python

import argparse
import sys
from .core import start_server, stop_server, test, run_node, stop_node, restart_node, log_node, create_node, remove_node, connect_node, print_node_list
from .constants import *


def command_list_node(argv):
    parser = argparse.ArgumentParser(description='list all node.')
    parser.prog += f' {sys.argv[1]}'
    print_node_list()


def command_create(argv):
    parser = argparse.ArgumentParser(description='create node.')
    parser.prog += f' {sys.argv[1]}'
    parser.add_argument('script', help="python script for runnning in the node.")
    parser.add_argument('--name', type=str,
                        help='unique name of the node.')
    args = parser.parse_args(argv)
    create_node(args.script, node_name=args.name)


def command_remove(argv):
    parser = argparse.ArgumentParser(description='run node process.')
    parser.prog += f' {sys.argv[1]}'
    parser.add_argument('node_name', nargs='+', help="node name or 'all'.")
    args = parser.parse_args(argv)
    remove_node(args.node_name)


def command_run(argv):
    parser = argparse.ArgumentParser(description='run node process.')
    parser.prog += f' {sys.argv[1]}'
    parser.add_argument('node_name', nargs='+', help="node name or 'all'.")
    args = parser.parse_args(argv)
    run_node(args.node_name)


def command_stop(argv):
    parser = argparse.ArgumentParser(description='run node process.')
    parser.prog += f' {sys.argv[1]}'
    parser.add_argument('node_name', nargs='+', help="node name or 'all'.")
    args = parser.parse_args(argv)
    stop_node(args.node_name)


def command_restart(argv):
    parser = argparse.ArgumentParser(description='run node process.')
    parser.prog += f' {sys.argv[1]}'
    parser.add_argument('node_name', nargs='+', help="node name or 'all'.")
    args = parser.parse_args(argv)
    restart_node(args.node_name)


def command_log(argv):
    parser = argparse.ArgumentParser(description='peint log.')
    parser.prog += f' {sys.argv[1]}'
    parser.add_argument('node_name', help="node name.")
    parser.add_argument("-f", "--follow", help="Follow log output", action="store_true")
    args = parser.parse_args(argv)
    log_node(args.node_name, follow=args.follow)


def command_connect(argv):
    parser = argparse.ArgumentParser(description='connect node.')
    parser.prog += f' {sys.argv[1]}'
    parser.add_argument('source', help='source_node:source_var_name')
    parser.add_argument('target', help='target_node_name:target_var_name')
    args = parser.parse_args(argv)
    connect_node(args.source.split(':')[0],
                 args.source.split(':')[1],
                 args.target.split(':')[0],
                 args.target.split(':')[1])



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
