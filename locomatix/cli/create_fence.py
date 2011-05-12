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

def create_fence():
  """docstring for create_fence"""
  parser = locomatix.ArgsParser()
  parser.add_description("Creates a fence")
  parser.add_arg('fenceid',    'Fence to be created')
  parser.add_arg('latitude',        'Latitude of the location')
  parser.add_arg('longitude',       'Longitude of the location')
  parser.add_arg('radius',     'Fence radius around the location')
  parser.add_arg('trigger',    'Trigger type (Ingress | Egress | IngressAndEgress)')
  parser.add_arg('callbackURL','Callback URL')
  parser.add_arg('from-feed',  'Feed to monitor the objects from')
  parser.add_option('nvpairs','v:', 'nv=',   'Name-value pairs (specified as name=value)', True)
  parser.add_option('once',  'n', 'once', 'Fire the alert only once', type='bool')

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
  
  fenceid    = args['fenceid']
  region     = locomatix.Circle(float(args['latitude']), float(args['longitude']), \
                                      float(args['radius']))
  trigger    = args['trigger']
  callback   = locomatix.URLCallback(args['callbackURL'])
  from_feed  = args['from-feed']
  once = True if args['once'] else False

  try:
    lxclient.create_fence(fenceid, region, trigger, callback, from_feed, nvpairs, once)
  
  except locomatix.LxException, e:
    dprint(args, lxclient.response_body(), "error: creating fence %s - %s" % (fenceid, str(e)))
    sys.exit(1)

  dprint(args, lxclient.response_body(), "Successfully created fence: %s" % fenceid)


if __name__ == '__main__':
  create_fence()
