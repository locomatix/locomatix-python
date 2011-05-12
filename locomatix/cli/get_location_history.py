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

def get_location_history():
  """docstring for get_location_history"""
  parser = locomatix.ArgsParser()
  parser.add_description("Gets the location history of an object")
  parser.add_arg('objectid', 'Object to be created')
  parser.add_arg('feed',  'Name of the feed')
  parser.add_option('start-time',  'b:', 'starttime=', 'Start time of the location history')
  parser.add_option('end-time',  'e:', 'endtime=', 'End time of the location history')
  args = parser.parse_args(sys.argv)
  
  objectid = args['objectid']
  feed = args['feed']

  try:
    start_time_present = True if len(args['start-time']) > 0 else False
    end_time_present = True if len(args['end-time']) > 0 else False

    if start_time_present and end_time_present:
      end_time = convert_time(args['end-time'])
      start_time = convert_time(args['start-time'])

    elif start_time_present:
      start_time = convert_time(args['start-time'])
      end_time = start_time + 3600

    elif end_time_present:
      end_time = convert_time(args['end-time'])
      start_time = end_time - 3600

    else:
      end_time = time.time()
      start_time = end_time - 3600

  except ValueError:
    print "start time or end time not in valid format" 
    sys.exit(1)
    
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

    start_key = locomatix.DEFAULT_FETCH_STARTKEY
    fetch_size = locomatix.DEFAULT_FETCH_SIZE

    while True:
      batch = lxclient._request('get_location_history', objectid, feed, start_time, end_time, start_key, fetch_size)
      dprint(args, lxclient.response_body(), '\n'.join('%s' % obj for obj in batch.locations))
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

  except locomatix.LxException, e:
    dprint(args, lxclient.response_body(), \
            "error: failed to retrieve location history for (%s in %s) - %s" % (objectid, feed, str(e)))
    sys.exit(1)

  except KeyboardInterrupt:
    sys.exit(1)

if __name__ == '__main__':
  get_location_history()
