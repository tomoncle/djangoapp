# djangoapp
django web application sample.

## [使用 Gunicorn 托管 Django](https://docs.djangoproject.com/zh-hans/4.2/howto/deployment/wsgi/gunicorn/) 

### 1.安装：
```bash
$ pip install gunicorn
```

### 2.使用 `wsgi` 需要将 当前项目 和 Python环境 加入 `PYTHONPATH` 环境变量

* 方法一：
```bash
$ export PYTHONPATH=${PYTHONPATH}:`pip -V | awk '{print $4}' | awk '{gsub(/\/pip/,"");print}'`:`pwd`
```

* 方法二：
```bash
$ export PYTHONPATH=${PYTHONPATH}:/root/.local/share/virtualenvs/djangoapp-yg1Eq-7T/lib/python3.9/site-packages:/opt/djangoapp
```

### 3.运行命令启动

常用参数：

* `-b` : 指定IP:端口, 例如 `-b 0.0.0.0:8080`
* `-w` : 启用进程数量，例如 `-w 4`
* `-D` : 后台启动
* `-k` : 工作模式, sync（默认），eventlet（协程异步），gevent（协程异步）
* `--threads` : 每个进程启用线程数量（需安装`gthread`库, 工作模式改为`-k gthread`），例如 `--threads 4 -k gthread`
* `--access-logfile` : 访问日志
* `--access-logfile` : 错误日志
* `--capture-output` : 重定向标准输出和标准错误信息到错误日志
* `--reload` : 热加载
* `--forwarded-allow-ips` : [127.0.0.1,192.168.0.0/24]

```bash
$ gunicorn djangoapp.wsgi -b 0.0.0.0:8080 -w 4 --log-level debug -D 
```