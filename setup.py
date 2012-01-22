from setuptools import setup, find_packages

setup(
    name = "Wicked Jukebox Daemon",
    version = "1.0dev1",
    packages = find_packages(),
    install_requires = [
        'mysql-python',
        'mutagen',
    ],
    entry_points = {
        'console_scripts': [
            'scan = jukeboxd.utils:cli_scan'
            ]
        }
)
