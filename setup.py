from setuptools import setup, find_packages
from pkg_resources import resource_string
setup(
    name="jukebox",
    version=resource_string('jukebox', 'version.txt').strip().decode('ascii'),
    packages=find_packages(),
    install_requires=[
        'config_resolver >= 4.0, <5.0',
        'cssmin',
        'flask',
        'flask-assets',
        'flask-jwt',
        'flask-login',
        'flask-mail',
        'flask-sqlalchemy',
        'flask-wtf',
        'passlib',
        'pymysql',
    ],
    include_package_data=True,
    author="Yves Thommes",
    author_email="ythommes@gmail.com",
    description="Wicked Jukebox",
    license="BSD",
    url="https://github.com/wickeddoc/wickedjukebox",
)
