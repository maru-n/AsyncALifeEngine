# AsyncALifeEngine

## Install

```ShellSession
$ pip install git+https://github.com/maru-n/AsyncALifeEngine.git
```

## Usage

計算ノードの作成
```ShellSession
$ ae-cli create --name [node_name] [python_script]
```


コネクションの作成
```ShellSession
$ ae-cli connect [node_name1] [node_name2]
```

ノードのスタート/ストップ
```ShellSession
$ ae-cli run [node_name]
$ ae-cli stop [node_name]
```

ログの表示
```ShellSession
$ ae-cli log -f [node_name]
```

ノードの削除
```ShellSession
$ ae-cli remove [node_name]
```

## Examples

https://github.com/maru-n/AsyncALifeEngine/tree/master/examples/simple_send_receive
