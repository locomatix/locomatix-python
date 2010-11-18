#!/usr/bin/env python

import sys
import httplib
import locomatix

def search_nearby():
  """docstring for search_nearby"""
  parser = locomatix.ArgsParser()
  parser.add_description("Finds all objects within a region around a given object")
  parser.add_roption('feed','f:', 'feed=', 'Name of the feed of paren object')
  parser.add_roption('objectid','o:', 'objectid=', 'Object around which to search')
  parser.add_roption('radius',  'r:', 'radius=', 'Radius of search region in meters')
  parser.add_roption('from-feeds','m:', 'from=', 'Feeds to include in search', True)
  args = parser.parse_args(sys.argv)
  
  try:
    lxclient = locomatix.Client(args['custid'], \
                             args['key'], \
                             args['secret-key'], \
                             args['host'], \
                             args['port'], \
                             args['use-ssl'])
  except:
    print "Unable to connect to %s at port %d" % (args['host'],args['port'])
    sys.exit(1)
  
  objectid = args['objectid']
  feed = args['feed']
  region = locomatix.CircleObjectRegion(args['radius'])
  from_feeds = args['from-feeds']
  
  for batch in lxclient.search_nearby_iterator(objectid, feed, region, from_feeds):
    for obj in batch.objects:
      print obj


if __name__ == '__main__':
  search_nearby()
