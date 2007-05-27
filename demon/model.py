from sqlalchemy import *
import ConfigParser, os

def LoadConfig(file, config={}):
    """
    returns a dictionary with key's of the form
    <section>.<option> and the values.

    from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65334
    """
    config = config.copy()
    cp = ConfigParser.ConfigParser()
    cp.read(file)
    for sec in cp.sections():
        name = sec.lower()
        for opt in cp.options(sec):
            config[name + "." + opt.lower()] = cp.get(sec, opt).strip()
    return config

# load the configuration file, and set up the DB-conenction
config = LoadConfig(os.path.join('..', 'config.ini'))

if config['database.type'] == 'sqlite':
   dburi = "%s:///%s" % (
         config['database.type'],
         config['database.file'],
         )
else:
   dburi = "%s://%s:%s@%s/%s" % (
         config['database.type'],
         config['database.user'],
         config['database.pass'],
         config['database.host'],
         config['database.base'],
         )

# ----------------------------------------------------------------------------
# Table definitions
# ----------------------------------------------------------------------------

metadata = BoundMetaData(dburi, encoding='utf-8', echo=True)

playmodeTable = Table( 'playmode', metadata, autoload=True )
channelTable = Table('channel', metadata, autoload=True )
settingTable = Table('setting', metadata, autoload=True )

# ----------------------------------------------------------------------------
# Mappers
# ----------------------------------------------------------------------------
