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

def activate_zone():
  """docstring for activate_zone."""
  parser = locomatix.ArgsParser()
  parser.add_description("Activates a zone")
  parser.add_arg('feed',    'Name of the feed')
  parser.add_arg('objectid','Object attached to zone')
  parser.add_arg('zoneids',  'Zones to be activated', True)
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
  
  feed = args['feed']
  objectid = args['objectid']
  zoneids = args['zoneids']

  try:
    for zoneid in zoneids:
      lxclient.activate_zone(zoneid, objectid, feed)
  
  except locomatix.LxException, e:
    dprint(args, lxclient.response_body(), "error: activating zone (%s around %s in %s) - %s" % \
                              (zoneid, objectid, feed, str(e)))
    sys.exit(1)
    
  dprint(args, lxclient.response_body(), "Successfully activated zone: %s" % ' '.join(zoneids))

if __name__ == '__main__':
  activate_zone()
