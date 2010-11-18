#!/usr/bin/env python

import sys
import httplib
import locomatix

def get_fence():
  """docstring for get_fence"""
  parser = locomatix.ArgsParser()
  parser.add_description("Gets the definition of a fence")
  parser.add_arg('fenceid', 'ID of the fence to be fetched')
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
  
  fenceid = args['fenceid']
  response = lxclient.get_fence(fenceid)
  
  if response.status != httplib.OK:
    print "error: get fence %s - %s" % (args['fenceid'], response.message)
    sys.exit(1)
  
  print response.fence


if __name__ == '__main__':
  get_fence()
