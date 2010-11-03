#!/usr/bin/env python

import sys
import httplib
import locomatix

def create_zone():
  """docstring for create_zone"""
  parser = locomatix.ArgsParser()
  parser.add_description("Create a zone around an object")
  parser.add_arg('zoneid', 'Zone to be created')
  parser.add_roption('feed',  'f:', 'feed=', 'Name of the feed')
  parser.add_roption('objectid','o:', 'objectid=', 'Object attached to zone')
  parser.add_roption('radius',  'r:', 'radius=', 'Radius around the object')
  parser.add_roption('trigger',  't:', 'trigger=', 'Trigger type (Ingress | Egress | IngressAndEgress)')
  parser.add_roption('callbackURL',  'u:', 'url=', 'Callback URL')
  parser.add_option('from-feeds','m:', 'from=',  'From feeds', True)
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
  
  zonekey    = locomatix.ZoneKey(args['zoneid'], args['objectid'], args['feed'])
  region     = locomatix.CircleObjectRegion(float(args['radius']))
  trigger    = args['trigger']
  callback   = locomatix.URLCallback(args['callbackURL'])
  from_feeds = args['from-feeds']
  if from_feeds == ['']: from_feeds = []
  
  response = lxclient.create_zone(zonekey, region, trigger, callback, from_feeds)
  
  if response.status != httplib.OK:
    print "error: creating zone (%s around %s in %s) - %s" % (args['zoneid'], args['objectid'], \
                  args['feed'], response.message)
    sys.exit(1)
  
  print "Successfully created zone: %s" % args['zoneid']


if __name__ == '__main__':
  create_zone()
