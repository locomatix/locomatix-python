#!/usr/bin/env python

import sys
import httplib
import locomatix

def get_zone():
  """docstring for get_zone"""
  parser = locomatix.ArgsParser()
  parser.add_description("Gets zone details")
  parser.add_roption('feed','f:', 'feed=', 'Name of the feed')
  parser.add_roption('objectid','o:', 'objectid=', 'Object attached to zone')
  parser.add_arg('zoneid', 'Zone to be fetched')
  args = parser.parse_args(sys.argv)
  
  lxsvc = locomatix.Service(args['custid'], \
                           args['key'], \
                           args['secret-key'], \
                           args['host'], \
                           args['port'], \
                           args['use-ssl'])
  
  response = lxsvc.get_zone(args['zoneid'], args['objectid'], args['feed'])
  
  if response.status != httplib.OK:
    print "error: getting zone (%s around %s in %s) - %s" % (args['zoneid'], 
                  args['objectid'], args['feed'], response.message)
    sys.exit(1)
  
  # Print the details of the zone
  print response.zone


if __name__ == '__main__':
  get_zone()
