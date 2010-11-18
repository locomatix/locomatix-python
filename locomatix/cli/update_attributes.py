#!/usr/bin/env python

import sys
import httplib
import locomatix

def update_attributes():
  """docstring for update_attributes"""
  parser = locomatix.ArgsParser()
  parser.add_description("Update the attributes of an object")
  parser.add_arg('objectid', 'Object to be updated')
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
  response = lxclient.update_attributes(objectid, feed, nvpairs)
  
  if response.status != httplib.OK:
    print "error: updating attributes for object (%s in %s) - %s" % (args['objectid'], \
                      args['feed'], response.message)
    sys.exit(1)
  
  print "Successfully update attributes for object: %s" % args['objectid']


if __name__ == '__main__':
  update_attributes()
