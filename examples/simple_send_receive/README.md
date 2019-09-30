```ShellSession
2つのノードを作成
$ ae-cli --name sender sender.py
$ ae-cli --name receiver receiver.py

コネクションの作成
$ ae-cli connect sender receiver

プログラムの開始
$ ae-cli run sender
$ ae-cli run receiver

ログの表示
$ ae-cli log sender -f
or
$ ae-cli log receiver -f
```
