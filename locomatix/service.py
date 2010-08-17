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

DEFAULT_FETCH_START   = 0
DEFAULT_FETCH_SIZE    = 20

REQUEST_RESPONSES = {
  'create_object':     (CreateObjectRequest,     CreateObjectResponse),
  'delete_object':     (DeleteObjectRequest,     DeleteObjectResponse),
  'list_objects':      (ListObjectsRequest,      ListObjectsResponse),
  'update_attributes': (UpdateAttributesRequest, UpdateAttributesResponse),
  'get_attributes':    (GetAttributesRequest,    GetAttributesResponse),
  'update_location':   (UpdateLocationRequest,   UpdateLocationResponse),
  'get_location':      (GetLocationRequest,      GetLocationResponse),
  'search_nearby':     (SearchNearbyRequest,     SearchNearbyResponse),
  'search_region':     (SearchRegionRequest,     SearchRegionResponse),
  'create_zone':       (CreateZoneRequest,       CreateZoneResponse),
  'get_zone':          (GetZoneRequest,          GetZoneResponse),
  'list_zones':        (ListZonesRequest,        ListZonesResponse),
  'delete_zone':       (DeleteZoneRequest,       DeleteZoneResponse),
  'create_fence':      (CreateFenceRequest,      CreateFenceResponse),
  'get_fence':         (GetFenceRequest,         GetFenceResponse),
  'list_fences':       (ListFencesRequest,       ListFencesResponse),
  'delete_fence':      (DeleteFenceRequest,      DeleteFenceResponse),
}

class LocomatixConnectionFailed(Exception):
  """Raised when the Service fails to establish a connection with the remote Locomatix server."""
  def __init__(self, parent_exception, host, port):
    self.ex = parent_exception
    self.host = host
    self.port = port
  def __str__(self):
    return "Failed to establish connection with %s:%d\n%s" % (self.host, self.port, self.ex)

class LocomatixRequestFailed(Exception):
  """Raised when the Service fails to establish a connection with the remote Locomatix server."""
  def __init__(self, parent_exception, host, port, req_type):
    self.ex = parent_exception
    self.req_type = req_type
    self.host = host
    self.port = port
  def __str__(self):
    return "Locomatix %s could not be completed on %s:%d\n%s" % (self.req_type, self.host, self.port, self.ex)

class Service():
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
  
  def create_object(self, objectid, feed, name_values={}):
    """Creates an object.
    
    Args:
      objectid: a unique object ID, required
      feed: a feed name, required
      name_values: a dictionary of name-value attribute pairs (optional)
    
    Return:
      A CreateObjectResponse object"""
    return self._request('create_object', objectid, feed, name_values)
  
  def delete_object(self, objectid, feed):
    """Delete an object.
    
    Args:
      objectid: a unique existing object ID, required
      feed: a feed name, required
    
    Return:
      A DeleteObjectResponse object"""
    return self._request('delete_object', objectid, feed)
  
  def list_objects(self, feed, 
                          fetch_start=DEFAULT_FETCH_START, \
                          fetch_size=DEFAULT_FETCH_SIZE):
    """List all the objects and its attributes in the feed.
    
    Args:
      feed: a feed name, required
      fetch_start: the index of the first object to return in a batch, optional
        default = 0
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      A ListObjectsResponse object"""
    return self._request('list_objects', feed, fetch_start, fetch_size)
  
  def list_objects_iterator(self, feed, fetch_size=DEFAULT_FETCH_SIZE):
    """Returns an iterator over batches of objects in the given feed.
    
    Args:
      feed: a feed name, required
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      An iterator over batches of objects in the feed.  For example:
      for batch in list_objects_iterator():
        for obj in batch.objects
          # do something with the object
    """
    fetch_start = 0
    while True:
      batch = self.list_objects(feed, fetch_start, fetch_size)
      if (batch.status > httplib.OK or len(batch.objects) == 0):
        break # there was some error or there are no results
      yield batch
      if len(batch.objects) < fetch_size:
        break # this is the last batch
      fetch_start += fetch_size
  
  def update_attributes(self, objectid, feed, name_values):
    """Update the attributes of an existing object.
    
    Args:
      objectid: a unique existing object ID, required
      feed: a feed name, required
      name_values: the new attributes to associate with the object, required
    
    Return:
      An UpdateAttributesResponse object"""
    return self._request('update_attributes', objectid, feed, name_values)
  
  def get_attributes(self, objectid, feed):
    """Get the attributes of an existing object.
    
    Args:
      objectid: a unique existing object ID, required
      feed: a feed name, required
    
    Return:
      A GetAttributesResponse object"""
    return self._request('get_attributes', objectid, feed)
  
  def update_location(self, objectid, feed, longitude, latitude, time, name_values={}):
    """Update the Location of an existing object.
    
    Args:
      objectid: a unique existing object ID, required
      feed: a feed name, required
      longitude: longitude (decimal degrees), required
      latitude: latitude (decimal degrees), required
      time: seconds since unix epoch, required
      name_values: a dictionary of name-value attribute pairs (optional)
    
    Return:
      An UpdateLocationResponse object"""
    return self._request('update_location', objectid, feed, longitude, latitude, time, name_values)
  
  def get_location(self, objectid, feed):
    """Get the current location of an object.
    
    Args:
      objectid: a unique existing object ID, required
      feed: a feed name, required
    
    Return:
      A GetLocationResponse object"""
    return self._request('get_location', objectid, feed)
  
  def search_nearby(self, objectid, feed, region, \
                          from_feeds=[], \
                          fetch_start=DEFAULT_FETCH_START, \
                          fetch_size=DEFAULT_FETCH_SIZE):
    """Search in a region near an existing object.
    
    Args:
      objectid: a unique existing object ID, required
      feed: a feed name, required
      region_type: type of region (only 'circle' supported), required
      region_params: dictionary of region parameters, distance in meters, required
        e.g. {'radius': 1000.0}
      from_feeds: list of feeds to search, optional
        default = [], searches only the feed of parent object
      fetch_start: the index of the first object to return in a batch, optional
        default = 0
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      A SearchNearbyResponse object"""
    return self._request('search_nearby', objectid, feed, region, \
                                          from_feeds, fetch_start, fetch_size)
  
  def search_nearby_iterator(self, objectid, feed, region, \
                             from_feeds=[], \
                             fetch_size=DEFAULT_FETCH_SIZE):
    """Iterates over batches of objects returned by the search.
    
    Args:
      objectid: a unique existing object ID, required
      feed: a feed name, required
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
    fetch_start = 0
    while True:
      batch = self.search_nearby(objectid, feed, region, from_feeds, \
                                 fetch_start, fetch_size)
      if (batch.status > httplib.OK or len(batch.objects) == 0):
        break # there was some error or there were no results
      yield batch
      if len(batch.objects) < fetch_size:
        break # this is the last batch
      fetch_start += fetch_size
  
  def search_region(self, region, \
                        from_feeds, \
                        fetch_start=DEFAULT_FETCH_START, \
                        fetch_size=DEFAULT_FETCH_SIZE):
    """Search a region at a geographic location.
    
    Args:
      region_type: type of region (only 'circle' supported), required
      region_params: dictionary of region parameters, distance in meters, required
        latitude/longitude must be specified in addition to any region specific params
        e.g. { 'latitude':45.0, 'longitude':45.0, 'radius': 1000.0 }
      from_feeds: list of feeds to search, optional
        default = [], searches all feeds
      fetch_start: the index of the first object to return in a batch, optional
        default = 0
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      A SearchRegionResponse object"""
    return self._request('search_region', region, \
                                          from_feeds, fetch_start, fetch_size)
  
  def search_region_iterator(self, region, \
                                   from_feeds, \
                                   fetch_size=DEFAULT_FETCH_SIZE):
    """Returns an iterator over batches of search_region results.

    Args:
      region_type: type of region (only 'circle' supported), required
      region_params: dictionary of region parameters, distance in meters, required
        latitude/longitude must be specified in addition to any region specific params
        e.g. { 'latitude':45.0, 'longitude':45.0, 'radius': 1000.0 }
      from_feeds: list of feeds to search, optional
        default = [], searches all feeds
      fetch_size: number of objects to return in a batch, optional
        default = 20

    Return:
      An iterator over batches of search_region results"""
    fetch_start = 0
    while True:
      batch = self.search_region(region, from_feeds, fetch_start, fetch_size)
      if (batch.status > httplib.OK or len(batch.objects) == 0):
        break # there was some error or there were no results
      yield batch
      if len(batch.objects) < fetch_size:
        break # this is the last batch
      fetch_start += fetch_size
  
  def create_zone(self, zoneid, objectid, feed, region, \
                        trigger, callback, from_feeds=[]):
    """Create a Zone associated with an existing object.
    
    Args:
      zoneid: a unique ID for the new Zone, required
      objectid: a unique existing object ID, required
      feed: a feed name, required
      region_type: type of region (only 'circle' supported), required
      region_params: dictionary of region parameters, distance in meters, required
        e.g. {'radius': 1000.0}
      callbackurl: alerts are POSTed to this URL, required
      from_feeds: list of feeds to search, optional
        default = [], monitors only the feed of the parent object
    
    Return:
      A CreateZoneResponse object"""
    return self._request('create_zone', zoneid, objectid, feed, region, \
                                        trigger, callback, from_feeds)
  
  def get_zone(self, zoneid, objectid, feed):
    """Get the Zone definition associated with an object.
    
    Args:
      zoneid: the id of the zone to get, required
      objectid: a unique existing object ID, required
      feed: a feed name, required
    
    Return:
      A GetZoneResponse object"""
    return self._request('get_zone', zoneid, objectid, feed)
  
  def list_zones(self, objectid, feed,
                          fetch_start=DEFAULT_FETCH_START, \
                          fetch_size=DEFAULT_FETCH_SIZE):
    """List all the Zones and its definitions associated with an object.
    
    Args:
      objectid: a unique existing object ID, required
      feed: a feed name, required
      fetch_start: the index of the first zone to return in a batch, optional
        default = 0
      fetch_size: number of zones to return in a batch, optional
        default = 20
    
    Return:
      A ListZonesResponse object"""
    return self._request('list_zones', objectid, feed, fetch_start, fetch_size)
  
  def list_zones_iterator(self, objectid, feed,
                                fetch_size=DEFAULT_FETCH_SIZE):
    """Returns an iterator over batches of zones associated with the object.

    Args:
      objectid: a unique existing object ID, required
      feed: a feed name, required
      fetch_size: number of zones to return in a batch, optional
        default = 20

    Return:
      An iterator over batches of zones associated with the object."""
    fetch_start = 0
    while True:
      batch = self.list_zones(objectid, feed, fetch_start, fetch_size)
      if (batch.status > httplib.OK or len(batch.zones) == 0):
        break # there was some error or there were no results
      yield batch
      if len(batch.zones) < fetch_size:
        break # this is the last batch
      fetch_start += fetch_size
  
  def delete_zone(self, zoneid, objectid, feed):
    """Delete a Zone associated with an object.
    
    Args:
      zoneid: the id of the zone to delete, required
      objectid: a unique existing object ID, required
      feed: a feed name, required
    
    Return:
      A DeleteZoneResponse object"""
    return self._request('delete_zone', zoneid, objectid, feed)
  
  def create_fence(self, fenceid, region, trigger,\
                         callback, from_feeds):
    """Create a Fence at a fixed geographic location.
    
    Args:
      fenceid: a unique ID for the new Fence, required
      region_type: type of region (only 'circle' supported), required
      region_params: dictionary of region parameters, distance in meters, required
        latitude/longitude must be specified in addition to any region specific params  
        e.g. { 'latitude':45.0, 'longitude':45.0, 'radius': 1000.0 }
      callbackurl: alerts will be POSTed to this URL, required
      from_feeds: list of feeds to search, optional
        default = [], monitors all feeds
    
    Return:
      A CreateFenceResponse object"""
    return self._request('create_fence', fenceid, region, \
                                         trigger, callback, from_feeds)
  
  def get_fence(self, fenceid):
    """Get the definition of an existing Fence.
    
    Args:
      fenceid: the ID of the Fence to get, required
    
    Return:
      A GetFenceResponse object"""
    return self._request('get_fence', fenceid)
  
  def list_fences(self, fetch_start=DEFAULT_FETCH_START, \
                        fetch_size=DEFAULT_FETCH_SIZE):
    """Get the definition of all existing Fences.
    
    Args:
      fetch_start: the index of the first zone to return in a batch, optional
        default = 0
      fetch_size: number of zones to return in a batch, optional
        default = 20

    Return:
      A ListFencesResponse object"""
    return self._request('list_fences', fetch_start, fetch_size)
  
  def list_fences_iterator(self, fetch_size=DEFAULT_FETCH_SIZE):
    """Returns an iterator over batches of fences.

    Args:
      fetch_size: number of zones to return in a batch, optional
        default = 20

    Return:
      An iterator over batches of fences"""
    fetch_start = 0
    while True:
      batch = self.list_fences(fetch_start, fetch_size)
      if (batch.status > httplib.OK or len(batch.fences) == 0):
        break # there was some error or there were no results
      yield batch
      if len(batch.fences) < fetch_size:
        break # this is the last batch
      fetch_start += fetch_size
  
  def delete_fence(self, fenceid):
    """Delete an existing Fence.
    
    Args:
      fenceid: the ID of the Fence to delete, required
    
    Return:
      A DeleteFenceResponse object"""
    return self._request('delete_fence', fenceid)
  
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


