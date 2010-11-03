#!/usr/bin/env python

import sys
import httplib
import locomatix

def delete_object():
  """docstring for delete_object"""
  parser = locomatix.ArgsParser()
  parser.add_description("Deletes an object")
  parser.add_roption('feed','f:', 'feed=', 'Name of the feed')
  parser.add_arg('objectid', 'Object to be deleted')
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
  response = lxclient.delete_object(objectkey)
  
  if response.status != httplib.OK:
    print "error: deleting object (%s in %s) - %s" % (args['objectid'], args['feed'], response.message)
    sys.exit(1)
  
  print "Successfully deleted object: %s" % args['objectid']


if __name__ == '__main__':
  delete_object()
