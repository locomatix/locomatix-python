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
from requests import *
from responses import *
from defaults import *

import sys
major, minor, micro, releaselevel, serial = sys.version_info
SUPPORT_TIMEOUT = (major >= 2 and minor >= 6)

DEFAULT_LOCOMATIX_VERSION = '0.9'
DEFAULT_LOCOMATIX_HOST = 'api.locomatix.com'
DEFAULT_LOCOMATIX_PORTS = { False:80, True:443 }

DEFAULT_FETCH_STARTKEY   = ''
DEFAULT_FETCH_START  = 0
DEFAULT_FETCH_SIZE  = 20

REQUEST_RESPONSES = {
  'create_object':       (CreateObjectRequest,       CreateObjectResponse),
  'delete_object':       (DeleteObjectRequest,       DeleteObjectResponse),
  'list_objects':        (ListObjectsRequest,        ListObjectsResponse),
  'update_attributes':   (UpdateAttributesRequest,   UpdateAttributesResponse),
  'get_attributes':      (GetAttributesRequest,      GetAttributesResponse),
  'update_location':     (UpdateLocationRequest,     UpdateLocationResponse),
  'get_location':        (GetLocationRequest,        GetLocationResponse),
  'search_nearby':       (SearchNearbyRequest,       SearchNearbyResponse),
  'search_region':       (SearchRegionRequest,       SearchRegionResponse),
  'create_zone':         (CreateZoneRequest,         CreateZoneResponse),
  'get_zone':            (GetZoneRequest,            GetZoneResponse),
  'list_zones':          (ListZonesRequest,          ListZonesResponse),
  'delete_zone':         (DeleteZoneRequest,         DeleteZoneResponse),
  'create_fence':        (CreateFenceRequest,        CreateFenceResponse),
  'get_fence':           (GetFenceRequest,           GetFenceResponse),
  'list_fences':         (ListFencesRequest,         ListFencesResponse),
  'delete_fence':        (DeleteFenceRequest,        DeleteFenceResponse),
  'get_location_history':(GetLocationHistoryRequest, GetLocationHistoryResponse),
  'get_space_activity':  (GetSpaceActivityRequest,   GetSpaceActivityResponse),
}

class LocomatixConnectionFailed(Exception):
  """Raised when the Client fails to establish a connection with the remote Locomatix server."""
  def __init__(self, parent_exception, host, port):
    self.ex = parent_exception
    self.host = host
    self.port = port
  def __str__(self):
    return "Failed to establish connection with %s:%d\n%s" % (self.host, self.port, self.ex)

class LocomatixRequestFailed(Exception):
  """Raised when the Client fails to establish a connection with the remote Locomatix server."""
  def __init__(self, parent_exception, host, port, req_type):
    self.ex = parent_exception
    self.req_type = req_type
    self.host = host
    self.port = port
  def __str__(self):
    return "Locomatix %s could not be completed on %s:%d\n%s" % (self.req_type, self.host, self.port, self.ex)

class Client():
  """The main interface used to consume Locomatix REST API services.
  
  All connection information and authorization credentials must be provided at
  initialization.  Upon initialization the client establishes a persistent
  connection to the remote server.  Multiple requests may be sent over the open
  connection before the user closes the connection with close()."""
  
  def __init__(self, custid, custkey, secretkey, 
                    host = DEFAULT_LOCOMATIX_HOST, \
                    port = None, ssl = True, \
                    version = DEFAULT_LOCOMATIX_VERSION, \
                    timeout=10, retry=3):
    """Initializes a persistent connection with the Locomatix server.
    
    Args:
      custid:    customer ID, required
      custkey:   customer Key, required
      secretkey: customer secret key, required
      host:      Locomatix Server hostname, required
      port:      Locomatix Server port, required
      ssl:       Use SSL for the connection, defualt True
      version:   Locomatix API version, required (currently 0.9)
      timeout:   Locomatix server connection timeout
      retry:     No. of retries while connecting to Locomatix service""" 
    self._http_headers = {
      'lx-custid':custid,
      'lx-custkey':custkey,
      'lx-secretkey':secretkey,
      'lx-apiversion':version }
    self._host = host
    if not port:
      self._port = DEFAULT_LOCOMATIX_PORTS[ssl]
    else:
      self._port = port
    self._ssl = ssl
    self._timeout = timeout
    self._retry = retry
    self._conn = None
    self._open()
  
  def close(self):
    """Closes the connection with the remote Locomatix server."""
    self._conn.close()
  
  def create_object(self, objectkey, name_values={}):
    """Creates an object.
    
    Args:
      objectkey: Key that uniquely identifes the object, required
      name_values: a dictionary of name-value attribute pairs (optional)
    
    Return:
      A CreateObjectResponse object"""
    return self._request('create_object', objectkey, name_values)
  
  def delete_object(self, objectkey):
    """Delete an object.
    
    Args:
      objectkey: Key that uniquely identifes the object, required
    
    Return:
      A DeleteObjectResponse object"""
    return self._request('delete_object', objectkey)
  
  def list_objects(self, feedkey, 
                          start_key=DEFAULT_FETCH_STARTKEY, \
                          fetch_size=DEFAULT_FETCH_SIZE):
    """List all the objects and its attributes in the feed.
    
    Args:
      feedkey: Key that represents the feed, required
      start_key: the key of the object to return in a batch, optional
        default = ""
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      A ListObjectsResponse object"""
    return self._request('list_objects', feedkey, start_key, fetch_size)
  
  def list_objects_iterator(self, feedkey, fetch_size=DEFAULT_FETCH_SIZE):
    """Returns an iterator over batches of objects in the given feed.
    
    Args:
      feedkey: Key that represents the feed, required
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      An iterator over batches of objects in the feed.  For example:
      for batch in list_objects_iterator():
        for obj in batch.objects
          # do something with the object
    """
    fetch_start = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self.list_objects(feedkey, fetch_start, fetch_size)
      if (batch.status > httplib.OK or len(batch.objects) == 0):
        break # there was some error or there are no results
      yield batch
      if batch.next_key == None:
        break # this is the last batch
      fetch_start = batch.next_key
  
  def update_attributes(self, objectkey, name_values):
    """Update the attributes of an existing object.
    
    Args:
      objectkey: Key that uniquely identifes the object, required
      name_values: the new attributes to associate with the object, required
    
    Return:
      An UpdateAttributesResponse object"""
    return self._request('update_attributes', objectkey, name_values)
  
  def get_attributes(self, objectkey):
    """Get the attributes of an existing object.
    
    Args:
      objectkey: Key that uniquely identifes the object, required
    
    Return:
      A GetAttributesResponse object"""
    return self._request('get_attributes', objectkey)
  
  def update_location(self, objectkey, longitude, latitude, time, name_values={}):
    """Update the Location of an existing object.
    
    Args:
      objectkey: Key that uniquely identifes the object, required
      longitude: longitude (decimal degrees), required
      latitude: latitude (decimal degrees), required
      time: seconds since unix epoch, required
      name_values: a dictionary of name-value attribute pairs (optional)
    
    Return:
      An UpdateLocationResponse object"""
    return self._request('update_location', objectkey, longitude, latitude, time, name_values)
  
  def get_location(self, objectkey):
    """Get the current location of an object.
    
    Args:
      objectkey: Key that uniquely identifes the object, required
    
    Return:
      A GetLocationResponse object"""
    return self._request('get_location', objectkey)
  
  def search_nearby(self, objectkey, objectregion, \
                          from_feeds=[], \
                          start_key=DEFAULT_FETCH_STARTKEY, \
                          fetch_size=DEFAULT_FETCH_SIZE):
    """Search in a region near an existing object.
    
    Args:
      objectkey: Key that uniquely identifes the object, required
      objectregion : type and specification of region around the object
      from_feeds: list of feeds to search, optional
        default = [], searches only the feed of parent object
      start_key: the start key of the first object to return in a batch, optional
        default = ""
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      A SearchNearbyResponse object"""
    return self._request('search_nearby', objectkey, objectregion, \
                                          from_feeds, start_key, fetch_size)
  
  def search_nearby_iterator(self, objectkey, region, \
                             from_feeds=[], \
                             fetch_size=DEFAULT_FETCH_SIZE):
    """Iterates over batches of objects returned by the search.
    
    Args:
      objectkey: Key that uniquely identifes the object, required
      region_type: type of region (only 'circle' supported), required
      region_params: dictionary of region parameters, distance in meters, required
        e.g. {'radius': 1000.0}
      from_feeds: list of feeds to search, optional
        default = [], searches only the feed of parent object
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      An iterator over batches of objects returned by the search.
    """
    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self.search_nearby(objectkey, region, from_feeds, \
                                 start_key, fetch_size)
      if (batch.status > httplib.OK or len(batch.objects) == 0):
        break # there was some error or there were no results
      yield batch
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key
  
  def search_region(self, region, \
                        from_feeds, \
                        start_key=DEFAULT_FETCH_STARTKEY, \
                        fetch_size=DEFAULT_FETCH_SIZE):
    """Search a region at a geographic location.
    
    Args:
      region : type and specification of region 
      from_feeds: list of feeds to search, optional
        default = [], searches all feeds
      start_key: the index of the first object to return in a batch, optional
        default = ""
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      A SearchRegionResponse object"""
    return self._request('search_region', region, \
                                          from_feeds, start_key, fetch_size)
  
  def search_region_iterator(self, region, \
                                   from_feeds, \
                                   fetch_size=DEFAULT_FETCH_SIZE):
    """Returns an iterator over batches of search_region results.

    Args:
      region : type and specification of region 
      from_feeds: list of feeds to search, optional
        default = [], searches all feeds
      fetch_size: number of objects to return in a batch, optional
        default = 20

    Return:
      An iterator over batches of search_region results"""
    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self.search_region(region, from_feeds, start_key, fetch_size)
      if (batch.status > httplib.OK or len(batch.objects) == 0):
        break # there was some error or there were no results
      yield batch
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key
  
  def create_zone(self, zonekey, objectregion, \
                        trigger, callback, from_feeds=[]):
    """Create a Zone associated with an existing object.
    
    Args:
      zonekey: Key that uniquely identifes the zone, required
      objectregion : type and specification of region around the object
      callback: type and specification for alerts to be POSTed, required
      from_feeds: list of feeds to search, optional
        default = [], monitors only the feed of the parent object
    
    Return:
      A CreateZoneResponse object"""
    return self._request('create_zone', zonekey, \
                             objectregion, trigger, callback, from_feeds)
  
  def get_zone(self, zonekey):
    """Get the Zone definition associated with an object.
    
    Args:
      zonekey: Key that uniquely identifes the zone, required
    
    Return:
      A GetZoneResponse object"""
    return self._request('get_zone', zonekey)
  
  def list_zones(self, objectkey,
                          start_key=DEFAULT_FETCH_STARTKEY, \
                          fetch_size=DEFAULT_FETCH_SIZE):
    """List all the Zones and its definitions associated with an object.
    
    Args:
      objectkey: Key that uniquely identifes the object, required
      start_key: the index of the first zone to return in next batch, optional
        default = ""
      fetch_size: number of zones to return in a batch, optional
        default = 20
    
    Return:
      A ListZonesResponse object"""
    return self._request('list_zones', objectkey, start_key, fetch_size)
  
  def list_zones_iterator(self, objectkey,
                                fetch_size=DEFAULT_FETCH_SIZE):
    """Returns an iterator over batches of zones associated with the object.

    Args:
      objectkey: Key that uniquely identifes the object, required
      fetch_size: number of zones to return in a batch, optional
        default = 20

    Return:
      An iterator over batches of zones associated with the object."""
    fetch_start = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self.list_zones(objectkey, fetch_start, fetch_size)
      if (batch.status > httplib.OK or len(batch.zones) == 0):
        break # there was some error or there were no results
      yield batch
      if batch.next_key == None:
        break # this is the last batch
      fetch_start = batch.next_key
  
  def delete_zone(self, zonekey):
    """Delete a Zone associated with an object.
    
    Args:
      zonekey: Key that uniquely identifes the zone, required
    
    Return:
      A DeleteZoneResponse object"""
    return self._request('delete_zone', zonekey)
  
  def create_fence(self, fencekey, region, trigger,\
                         callback, from_feeds):
    """Create a Fence at a fixed geographic location.
    
    Args:
      fencekey: Key that uniquely identifes the fence, required
      region : type and specification of region 
      callback: type and specification for alerts to be POSTed, required
      from_feeds: list of feeds to search, optional
        default = [], monitors all feeds
    
    Return:
      A CreateFenceResponse object"""
    return self._request('create_fence', fencekey, region, \
                                         trigger, callback, from_feeds)
  
  def get_fence(self, fencekey):
    """Get the definition of an existing Fence.
    
    Args:
      fencekey: Key that uniquely identifes the fence, required
    
    Return:
      A GetFenceResponse object"""
    return self._request('get_fence', fencekey)
  
  def list_fences(self, start_key=DEFAULT_FETCH_STARTKEY, \
                        fetch_size=DEFAULT_FETCH_SIZE):
    """Get the definition of all existing Fences.
    
    Args:
      start_key: the index of the first zone to return in a batch, optional
        default = ""
      fetch_size: number of zones to return in a batch, optional
        default = 20

    Return:
      A ListFencesResponse object"""
    return self._request('list_fences', start_key, fetch_size)
  
  def list_fences_iterator(self, fetch_size=DEFAULT_FETCH_SIZE):
    """Returns an iterator over batches of fences.

    Args:
      fetch_size: number of zones to return in a batch, optional
        default = 20

    Return:
      An iterator over batches of fences"""
    fetch_start = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self.list_fences(fetch_start, fetch_size)
      if (batch.status > httplib.OK or len(batch.fences) == 0):
        break # there was some error or there were no results
      yield batch
      if batch.next_key == None:
        break # this is the last batch
      fetch_start = batch.next_key
  
  def delete_fence(self, fencekey):
    """Delete an existing Fence.
    
    Args:
      fencekey: Key that uniquely identifes the fence, required
    
    Return:
      A DeleteFenceResponse object"""
    return self._request('delete_fence', fencekey)
  
  def get_location_history(self, objectkey, start_time, end_time, \
                         start_key=DEFAULT_FETCH_STARTKEY, \
                         fetch_size=DEFAULT_FETCH_SIZE):
    """Get the location history of an object.
    
    Args:
      objectkey: Key that represents a unique existing object, required
      start_time: start of the time slice to retrieve history
      end_time: end of the time slice to retrieve history
      start_key: the index of the first zone to return in a batch, optional
        default = ""
      fetch_size: number of location history to return in a batch, optional
        default = 20

    Return:
      A GetLocationHistoryResponse object"""
    return self._request('get_location_history', objectkey, start_time, \
                          end_time, start_key, fetch_size)
  
  def get_location_history_iterator(self, objectkey, start_time, end_time, \
                                    fetch_size=DEFAULT_FETCH_SIZE):
    """Returns an iterator over location history of object.

    Args:
      objectkey: Key that represents a unique existing object, required
      start_time: start of the time slice to retrieve history
      start_time: start of the time slice to retrieve history
      end_time: end of the time slice to retrieve history
      fetch_size: number of zones to return in a batch, optional
        default = 20

    Return:
      An iterator over location of object"""
    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self.get_location_history(objectkey, start_time, end_time, \
                                        start_key, fetch_size)
      if (batch.status > httplib.OK or len(batch.locations) == 0):
        break # there was some error or there were no results
      yield batch
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

  def get_space_activity(self, feedkey, region, start_time, end_time, \
                         start_key=DEFAULT_FETCH_STARTKEY, \
                         fetch_size=DEFAULT_FETCH_SIZE):
    """Get the objects entered into the given space in a time slice
    
    Args:
      feedkey: Key that represents the feed, required
      region: specify the region of interest
      start_time: start of the time slice to retrieve history
      end_time: end of the time slice to retrieve history
      start_key: the index of the first zone to return in a batch, optional
        default = ""
      fetch_size: number of location history to return in a batch, optional
        default = 20

    Return:
      A GetSpaceActivityResponse object"""
    return self._request('get_space_activity', feedkey, region, start_time, \
                          end_time, start_key, fetch_size)
  
  def get_space_activity_iterator(self, feedkey, region, start_time, end_time, \
                                  fetch_size=DEFAULT_FETCH_SIZE):
    """Returns an iterator over location history of object.

    Args:
      feedkey: Key that represents the feed, required
      region: specifes the region of interest
      start_time: start of the time slice to retrieve history
      end_time: end of the time slice to retrieve history
      fetch_size: number of zones to return in a batch, optional
        default = 20

    Return:
      An iterator over location of object"""
    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self.get_space_activity(feedkey, region, start_time, end_time, \
                                      start_key, fetch_size)
      if (batch.status > httplib.OK or len(batch.objects) == 0):
        break # there was some error or there were no results
      yield batch
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key


  # private methods
  
  def _request(self, request_type, *args):
    Request, Response = REQUEST_RESPONSES[request_type]
    method, uri, body = Request(*args).dump()
    # try the request response cycle retry times
    for i in range(self._retry):
      try:
        self._conn.request(method, uri, body, self._http_headers)
        http_response = self._conn.getresponse()
      except Exception, ex:
        continue
      else:
        # got a response, no connection problems
        return Response(http_response, *args)
    # request/response cycle failed after retries
    raise LocomatixRequestFailed(ex, self._host, self._port, self.__class__.__name__)
  
  def _open(self):
    if self._ssl == True:
      if SUPPORT_TIMEOUT:
        self._conn = httplib.HTTPSConnection(self._host, self._port, timeout=self._timeout)
      else:
        self._conn = httplib.HTTPSConnection(self._host, self._port)
    else:
      if SUPPORT_TIMEOUT:
        self._conn = httplib.HTTPConnection(self._host, self._port, timeout=self._timeout)
      else:
        self._conn = httplib.HTTPConnection(self._host, self._port)
    # try to connect retry times
    for i in range(self._retry):
      try:
        self._conn.connect()
      except Exception, ex:
        continue
      else:
        return # the connection was successful
    # connection could not be made after retries
    raise LocomatixConnectionFailed(ex, self._host, self._port)


