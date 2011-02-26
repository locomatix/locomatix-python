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

def get_fence():
  """docstring for get_fence"""
  parser = locomatix.ArgsParser()
  parser.add_description("Gets the definition of a fence")
  parser.add_arg('fenceid', 'ID of the fence to be fetched')
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
  
  fenceid = args['fenceid']
  response = lxclient._get_fence(fenceid)
  
  if response.status != httplib.OK:
    dprint(args, response, "error: get fence %s - %s" % (args['fenceid'], response.message))
    sys.exit(1)
  
  dprint(args, response, '%s' % response.fence)


if __name__ == '__main__':
  get_fence()
