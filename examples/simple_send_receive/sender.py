import alifeengine
import time

x = 0
while True:
    x += 1
    print(f'My variable x: {x}')
    alifeengine.send('msg', 'I incremented X!')
    alifeengine.send('X', x)
    time.sleep(1)
