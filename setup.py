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
        'alembic',
        'config_resolver',
        'mutagen',
        'mysql-python',
        'ply',
        'requests',
        'scrobbler',
        'shout-python',
        'sqlalchemy',
    ],
    include_package_data=True,
    zip_safe=False
)
