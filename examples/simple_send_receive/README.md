## Tutorial

### 1. start ALifeEngine server

```ShellSession
$ ae-cli server start
```

### 2. create 2 nodes, sender and receiver

```ShellSession
$ ae-cli --name sender sender.py
$ ae-cli --name receiver receiver.py
```

![Untitled (12)](https://user-images.githubusercontent.com/1583412/66202306-5f73d400-e6e0-11e9-958a-7653ddc3cc40.png)

### 3. start nodes and show log

```ShellSession
$ ae-cli start sender
$ ae-cli start receiver
```

![Untitled (11)](https://user-images.githubusercontent.com/1583412/66202307-5f73d400-e6e0-11e9-9b7b-685838b907e4.png)

```ShellSession
$ ae-cli log sender -f
My variable x: 1
My variable x: 2
My variable x: 3
...
```

別のコンソールで
```
$ ae-cli log receiver -f
```
ここでは何も表示されない

### 4. connect 2 nodes

sender nodeのXチャネルをreceiverノードのrecvチャネルをつなぐ
```ShellSession
$ ae-cli connect sender:X receiver2:recv
```
上のreceiverのlogコンソールに表示が始まる
```ShellSession
Received: 36
Received: 37
Received: 38
...
```

![Untitled (10)](https://user-images.githubusercontent.com/1583412/66202309-600c6a80-e6e0-11e9-9eed-95e7aa6865f8.png)

### 5. make new receiver node

```ShellSession
$ ae-cli --name receiver2 receiver.py
$ ae-cli start receiver2
$ ae-cli connect sender:msg receiver2:recv
$ ae-cli log receiver2 -f
Received: I incremented X!
Received: I incremented X!
Received: I incremented X!
...
```

![Untitled (9)](https://user-images.githubusercontent.com/1583412/66202310-600c6a80-e6e0-11e9-97a8-0c7253ad1be9.png)


