import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages

setup(
    name = "Wicked Jukebox",
    version = "2.0",
    packages = find_packages(),
    scripts = ['arbiter.py', 'run_channel.py', 'jukebox-admin.py'],

    install_requires = [
        'sqlalchemy',
        'mysql-python',
        'mutagen',
        'simplejson',
        'ply',
        'scrobbler',
        'ElementTree', # required by lastfm module
    ],

)
