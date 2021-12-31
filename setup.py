from os.path import join

from setuptools import find_packages, setup

NAME = "wickedjukebox"

setup(
    name=NAME,
    version="3.0.0a1",
    packages=find_packages(exclude=["test"]),
    entry_points={
        "console_scripts": [
            "run-channel=wickedjukebox.cli.run_channel:main",
            "jukebox-admin=wickedjukebox.cli.jukebox_admin:main",
        ]
    },
    install_requires=[
        "alembic",
        "config-resolver",
        "gouge",
        "mutagen",
        "ply",
        "progress",
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
            "sphinx",
        ]
    },
    include_package_data=True,
    zip_safe=False,
)
