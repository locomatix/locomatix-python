#!/usr/bin/env python

import sys
import httplib
import locomatix

def update_location():
  """docstring for update_location"""
  parser = locomatix.ArgsParser()
  parser.add_description("Update the location of an object")
  parser.add_arg('objectid', 'Object to be updated')
  parser.add_roption('feed',  'f:', 'feed=', 'Name of the feed')
  parser.add_roption('long',   'g:', 'long=', 'Longitude of the location')
  parser.add_roption('lat',   'l:', 'lat=', 'Latitude of the location')
  parser.add_roption('time',  't:', 'time=', 'Latitude of the location')
  parser.add_option('nvpairs','v:', 'nv=',  'Name-value pairs (specified as name=value)', True)
  args = parser.parse_args(sys.argv)
  
  longitude  = float(args['long'])
  latitude   = float(args['lat'])
  time       = long(args['time'])
  objectid   = args['objectid']
  feedid     = args['feed']
  nvpairs    = dict()
  
  for anv in args['nvpairs']:
    nv = anv.split('=')
    nvpairs[nv[0].strip()] = nv[1].strip()
  
  try:
    lxsvc = locomatix.Service(args['custid'], \
                             args['key'], \
                             args['secret-key'], \
                             args['host'], \
                             args['port'], \
                             args['use-ssl'])
  except:
    print "Unable to connect to %s at port %d" % (args['host'],args['port'])
    sys.exit(1)
  
  response = lxsvc.update_location(objectid, feedid, longitude, latitude, time, nvpairs)
  
  if response.status != httplib.OK:
    print "error: updating location for object (%s in %s) - %s" % (objectid, feedid, response.message)
    sys.exit(1)
  
  print "Successfully updated location of object: %s" % objectid


if __name__ == '__main__':
  update_location()
