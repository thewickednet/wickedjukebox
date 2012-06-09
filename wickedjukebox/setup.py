from setuptools import setup
setup(
   name = "wickedjukebox Model",
   version = "1.0dev1",
   packages = ["wickedjukebox.model"],
   install_requires = [
      'psycopg2',
      'sqlalchemy',
      ],
   author = "Michel Albert",
   author_email = "michel@albert.lu",
   description = "Core model for the wickedjukebox",
   license = "BSD",
)
