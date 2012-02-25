from distutils.core import setup
import py2exe
setup(
   windows = [{"script": "wickedclient.py"}],
   options = {"py2exe":{"includes":["sip", "PyQt4._qt"]}}
   )