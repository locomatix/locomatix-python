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

def query_search_nearby():
  """docstring for query_search_nearby"""
  parser = locomatix.ArgsParser()
  parser.add_description("Finds all objects within a region around a given object")
  parser.add_arg('feed',     'Name of the feed of paren object')
  parser.add_arg('objectid', 'Object around which to search')
  parser.add_arg('radius',   'Radius of search region in meters')
  parser.add_arg('query','LQL query to execute')
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
    objectid = args['objectid']
    feed = args['feed']
    region = locomatix.Circle(float(args['radius']))
    query = args['query']

    predicate = lql.Query(query)

    start_key = locomatix.DEFAULT_FETCH_STARTKEY
    fetch_size = locomatix.DEFAULT_FETCH_SIZE

    while True:
      batch = lxclient._request('search_nearby', objectid, feed, region, predicate._query, start_key, fetch_size)
      dprint(args, lxclient.response_body(), '\n'.join('%s' % obj for obj in batch.objlocs))
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

  except locomatix.LxException, e:
    dprint(args, lxclient.response_body(), \
        "error: failed to retrieve search nearby list for (%s in %s) - %s" % (objectid, feed, str(e)))
    sys.exit(1)

  except KeyboardInterrupt:
    sys.exit(1)

if __name__ == '__main__':
  query_search_nearby()
