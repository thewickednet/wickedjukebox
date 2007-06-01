import os,ConfigParser, threading

def loadConfig(file, config={}):
    """
    returns a dictionary with key's of the form
    <section>.<option> and the values.

    from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65334
    """
    if not os.path.exists( file ):
       raise ValueError, 'Cannot find configfile "%s"' % file
    config = config.copy()
    cp = ConfigParser.ConfigParser()
    cp.read(file)
    for sec in cp.sections():
        name = sec.lower()
        for opt in cp.options(sec):
            config[name + "." + opt.lower()] = cp.get(sec, opt).strip()
    return config

# load the configuration file, and set up the DB-conenction
config = loadConfig(os.path.join('config.ini'))

class Scrobbler(threading.Thread):

   """
   Submits tracks to last.fm. It does not submit more than one song per minute
   to easen last.fm's load
   """

   __keepRunning = True

   def __init__(self, user, passwd):
      """
      Constructor
      """
      threading.Thread.__init__(self)
      self.setName( '%s (%s)' % (self.getName(), 'Scro') )

      self.__user = user
      self.__pwd  = passwd

   def getConnection(self, user, password):

      url = "post.audioscrobbler.com"

      print "opening last.fm handshake uri"

      params = urllib.urlencode({
         'hs': 'true',
         'p':  '1.1',
         'c':  'tst',
         'v':  '1.0',
         'u':  user
         })
      conn = httplib.HTTPConnection(url)
      conn.request("GET", "/?%s" % params )
      r = conn.getresponse()
      data = r.read()
      print "Last.FM response: \n %s" % data
      conn.close()
      print "... response received. Authencitating... "

      challenge = data.split()[1]
      posturl   = data.split()[2]
      interval  = data.split()[4]

      challengeresponse = md5.md5('%s%s' % (password, challenge)).hexdigest()
      return (challengeresponse, posturl, float(interval))

   def scrobble(self, song, time_played):
      pltime = time_played.isoformat(' ')
      if '.' in pltime:
         pltime = pltime.split('.')[0]
      try:
         print 'Scrobbling %s - %s' % (song.artist.name, song.title)
         while True:
            try:
               conn = httplib.HTTPConnection(self.__posturl.split('/')[2])
               params = urllib.urlencode({
                  'u': 'exhuma',
                  's': self.__cr,
                  'a[0]': unicode(song.artist.name),
                  't[0]': unicode(song.title),
                  'b[0]': unicode(song.album.title),
                  'm[0]': '',
                  'l[0]': song.duration,
                  'i[0]': pltime
               })
               print "params: %s" % params
               headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
               conn.request("POST", '/' + '/'.join(self.__posturl.split('/')[3:]), params, headers)
               r = conn.getresponse()
               data = r.read()
               print "Last.FM response: \n %s" % data
               conn.close()
            except Exception, ex:
               # Wait 3 seconds, the loop
               print 'Exception caught (%s). Retrying...' % str(ex)
               time.sleep(3)
               continue
            ## except BadStatusLine:
            ##    # Wait 3 seconds, the loop
            ##    self.__logger.warning('Bad Status Line error received. Retrying...')
            ##    time.sleep(3)
            ##    continue
            # No more exceptions, so we can break out of the loop
            break
      except UnicodeDecodeError:
         import traceback
         print "UTF-8 error when scrobbling. Skipping this song\n%s" % traceback.format_exc()

   def run(self):
      """
      The main control loop of the Scrobbler.
      It checks once a minute if there are new songs on the scrobbler queue
      that should be submitted, then submits them.
      """

      self.__cr, self.__posturl, self.__interval = self.getConnection(self.__user, self.__pwd)
      print "Scrobbler started"

      while self.__keepRunning:
         try:
            nextScrobble = LastFMQueue.select(orderBy=LastFMQueue.q.id)[0]
            self.scrobble( song = nextScrobble.song, time_played=nextScrobble.time_played )
            nextScrobble.destroySelf()
         except IndexError:
            # nothing to scrobble
            pass
         time.sleep(5)
      print "Scrobbler stopped"

   def stop(self):
      self.__keepRunning = False

