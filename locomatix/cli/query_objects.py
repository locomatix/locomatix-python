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

def query_objects():
  """docstring for query_objects"""
  parser = locomatix.ArgsParser()
  parser.add_description("Query objects")
  parser.add_arg('query', 'LQL query to execute', False)
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
  
  query = args['query']

  try:
    query = lql.Query(query)._query

    start_key = locomatix.DEFAULT_FETCH_STARTKEY
    fetch_size = locomatix.DEFAULT_FETCH_SIZE
    while True:
      batch = lxclient._request('list_objects', query, start_key, fetch_size)
      if len(batch.objects) > 0:
        dprint(args, lxclient.response_body(), '\n'.join('%s' % obj for obj in batch.objects))
      elif len(batch.aggrs) > 0:
        dprint(args, lxclient.response_body(), '\n'.join('%s' % aggr for aggr in batch.aggrs))
         
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

  except locomatix.LxException, e:
    dprint(args, lxclient.response_body(), "error: failed to query for (%s) - %s" % (query, str(e)))
    sys.exit(1)
    
  except KeyboardInterrupt:
    sys.exit(1)

if __name__ == '__main__':
  query_objects()
