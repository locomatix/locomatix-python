#!/usr/bin/env python

import sys
import time
import locomatix

LOCOMATIX_CUSTID = '<enter your locomatix custid>'
LOCOMATIX_KEY = '<enter your locomatix custkey>'
LOCOMATIX_SECRET_KEY = '<enter your locomatix secret key>'

SPEEDTRAPS_DATA_FILE = 'speedtraps.data'
FEED_SPEEDTRAPS = 'speedtraps'

class SpeedTraps(object):

  def setUp(self):

    # First create a Locomatix client with the credentials
    self.conn = locomatix.Client(LOCOMATIX_CUSTID,
                                 LOCOMATIX_KEY,
                                 LOCOMATIX_SECRET_KEY)

  def tearDown(self):
    self.conn.close() 

  def load(self):

    # Open the data speed trap file
    try:
      handle = open(SPEEDTRAPS_DATA_FILE, 'r')

    # If there are any errors, spit it and exit
    except IOError :
      print "Error opening data file %s" % (SPEEDTRAPS_DATA_FILE)
      sys.exit(1)

    # Now read the data file 
    igot = handle.readlines()
    for line in igot:
      data = line.rstrip().split(',')
      if data == [] or len(data) < 8:
        continue

      cid = data[0]
      latitude = data[1]
      longitude = data[2]
      nvpairs = { 
        'SpeedLimit' : data[3], 'Type' :  data[4],
        'City' : data[5], 'State' : data[6], 'Comments' : data[7]
      }

      location = locomatix.Point(latitude, longitude)

      try:
        self.conn.create_object(cid, FEED_SPEEDTRAPS, nvpairs, location, time.time());

      # Make sure that we have created the object successfully
      except locomatix.LxException, ex:
        print 'unable to create object %s in feed %s - %s' % \
          (cid, FEED_SPEEDTRAPS, ex.message)

if __name__ == '__main__':

  speedtraps = SpeedTraps()

  speedtraps.setUp()
  speedtraps.load()
  speedtraps.tearDown()
