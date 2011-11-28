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

def create_feed():
  """docstring for create_feed"""
  parser = locomatix.ArgsParser()
  parser.add_description("Creates a feed")
  parser.add_arg('feed', 'Feed to be created')
  parser.add_arg('delete-after', 'Duration after which to delete objects (in seconds | forever)')
  parser.add_arg('flush-location', 'Duration after which to flush location to disk (in seconds | foreover)') 
  parser.add_option('nvpairs','v:', 'nv=',   'Name-value pairs (specified as name=value)', True)
  args = parser.parse_args(sys.argv)

  nvpairs = form_nvpairs(args['nvpairs'])

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
  object_expiry = args['delete-after']
  location_expiry = args['flush-location']

  try:
    lxclient.create_feed(feed, object_expiry, location_expiry, nvpairs)  

  except locomatix.LxException, e:
    dprint(args, lxclient.response_body(), "error: creating feed %s - %s" % (feed, str(e)))
    sys.exit(1)
  
  dprint(args, lxclient.response_body(), "Successfully created feed: %s" % feed)


if __name__ == '__main__':
  create_feed()
