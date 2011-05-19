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

def create_zone():
  """docstring for create_zone"""
  parser = locomatix.ArgsParser()
  parser.add_description("Create a zone around an object")
  parser.add_arg('feed',     'Name of the feed')
  parser.add_arg('objectid', 'Object attached to zone')
  parser.add_arg('zoneid',   'Zone to be created')
  parser.add_arg('radius',   'Radius around the object')
  parser.add_arg('trigger',  'Trigger type (Ingress | Egress | IngressAndEgress)')
  parser.add_arg('callbackURL', 'Callback URL')
  parser.add_arg('from-feed', 'Feed to monitor the objects from')
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
  
  zoneid     = args['zoneid']
  objectid   = args['objectid']
  feed       = args['feed']
  region     = locomatix.Circle(float(args['radius']))
  trigger    = args['trigger']
  callback   = locomatix.URLCallback(args['callbackURL'])
  from_feed  = args['from-feed']
  once = True if args['once'] else False

  try:
    lxclient.create_zone(zoneid, objectid, feed, region, trigger, callback, from_feed, nvpairs, once)
  
  except locomatix.LxException, e:
    dprint(args, lxclient.response_body(), "error: creating zone (%s around %s in %s) - %s" % \
                             (zoneid, objectid, feed, str(e)))
    sys.exit(1)

  dprint(args, lxclient.response_body(), "Successfully created zone: %s" % zoneid)


if __name__ == '__main__':
  create_zone()
