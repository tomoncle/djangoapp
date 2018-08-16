## install:
  ```
  $ pip install pipenv
  ```

## usage:
* step1 新建项目`djangoapp` : `$ mkdir djangoapp_env　& cd djangoapp_env`
* step2 初始化Python版本 : `$ pipenv --python 2.7` or `$ pipenv --python 3.6`
* step3 进入虚拟环境 : $ `pipenv shell`, 检测环境
  ```
    (djangoapp-UYxpfvzv)liyuanjun@aric-ThinkPad-E450:~/.r/djangoapp_env$ python -V
    Python 2.7.6
    (djangoapp-UYxpfvzv)liyuanjun@aric-ThinkPad-E450:~/.r/djangoapp_env$ python -c "import os"
    (djangoapp-UYxpfvzv)liyuanjun@aric-ThinkPad-E450:~/.r/djangoapp_env$ python -c "import requests"
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
    ImportError: No module named requests
    (djangoapp-UYxpfvzv)liyuanjun@aric-ThinkPad-E450:~/.r/djangoapp_env$
  ```
* step4 安装依赖包 : `$ pipenv install requests` 或 `$ pipenv install` 会安装Pipfile中的所有依赖
* step5 退出 : `$ exit`