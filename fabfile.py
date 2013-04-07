""" Deployment of your django project.
"""

from fabric.api import *
import os
import time
# import requests

#env.hosts = ['triviastats.com']
env.user = "triviastats"

def update_django_project(path, branch):
    """ Updates the remote django project.
    """
    with cd(path):
        sudo('git stash')
        sudo('git pull origin {0}'.format(branch))
        sudo('git checkout {0}'.format(branch))
        # sudo('git clean -f')


def django_functions(path, settings):
    with cd(path):
        with prefix('source ' + os.path.join(path, 'bin/activate')):
            # Need newer distribute for MySQL-python package
            sudo('pip install -r ' + os.path.join(path, 'requirements.txt'))
            sudo('python manage.py syncdb --settings={0}'.format(settings))
            # sudo('python manage.py collectstatic -c --noinput --settings={0}'.format(settings))
            #sudo('python manage.py migrate') # if you use south

def south_migration(path, settings):
    with cd(path):
        with prefix('source ' + os.path.join(path, 'bin/activate')):

            sudo('python manage.py migrate'.format(settings)) # if you use south

def update_permissions(path):
    with cd(path):
        sudo('chown -R {0}:{0} {1}'.format(env.user, path))


def restart_webserver(service):
    """ Restarts remote nginx and uwsgi.
    """
    sudo("stop {0}".format(service))
    # Give uwsgi time to shut down cleanly
    time.sleep(2)
    sudo("start {0}".format(service))
    sudo("/etc/init.d/nginx reload")


def install_packages():
    sudo("apt-get install libxml2-dev libxml2 libxslt-dev python-dev libsqlite3-dev mysql-client python-mysqldb libmysqlclient-dev")


def mkdirs(path):
    sudo("mkdir -p {0}/staticfiles".format(path))


def deploy():
    """ Deploy Django Project.
    """
    path = '/home/triviastats/90fm_trivia_stats'
    # install_packages()
    # mkdirs(path)
    update_django_project(path, branch='master')
    update_permissions(path)
    django_functions(path, settings='trivia_stats.settings')
    # south_migration(path, settings='trivia_stats.settings')
    restart_webserver(service='triviastats')


def production():
    env.hosts = ['triviastats.com']

# def testing():
#     env.hosts = ['testing.triviastats.com']

