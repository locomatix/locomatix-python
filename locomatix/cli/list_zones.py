#!/usr/bin/env python

import sys
import httplib
import locomatix

def list_zones():
  """docstring for list_zones"""

  parser = locomatix.ArgsParser()
  parser.add_description("Gets the details of all zones attached to object")
  parser.add_roption('feed','f:', 'feed=', 'Name of the feed')
  parser.add_arg('objectid','Object attached to the zones')
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
  
  objectkey = locomatix.ObjectKey(args['objectid'], args['feed'])
  for batch in lxclient.list_zones_iterator(objectkey):
    for zone in batch.zones:
      print zone


if __name__ == '__main__':
  list_zones()
