#!/usr/bin/env python

import sys
import httplib
import locomatix

def create_object():
  """docstring for create_object"""
  parser = locomatix.ArgsParser()
  parser.add_description("Creates an object")
  parser.add_arg('objectid', 'Object to be created')
  parser.add_roption('feed',  'f:', 'feed=', 'Name of the feed')
  parser.add_option('nvpairs','v:', 'nv=',   'Name-value pairs (specified as name=value)', True)
  args = parser.parse_args(sys.argv)
  nvpairs = dict()
  
  for anv in args['nvpairs']:
    nv = anv.split('=')
    nvpairs[nv[0].strip()] = nv[1].strip()
  
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
  response = lxclient.create_object(objectid, feed, nvpairs)
  
  if response.status != httplib.OK:
    print "error: creating object (%s in %s) - %s" % (args['objectid'], args['feed'], response.message)
    sys.exit(1)
  
  print "Successfully created object: %s" % args['objectid']


if __name__ == '__main__':
  create_object()
