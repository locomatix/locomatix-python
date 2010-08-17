#!/usr/bin/env python

import sys
import httplib
import locomatix

def get_attributes():
  """docstring for get_attributes"""
  parser = locomatix.ArgsParser()
  parser.add_description("Get the attributes of an object")
  parser.add_arg('objectid', 'Object to be fetched')
  parser.add_roption('feed',  'f:', 'feed=', 'Name of the feed')
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
  
  response = lxsvc.get_attributes(args['objectid'], args['feed'])
  
  if response.status != httplib.OK:
    print "error: getting attributes for object (%s in %s) - %s" % (args['objectid'], \
                                        args['feed'], response.message)
    sys.exit(1)
  
  print response.object


if __name__ == '__main__':
  get_attributes()
