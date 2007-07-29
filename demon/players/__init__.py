def create(modname, backend_params=None):
   # parse parameters, and put them into a dictionary
   params = {}
   if backend_params is not None:
      for param in backend_params.split(','):
         key, value = param.split('=')
         params[key.strip()] = value.strip()

   module = 'demon.players.%s' % modname
   __import__(module)
   globals()[modname].config(params)
   return globals()[modname]
