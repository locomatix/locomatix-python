#!/usr/bin/env python

import sys
import httplib
import locomatix

def get_location_history():
  """docstring for get_location_history"""
  parser = locomatix.ArgsParser()
  parser.add_description("Gets the location history of an object")
  parser.add_arg('objectid', 'Object to be created')
  parser.add_roption('feed',  'f:', 'feed=', 'Name of the feed')
  parser.add_roption('starttime',  'b:', 'starttime=', 'Start time of the location history')
  parser.add_roption('endtime',  'e:', 'endtime=', 'End time of the location history')
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
  for batch in lxclient.get_location_history_iterator(objectid, feed, \
                         args['starttime'], args['endtime']):
    for obj in batch.locations:
      print obj


if __name__ == '__main__':
  list_objects()
