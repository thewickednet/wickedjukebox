import fabric.api as fab

PATH = '/var/www/wickedjukebox.com/flask'


@fab.task
def undeploy():
    fab.local(PATH + '/venv/bin/pip uninstall jukebox')


@fab.task
def deploy():
    fab.local(PATH + '/venv/bin/pip install .')
    fab.local('sudo service apache2 reload')


@fab.task
def redeploy():
    fab.execute(undeploy)
    fab.execute(deploy)
