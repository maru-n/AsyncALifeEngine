AE_SERVER_HOSTNAME = 'host.docker.internal'

# Default node name is {DEFAULT_NODE_NAME}{INDEX}
DEFAULT_NODE_NAME = 'node_'

AE_SERVER_HOST = '127.0.0.1'
AE_SERVER_COMMAND_PORT = 8888
AE_SERVER_MESSAGE_PORT = 8889

LIBRARY_REQUIPMENTS = ['bottle']

## settings related with Docker ##
# Docker container name is {DOCKER_CONTAINER_NAME_PREFIX}{NODE_NAME}
DOCKER_CONTAINER_NAME_PREFIX = 'aenode.'
DOCKER_CONTAINER_SCRIPT_DIR = '/app/scripts'
DOCKER_CONTAINER_LIBRARY_DIR = '/app/alifeengine'
DOCKER_IMAGE_NAME = 'marun/alifeengine_node:latest'
DOCKER_NETWORK_NAME = 'alifeengine_network'
DOCKER_CONTAINER_LOG_PATH = '/var/log/aenode.log'
DOCKER_CONTAINER_MESSAGE_PORT = 8889
