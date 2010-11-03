#!/usr/bin/env python

import sys
import httplib
import locomatix

def get_space_activity():
  """docstring for get_space_activity"""
  parser = locomatix.ArgsParser()
  parser.add_description("Finds all objects that entered the given region within the given time slice")
  parser.add_arg('feed', 'Name of the feed')
  parser.add_roption('long', 'g:', 'long=', 'Longitude of the location')
  parser.add_roption('lat',  'l:', 'lat=', 'Latitude of the location')
  parser.add_roption('starttime',  'b:', 'starttime=', 'Start time of space activity')
  parser.add_roption('endtime',  'e:', 'endtime=', 'End time of space activity')
  parser.add_roption('radius',  'r:', 'radius=', 'Radius of the circle region')
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
  
  feedkey = locomatix.FeedKey(args['feed'])
  region = locomatix.CircleRegion(args['long'], args['lat'], args['radius'])
  
  for batch in lxclient.get_space_activity_iterator(feedkey, region, args['starttime'], args['endtime']):
    for obj in batch.objects:
      print obj

if __name__ == '__main__':
  search_region()
