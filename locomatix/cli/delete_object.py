#!/usr/bin/env python
###############################################################################
#
# Copyright 2010 Locomatix, Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################
import sys
import locomatix
from _utils import *

def delete_object():
  """docstring for delete_object"""
  parser = locomatix.ArgsParser()
  parser.add_description("Deletes an object")
  parser.add_arg('feed',     'Name of the feed')
  parser.add_arg('objectids', 'Object to be deleted', True)
  args = parser.parse_args(sys.argv)
  
  try:
    lxclient = locomatix.Client(args['custid'], \
                             args['key'], \
                             args['secret-key'], \
                             args['host'], \
                             args['port'])
  except:
    print "Unable to connect to %s at port %d" % (args['host'],args['port'])
    sys.exit(1)
  
  feed     = args['feed']
  objectids = args['objectids']

  try:
    for objectid in objectids:
      lxclient.delete_object(objectid, feed)
  
  except locomatix.LxException, e:
    dprint(args, lxclient.response_body(), "error: deleting object (%s in %s) - %s" % (objectid, feed, str(e)))
    sys.exit(1)

  dprint(args, lxclient.response_body(), "Successfully deleted object: %s" % ' '.join(objectids))


if __name__ == '__main__':
  delete_object()
