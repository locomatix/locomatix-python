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

def list_fences():
  """docstring for list_fences"""
  parser = locomatix.ArgsParser()
  parser.add_description("Gets the details of all fences")
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
  
  for batch in lxclient._list_fences_iterator(allow_error=True):
    if batch.status > httplib.OK:
      dprint(args, batch, "error: failed to retrieve fence list - %s" % (batch.message))
      continue

    dprint(args, batch, '\n'.join('%s' % fence for fence in batch.fences))


if __name__ == '__main__':
  list_fences()
