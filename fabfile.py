from ConfigParser import SafeConfigParser

import fabric.api as fab
import fabric.colors as clr


@fab.task
def develop():
    fab.local('virtualenv env')
    fab.local('./env/bin/pip install -e .')
    fab.local('./env/bin/pip install alembic')

    ipy = fab.prompt(clr.green('Do you want ipython [Y/n]?'),
                     default='Y').strip().upper()
    if ipy == 'Y':
        fab.local('./env/bin/pip install ipython')

    conf = SafeConfigParser()
    conf.read('alembic.ini.dist')
    conf.read('alembic.ini')
    url = fab.prompt(clr.green('Please enter the database DSN:'),
                     default=conf.get('alembic', 'sqlalchemy.url'))
    conf.set('alembic', 'sqlalchemy.url', url)
    with open('alembic.ini', 'w') as fptr:
        conf.write(fptr)
