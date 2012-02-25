from multiprocessing import Process
import logging
from time import sleep
from pydata import setup_logging

from run_channel import run_channel

setup_logging()

LOG = logging.getLogger(__name__)
POOL =[]
CHANNELS = ['wicked', 'fiction']

def monitor():
   while True:
      for proc in POOL:
         if not proc.is_alive() and proc.exitcode != 0:
            LOG.warning( "Channel %-10s died. Restarting...." % proc.name )
            POOL.remove(proc)
            new_proc = Process(
                  target=run_channel,
                  args=(proc.name,),
                  name=proc.name )
            POOL.append( new_proc )
            new_proc.start()
      sleep(1)

def main():
   for channel_name in CHANNELS:
      proc = Process(
            target=run_channel,
            args=(channel_name,),
            name=channel_name )
      POOL.append(proc)
      proc.start()

   # start monitoring
   monitor()

if __name__ == "__main__":
   main()

