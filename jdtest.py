from jukeboxd import daemon
from time import sleep
import logging
logging.basicConfig()

q = daemon.run()
print "started"
sleep(2)
print "stopping"
daemon.stop(q)
print "stopped"
