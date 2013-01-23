from setuptools import setup, find_packages

setup(
    name="wickedjukebox",
    version="2.0.2",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
                'run-channel=wickedjukebox.cli.run_channel:main',
                'jukebox-admin=wickedjukebox.cli.jukebox_admin:main',
            ]
        },
    install_requires=[
        'sqlalchemy==0.7.1',
        'mysql-python==1.2.3',
        'mutagen==1.20',
        'ply==3.4',
        'scrobbler==1.0.0a2',
        'shout-python==0.2.1',
        'config_resolver==3.0',
        'elementtree==1.2.7-20070827-preview',  # required by lastfm module
    ],
    dependency_links=['http://downloads.us.xiph.org/releases/libshout/']

)
