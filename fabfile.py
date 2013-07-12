import fabric.api as fab


@fab.task
def develop():
    fab.local('virtualenv env')
    fab.local('./env/bin/pip install -e .')
    fab.local('./env/bin/pip install alembic')

    ipy = fab.prompt('Do you want ipython [Y/n]?', default='Y').strip().upper()
    if ipy == 'Y':
        fab.local('./env/bin/pip install ipython')
