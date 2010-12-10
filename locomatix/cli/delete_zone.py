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
import httplib
import locomatix
from _utils import *

def delete_zone():
  """docstring for delete_zone."""
  parser = locomatix.ArgsParser()
  parser.add_description("Deletes a zone")
  parser.add_roption('feed','f:', 'feed=', 'Name of the feed')
  parser.add_roption('objectid','o:', 'objectid=', 'Object attached to zone')
  parser.add_arg('zoneid', 'Zone to be deleted')
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
  
  zoneid = args['zoneid']
  objectid = args['objectid']
  feed = args['feed']
  response = lxclient.delete_zone(zoneid, objectid, feed)
  
  if response.status != httplib.OK:
    dprint(args, response, "error: deleting zone (%s around %s in %s) - %s" % \
                              (args['zoneid'], args['objectid'], args['feed'], response.message))
    sys.exit(1)
    
  dprint(args, response, "Successfully deleted zone: %s" % args['zoneid'])


if __name__ == '__main__':
  delete_zone()
