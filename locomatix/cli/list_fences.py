#!/usr/bin/env python

import sys
import httplib
import locomatix

def list_fences():
  """docstring for list_fences"""
  parser = locomatix.ArgsParser()
  parser.add_description("Gets the details of all fences")
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
  
  for batch in lxclient.list_fences_iterator():
    for fence in batch.fences:
      print fence


if __name__ == '__main__':
  list_fences()
