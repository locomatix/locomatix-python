#!/usr/bin/env python

import sys
import time
import getopt
import locomatix
from threading import Thread

# Provide your Locomatix Credentials
LOCOMATIX_CUSTID = '<enter your locomatix custid>'
LOCOMATIX_KEY = '<enter your locomatix custkey>'
LOCOMATIX_SECRET_KEY = '<enter your locomatix secret key>'

FEED_CARS       = 'cars'
FEED_SPEEDTRAPS = 'speedtraps'
MOVEMENT_DATA_FILE = 'movement.data'

class Car(Thread):

  ###################################################################
  # Initialize - 
  # Each car creates its own connection to Locomatix cloud so that
  # it can continuously transmit its location.
  ###################################################################
  def __init__(self, id, name, license, radius, callback_url):

    # Initialize the base class
    Thread.__init__(self)

    self.carid = id
    self.name = name
    self.license = license
    self.radius = radius
    self.callback_url = callback_url
    self.movement = []

  ####################################################################
  # Create -
  # Creates an object in the Locomatix cloud that represents the car
  ####################################################################
  def create(self, id, name, license):

    # First create the attribute name value pairs for the car
    car_nvpairs = { 'Name' : name , 'License' : license }

    # Now create the car object in the feed 'cars'
    try:
      self.conn.create_object(id, FEED_CARS, car_nvpairs)

    # Make sure that we have created the car object successfully
    except locomatix.LxException, ex:
      print 'unable to create car %s in feed %s - %s' % (id, FEED_CARS, ex.message)

  ###########################################################################
  # Add Zone - 
  # Create a zone of given radius around the car for checking speed traps.
  # If any alert occurs, post to the URL callback 
  ###########################################################################
  def add_zone(self, radius, callback_url):
   
    # Construct a unique zoneid so that we can refer to it later 
    self.zoneid = self.carid + '-zone'

    # Create an object region of given radius
    region = locomatix.Circle(radius)

    # Create an URL callback 
    callback = locomatix.URLCallback(callback_url)

    # Indicate that only speed traps are to be monitored in the cars zone
    from_feed = FEED_SPEEDTRAPS

    # Create a zone around the car in the Locomatix cloud and inform that alert 
    # is to be generated when a speed trap enters the zone
    try:
      self.conn.create_zone(self.zoneid, self.carid, 
                                FEED_CARS, region, 'Ingress', callback, from_feed)

    # Make sure that we have created the zone around object successfully
    except locomatix.LxException, ex:
      print 'unable to create zone %s around %s in feed %s - %s' % \
           (self.zoneid, self.carid, FEED_CARS, ex.message)

  ####################################################################
  # Move -
  # When the car moves transmit the new location to Locomatix cloud
  ####################################################################
  def move(self, longitude, latitude):
   
    # Update the location of the car in the locomatix cloud
    location = locomatix.Point(latitude, longitude)

    try:
      self.conn.update_location(self.carid, FEED_CARS, location, time.time())

    # Make sure that we have updated the car location successfully
    except locomatix.LxException, ex:
      print 'unable to update location of car %s in feed %s - %s' % \
        (self.carid, FEED_CARS, ex.message)

  #################################################################################
  # Setup -
  # Setups the Locomatix cloud connection, creates car object and speed alert zone
  #################################################################################
  def setUp(self):

    try:
      # First create Locomatix Client with the credentials
      self.conn = locomatix.Client(LOCOMATIX_CUSTID, 
                                   LOCOMATIX_KEY,
                                   LOCOMATIX_SECRET_KEY)

      # Create the car object in Locomatix cloud
      self.create(self.carid, self.name, self.license)

      # Add a speed alert zone around the car
      self.add_zone(self.radius, self.callback_url)

    except locomatix.LxException, ex:
      print 'error occurred for car %s in feed %s - %s' % (self.carid, FEED_CARS, ex.message)
      sys.exit(1)

    # Now read the movement data file
    try:
      handle = open(MOVEMENT_DATA_FILE, 'r')

    # If there is an error, spit it out and exit
    except IOError :
      print "Error opening data file %s" % (MOVEMENT_DATA_FILE)
      sys.exit(1)

    # Read the file line by line
    igot = handle.readlines()
    for line in igot:
      data = line.rstrip().split(',')
      self.movement.append((float(data[1]), float(data[0])))

    # close the file
    handle.close()

   
  ####################################################################
  # Shutdown -
  # Remove the car from the Locomatix cloud and close the connection
  ####################################################################
  def tearDown(self):

    try:
      # First delete the zone around the car
      self.conn.delete_zone(self.zoneid, self.carid, FEED_CARS)

    # Make sure that we have deleted the zone around the car successfully
    except locomatix.LxException, ex: 
      print 'unable to delete zone %s around car %s in feed %s - %s' % \
        (self.zoneid, self.carid, FEED_CARS, ex.message)

    try:
      # Delete the car object in the feed 'cars'
      self.conn.delete_object(self.carid, FEED_CARS)

    # Make sure that we have deleted the car successfully
    except locomatix.LxException, ex: 
      print 'unable to delete car %s in feed %s - %s' % \
        (self.carid, FEED_CARS, ex.message)
  
    # Now close the Locomatix cloud connection
    self.conn.close()

  ####################################################################
  # Run -
  # Simulates the car moving around in physical space
  ####################################################################
  def run(self):

    # First setup up the car in the Locomatix cloud
    self.setUp()

    for location in self.movement:
      print '%s moving to %f %f' % (self.name, location[0], location[1])
      self.move(location[0], location[1])
      time.sleep(1)

    # We are done and do cleanup
    self.tearDown()
   
####################################################################
# Show -
# How to use this program
####################################################################
def usage(progname):
   print '%s -u | --url <callback-url>' % (progname)

if __name__ == "__main__" :

  # Process the command line parameters
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'u:h', ['url=', "help"])

  # If any error, split out the message and exit
  except getopt.GetoptError, err :
    print str(err)
    usage(sys.argv[0])
    sys.exit(1)

  # Get the URL from command line argument
  url = None
  for o, a in opts:
    if o in ["-u", '--url'] :
      url = a
    elif o in ("-h", "--help"):
      usage(sys.argv[0])
      sys.exit(1)
    else:
      usage(sys.argv[0])
      sys.exit(1)

  # If no URL in command line, exit 
  if url == None:
    usage(sys.argv[0])
    sys.exit(1)

  # Now create a car instance called 'carA'
  carA = Car('car-a', 'Cab A', '2992992', 500, url)

  # Now create a car instance called 'carB'
  carB = Car('car-b', 'Cab B', '8388288', 500, url)

  # Start moving the car 'carA' 
  carA.start()

  # Start moving the car 'carB' 
  carB.start()

  # Wait until the car 'carB' is complete
  carB.join()

  # Wait until the car 'carA' is complete
  carA.join()
   
  sys.exit(0)
