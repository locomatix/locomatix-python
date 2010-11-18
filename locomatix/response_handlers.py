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
import urllib
import xml.sax
from response_objects import *
from region import *
from object_region import *
from callback import *
from keys import *

class LxResponseHandler(xml.sax.ContentHandler):
  """All the Response handlers derive from this."""
  def __init__(self):
    self.message = ''
    self.curr_text = ''
    self.col_name = ''
  
  def startElement(self, name, attrs):
    pass
  
  def endElement(self, name):
    """The default endElement handler.
    
    This handler catches the status tag (all responses have a status tag). If it's not the
    status tag then it converts the curr_text to ascii, unescapes it, and delegates handling 
    to the afterEndElement hook.  Derived class should do their end element handling in this
    hook.  Once the hook completes, it resets the curr_text for the next segment."""
    if name == 'Status':
      self.message = self.curr_text
    else:
      self.afterEndElement(name)
    self.curr_text = ''
  
  def afterEndElement(self, name):
    """derived handlers should call this for their end element hook."""
    pass
  
  def characters(self, content):
    self.curr_text += content

  def createCallback(self, params):
    callbacktype = params['type'] 
    if callbacktype == 'URL':
      return URLCallback(params['URL'])
    return None

  def createRegion(self, params):
    regiontype = params['type'] 
    if regiontype == 'Circle':
      return CircleRegion(params['longitude'], params['latitude'], \
                              params['radius'])
    return None

  def createObjectRegion(self, params):
    regiontype = params['type'] 
    if regiontype == 'Circle':
      return CircleObjectRegion(params['radius'])
    return None

class StatusResponseHandler(LxResponseHandler):
  """Behaves exactly as the base response handler."""
  pass


class GetAttributesResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.object = LxObject()
    
  def afterEndElement(self, name):
    if name == 'Feed':
      self.object.feed = self.curr_text
    elif name == 'ObjectID':
      self.object.objectid = self.curr_text
    elif name == 'Name':
      self.col_name = self.curr_text
    elif name == 'Value':
      self.object.name_values[self.col_name] = self.curr_text


class ListObjectsResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.curr_object = None
    self.objects = []
    self.next_key = None
    
  def startElement(self, name, attrs):
    if name == 'Object':
      self.curr_object = LxObject()
    
  def afterEndElement(self, name):
    if name == 'Feed':
      self.curr_object.feed = self.curr_text
    elif name == 'ObjectID':
      self.curr_object.objectid = self.curr_text
    elif name == 'NextKey':
      self.next_key = self.curr_text
    elif name == 'Name':
      self.col_name = self.curr_text
    elif name == 'Value':
      self.curr_object.name_values[self.col_name] = self.curr_text
    elif name == 'Object':
      self.objects.append(self.curr_object)


class GetLocationResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.object = LxObject()
    self.object.location = LxLocation()
  
  def afterEndElement(self, name):
    if name == 'Feed':
      self.object.feed = self.curr_text
    elif name == 'ObjectID':
      self.object.objectid = self.curr_text
    elif name == 'Longitude':
      self.object.location.longitude = float(self.curr_text)
    elif name == 'Latitude':
      self.object.location.latitude = float(self.curr_text)
    elif name == 'Time':
      self.object.location.time = int(self.curr_text)
    elif name == 'Name':
      self.col_name = self.curr_text
    elif name == 'Value':
      self.object.location.name_values[self.col_name] = self.curr_text


class SearchResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.curr_object = None
    self.objects = []
    self.next_key = None
  
  def startElement(self, name, attrs):
    if name == 'Object':
      self.curr_object = LxObject()
    elif name == 'Location':
      self.curr_object.location = LxLocation()
  
  def afterEndElement(self, name):
    if name == 'ObjectID':
      self.curr_object.objectid = self.curr_text
    elif name == 'Feed':
      self.curr_object.feed = self.curr_text
    elif name == 'Longitude':
      self.curr_object.location.longitude = float(self.curr_text)
    elif name == 'Latitude':
      self.curr_object.location.latitude = float(self.curr_text)
    elif name == 'Object':
      self.objects.append(self.curr_object)
    elif name == 'NextKey':
      self.next_key = self.curr_text


class GetZoneResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.zone = LxZone()
    self.parent_name = None

    # private variables
    self._objectregion = dict()
    self._callback = dict()
  
  def startElement(self, name, attrs):
    """docstring for startElement"""
    if name == 'FromFeeds':
      self.parent_name = name
    elif name == 'FollowObject':
      self.parent_name = name
  
  def afterEndElement(self, name):
    if name == 'ZoneID':
      self.zone.zoneid = self.curr_text
    elif name == 'RegionType':
      self._objectregion['type'] = self.curr_text
    elif name == 'Radius':
      self._objectregion['radius'] = float(self.curr_text)
    elif name == 'Region':
      self.zone.object_region = self.createObjectRegion(self._objectregion)
    elif name == 'Trigger':
      self.zone.trigger = self.curr_text
    elif name == 'CallbackURL':
      self._callback['URL'] = self.curr_text
    elif name == 'CallbackType':
      self._callback['type'] = self.curr_text
    elif name == 'Callback':
      self.zone.callback = self.createCallback(self._callback)
    elif name == 'Feed':
      if self.parent_name == 'FromFeeds':
        self.zone.from_feeds.append(self.curr_text)
      elif self.parent_name == 'FollowObject':
        self.zone.feed = self.curr_text
    elif name == 'ObjectID':
      if self.parent_name == 'FollowObject':
        self.zone.objectid = self.curr_text
    elif name == 'FromFeeds':
      self.zone.all_feeds = (self.curr_text.lower() == 'all')


class ListZonesResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.zones = []
    self.curr_zone = None
    self.parent_name = None
    self.next_key = None

    # private variables
    self._callback = dict()
    self._objectregion = dict()
    
  def startElement(self, name, attrs):
    if name == 'Zone':
      self.curr_zone = LxZone()
    elif name == 'FromFeeds':
      self.parent_name = name
    elif name == 'FollowObject':
      self.parent_name = name
    elif name == 'Callback':
      self._callback = dict()
    elif name == 'Region':
      self._objectregion = dict()
    
  def afterEndElement(self, name):
    if name == 'ZoneID':
      self.curr_zone.zoneid = self.curr_text
    elif name == 'RegionType':
      self._objectregion['type'] = self.curr_text
    elif name == 'Radius':
      self._objectregion['radius'] = float(self.curr_text)
    elif name == 'Region':
      self.curr_zone.object_region = self.createObjectRegion(self._objectregion)
    elif name == 'Trigger':
      self.curr_zone.trigger = self.curr_text
    elif name == 'CallbackURL':
      self._callback['URL'] = self.curr_text
    elif name == 'CallbackType':
      self._callback['type'] = self.curr_text
    elif name == 'Callback':
      self.curr_zone.callback = self.createCallback(self._callback)
    elif name == 'Feed':
      if self.parent_name == 'FromFeeds':
        self.curr_zone.from_feeds.append(self.curr_text)
      elif self.parent_name == 'FollowObject':
        self.curr_zone.feed = self.curr_text
    elif name == 'ObjectID':
      if self.parent_name == 'FollowObject':
        self.curr_zone.objectid = self.curr_text
    elif name == 'FromFeeds':
      self.curr_zone.all_feeds = (self.curr_text.lower() == 'all')
    elif name == 'NextKey':
      self.next_key = self.curr_text
    elif name == 'Zone':
      self.zones.append(self.curr_zone)


class GetFenceResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.fence = LxFence()

    # private variables
    self._region = dict()
    self._callback = dict()
  
  def afterEndElement(self, name):
    if name == 'FenceID':
      self.fence.fenceid = self.curr_text
    if name == 'RegionType':
      self._region['type'] = self.curr_text
    elif name == 'Longitude':
      self._region['longitude'] = float(self.curr_text)
    elif name == 'Latitude':
      self._region['latitude'] = float(self.curr_text)
    elif name == 'Radius':
      self._region['radius'] = float(self.curr_text)
    elif name == 'Region':
      self.fence.region = self.createRegion(self._region)
    elif name == 'Trigger':
      self.fence.trigger = self.curr_text
    elif name == 'CallbackURL':
      self._callback['URL'] = self.curr_text
    elif name == 'CallbackType':
      self._callback['type'] = self.curr_text
    elif name == 'Callback':
      self.fence.callback = self.createCallback(self._callback)
    elif name == 'Feed':
      self.fence.from_feeds.append(self.curr_text)
    elif name == 'FromFeeds':
      self.fence.all_feeds = (self.curr_text.lower() == 'all')


class ListFencesResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.fences = []
    self.curr_fence = None
    self.next_key = None

    # private variables
    self._callback = dict()
    self._region = dict()
    
  def startElement(self, name, attrs):
    if name == 'Fence':
      self.curr_fence = LxFence()
    elif name == 'Callback':
      self._callback = dict()
    elif name == 'Region':
      self._region = dict()
    
  def afterEndElement(self, name):
    if name == 'FenceID':
      self.curr_fence.fenceid = self.curr_text
    elif name == 'RegionType':
      self._region['type'] = self.curr_text
    elif name == 'Longitude':
      self._region['longitude'] = float(self.curr_text)
    elif name == 'Latitude':
      self._region['latitude'] = float(self.curr_text)
    elif name == 'Radius':
      self._region['radius'] = float(self.curr_text)
    elif name == 'Region':
      self.curr_fence.region = self.createRegion(self._region)
    elif name == 'Trigger':
      self.curr_fence.trigger = self.curr_text
    elif name == 'CallbackURL':
      self._callback['URL'] = self.curr_text
    elif name == 'CallbackType':
      self._callback['type'] = self.curr_text
    elif name == 'Callback':
      self.curr_fence.callback = self.createCallback(self._callback)
    elif name == 'Feed':
      self.curr_fence.from_feeds.append(self.curr_text)
    elif name == 'FromFeeds':
      self.curr_fence.all_feeds = (self.curr_text.lower() == 'all')
    elif name == 'NextKey':
      self.next_key = self.curr_text
    elif name == 'Fence':
      self.fences.append(self.curr_fence)

class GetLocationHistoryResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.locations = []
    self.curr_location = None
    self.next_key = None
    
  def startElement(self, name, attrs):
    if name == 'Location':
      self.curr_location = LxLocation()
    
  def afterEndElement(self, name):
    if name == 'Longitude':
      self.curr_location.longitude = float(self.curr_text)
    elif name == 'Latitude':
      self.curr_location.latitude = float(self.curr_text)
    elif name == 'Time':
      self.curr_location.time = int(self.curr_text)
    elif name == 'Name':
      self.col_name = self.curr_text
    elif name == 'Value':
      self.curr_location.name_values[self.col_name] = self.curr_text
    elif name == 'NextKey':
      self.next_key = self.curr_text
    elif name == 'Location':
      self.locations.append(self.curr_location)

class GetSpaceActivityResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.objects = []
    self.curr_object = None
    self.next_key = None
  
  def startElement(self, name, attrs):
    if name == 'Location':
      self.curr_object = LxObject()
      self.curr_object.location = LxLocation()

  def afterEndElement(self, name):
    if name == 'Feed':
      self.curr_object.objectkey.feed = self.curr_text
    elif name == 'ObjectID':
      self.curr_object.objectkey.objectid = self.curr_text
    elif name == 'Longitude':
      self.curr_object.location.longitude = float(self.curr_text)
    elif name == 'Longitude':
      self.curr_object.location.longitude = float(self.curr_text)
    elif name == 'Latitude':
      self.curr_object.location.latitude = float(self.curr_text)
    elif name == 'Time':
      self.curr_object.location.time = int(self.curr_text)
    elif name == 'Name':
      self.col_name = self.curr_text
    elif name == 'Value':
      self.curr_object.location.name_values[self.col_name] = self.curr_text
    elif name == 'NextKey':
      self.next_key = self.curr_text
    elif name == 'Location':
      self.objects.append(self.curr_object)

