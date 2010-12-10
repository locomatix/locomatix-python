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

def search_nearby():
  """docstring for search_nearby"""
  parser = locomatix.ArgsParser()
  parser.add_description("Finds all objects within a region around a given object")
  parser.add_roption('feed','f:', 'feed=', 'Name of the feed of paren object')
  parser.add_roption('objectid','o:', 'objectid=', 'Object around which to search')
  parser.add_roption('radius',  'r:', 'radius=', 'Radius of search region in meters')
  parser.add_roption('from-feed','m:', 'from=', 'Feed to include in search')
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
  
  objectid = args['objectid']
  feed = args['feed']
  region = locomatix.Circle(float(args['radius']))
  from_feed = args['from-feed']

  for batch in lxclient._search_nearby_iterator(objectid, feed, region, from_feed, allow_error=True):
    if batch.status > httplib.OK:
      dprint(args, batch, "error: failed to retrieve search nearby list for (%s in %s) - %s" % (objectid, feed, batch.message))
      continue

    dprint(args, batch, '\n'.join('%s' % obj for obj in batch.objects))


if __name__ == '__main__':
  search_nearby()
