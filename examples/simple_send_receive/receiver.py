import alifeengine
import time

def func2(var):
    print(f'Received: {var}')

alifeengine.add_listener(func2, 'recv')

while True:
    time.sleep(10)
