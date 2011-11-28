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

import time
from objects import PrintableAttributes
from region import createRegion
from callback import createCallback

class LxResponseMetadata(PrintableAttributes):
  """Represents the metadata returned for the request"""
  def __init__(self):
    self.message = ''
    self.response_time = 0.0
    self.total_time = 0.0

class LxFeed(PrintableAttributes):
  """Represents a locomatix feed."""
  def __init__(self):
    self.name = None
    self.object_expiry = None
    self.location_expiry = None
    self.name_values = dict()

  def __str__(self):
    """Returns a json-like representation of the object"""
    params = dict()
    for key, value in self.__dict__.items():
      if value == None: continue
      params[key] = value
    return str(params)

  def to_map(self):
    params = dict()
    params['lxtype'] = 'LxFeed'
    params['name'] = self.name
    params['object_expiry'] = self.object_expiry
    params['location_expiry'] = self.location_expiry
    params['name_values'] = self.name_values
    return params

  def from_map(self, params):
    self.name = params['name'] 
    self.object_expiry = params['object_expiry'] 
    self.location_expiry = params['location_expiry']
    self.name_values = params['name_values']

class LxObject(PrintableAttributes):
  """Represents a locomatix object."""
  def __init__(self):
    self.objectid = None
    self.feed = None
    self.name_values = dict()

  def __str__(self):
    """Returns a json-like representation of the object"""
    params = dict()
    for key, value in self.__dict__.items():
      if value == None: continue
      if key != 'feed': 
        params[key] = value
    return str(params)

  def to_map(self):
    params = dict()
    params['lxtype'] = 'LxObject'
    params['objectid'] = self.objectid
    params['feed'] = self.feed
    params['name_values'] = self.name_values
    return params

  def from_map(self, params):
    self.feed = params['feed'] 
    self.objectid = params['objectid'] 
    self.feed = params['feed'] 
    self.name_values = params['name_values']

class LxLocation(PrintableAttributes):
  """Represents a locomatix location."""
  def __init__(self):
    self.longitude = None
    self.latitude = None
    self.time = None
    self.lname_values = dict()

  def __str__(self):
    """Returns a json-like representation of the object"""
    params = dict()
    for key, value in self.__dict__.items():
      if value == None: continue
      if key == 'time':
        t = time.gmtime(int(value))
        params['time'] = time.strftime("%m/%d/%Y:%H:%M:%S", t)
        continue
      params[key] = value
    return str(params)

  def to_map(self):
    params = dict()
    params['lxtype'] = 'LxLocation'
    params['longitude'] = self.longitude
    params['latitude'] = self.latitude
    params['time'] = self.time
    params['lname_values'] = self.lname_values
    return params

  def from_map(self, params):
    self.longitude = params['longitude'] 
    self.latitude = params['latitude'] 
    self.time = params['time'] 
    self.lname_values = params['lname_values']


class LxObjectLocation(PrintableAttributes):
  """Represents a locomatix object and its location."""
  def __init__(self):
    self.objectid = None
    self.feed = None
    self.name_values = dict()

    self.longitude = None
    self.latitude = None
    self.time = None
    self.lname_values = dict()

  def __str__(self):
    """Returns a json-like representation of the object"""
    params = dict()
    for key, value in self.__dict__.items():
      if value == None: continue
      if key == 'time':
        t = time.gmtime(int(value))
        params['time'] = time.strftime("%m/%d/%Y:%H:%M:%S", t)
        continue
      params[key] = value
    return str(params)

  def to_map(self):
    params = dict()
    params['lxtype'] = 'LxObjectLocation'
    params['objectid'] = self.objectid
    params['feed'] = self.feed
    params['name_values'] = self.name_values

    params['longitude'] = self.longitude
    params['latitude'] = self.latitude
    params['time'] = self.time
    params['lname_values'] = self.lname_values

    return params

  def from_map(self, params):
    self.objectid = params['objectid']
    self.feed = params['feed']
    self.name_values = params['name_values']

    self.longitude = params['longitude'] 
    self.latitude = params['latitude'] 
    self.time = params['time'] 
    self.lname_values = params['lname_values']

class LxFence(PrintableAttributes):
  """Represents a locomatix fence."""
  def __init__(self):
    self.fenceid = None
    self.region = None
    self.trigger = None
    self.callback = None
    self.query = None
    self.from_feed = None
    self.name_values = dict()
    self.state = None

  def to_map(self):
    params = dict()
    params['lxtype'] = 'LxFence'
    params['fenceid'] = self.fenceid
    params['region'] = self.region.to_map()
    params['trigger'] = self.trigger
    params['callback'] = self.callback.to_map()
    params['query'] = self.query
    params['from_feed'] = self.from_feed
    params['name_values'] = self.name_values
    params['state'] = self.state

    return params

  def from_map(self, params):
    self.fenceid = params['fenceid']
    self.region = createRegion(params['region'])
    self.trigger = params['trigger']
    self.callback = createCallback(params['callback'])
    self.query = params['query']
    self.from_feed = params['from_feed']
    self.name_values = params['name_values']
    self.state = params['state']

class LxZone(PrintableAttributes):
  """Represents a locomatix zone."""
  def __init__(self):
    self.zoneid = None
    self.objectid = None
    self.feed = None
    self.region = None
    self.trigger = None
    self.callback = None
    self.query = None
    self.from_feed = None
    self.name_values = dict()
    self.state = None

  def to_map(self):
    params = dict()
    params['lxtype'] = 'LxZone'
    params['zoneid'] = self.zoneid
    params['objectid'] = self.objectid
    params['feed'] = self.feed
    params['region'] = self.region.to_map()
    params['trigger'] = self.trigger
    params['callback'] = self.callback.to_map()
    params['query'] = self.query
    params['from_feed'] = self.from_feed
    params['name_values'] = self.name_values
    params['state'] = self.state

    return params

  def from_map(self, params):
    self.zoneid = params['zoneid']
    self.objectid = params['objectid']
    self.feed = params['feed']
    self.region = createRegion(params['region'])
    self.trigger = params['trigger']
    self.callback = createCallback(params['callback'])
    self.query = params['query']
    self.from_feed = params['from_feed']
    self.name_values = params['name_values']
    self.state = params['state']


class LxAggregate(PrintableAttributes):
  """Represents a locomatix object and its location."""
  def __init__(self):
    self.feed = None
    self.count = None
    self.sum = None
    self.max = None
    self.min = None

  def __str__(self):
    """Returns a json-like representation of the object"""
    params = dict()
    for key, value in self.__dict__.items():
      if value == None: continue
      params[key] = value
    return str(params)

class LxGridAggregates(PrintableAttributes):
  """Represents a locomatix grid aggregates."""
  def __init__(self):
    self.nhslices = None
    self.nvslices = None
    self.aggregates = []
