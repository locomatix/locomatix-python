#!/usr/bin/env python

import sys
import httplib
import locomatix

def delete_zone():
  """docstring for delete_zone."""
  parser = locomatix.ArgsParser()
  parser.add_description("Deletes a zone")
  parser.add_roption('feed','f:', 'feed=', 'Name of the feed')
  parser.add_roption('objectid','o:', 'objectid=', 'Object attached to zone')
  parser.add_arg('zoneid', 'Zone to be deleted')
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
  
  zonekey = locomatix.ZoneKey(args['zoneid'], args['objectid'], args['feed'])
  response = lxclient.delete_zone(zonekey)
  
  if response.status != httplib.OK:
    print "error: deleting zone (%s around %s in %s) - %s" % (args['zoneid'], args['objectid'], \
                                                  args['feed'], response.message)
    sys.exit(1)
  
  print "Successfully deleted zone: %s" % args['zoneid']


if __name__ == '__main__':
  delete_zone()
