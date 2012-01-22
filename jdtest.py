from time import sleep
import logging
logging.basicConfig()

from jukeboxd import daemon

q = daemon.run()
print "started"
sleep(2)
print "stopping"
daemon.stop(q)
print "stopped"
