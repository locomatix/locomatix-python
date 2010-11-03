#!/usr/bin/env python

import sys
import httplib
import locomatix

def list_objects():
  """docstring for list_objects"""
  parser = locomatix.ArgsParser()
  parser.add_description("Gets the details of all objects")
  parser.add_arg('feed', 'Name of the feed')
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
  
  feedkey = locomatix.FeedKey(args['feed'])
  for batch in lxclient.list_objects_iterator(feedkey):
    for obj in batch.objects:
      print obj


if __name__ == '__main__':
  list_objects()
