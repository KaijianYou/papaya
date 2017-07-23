# Papaya
A simple blog system based on Flask -- a framework for Python.<br/>


## Demo
[Wasted] Please visit https://flaskfb.herokuapp.com/<br>


## Reference
*Flask Web Development: Developing Web Applications with Python* by Miguel Grinberg (O'Reilly). CopyRight 2014 Miguel Grinberg, 978-1-449-3726-2<br/>
中文版：《Flask Web开发  基于Python的Web应用开发实战》，作者：Miguel Grinberg，译者：安道，人民邮电出版社 2015，ISBN: 978-7-115-37399-1


## Quick Start
### Install and run database
    # Mac OS X
    $ brew install postgresql

    # initiate database
    $ initdb /usr/local/var/postgres -E utf8

    # run database
    $ pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start


### Create user and dababase
    # login postgresql console
    $ psql

    =# CREATE USER your_username WITH PASSOWRD 'your_password';
    =# CREATE DATABASE your_dbname OWNER your_username;
    =# GRANT ALL PRIVILEGES ON DATABASE your_dbname TO your_username;


### Create isolated python environment
    $ virtualenv --no-site-packages venv

    # activate isolated python environment
    $ source venv/bin/activate

    # if you want to exit isolated python environment, please run
    (venv) $ deactivate


### Install python packages
    (venv) $ pip install -r requirements/development.txt


### Initiate Data
    (venv) $ python manage.py db upgrade
    (venv) $ python manage.py shell
    >>> Role.insert_roles()
    >>> Category.insert_categories()
    >>> User.add_self_follows()


### Set environment variables
    (venv) $ export MAIL_USERNAME='your_qq_email_address'
    (venv) $ export MAIL_PASSWORD='your_qq_email_password'
    (venv) $ export DEV_DATABASE_URL='your_database_url'
    (venv) $ export ADMIN_EMAIL='your_qq_email_address'
`database_url`: for example,
> 'postgresql+psycopg2://username:password@host/database_name'

Otherwise, if you don't have a QQ email address, you can use others. But you should modify the configuration about QQ email in 'config.py' file and ensure they can work.<br/>

For further information, please see [SQLAlchemy Engine Configuration](http://docs.sqlalchemy.org/en/latest/core/engines.html)<br/>


### Run web application
    (venv) $ python manage.py runserver

Now open your browser and visit http://127.0.0.1:5000/<br/>


### Acknowledgements
Thanks Python and Flask and their developers
<br>
Thanks Miguel Grinberg

如果发现有什么问题，请不吝赐教。ㄟ( ▔, ▔ )ㄏ
