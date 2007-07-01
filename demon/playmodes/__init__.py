def create(modname):
   module = 'demon.playmodes.%s' % modname
   __import__(module)
   return globals()[modname]
