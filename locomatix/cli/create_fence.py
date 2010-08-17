#!/usr/bin/env python


import sys
import httplib
import locomatix

def create_fence():
  """docstring for create_fence"""
  parser = locomatix.ArgsParser()
  parser.add_description("Creates a fence")
  parser.add_arg('fenceid', 'Fence to be created')
  parser.add_roption('long', 'g:', 'long=', 'Longitude of the location')
  parser.add_roption('lat',  'l:', 'lat=', 'Latitude of the location')
  parser.add_roption('radius',  'r:', 'radius=', 'Fence radius around the location')
  parser.add_roption('trigger',  't:', 'trigger=', 'Trigger type (Ingress | Egress | IngressAndEgress)')
  parser.add_roption('callbackURL',  'u:', 'url=', 'Callback URL')
  parser.add_roption('from-feeds','m:', 'from=',  'From feeds', True)
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
  
  fenceid    = args['fenceid']
  region     = { 'type':'circle', 'radius':float(args['radius']), \
                 'longitude':float(args['long']), 'latitude':float(args['lat']) }
  trigger    = args['trigger']
  callback   = { 'type':'URL', 'URL':args['callbackURL'] }
  from_feeds = args['from-feeds']
  
  response = lxsvc.create_fence(fenceid, region, trigger, callback, from_feeds)
  
  if response.status != httplib.OK:
    print "error: creating fence %s - %s" % (args['fenceid'], response.message)
    sys.exit(1)
  
  print "Successfully created fence: %s" % fenceid


if __name__ == '__main__':
  create_fence()