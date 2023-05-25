# djangoapp
django web application sample.

## [使用 Gunicorn 托管 Django](https://docs.djangoproject.com/zh-hans/4.2/howto/deployment/wsgi/gunicorn/) 

* 1.安装：
```bash
$ pip install gunicorn
```

* 2.使用 `wsgi` 需要将当前项目加入 `PYTHONPATH` 环境变量
```bash
# 方法一：通用命令
$ export PYTHONPATH=${PYTHONPATH}:`pip -V | awk '{print $4}' | awk '{gsub(/\/pip/,"");print}'`:`pwd`

# 方法二：指定你的项目及python环境
$ export PYTHONPATH=${PYTHONPATH}:/root/.local/share/virtualenvs/djangoapp-yg1Eq-7T/lib/python3.9/site-packages:/opt/djangoapp
```

* 3.运行命令启动
```bash
######################### 常用参数 #########################
# -b 0.0.0.0:8080 指定IP：端口，-w 4 启用4个进程，-D 后台运行
# --access-logfile /var/log/django-access.log 访问日志
# --error-logfile  /var/log/django-error.log  错误日志
# --capture-output 重定向标准输出和标准错误信息到错误日志

$ gunicorn djangoapp.wsgi \
  -b 0.0.0.0:8080 \
  -w 4 \
  --capture-output \
  --access-logfile /var/log/django-access.log \
  --error-logfile  /var/log/django-error.log \
  --log-level debug \
  -D 
```