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
  
  lxsvc = locomatix.Service(args['custid'], \
                           args['key'], \
                           args['secret-key'], \
                           args['host'], \
                           args['port'], \
                           args['use-ssl'])
  
  for batch in lxsvc.list_zones_iterator(args['objectid'], args['feed']):
    for zone in batch.zones:
      print zone


if __name__ == '__main__':
  list_zones()
