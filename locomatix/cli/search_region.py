#!/usr/bin/env python

import sys
import httplib
import locomatix

def search_region():
  """docstring for list_objects"""
  parser = locomatix.ArgsParser()
  parser.add_description("Finds all objects within a fixed region")
  parser.add_roption('long', 'g:', 'long=', 'Longitude of the location')
  parser.add_roption('lat',  'l:', 'lat=', 'Latitude of the location')
  parser.add_roption('radius',  'r:', 'radius=', 'Fence radius around the location')
  parser.add_roption('from-feeds','m:', 'from=', 'From feeds', True)
  args = parser.parse_args(sys.argv)
  
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
  
  region = { 'latitude': args['lat'], 'longitude': args['long'],  'type':'Circle', 'radius': args['radius'] }
  from_feeds = args['from-feeds']
  
  for batch in lxsvc.search_region_iterator(region, from_feeds):
    for obj in batch.objects:
      print obj


if __name__ == '__main__':
  search_region()