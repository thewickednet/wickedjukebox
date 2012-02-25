from setuptools import setup, find_packages

setup(
    name = "wickedjukebox",
    version = "3.0dev1",
    packages = find_packages(),
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
