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

def delete_feed():
  """docstring for delete_feed"""
  parser = locomatix.ArgsParser()
  parser.add_description("Deletes one or many feeds")
  parser.add_arg('feeds', 'Feeds to be deleted', True)
  parser.add_option('robjects',  'r', 'remove', 'Remove the objects in feed', type='bool')
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
  
  feeds = args['feeds']
  robjects = args['robjects']

  try:
    for feed in feeds:
      if robjects:
        try:
          for obj in lxclient.list_objects(feed):
            lxclient.delete_object(obj.objectid, obj.feed)
            dprint(args, lxclient.response_body(), None)

        except locomatix.LxException, e:
          dprint(args, lxclient.response_body(), "error: failed to delete objects in %s - %s" % (feed, str(e)))
          sys.exit(1)

      lxclient.delete_feed(feed)

  except locomatix.LxException, e:
    dprint(args, lxclient.response_body(), "error: deleting feed %s - %s" % (feed, str(e)))
    sys.exit(1)

  dprint(args, lxclient.response_body(), "Successfully deleted feeds: %s" % ' '.join(feeds))


if __name__ == '__main__':
  delete_feed()
