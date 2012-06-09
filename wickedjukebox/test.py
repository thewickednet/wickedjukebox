from wickedjukebox.model.core import *
from getpass import getpass

from sqlalchemy import create_engine
engine = create_engine('postgresql+psycopg2://exhuma:%s@localhost/crazydb' % getpass(), echo=True)


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
