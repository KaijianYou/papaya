# FlaskFB
A simple blog system based on Flask -- a framework for Python.<br/>
一个基于 Python Web 框架 —— Flask 开发的简单博客。

## Demo
Please visit https://flaskfb.herokuapp.com/<br>
请访问：https://flaskfb.herokuapp.com/

## Reference
*Flask Web Development: Developing Web Applications with Python* by Miguel Grinberg (O'Reilly). CopyRight 2014 Miguel Grinberg, 978-1-449-3726-2<br/>
中文版：《Flask Web开发  基于Python的Web应用开发实战》，作者：Miguel Grinberg，译者：安道，人民邮电出版社 2015，ISBN: 978-7-115-37399-1

## Start
### Install and run database 安装数据库
    # Mac OS X
    $ brew install postgresql

    # initiate database
    $ initdb /usr/local/var/postgres -E utf8

    # run database
    $ pg_ctl -D /usr/local/var/postgres -l /usr/lcoal/var/postgres/server.log start

### Create user and dababase  创建数据库用户和数据库
    # login postgresql console
    $ psql

    =# CREATE USER your_username WITH PASSOWRD 'your_password';
    =# CREATE DATABASE your_dbname OWNER your_username;
    =# GRANT ALL PRIVILEGES ON DATABASE your_dbname TO your_username;

### Create isolated python environment  创建虚拟 python 环境
    $ virtualenv --no-site-page venv

    # activate isolated python environment 激活虚拟环境
    $ source venv/bin/activate

    # if you want to exit isolated python environment, please run  如果想退出虚拟环境，则运行
    (venv) $ deactivate

### Install python packages  安装 python 包
    (venv) $ pip install -r requirements/development.txt

### Initiate Data  初始化数据
    (venv) $ python manage.py db upgrade
    (venv) $ python manage.py shell
    >>> Role.insert_roles()
    >>> User.add_self_follows()

### Set necessary environment variables  设置必要的环境变量
    (venv) $ export MAIL_USERNAME='your_qq_email_address'
    (venv) $ export MAIL_PASSWORD='your_qq_email_password'
    (venv) $ export DEV_DATABASE_URL='database_url'  # ???
    (venv) $ export ADMIN_EMAIL='your_qq_email_address'
**database_url**: for example, 举个例子
> 'postgresql+psycopg2://username:password@host/database_name'

Otherwise, if you don't have a QQ email address, you can use others. But you should modify the configuration about QQ email in 'config.py' file and ensure they can work.<br/>
另外，如果您没有 QQ，可以使用其他的邮箱。但是你要更改 “config.py” 文件中有关 QQ 邮箱的设置，然后确保它们能正常使用。

for further information, please see [SQLAlchemy Engine Configuration](http://docs.sqlalchemy.org/en/latest/core/engines.html)<br/>
具体设置请见 [SQLAlchemy Engine Configuration](http://docs.sqlalchemy.org/en/latest/core/engines.html)

### Run web application  运行 web 应用
    (venv) $ python manage.py runserver

now open your browser and visit http://127.0.0.1:5000/<br/>
现在可以打开浏览器并访问 http://127.0.0.1:5000/

如果发现问题请不吝赐教。不过我想也没人会看。