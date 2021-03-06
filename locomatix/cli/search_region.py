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
import locomatix.lql as lql
from _utils import *

def search_region():
  """docstring for list_objects"""
  parser = locomatix.ArgsParser()
  parser.add_description("Finds all objects within a fixed region")
  parser.add_arg('latitude',  'Latitude of the location')
  parser.add_arg('longitude', 'Longitude of the location')
  parser.add_arg('radius',    'Fence radius around the location')
  parser.add_arg('from-feed-or-query', 'Feed to search or query to execute')

  # Look for the first negative number (if any)
  for i, arg in enumerate(sys.argv[1:]):
    if arg[0] != "-": break
    try:
      f = float(arg)
      sys.argv.insert(i+1,"--")
      break;
    except ValueError:
      pass

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
  
  try:

    from_feed = args['from-feed-or-query']
    latitude = float(args['latitude'])
    longitude = float(args['longitude'])
    radius = float(args['radius'])

    region = locomatix.Circle(latitude, longitude, radius)

    predicate = None
    if from_feed.upper().find(" FROM ") < 0:
      predicate = lql.SelectObjectLocation(from_feed)
    else:
      predicate = lql.Query(from_feed)

    start_key = locomatix.DEFAULT_FETCH_STARTKEY
    fetch_size = locomatix.DEFAULT_FETCH_SIZE

    while True:
      batch = lxclient._request('search_region', region, predicate._query, start_key, fetch_size)
      if len(batch.objlocs) > 0:
        dprint(args, lxclient.response_body(), '\n'.join('%s' % obj for obj in batch.objlocs))
      else:
        dprint(args, lxclient.response_body(), '\n'.join('%s' % aggr for aggr in batch.aggrs))

      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

  except locomatix.LxException, e:
    dprint(args, lxclient.response_body(), \
         "error: failed to retrieve search region list - %s" % (str(e)))
    sys.exit(1)

  except KeyboardInterrupt:
    sys.exit(1)



if __name__ == '__main__':
  search_region()
