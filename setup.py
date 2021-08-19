from setuptools import setup, find_packages
from os.path import join

NAME = 'wickedjukebox'

setup(
    name=NAME,
    version="2.2.3",
    packages=find_packages(exclude=["test"]),
    entry_points={
        'console_scripts': [
                'run-channel=wickedjukebox.cli.run_channel:main',
                'jukebox-admin=wickedjukebox.cli.jukebox_admin:main',
            ]
        },
    install_requires=[
        "alembic",
        "blessings",
        "config-resolver",
        "gouge",
        "mutagen",
        "ply",
        "progress",
        "pusher",
        "pymysql",
        "python-mpd2",
        "requests",
        "sqlalchemy",
    ],
    extras_require={
        "dev": [
            "black",
            "coverage[toml]",
            "pylint",
            "pytest",
            "pytest-cache",
            "pytest-coverage",
            "pytest-sqlalchemy",
        ]
    },
    include_package_data=True,
    zip_safe=False
)
