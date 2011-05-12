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

def create_object():
  """docstring for create_object"""
  parser = locomatix.ArgsParser()
  parser.add_description("Creates an object")
  parser.add_arg('objectid', 'Object to be created')
  parser.add_arg('feed',     'Name of the feed')
  parser.add_option('nvpairs','v:', 'nv=',   'Name-value pairs (specified as name=value)', True)
  parser.add_option('latitude',   'l:', 'latitude=', 'Latitude of the location')
  parser.add_option('longitude',  'g:', 'longitude=', 'Longitude of the location')
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

  location_given = len(args['latitude']) > 0 and len(args['longitude']) > 0 and len(args['time']) > 0
  partial_location = len(args['latitude']) > 0 or len(args['longitude']) > 0 or len(args['time']) > 0

  if location_given:
    latitude =  args['latitude'] 
    longitude =  args['longitude'] 
    time = convert_time(args['time'])
    ttl =  args['ttl'] 
    location = locomatix.Point(latitude, longitude)

    try:
      lxclient.create_object(objectid, feed, nvpairs, location, time, ttl)  

    except locomatix.LxException, e:
      dprint(args, response, "error: creating object (%s in %s) - %s" % (objectid, feed, str(e)))
      sys.exit(1)

  elif partial_location:
    parser.usage(sys.argv)
    sys.exit(1)

  else: 
    try:
      lxclient.create_object(objectid, feed, nvpairs)

    except locomatix.LxException, e:
      dprint(args, lxclient.response_body(), "error: creating object (%s in %s) - %s" % (objectid, feed, str(e)))
      sys.exit(1)

  dprint(args, lxclient.response_body(), "Successfully created object: %s" % objectid)


if __name__ == '__main__':
  create_object()
