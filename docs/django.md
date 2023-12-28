## install

* 1.安装django : 
```bash
$ pip install django==4.2.1
```

* 2.创建项目 : 
```bash
$ django-admin startproject djangoapp
```

查看项目结构，最外层`djangoapp`为项目名称或者工作目录，这个名称是可以修改的。
第二层`djangoapp`，为应用程序目录，这个就不建议修改了. 自己新增的模块应该在第二层`djangoapp`下面.
```
$ tree
├── djangoapp
│   ├── djangoapp
│   │   ├── asgi.py
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── manage.py
```

* 3.进入虚拟环境 : 
```bash
# 进入项目目录
$ cd dangoapp 
# 初始化虚拟环境
$ pipenv --python 3.9
# 进入虚拟环境
$ pipenv shell
```

* 4.创建模型 : 
```bash
# 进入与项目同名的程序目录，将自己的模块创建在与 settings.py 同级的目录中
$ cd djangoapp
# 创建模型/模块，命令： python ../manage.py startapp student(模块名称)
$ python ../manage.py startapp student
$ python ../manage.py startapp clazz
$ python ../manage.py startapp school
$ python ../manage.py startapp course
```
  
* 将模型生成数据库表：
```bash
# 生成数据库配置文件，命令格式：python manage.py makemigrations ${app_name}
$ python manage.py makemigrations student
# 同步到数据库
$ python manage.py migrate
```