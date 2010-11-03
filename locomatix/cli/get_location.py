#!/usr/bin/env python

import sys
import httplib
import locomatix

def get_location():
  """docstring for get_location"""
  parser = locomatix.ArgsParser()
  parser.add_description("Get the location of an object")
  parser.add_arg('objectid', 'Object to be fetched')
  parser.add_roption('feed',  'f:', 'feed=', 'Name of the feed')
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
  response = lxclient.get_location(objectkey)
  
  if response.status != httplib.OK:
    print "error: getting location for object (%s in %s) - %s" % (args['objectid'], \
      args['feed'], response.message)
    sys.exit(1)
  
  print response.object


if __name__ == '__main__':
  get_location()
