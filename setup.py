from setuptools import setup, find_packages
from os.path import join

NAME = 'wickedjukebox'
VERSION = open(join(NAME, 'version.txt')).read().strip()

setup(
    name=NAME,
    version=VERSION,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
                'run-channel=wickedjukebox.cli.run_channel:main',
                'jukebox-admin=wickedjukebox.cli.jukebox_admin:main',
            ]
        },
    install_requires=[
        'sqlalchemy',
        'mysql-python',
        'mutagen',
        'ply',
        'scrobbler',
        'shout-python',
        'config_resolver',
        'elementtree',  # required by lastfm module
    ],
    include_package_data=True,
    zip_safe=False
)
