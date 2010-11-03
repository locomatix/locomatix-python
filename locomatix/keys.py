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

import sys, os
import httplib, urllib

from response_objects import PrintableAttributes

class LocomatixKey(PrintableAttributes):
  """An abstract region object from which all regions will be derived."""
  def __init__(self, params):
    self._params = params
  
class FeedKey(LocomatixKey):
  def __init__(self, feed):
    self.feed = feed
    params = { 'feed': feed }
    super(FeedKey, self).__init__(params)

class ObjectKey(LocomatixKey):
  def __init__(self, objectid, feed):
    self.objectid = objectid
    self.feed = feed
    params = { 'oid':objectid, 'feed': feed }
    super(ObjectKey, self).__init__(params)

class ZoneKey(LocomatixKey):
  def __init__(self, zoneid, objectid, feed):
    self.zoneid = zoneid
    self.objectid = objectid
    self.feed = feed
    params = { 'zoneid': zoneid, 'oid': objectid, 'feed': feed }
    super(ZoneKey, self).__init__(params)

class FenceKey(LocomatixKey):
  def __init__(self, fenceid):
    self.fenceid = fenceid
    params = { 'fenceid': fenceid }
    super(FenceKey, self).__init__(params)
