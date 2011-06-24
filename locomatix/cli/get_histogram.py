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

def get_histogram():
  """docstring for get_histogram"""
  parser = locomatix.ArgsParser()
  parser.add_description("Get counts of objects that in the given region in the given time slice")
  parser.add_arg('feed',             'Name of the feed')
  parser.add_arg('latlow',           'Lower latitude of the bounding box')
  parser.add_arg('longlow',          'Lower longitude of the bounding box')
  parser.add_arg('lathigh',          'High latitude of the bounding box')
  parser.add_arg('longhigh',         'High longitude of the bounding box')
  parser.add_arg('time-interval',    'Number of seconds from now')
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
  latlow = float(args['latlow'])
  longlow = float(args['longlow'])
  lathigh = float(args['lathigh'])
  longhigh = float(args['longhigh'])
  timei = float(args['time-interval'])

  region = locomatix.Rectangle(latlow, longlow, lathigh, longhigh)

  try:

    etime = time.time() - timei 
    counts  = lxclient.get_histogram(feed, region, 50, 50, etime)

    matrix = ''
    for i in counts.counts:
      matrix += '%s\n' % str(i) 
    dprint(args, lxclient.response_body(), '%s' % matrix)

  except locomatix.LxException, e:
    dprint(args, lxclient.response_body(), \
      "error: failed to get histogram for feed (%s) - %s" % (feed, str(e)))
    sys.exit(1)
    
if __name__ == '__main__':
  get_histogram()
