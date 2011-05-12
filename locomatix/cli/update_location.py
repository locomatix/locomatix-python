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

def update_location():
  """docstring for update_location"""
  parser = locomatix.ArgsParser()
  parser.add_description("Update the location of an object")
  parser.add_arg('objectid', 'Object to be updated')
  parser.add_arg('feed',     'Name of the feed')
  parser.add_arg('latitude', 'Latitude of the location')
  parser.add_arg('longitude','Longitude of the location')
  parser.add_arg('time',     'Time at this location')
  parser.add_option('ttl',    'u:', 'ttl=', 'TTL - Time validity of the location')
  parser.add_option('nvpairs','v:', 'nv=',  'Name-value pairs (specified as name=value)', True)
  args = parser.parse_args(sys.argv)
  
  longitude  = float(args['longitude'])
  latitude   = float(args['latitude'])
  time       = convert_time(args['time'])
  objectid   = args['objectid']
  feed       = args['feed']
  location   = locomatix.Point(latitude, longitude) 

  nvpairs    = dict()
  for anv in args['nvpairs']:
    nv = anv.split('=')
    nvpairs[nv[0].strip()] = nv[1].strip()

  ttl = 0 if args['ttl'] == '' else long(args['ttl'])

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
    lxclient.update_location(objectid, feed, location, time, nvpairs, ttl)
  
  except locomatix.LxException, e:
    dprint(args, lxclient.response_body(), 
      "error: updating location for object (%s in %s) - %s" % (objectid, feed, str(e)))
    sys.exit(1)

  dprint(args, lxclient.response_body(), \
            "Successfully updated location of object: %s" % objectid)

if __name__ == '__main__':
  update_location()
