import alifeengine
import time

def func(var, variable_name):
    print(f'Received {variable_name}:{var}')

def func2(var):
    print(f'Received_X {var}')

alifeengine.add_listener(func)
alifeengine.add_listener(func2, 'r_X')

while True:
    time.sleep(10)
