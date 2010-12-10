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

def create_object():
  """docstring for create_object"""
  parser = locomatix.ArgsParser()
  parser.add_description("Creates an object")
  parser.add_arg('objectid', 'Object to be created')
  parser.add_roption('feed',  'f:', 'feed=', 'Name of the feed')
  parser.add_option('nvpairs','v:', 'nv=',   'Name-value pairs (specified as name=value)', True)
  parser.add_option('lat',   'l:', 'lat=', 'Latitude of the location')
  parser.add_option('long',  'g:', 'long=', 'Longitude of the location')
  parser.add_option('time',  't:', 'time=', 'Time of the location')
  parser.add_option('ttl',    'u:', 'ttl=', 'TTL - Time validity of the location')
  args = parser.parse_args(sys.argv)

  nvpairs = dict()
  for anv in args['nvpairs']:
    nv = anv.split('=')
    nvpairs[nv[0].strip()] = nv[1].strip()

       
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

  response = None

  location_given = len(args['lat']) > 0 and len(args['long']) > 0 and len(args['time']) > 0
  partial_location = len(args['lat']) > 0 or len(args['long']) > 0 or len(args['time']) > 0

  if location_given == True:
    latitude =  args['lat'] 
    longitude =  args['long'] 
    time =  args['time'] 
    ttl =  args['ttl'] 
    location = locomatix.Point(latitude, longitude)
    response = lxclient.create_object(objectid, feed, nvpairs, location, time, ttl)  
  elif partial_location == True:
    parser.usage(sys.argv)
    sys.exit(1)
  else: 
    response = lxclient.create_object(objectid, feed, nvpairs)
  
  if response.status != httplib.OK:
    dprint(args, response, "error: creating object (%s in %s) - %s" % (args['objectid'], args['feed'], response.message))
    sys.exit(1)
  
  dprint(args, response, "Successfully created object: %s" % args['objectid'])


if __name__ == '__main__':
  create_object()
