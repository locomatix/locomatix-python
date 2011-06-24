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
from exceptions import *
import locomatix.logger as logger
import logging
import sys, time
major, minor, micro, releaselevel, serial = sys.version_info
SUPPORT_TIMEOUT = (major >= 2 and minor >= 6)
log = logging.getLogger('locomatix')

lql_detected = False
try: 
  import lql 
  lql_detected = True
except ImportError:
  pass

try: import simplejson as json
except ImportError:
  try: import json
  except ImportError:
    raise ImportError("simplejson is not installed. Please download it from http://code.google.com/p/simplejson/")

REQUEST_RESPONSES = {
  'create_feed':         (CreateFeedRequest,         CreateFeedResponse),
  'delete_feed':         (DeleteFeedRequest,         DeleteFeedResponse),
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
  'activate_zone':       (ActivateZoneRequest,       ActivateZoneResponse),
  'get_zone':            (GetZoneRequest,            GetZoneResponse),
  'list_zones':          (ListZonesRequest,          ListZonesResponse),
  'deactivate_zone':     (DeactivateZoneRequest,     DeactivateZoneResponse),
  'delete_zone':         (DeleteZoneRequest,         DeleteZoneResponse),
  'create_fence':        (CreateFenceRequest,        CreateFenceResponse),
  'activate_fence':      (ActivateFenceRequest,      ActivateFenceResponse),
  'get_fence':           (GetFenceRequest,           GetFenceResponse),
  'list_fences':         (ListFencesRequest,         ListFencesResponse),
  'deactivate_fence':    (DeactivateFenceRequest,    DeactivateFenceResponse),
  'delete_fence':        (DeleteFenceRequest,        DeleteFenceResponse),
  'get_location_history':(GetLocationHistoryRequest, GetLocationHistoryResponse),
  'get_space_activity':  (GetSpaceActivityRequest,   GetSpaceActivityResponse),
  'get_histogram':       (GetHistogramRequest,       GetHistogramResponse),
}

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
    self._response_metadata = None
    self._response_body = None
    self._total_time = 0.0
    self._open()
  
  def close(self):
    """Closes the connection with the remote Locomatix server."""
    self._conn.close()
  
  def response_metadata(self):
    return self._response_metadata

  def response_body(self):
    return self._response_body

  def create_feed(self, feed, name_values={}):
    """Create a feed.
    
    Args:
      feed: The name of the feed
      name_value: Optional name value pairs associated with the feed

    Return:
      A CreateFeedResponse object"""

    self._request('create_feed', feed, name_values)
  
  def delete_feed(self, feed):
    """Delete a feed.
    
    Args:
      feed: The name of the feed

    Return:
      A DeleteFeedResponse object"""

    self._request('delete_feed', feed)
  
  def list_feeds(self, fetch_size=DEFAULT_FETCH_SIZE):
    """Get all the existing feeds for a custid.
    
    Args:
      fetch_size: number of feeds to return in a batch, optional
        default = 20

    Return:
      A ListFeedsResponse object"""

    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self._request('list_feeds', start_key, fetch_size)
      for feed in batch.feeds:
        yield feed
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

  
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
      Nothing"""

    self._request('create_object', objectid, feed, name_values, location, time, ttl)
  
  def delete_object(self, objectid, feed):
    """Delete an object.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name in which the object needs to be created, required
    
    Return:
      Nothing"""

    self._request('delete_object', objectid, feed)

  def list_objects(self, feed, fetch_size=DEFAULT_FETCH_SIZE):
    """List all the objects and its attributes in the feed.
    
    Args:
      feed: A feed name, required
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      An LxObject object"""

    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self._request('list_objects', feed, start_key, fetch_size)
      for obj in batch.objects:
        yield obj
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

 
  def update_attributes(self, objectid, feed, name_values):
    """Update the attributes of an existing object.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name in which the object needs to be updated, required
      name_values: the new attributes to associate with the object, required
    
    Return:
      Nothing"""

    self._request('update_attributes', objectid, feed, name_values)

  def get_attributes(self, objectid, feed):
    """Get the attributes of an existing object.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
    
    Return:
      A LxObject object"""

    response = self._request('get_attributes', objectid, feed)
    return response.object
  
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
      Nothing"""

    self._request('update_location', objectid, feed, location, time, name_values, ttl)
  
  def get_location(self, objectid, feed, allow_expired=False):
    """Get the current location of an object.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      allow_expired: Flag to fetch the expired location if applicable, optional
    
    Return:
      An LxLocation object"""

    response = self._request('get_location', objectid, feed, allow_expired)
    return response.location
  
  def search_nearby(self, objectid, feed, objectregion, \
                          from_feed, fetch_size=DEFAULT_FETCH_SIZE):
    """Search in a region near an existing object.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      objectregion : type and specification of region around the object
      from_feed: Feed to search, required
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      Multiple LxObjectLocation """

    start_key = DEFAULT_FETCH_STARTKEY
    predicate = self._lql_query(from_feed)
    while True:
      batch = self._request('search_nearby', objectid, feed, objectregion, predicate, \
                                 start_key, fetch_size)
      for objloc in batch.objlocs:
        yield objloc
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

  
  def search_region(self, region, from_feed, \
                        fetch_size=DEFAULT_FETCH_SIZE):
    """Search a region at a geographic location.
    
    Args:
      region : type and specification of region 
      from_feed: Feed to search, required
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      Multiple LxObjectLocation """

    start_key = DEFAULT_FETCH_STARTKEY
    predicate = self._lql_query(from_feed)
    while True:
      batch = self._request('search_region', region, predicate, start_key, fetch_size)
      for objloc in batch.objlocs:
        yield objloc
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key
  
  def create_zone(self, zoneid, objectid, feed, region, \
                  trigger, callback, from_feed, name_values={}, deactivate=False, once=False):
    """Create a Zone associated with an existing object.
    
    Args:
      zoneid: a unique ID for the new Zone, required
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      region : type and specification of region around the object
      callback: type and specification for alerts to be POSTed, required
      from_feed: feed to search, required
      name_values: a dictionary of name-value attribute pairs, optional
      deactivate: indicate whether to deactivate 
    
    Return:
      Nothing"""

    self._request('create_zone', zoneid, objectid, feed, \
                       region, trigger, callback, self._lql_query_zone(from_feed), name_values, deactivate, once)

  def activate_zone(self, zoneid, objectid, feed):
    """Activate a Zone associated with an object.
    
    Args:
      zoneid: a unique ID for the new Zone, required
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
    
    Return:
      Nothing"""

    self._request('activate_zone', zoneid, objectid, feed)

  def get_zone(self, zoneid, objectid, feed):
    """Get the Zone definition associated with an object.
    
    Args:
      zoneid: a unique ID for the new Zone, required
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
    
    Return:
       An LxZone object"""

    response = self._request('get_zone', zoneid, objectid, feed)
    return response.zone
  
  def list_zones(self, objectid, feed, fetch_size=DEFAULT_FETCH_SIZE):
    """List all the Zones and its definitions associated with an object.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      fetch_size: number of zones to return in a batch, optional
        default = 20
    
    Return:
      Multiple LxZone objects"""

    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self._request('list_zones', objectid, feed, start_key, fetch_size)
      for zone in batch.zones:
        yield zone
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key
  
  def deactivate_zone(self, zoneid, objectid, feed):
    """Deactivate a Zone associated with an object.
    
    Args:
      zoneid: a unique ID for the new Zone, required
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
    
    Return:
      Nothing"""

    self._request('deactivate_zone', zoneid, objectid, feed)

  def delete_zone(self, zoneid, objectid, feed):
    """Delete a Zone associated with an object.
    
    Args:
      zoneid: a unique ID for the new Zone, required
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
    
    Return:
      Nothing"""

    self._request('delete_zone', zoneid, objectid, feed)
  
  def create_fence(self, fenceid, region, trigger,\
                         callback, from_feed, name_values={}, deactivate=False, once=False):
    """Create a Fence at a fixed geographic location.
    
    Args:
      fenceid: a unique ID for the new Fence, required
      region : type and specification of region 
      callback: type and specification for alerts to be POSTed, required
      from_feed: feed to search, required
      name_values: a dictionary of name-value attribute pairs, optional
    
    Return:
      Nothing"""

    self._request('create_fence', fenceid, region, \
          trigger, callback, self._lql_query_fence(from_feed), name_values, deactivate, once)

  def activate_fence(self, fenceid):
    """Activate an existing Fence.
    
    Args:
      fenceid: a unique ID for the new Fence, required
    
    Return:
      Nothing"""

    self._request('activate_fence', fenceid)

  def get_fence(self, fenceid):
    """Get the definition of an existing Fence.
    
    Args:
      fenceid: a unique ID for the new Fence, required
    
    Return:
      A LxFence object"""

    response = self._request('get_fence', fenceid)
    return response.fence
  
  def list_fences(self, fetch_size=DEFAULT_FETCH_SIZE):
    """Get the definition of all existing Fences.
    
    Args:
      fetch_size: number of zones to return in a batch, optional
        default = 20

    Return:
      Multiple LxFence objects"""

    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self._request('list_fences', start_key, fetch_size)
      for fence in batch.fences:
        yield fence
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key
  
  def deactivate_fence(self, fenceid):
    """Deactivate an existing Fence.
    
    Args:
      fenceid: a unique ID for the new Fence, required
    
    Return:
      Nothing"""

    self._request('deactivate_fence', fenceid)

  def delete_fence(self, fenceid):
    """Delete an existing Fence.
    
    Args:
      fenceid: a unique ID for the new Fence, required
    
    Return:
      Nothing"""

    self._request('delete_fence', fenceid)

  def get_location_history(self, objectid, feed, start_time, end_time, \
                         fetch_size=DEFAULT_FETCH_SIZE):
    """Get the location history of an object.
    
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      start_time: start of the time slice to retrieve history
      end_time: end of the time slice to retrieve history
      fetch_size: number of location history to return in a batch, optional
        default = 20

    Return:
      Multiple LxLocation """

    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self._request('get_location_history', objectid, feed, start_time, end_time, \
                                        start_key, fetch_size)
      for location in batch.locations:
        yield location
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key
  
  def get_space_activity(self, feed, region, start_time, end_time, \
                         fetch_size=DEFAULT_FETCH_SIZE):
    """Get the objects entered into the given space in a time slice
    
    Args:
      feed: A feed name, required
      region: specify the region of interest
      start_time: start of the time slice to retrieve history
      end_time: end of the time slice to retrieve history
      fetch_size: number of location history to return in a batch, optional
        default = 20

    Return:
      Multiple LxObjectLocation """

    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self._request('get_space_activity', feed, region, start_time, end_time, \
                                      start_key, fetch_size)
      for objloc in batch.objlocs:
        yield objloc
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key
  
  def get_histogram(self, feed, bbox, nhslices, nvslices, etime):
    """Get the distribution of objects in a space from the given etime

    Args:
      feed: A feed name, required
      bbox: A bounding box that specifies the space of interest 
      nhslices: No. of slices to divide the bbox horizontaly 
      nvslices: No. of slices to divide the bbox vertically 
      etime: earliest time of the objects in the space to include

    Return:
      A list of grid counts"""

    response = self._request('get_histogram', feed, bbox, nhslices, nvslices, etime)
    return response.grid_counts

  #######################################################
  # private methods
  #######################################################

  def _lql_query(self, sorq):
    predicate = None

    if isinstance(sorq, str):
      predicate = 'FROM ' + sorq if len(sorq) > 0 else ''
    elif lql_detected:
      if isinstance(sorq, lql.LqlQuery):
        predicate = sorq._query

    return predicate

  def _lql_query_fence(self, sorq):
    predicate = None

    if isinstance(sorq, str):
      predicate = 'FROM ' + sorq if len(sorq) > 0 else ''
    elif lql_detected:
      if isinstance(sorq, lql.LqlQueryFence):
        predicate = sorq._query

    return predicate

  def _lql_query_zone(self, sorq):
    predicate = None

    if isinstance(sorq, str):
      predicate = 'FROM ' + sorq if len(sorq) > 0 else ''
    elif lql_detected:
      if isinstance(sorq, lql.LqlQueryZone):
        predicate = sorq._query

    return predicate

  def _request(self, request_type, *args):
    Request, Response = REQUEST_RESPONSES[request_type]
    method, uri, body = Request(*args).dump()
    log.log(logger.REQUEST, 'Request:\n%s http://%s:%s%s' % (method, self._host, self._port , uri))
    if body != '':
      log.log(logger.REQUEST, 'body: %s' % body)

    # Note the request start time
    starttime = time.time()

    # try the request response cycle retry times
    for i in range(self._retry):
      try:
        self._conn.request(method, uri, body, self._http_headers)
        http_response = self._conn.getresponse()
      except Exception, ex:
        self._conn.close()
        time.sleep(1)
        self._open()
        continue
      else:
        # got a response, no connection problems
        response = Response(http_response)
        response.request_signature = (self._host, self._port, method, uri, body)

        # Note the request end time
        endtime = time.time()

        # Now set the response meta data and response body
        self._response_metadata = response.get_metadata()
  
        # Include the total time - network + server execution
        response.body['TotalTime'] = str((endtime-starttime)*1000)  
        self._response_metadata._total_time = str((endtime-starttime)*1000)  
        self._response_body = json.dumps(response.body, indent=4) 

        if self._response_metadata.message != 'Success': 
          raise EXCEPTIONS[self._response_metadata.message]
        return response 

    # request/response cycle failed after retries
    self._response_metadata = None
    raise RequestFailed(ex, self._host, self._port, self.__class__.__name__)
  
  def _open(self):
    if SUPPORT_TIMEOUT:
      self._conn = httplib.HTTPSConnection(self._host, self._port)
    else:
      self._conn = httplib.HTTPSConnection(self._host, self._port)

    try:
      self._conn.connect()
    except Exception, ex:
      raise ConnectionFailure(ex, self._host, self._port)

    return # the connection was successful
