#!/usr/bin/python

import unittest
from demon.model import *

class TestSettings(unittest.TestCase):
   def setUp(self):
      "Bootstrapping"
      i = settingTable.insert( values = { 'var': bindparam("var"), 'value': bindparam("value"), "channel_id": bindparam("channel_id"), "user_id": bindparam("user_id") } )
      i.execute(
            { "var": "unittest_testglobal", "value": 1, "channel_id": 0, "user_id": 0 },
            { "var": "unittest_testuser", "value": 1, "channel_id": 0, "user_id": 1 },
            { "var": "unittest_testchannel", "value": 1, "channel_id": 1, "user_id": 0 },
            { "var": "unittest_testuserchannel", "value": 1, "channel_id": 1, "user_id": 1 },
            )

   def tearDown(self):
      "Cleanung up"
      settingTable.delete( settingTable.c.var == "unittest_testglobal" ).execute()
      settingTable.delete( settingTable.c.var == "unittest_testuser" ).execute()
      settingTable.delete( settingTable.c.var == "unittest_testchannel" ).execute()
      settingTable.delete( settingTable.c.var == "unittest_testuserchannel" ).execute()

   def testMissingValueDefault(self):
      "Test if we get back the default value if the setting did not exist, but we specified a value"
      expectedValue = 1
      result = getSetting( "unittest_bogusVariable", 1 )
      self.assertEqual( expectedValue, result )

   def testMissingValueNoDefault(self):
      "Test if we get back None (NULL) if the setting did not exist, and we did not specify a default"
      expectedValue = None
      result = getSetting( "unittest_bogusVariable" )
      self.assertEqual( expectedValue, result )

   def testGlobalValue(self):
      "Test if we get back global values correctly"
      expectedValue = "1"
      result = getSetting( "unittest_testglobal" )
      self.assertEqual( expectedValue, result )

   def testUserValue(self):
      "Test if we get back user values correctly"
      expectedValue = "1"
      result = getSetting( "unittest_testuser", user=1 )
      self.assertEqual( expectedValue, result )

   def testChannelValue(self):
      "Test if we get back channel values correctly"
      expectedValue = "1"
      result = getSetting( "unittest_testchannel", channel=1 )
      self.assertEqual( expectedValue, result )

   def testFallbackValue(self):
      "Test if we properly do a fallback from a channel to a global setting"
      expectedValue = "1"
      result = getSetting( "unittest_testglobal", channel=1 )
      self.assertEqual( expectedValue, result )

if __name__ == '__main__':
   suite = unittest.TestLoader().loadTestsFromTestCase(TestSettings)
   unittest.TextTestRunner(verbosity=2).run(suite)

