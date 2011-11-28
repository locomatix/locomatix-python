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

  def convertnvpairs(self, jsonarray):
    rnvpairs = dict()
    for nvpairs in jsonarray:
      for name, value in nvpairs.iteritems():
        if name in rnvpairs and isinstance(rnvpairs[name], list):
          rnvpairs[name].append(value)
        elif name in rnvpairs:
          rnvpairs[name] = [rnvpairs[name], value]
        else:
          rnvpairs[name] = value
    return rnvpairs

  def createCallback(self, atype, params): 
    if atype == 'URL':
      return URLCallback(params['CallbackURL'])

    elif atype == 'ApplePushNotification':
      info = params['ApplePushNotificationInfo']
      return ApplePushCallback(info['Message'], info['Sound'], info['Token'])
    return None

  def createRegion(self, atype, params): 
    if atype == 'Circle':
      return Circle(params['Latitude'], params['Longitude'], params['Radius'])

    elif atype == 'Polygon':
      points = params['Points']
      pt_list = [(pt['Latitude'], pt['Longitude']) for pt in points]
      return Polygon(pt_list)

    return None

  def createObjectRegion(self, atype, params): 
    if atype == 'Circle':
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
    zone.query = rzone['Predicate']

    predicate = rzone['Predicate'].rstrip().split(' ')
    zone.from_feed = predicate[1]

    zone.feed = follow_object['Feed']
    zone.objectid = follow_object['ObjectID']
    zone.name_values = self.convertnvpairs(rzone.get('NameValues',[]))
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
    fence.query = rfence['Predicate']

    predicate = rfence['Predicate'].rstrip().split(' ')
    fence.from_feed = predicate[1]

    fence.name_values = self.convertnvpairs(rfence.get('NameValues',[]))
    fence.state = rfence['State']
    return fence

def HandleAggregates(data):
  aggrs = LxAggregate()
  aggrs_found = False

  if 'Count' in data['Result']:
    aggrs.count = int(data['Result']['Count'])
    aggrs_found = True

  if 'Sum' in data['Result']:
    aggrs.sum = float(data['Result']['Sum'])
    aggrs_found = True

  if 'Maximum' in data['Result']:
    aggrs.max = float(data['Result']['Maximum'])
    aggrs_found = True

  if 'Minimum' in data['Result']:
    aggrs.min = float(data['Result']['Minimum'])
    aggrs_found = True

  return [aggrs] if aggrs_found else []

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
    for rfeed in data['Result']['Feeds']:
      feed = LxFeed()
      feed.feed = rfeed['Feed']
      feed.object_expiry = 'forever' if rfeed['ObjectExpiry'] < 0 else rfeed['ObjectExpiry']
      feed.location_expiry = 'forever' if rfeed['LocationExpiry'] < 0 else rfeed['LocationExpiry']
      self.feeds.append(feed)
    
class GetAttributesResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.object = LxObject()
    
  def handle(self, data):
    super(GetAttributesResponseHandler, self).handle(data)
    obj = data['Result']['Object']
    self.object.feed = obj['Feed']
    self.object.objectid = obj['ObjectID']
    self.object.name_values = self.convertnvpairs(obj.get('ObjectNameValues',[]))

class ListObjectsResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.objects = []
    self.aggrs = []
    self.next_key = None

  def handle(self, data):
    super(ListObjectsResponseHandler, self).handle(data)
    self.next_key = data['Result'].get('NextKey')

    self.aggrs = HandleAggregates(data)
    if len(self.aggrs) > 0: return

    for robject in data['Result']['Objects']:
      obj = LxObject()
      obj.feed = robject['Feed']
      obj.objectid = robject['ObjectID']
      obj.name_values = self.convertnvpairs(robject.get('ObjectNameValues', []))
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

    self.location.lname_values = self.convertnvpairs(location.get('LocationNameValues', []))

class SearchResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.objlocs = []
    self.aggrs = []
    self.next_key = None

  def handle(self, data):
    super(SearchResponseHandler, self).handle(data)
    self.next_key = data['Result'].get('NextKey')

    self.aggrs = HandleAggregates(data)
    if len(self.aggrs) > 0: return

    for robject in data['Result']['Objects']:
      objloc = LxObjectLocation()

      objloc.feed = robject['Feed']
      objloc.objectid = robject['ObjectID']

      if 'ObjectNameValues' in robject:
        nvpairs = robject.get('ObjectNameValues', [])
        objloc.name_values = self.convertnvpairs(nvpairs)

      if 'Longitude' in robject:
        objloc.longitude = robject['Longitude']

      if 'Latitude' in robject:
        objloc.latitude = robject['Latitude']

      if 'Time' in robject:
        objloc.time = int(robject['Time'])

      if 'LocationNameValues' in robject:
        nvpairs = robject.get('LocationNameValues', [])
        objloc.lname_values = self.convertnvpairs(nvpairs)

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
    self.aggrs = []
    self.next_key = None

  def handle(self, data):
    super(GetLocationHistoryResponseHandler, self).handle(data)
    self.next_key = data['Result'].get('NextKey')

    self.aggrs = HandleAggregates(data)
    if len(self.aggrs) > 0: return

    for rlocation in data['Result']['Objects']:
      location = LxLocation()

      if 'Longitude' in rlocation:
        location.longitude = float(rlocation['Longitude'])

      if 'Latitude' in rlocation:
        location.latitude = float(rlocation['Latitude'])

      if 'Time' in rlocation:
        location.time = int(rlocation['Time'])

      location.lname_values = self.convertnvpairs(rlocation.get('LocationNameValues', []))
      self.locations.append(location)
    
class GetSpaceActivityResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.objlocs = []
    self.aggrs = []
    self.next_key = None

  def handle(self, data):
    super(GetSpaceActivityResponseHandler, self).handle(data)
    self.next_key = data['Result'].get('NextKey')

    self.aggrs = HandleAggregates(data)
    if len(self.aggrs) > 0: return

    for robject in data['Result']['Objects']:
      objloc = LxObjectLocation()
      objloc.feed = robject['Feed']
      objloc.objectid = robject['ObjectID']

      if 'Longitude' in robject:
        objloc.longitude = float(robject['Longitude'])

      if 'Latitude' in robject:
        objloc.latitude = float(robject['Latitude'])

      if 'Time' in robject:
        objloc.time = int(robject['Time'])

      objloc.lname_values = self.convertnvpairs(robject.get('LocationNameValues', []))
      self.objlocs.append(objloc)

class GetHistogramResponseHandler(LxResponseHandler):
  def __init__(self):
    LxResponseHandler.__init__(self)
    self.grid_aggregates = LxGridAggregates()

  def handle(self, data):
    super(GetHistogramResponseHandler, self).handle(data)
    self.grid_aggregates.nhslices = data['Result']['HorizontalSlices']  
    self.grid_aggregates.nvslices = data['Result']['VerticalSlices']  

    count = 0
    grid_row = []
    for i in data['Result']['ObjectGrid']:
      grid_row.append(i) 
      count = count + 1
      if count % self.grid_aggregates.nhslices == 0:
        self.grid_aggregates.aggregates.append(grid_row)
        count = 0
        grid_row = []
