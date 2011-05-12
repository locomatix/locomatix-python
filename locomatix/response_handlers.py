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
from response_objects import *
from region import *
from callback import *
from keys import *
from exceptions import *

class LxResponseHandler(object):
  def __init__(self):
    self.message = ''
    self.response_time = 0.0

  def handle(self, data):
    self.message = data['Status']
    self.response_time = data['ExecutionTime']

  def createCallback(self, type, params): 
    if type == 'URL':
      return URLCallback(params['CallbackURL'])

    elif type == 'ApplePushNotification':
      info = params['ApplePushNotificationInfo']
      return ApplePushCallback(info['Message'], info['Sound'], info['Token'])
    return None

  def createRegion(self, type, params): 
    if type == 'Circle':
      return Circle(params['Latitude'], params['Longitude'], params['Radius'])

    elif type == 'Polygon':
      points = params['Points']
      pt_list = [(pt['Latitude'], pt['Longitude']) for pt in points]
      return Polygon(pt_list)

    return None

  def createObjectRegion(self, type, params): 
    if type == 'Circle':
      return Circle(params['Radius'])
    return None

  def createZone(self, rzone):
    zone = LxZone() 
    region = rzone['Region']
    callback = rzone['Callback']
    follow_object = rzone['FollowObject']

    zone.zoneid = rzone['ZoneID']
    zone.region = self.createObjectRegion(region['RegionType'], \
                                                 region['RegionParams'])
    zone.callback = self.createCallback(callback['CallbackType'], callback) 
    zone.trigger = rzone['Trigger']
    zone.predicate = rzone['Predicate']

    predicate = rzone['Predicate'].rstrip().split(' ')
    zone.from_feed = predicate[1]

    zone.feed = follow_object['Feed']
    zone.objectid = follow_object['ObjectID']
    zone.name_values = rzone.get('NameValues',{})
    zone.state = rzone['State']
    return zone

  def createFence(self, rfence):
    fence = LxFence()
    region = rfence['Region']
    callback = rfence['Callback']

    fence.fenceid = rfence['FenceID']
    fence.region = self.createRegion(region['RegionType'], \
                                     region['RegionParams'])
    fence.callback = self.createCallback(callback['CallbackType'], callback)
    fence.trigger = rfence['Trigger']
    fence.predicate = rfence['Predicate']

    predicate = rfence['Predicate'].rstrip().split(' ')
    fence.from_feed = predicate[1]

    fence.name_values = rfence.get('NameValues',{})
    fence.state = rfence['State']
    return fence

class StatusResponseHandler(LxResponseHandler):
  """Behaves exactly as the base response handler."""
  pass

class ListFeedsResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.feeds = []
    self.next_key = None

  def handle(self, data):
    super(ListFeedsResponseHandler, self).handle(data)
    self.next_key = data['Result'].get('NextKey')
    self.feeds = data['Result']['Feeds']
    
class GetAttributesResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.object = LxObject()
    
  def handle(self, data):
    super(GetAttributesResponseHandler, self).handle(data)
    obj = data['Result']['Object']
    self.object.feed = obj['Feed']
    self.object.objectid = obj['ObjectID']
    self.object.name_values = obj.get('NameValues',{})

class ListObjectsResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.objects = []
    self.next_key = None

  def handle(self, data):
    super(ListObjectsResponseHandler, self).handle(data)
    self.next_key = data['Result'].get('NextKey')
    for robject in data['Result']['Objects']:
      obj = LxObject()
      obj.feed = robject['Feed']
      obj.objectid = robject['ObjectID']
      obj.name_values = robject.get('NameValues', {})
      self.objects.append(obj)

class GetLocationResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.location = LxLocation()
  
  def handle(self, data):
    super(GetLocationResponseHandler, self).handle(data)
    location = data['Result']['Location']
    self.location.longitude = float(location['Longitude'])
    self.location.latitude = float(location['Latitude'])
    self.location.time = int(location['Time'])
    self.location.name_values = location.get('NameValues', {})

class SearchResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.objlocs = []
    self.next_key = None

  def handle(self, data):
    super(SearchResponseHandler, self).handle(data)
    self.next_key = data['Result'].get('NextKey')
    for robject in data['Result']['Objects']:
      objloc = LxObjectLocation()
      objloc.feed = robject['Feed']
      objloc.objectid = robject['ObjectID']
      rloc = robject['Location']
      objloc.longitude = rloc['Longitude']
      objloc.latitude = rloc['Latitude']
      self.objlocs.append(objloc)

class GetZoneResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.zone = None

  def handle(self, data):
    super(GetZoneResponseHandler, self).handle(data)
    self.zone = self.createZone(data['Result']['Zone'])
  
class ListZonesResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.zones = []
    self.next_key = None

  def handle(self, data):
    super(ListZonesResponseHandler, self).handle(data)
    self.next_key = data['Result'].get('NextKey')
    self.zones = [self.createZone(zone) for zone in data['Result']['Zones']]

class GetFenceResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.fence = LxFence()

  def handle(self, data):
    super(GetFenceResponseHandler, self).handle(data)
    self.fence = self.createFence(data['Result']['Fence'])
  
class ListFencesResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.fences = []
    self.next_key = None

  def handle(self, data):
    super(ListFencesResponseHandler, self).handle(data)
    self.next_key = data['Result'].get('NextKey')
    self.fences = [self.createFence(fence) for fence in data['Result']['Fences']]
    
class GetLocationHistoryResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.locations = []
    self.next_key = None

  def handle(self, data):
    super(GetLocationHistoryResponseHandler, self).handle(data)
    self.next_key = data['Result'].get('NextKey')
    for rlocation in data['Result']['Trail']:
      location = LxLocation()
      location.longitude = float(rlocation['Longitude'])
      location.latitude = float(rlocation['Latitude'])
      location.time = int(rlocation['Time'])
      location.name_values = rlocation.get('NameValues', {})
      self.locations.append(location)
    
class GetSpaceActivityResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.objlocs = []
    self.next_key = None

  def handle(self, data):
    super(GetSpaceActivityResponseHandler, self).handle(data)
    self.next_key = data['Result'].get('NextKey')
    for robject in data['Result']['Activity']:
      objloc = LxObjectLocation()
      objloc.feed = robject['Feed']
      objloc.objectid = robject['ObjectID']
      objloc.longitude = float(robject['Longitude'])
      objloc.latitude = float(robject['Latitude'])
      objloc.time = int(robject['Time'])
      objloc.name_values = robject.get('NameValues', {})
      self.objlocs.append(objloc)

class GetHistogramResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.grid_counts = LxGridCounts()

  def handle(self, data):
    super(GetHistogramResponseHandler, self).handle(data)
    self.grid_counts.nhslices = data['Result']['HorizontalSlices']  
    self.grid_counts.nvslices = data['Result']['VerticalSlices']  

    count = 0
    grid_row = []
    for i in data['Result']['ObjectGrid']:
      grid_row.append(i) 
      count = count + 1
      if count % self.grid_counts.nhslices == 0:
        self.grid_counts.counts.append(grid_row)
        count = 0
        grid_row = []
