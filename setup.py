"""
Setup script for the wickedjukebox module.
"""
from setuptools import setup, find_packages

setup(
    name="wickedjukebox",
    version=__import__('wickedjukebox').__version__,
    packages=find_packages(),
    install_requires=[
        'sqlalchemy',
        'mutagen',
        'shout-python',
    ],
    dependency_links=['http://downloads.us.xiph.org/releases/libshout/']

)
