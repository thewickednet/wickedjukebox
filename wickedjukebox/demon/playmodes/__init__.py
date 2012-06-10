def create(modname):
   if modname in globals():
      return reload(globals()[modname])

   module = 'wickedjukebox.demon.playmodes.%s' % modname
   __import__(module)
   return globals()[modname]
