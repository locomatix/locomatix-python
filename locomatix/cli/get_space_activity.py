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

def get_space_activity():
  """docstring for get_space_activity"""
  parser = locomatix.ArgsParser()
  parser.add_description("Finds all objects that entered the given region within the given time slice")
  parser.add_arg('feed', 'Name of the feed')
  parser.add_roption('lat',  'l:', 'lat=', 'Latitude of the location')
  parser.add_roption('long', 'g:', 'long=', 'Longitude of the location')
  parser.add_roption('starttime',  'b:', 'starttime=', 'Start time of space activity')
  parser.add_roption('endtime',  'e:', 'endtime=', 'End time of space activity')
  parser.add_roption('radius',  'r:', 'radius=', 'Radius of the circle region')
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
  region = locomatix.Circle(float(args['lat']), float(args['long']), \
                            float(args['radius']))

  for batch in lxclient._get_space_activity_iterator(feed, region, args['starttime'], args['endtime'], allow_error=True):
    if batch.status > httplib.OK:
      dprint(args, batch, "error: failed to retrieve space activity list for feed (%s) - %s" % (feed, batch.message))
      continue
    
    dprint(args, batch, '\n'.join('%s' % obj for obj in batch.objects)) 

if __name__ == '__main__':
  search_region()
