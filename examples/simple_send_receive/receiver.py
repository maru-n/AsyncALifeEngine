import alifeengine
import time

def func(x):
    print(f'Received variable {x}')

alifeengine.add_listener('sender', func)

while True:
    print("hello")
    time.sleep(1)
