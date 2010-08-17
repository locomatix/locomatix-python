#!/usr/bin/env python

import sys
import httplib
import locomatix

def delete_fence():
  """docstring for delete_fence"""
  parser = locomatix.ArgsParser()
  parser.add_description("Deletes a fence")
  parser.add_arg('fenceid', 'ID of the fence to be deleted')
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
  
  response = lxsvc.delete_fence(args['fenceid'])
  
  if response.status != httplib.OK:
    print "error: deleting fence %s - %s" % (args['fenceid'], response.message)
    sys.exit(1)
  
  print "Successfully deleted fence: %s" % args['fenceid']


if __name__ == '__main__':
  delete_fence()