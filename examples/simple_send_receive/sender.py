import alifeengine
import time

x = 0
while True:
    print(f'My variable x:{x}')
    x += 1
    alifeengine.send('receiver', {'X': x})
    time.sleep(1)
