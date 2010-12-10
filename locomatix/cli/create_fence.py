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

def create_fence():
  """docstring for create_fence"""
  parser = locomatix.ArgsParser()
  parser.add_description("Creates a fence")
  parser.add_arg('fenceid', 'Fence to be created')
  parser.add_roption('lat',  'l:', 'lat=', 'Latitude of the location')
  parser.add_roption('long', 'g:', 'long=', 'Longitude of the location')
  parser.add_roption('radius',  'r:', 'radius=', 'Fence radius around the location')
  parser.add_roption('trigger',  't:', 'trigger=', 'Trigger type (Ingress | Egress | IngressAndEgress)')
  parser.add_roption('callbackURL',  'u:', 'url=', 'Callback URL')
  parser.add_roption('from-feed','m:', 'from=',  'From feed')
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
  
  fencekey   = args['fenceid']
  region     = locomatix.Circle(float(args['lat']), float(args['long']), \
                                      float(args['radius']))
  trigger    = args['trigger']
  callback   = locomatix.URLCallback(args['callbackURL'])
  from_feed  = args['from-feed']
  
  response = lxclient.create_fence(fencekey, region, trigger, callback, from_feed)
  
  if response.status != httplib.OK:
    dprint(args, response, "error: creating fence %s - %s" % (args['fenceid'], response.message))
    sys.exit(1)

  dprint(args, response, "Successfully created fence: %s" % args['fenceid'])


if __name__ == '__main__':
  create_fence()
