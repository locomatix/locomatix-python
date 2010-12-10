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

# DEFAULT_LOCOMATIX_VERSION = '0.9'
# DEFAULT_LOCOMATIX_HOST = 'api.locomatix.com'
# DEFAULT_LOCOMATIX_PORT = 443

# DEFAULT_FETCH_STARTKEY   = ''
# DEFAULT_FETCH_START  = 0
# DEFAULT_FETCH_SIZE  = 20

REQUEST_RESPONSES = {
  'list_feeds':          (ListFeedsRequest,          ListFeedsResponse),
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
                    port = None, version = DEFAULT_LOCOMATIX_VERSION, \
                    timeout=10, retry=3):
    """Initializes a persistent connection with the Locomatix server.
    
    Args:
      custid:    customer ID, required
      custkey:   customer Key, required
      secretkey: customer secret key, required
      host:      Locomatix Server hostname, required
      port:      Locomatix Server port, required
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
      self._port = DEFAULT_LOCOMATIX_PORT
    else:
      self._port = port
    self._timeout = timeout
    self._retry = retry
    self._conn = None
    self._open()
  
  def close(self):
    """Closes the connection with the remote Locomatix server."""
    self._conn.close()
  
  def list_feeds(self, start_key=DEFAULT_FETCH_STARTKEY, \
                        fetch_size=DEFAULT_FETCH_SIZE):
    """Get all the existing feeds for a custid.
    
    Args:
      start_key: the index of the first feed to return in a batch, optional
        default = ""
      fetch_size: number of feeds to return in a batch, optional
        default = 20

    Return:
      A ListFeedsResponse object"""
    return self._request('list_feeds', start_key, fetch_size)
  
  def list_feeds_iterator(self, fetch_size=DEFAULT_FETCH_SIZE):
    """Returns an iterator over batches of feeds.

    Args:
      fetch_size: number of feeds to return in a batch, optional
        default = 20

    Return:
      An iterator over batches of feeds"""
    return self._list_feeds_iterator(fetch_size)
  
  def create_object(self, objectid, feed, name_values={}, \
                    location = None, time = 0, ttl=0):
    """Creates an object.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name in which the object needs to be created, required
      name_values: a dictionary of name-value attribute pairs, optional
      location: a initial location, optional
      time: seconds since unix epoch, required if location is specified
      ttl: time validity of the location in seconds, optional if location is specified
    
    Return:
      A CreateObjectResponse object"""
    return self._request('create_object', objectid, feed, name_values, 
                         location, time, ttl)
  
  def delete_object(self, objectid, feed):
    """Delete an object.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name in which the object needs to be created, required
    
    Return:
      A DeleteObjectResponse object"""
    return self._request('delete_object', objectid, feed)
  
  def list_objects(self, feed, 
                          start_key=DEFAULT_FETCH_STARTKEY, \
                          fetch_size=DEFAULT_FETCH_SIZE):
    """List all the objects and its attributes in the feed.
    
    Args:
      feed: A feed name, required
      start_key: the key of the object to return in a batch, optional
        default = ""
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      A ListObjectsResponse object"""
    return self._request('list_objects', feed, start_key, fetch_size)
 
  def list_objects_iterator(self, feed, fetch_size=DEFAULT_FETCH_SIZE):
    """Returns an iterator over batches of objects in the given feed.
    
    Args:
      feed: A feed name, required
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      An iterator over batches of objects in the feed.  For example:
      for batch in list_objects_iterator():
        for obj in batch.objects
          # do something with the object
    """
    return self._list_objects_iterator(feed, fetch_size)
  
  def update_attributes(self, objectid, feed, name_values):
    """Update the attributes of an existing object.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name in which the object needs to be updated, required
      name_values: the new attributes to associate with the object, required
    
    Return:
      An UpdateAttributesResponse object"""
    return self._request('update_attributes', objectid, feed, name_values)
  
  def get_attributes(self, objectid, feed):
    """Get the attributes of an existing object.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
    
    Return:
      A GetAttributesResponse object"""
    return self._request('get_attributes', objectid, feed)
  
  def update_location(self, objectid, feed, location, time, 
                      name_values={}, ttl = 0):
    """Update the Location of an existing object.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      location: Location contains latitude and longitude, required
      time: seconds since unix epoch, required
      name_values: a dictionary of name-value attribute pairs, optional
      ttl: time validity of the location in seconds, optional
    
    Return:
      An UpdateLocationResponse object"""
    return self._request('update_location', objectid, feed, location, time, name_values, ttl)
  
  def get_location(self, objectid, feed, allow_expired=False):
    """Get the current location of an object.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      allow_expired: Flag to fetch the expired location if applicable, optional
    
    Return:
      A GetLocationResponse object"""
    return self._request('get_location', objectid, feed, allow_expired)
  
  def search_nearby(self, objectid, feed, objectregion, \
                          from_feed, \
                          start_key=DEFAULT_FETCH_STARTKEY, \
                          fetch_size=DEFAULT_FETCH_SIZE):
    """Search in a region near an existing object.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      objectregion : type and specification of region around the object
      from_feed: Feed to search, required
        default = [], searches only the feed of parent object
      start_key: the start key of the first object to return in a batch, optional
        default = ""
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      A SearchNearbyResponse object"""
    return self._request('search_nearby', objectid, feed, objectregion, \
                                          from_feed, start_key, fetch_size)
  
  def search_nearby_iterator(self, objectid, feed, region, \
                             from_feed, \
                             fetch_size=DEFAULT_FETCH_SIZE):
    """Iterates over batches of objects returned by the search.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      region: Region to search, required
      from_feed: Feed to search, required
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      An iterator over batches of objects returned by the search.
    """
    return self._search_nearby_iterator(objectid, feed, region, from_feed, fetch_size)
  
  def search_region(self, region, \
                        from_feed, \
                        start_key=DEFAULT_FETCH_STARTKEY, \
                        fetch_size=DEFAULT_FETCH_SIZE):
    """Search a region at a geographic location.
    
    Args:
      region : type and specification of region 
      from_feed: Feeds to search, required
        default = [], searches all feeds
      start_key: the index of the first object to return in a batch, optional
        default = ""
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      A SearchRegionResponse object"""
    return self._request('search_region', region, \
                                          from_feed, start_key, fetch_size)
  
  def search_region_iterator(self, region, \
                                   from_feed, \
                                   fetch_size=DEFAULT_FETCH_SIZE):
    """Returns an iterator over batches of search_region results.

    Args:
      region : type and specification of region 
      from_feed: Feed to search, required
        default = [], searches all feeds
      fetch_size: number of objects to return in a batch, optional
        default = 20

    Return:
      An iterator over batches of search_region results"""
    return self._search_region_iterator(region, from_feed, fetch_size)
  
  def create_zone(self, zoneid, objectid, feed, objectregion, \
                        trigger, callback, from_feed):
    """Create a Zone associated with an existing object.
    
    Args:
      zoneid: a unique ID for the new Zone, required
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      objectregion : type and specification of region around the object
      callback: type and specification for alerts to be POSTed, required
      from_feed: Feed to search, required
        default = [], monitors only the feed of the parent object
    
    Return:
      A CreateZoneResponse object"""
    return self._request('create_zone', zoneid, objectid, feed, \
                             objectregion, trigger, callback, from_feed)
  
  def get_zone(self, zoneid, objectid, feed):
    """Get the Zone definition associated with an object.
    
    Args:
      zoneid: a unique ID for the new Zone, required
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
    
    Return:
      A GetZoneResponse object"""
    return self._request('get_zone', zoneid, objectid, feed)
  
  def list_zones(self, objectid, feed,
                          start_key=DEFAULT_FETCH_STARTKEY, \
                          fetch_size=DEFAULT_FETCH_SIZE):
    """List all the Zones and its definitions associated with an object.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      start_key: the index of the first zone to return in next batch, optional
        default = ""
      fetch_size: number of zones to return in a batch, optional
        default = 20
    
    Return:
      A ListZonesResponse object"""
    return self._request('list_zones', objectid, feed, start_key, fetch_size)
  
  def list_zones_iterator(self, objectid, feed,
                                fetch_size=DEFAULT_FETCH_SIZE):
    """Returns an iterator over batches of zones associated with the object.

    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      fetch_size: number of zones to return in a batch, optional
        default = 20

    Return:
      An iterator over batches of zones associated with the object."""
    return self._list_zones_iterator(objectid, feed, fetch_size)
  
  def delete_zone(self, zoneid, objectid, feed):
    """Delete a Zone associated with an object.
    
    Args:
      zoneid: a unique ID for the new Zone, required
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
    
    Return:
      A DeleteZoneResponse object"""
    return self._request('delete_zone', zoneid, objectid, feed)
  
  def create_fence(self, fenceid, region, trigger,\
                         callback, from_feed):
    """Create a Fence at a fixed geographic location.
    
    Args:
      fenceid: a unique ID for the new Fence, required
      region : type and specification of region 
      callback: type and specification for alerts to be POSTed, required
      from_feed: Feeds to search, optional
    
    Return:
      A CreateFenceResponse object"""
    return self._request('create_fence', fenceid, region, \
                                         trigger, callback, from_feed)
  
  def get_fence(self, fenceid):
    """Get the definition of an existing Fence.
    
    Args:
      fenceid: a unique ID for the new Fence, required
    
    Return:
      A GetFenceResponse object"""
    return self._request('get_fence', fenceid)
  
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
    return self._list_fences_iterator(fetch_size)

  def delete_fence(self, fenceid):
    """Delete an existing Fence.
    
    Args:
      fenceid: a unique ID for the new Fence, required
    
    Return:
      A DeleteFenceResponse object"""
    return self._request('delete_fence', fenceid)
  
  def get_location_history(self, objectid, feed, start_time, end_time, \
                         start_key=DEFAULT_FETCH_STARTKEY, \
                         fetch_size=DEFAULT_FETCH_SIZE):
    """Get the location history of an object.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      start_time: start of the time slice to retrieve history
      end_time: end of the time slice to retrieve history
      start_key: the index of the first zone to return in a batch, optional
        default = ""
      fetch_size: number of location history to return in a batch, optional
        default = 20

    Return:
      A GetLocationHistoryResponse object"""
    return self._request('get_location_history', objectid, feed, start_time, \
                          end_time, start_key, fetch_size)
  

  def get_location_history_iterator(self, objectid, feed, start_time, end_time, \
                                    fetch_size=DEFAULT_FETCH_SIZE):
    """Returns an iterator over location history of object.

    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      start_time: start of the time slice to retrieve history
      end_time: end of the time slice to retrieve history
      fetch_size: number of zones to return in a batch, optional
        default = 20

    Return:
      An iterator over location of object"""
    return self._get_location_history_iterator(objectid, feed, start_time, end_time, fetch_size)

  def get_space_activity(self, feed, region, start_time, end_time, \
                         start_key=DEFAULT_FETCH_STARTKEY, \
                         fetch_size=DEFAULT_FETCH_SIZE):
    """Get the objects entered into the given space in a time slice
    
    Args:
      feed: A feed name, required
      region: specify the region of interest
      start_time: start of the time slice to retrieve history
      end_time: end of the time slice to retrieve history
      start_key: the index of the first zone to return in a batch, optional
        default = ""
      fetch_size: number of location history to return in a batch, optional
        default = 20

    Return:
      A GetSpaceActivityResponse object"""
    return self._request('get_space_activity', feed, region, start_time, \
                          end_time, start_key, fetch_size)
  
  def get_space_activity_iterator(self, feed, region, start_time, end_time, \
                                  fetch_size=DEFAULT_FETCH_SIZE):
    """Returns an iterator over location history of object.

    Args:
      feed: A feed name, required
      region: specifes the region of interest
      start_time: start of the time slice to retrieve history
      end_time: end of the time slice to retrieve history
      fetch_size: number of zones to return in a batch, optional
        default = 20

    Return:
      An iterator over location of object"""
    return self._get_space_activity_iterator(feed, region, start_time, end_time, fetch_size)


  #######################################################
  # private methods
  #######################################################

  def _list_feeds_iterator(self, fetch_size=DEFAULT_FETCH_SIZE, \
                            allow_error=False):
    fetch_start = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self.list_feeds(fetch_start, fetch_size)
      if not allow_error and (batch.status > httplib.OK or len(batch.feeds) == 0):
        break # there was some error or there were no results
      yield batch
      if batch.next_key == None:
        break # this is the last batch
      fetch_start = batch.next_key


  def _list_objects_iterator(self, feed, fetch_size=DEFAULT_FETCH_SIZE, \
                             allow_error=False):
    fetch_start = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self.list_objects(feed, fetch_start, fetch_size)
      if not allow_error and (batch.status > httplib.OK or len(batch.objects) == 0):
        break # there was some error or there are no results
      yield batch
      if batch.next_key == None:
        break # this is the last batch
      fetch_start = batch.next_key

  def _search_nearby_iterator(self, objectid, feed, region, \
                             from_feed, \
                             fetch_size=DEFAULT_FETCH_SIZE,
                             allow_error=False):
    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self.search_nearby(objectid, feed, region, from_feed, \
                                 start_key, fetch_size)
      if not allow_error and (batch.status > httplib.OK or len(batch.objects) == 0):
        break # there was some error or there were no results
      yield batch
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

  def _search_region_iterator(self, region, \
                                   from_feed, \
                                   fetch_size=DEFAULT_FETCH_SIZE, \
                                   allow_error=False):
    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self.search_region(region, from_feed, start_key, fetch_size)
      if not allow_error and (batch.status > httplib.OK or len(batch.objects) == 0):
        break # there was some error or there were no results
      yield batch
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

  def _list_zones_iterator(self, objectid, feed,
                                fetch_size=DEFAULT_FETCH_SIZE,
                                allow_error=False):
    fetch_start = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self.list_zones(objectid, feed, fetch_start, fetch_size)
      if not allow_error and (batch.status > httplib.OK or len(batch.zones) == 0):
        break # there was some error or there were no results
      yield batch
      if batch.next_key == None:
        break # this is the last batch
      fetch_start = batch.next_key

  def _list_fences_iterator(self, fetch_size=DEFAULT_FETCH_SIZE, allow_error=False):
    fetch_start = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self.list_fences(fetch_start, fetch_size)
      if not allow_error and (batch.status > httplib.OK or len(batch.fences) == 0):
        break # there was some error or there were no results
      yield batch
      if batch.next_key == None:
        break # this is the last batch
      fetch_start = batch.next_key

  def _get_location_history_iterator(self, objectid, feed, start_time, end_time, \
                             fetch_size=DEFAULT_FETCH_SIZE, allow_error=False):
    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self.get_location_history(objectid, feed, start_time, end_time, \
                                        start_key, fetch_size)
      if not allow_error and (batch.status > httplib.OK or len(batch.locations) == 0):
        break # there was some error or there were no results
      yield batch
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

  def _get_space_activity_iterator(self, feed, region, start_time, end_time, \
                              fetch_size=DEFAULT_FETCH_SIZE, allow_error=False):
    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self.get_space_activity(feed, region, start_time, end_time, \
                                      start_key, fetch_size)
      if not allow_error and (batch.status > httplib.OK or len(batch.objects) == 0):
        break # there was some error or there were no results
      yield batch
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

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
        response = Response(http_response, *args)
        response.request_signature = (self._host, self._port, method, uri, body)
        return response

    # request/response cycle failed after retries
    raise LocomatixRequestFailed(ex, self._host, self._port, self.__class__.__name__)
  
  def _open(self):
    if SUPPORT_TIMEOUT:
      self._conn = httplib.HTTPSConnection(self._host, self._port, \
                                           timeout=self._timeout)
    else:
      self._conn = httplib.HTTPSConnection(self._host, self._port)

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


