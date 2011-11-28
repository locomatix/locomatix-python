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
import locomatix.lql as lql
import logging
import sys, time
major, minor, micro, releaselevel, serial = sys.version_info
SUPPORT_TIMEOUT = (major >= 2 and minor >= 6)
log = logging.getLogger('locomatix')


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

  ###################################################################################
  # create_feed
  #    - creates the given feed for the customer. The feed takes as input how long
  #      the long the object will live in the feed and also how long its recent 
  #      location is valid before it expires.
  ###################################################################################
  def create_feed(self, feed, object_expiry, location_expiry, name_values={}):
    """
    Args:
      feed: The name of the feed
      object_expiry: Time duration (in seconds | forever) after which the object is deleted. 
      location_expiry: Time duration (in seconds | forever) after which the location is flushed.
      name_value: Optional name value pairs associated with the feed

    Return:
      A CreateFeedResponse object"""

    self._request('create_feed', feed, object_expiry, location_expiry, name_values)
  
  ###################################################################################
  # delete_feed
  #    - Deletes the given feed for the customer. The feed has to be empty. 
  ###################################################################################
  def delete_feed(self, feed):
    """
    Args:
      feed: The name of the feed

    Return:
      A DeleteFeedResponse object"""

    self._request('delete_feed', feed)
  
  ###################################################################################
  # list_feeds
  #    - List all the feeds created by the customer/custid
  ###################################################################################
  def list_feeds(self, fetch_size=DEFAULT_FETCH_SIZE):
    """
    Args:
      fetch_size: number of feeds to return in a batch, optional
        default = 20

    Return:
      An LxFeed object"""

    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self._request('list_feeds', start_key, fetch_size)
      for feed in batch.feeds:
        yield feed
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

  ###################################################################################
  # create_object
  #    - create an object in the feed
  ###################################################################################
  def create_object(self, objectid, feed, name_values={}, \
                    location = None, time = 0):
    """
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name in which the object needs to be created, required
      name_values: a dictionary of name-value attribute pairs, optional
      location: a initial location, optional
      time: seconds since unix epoch, required if location is specified
    
    Return:
      Nothing"""

    self._request('create_object', objectid, feed, name_values, location, time)

  ###################################################################################
  # create_object_location
  #    - create an object in the feed and append a location with name value pairs
  ###################################################################################
  def create_object_location(self, objectid, feed, location, time, lname_values = {}):
    """
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name in which the object needs to be created, required
      location: a initial location, required
      time: seconds since unix epoch, required 
      name_values: a dictionary of location name-value attribute pairs, optional
    
    Return:
      Nothing"""

    # Create the object
    self._request('create_object', objectid, feed, dict(), None, 0)

    # Now update the location
    self._request('update_location', objectid, feed, location, time, lname_values)
  
  ###################################################################################
  # delete_object
  #    - Delete the given object from the feed.
  ##################################################################################
  def delete_object(self, objectid, feed):
    """
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name in which the object needs to be created, required
    
    Return:
      Nothing"""

    self._request('delete_object', objectid, feed)

  ###################################################################################
  # list_objects
  #    - List all the object and their profiles in a feed. Returns all the objects
  #      in the feed one by one.
  ##################################################################################
  def list_objects(self, feed, fetch_size=DEFAULT_FETCH_SIZE):
    """
    Args:
      feed: A feed name, required
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      An LxObject object"""

    # First, form the query
    if not isinstance(feed, str) and not isinstance(feed, unicode):
      raise EXCEPTIONS['InvalidFeed']

    query = lql.SelectObject(feed)
    for obj in self._list_objects(query, fetch_size):
      yield obj

  ###################################################################################
  # query_objects
  #    - Query objects and their profiles in a feed. Returns those objects that 
  #      satisfy the query.
  ##################################################################################
  def query_objects(self, query, fetch_size=DEFAULT_FETCH_SIZE):
    """
    Args:
      query: A query, required
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      An LxObject or LxAggregate object"""

    if not isinstance(query, lql.Query):
      raise EXCEPTIONS['InvalidQuery']

    for obj in self._list_objects(query, fetch_size):
      yield obj

  ###################################################################################
  # update_attributes
  #    - updates the attributes of the object. Note that the new set of
  #      of attributes completely replace the old set of attributes.
  ##################################################################################
  def update_attributes(self, objectid, feed, name_values):
    """
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name in which the object needs to be updated, required
      name_values: the new attributes to associate with the object, required
    
    Return:
      Nothing"""

    self._request('update_attributes', objectid, feed, name_values)

  ###################################################################################
  # get_attributes
  #    - get the attributes of an object - only the object profile. 
  ##################################################################################
  def get_attributes(self, objectid, feed):
    """
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
    
    Return:
      A LxObject object"""

    response = self._request('get_attributes', objectid, feed)
    return response.object
  
  ###################################################################################
  # update_location
  #    - appends a location (or location profile) to an object. This does not mean
  #      the old location is deleted. It just merely indicates that the location has
  #      changed and the current location is the one being updated. The life time of
  #      the location depends on the location expiry parameter set in the feed. Once
  #      the location expires the current location of the object is not known until
  #      a new location is provided. The expired location is flushed into the disk.
  ###################################################################################
  def update_location(self, objectid, feed, location, time, name_values={}):
    """
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      location: Location contains latitude and longitude, required
      time: seconds since unix epoch, required
      name_values: a dictionary of name-value attribute pairs, optional
    
    Return:
      Nothing"""

    self._request('update_location', objectid, feed, location, time, name_values)
  
  ###################################################################################
  # get_location
  #    - get the last known and non expired location of an object. If a flag is 
  #      supplied you can get the recent expired location as well. 
  ###################################################################################
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
  
  ###################################################################################
  # search_nearby
  #    - search nearby the last known location of the given object. The search returns
  #      results only if location of the object is expired.
  ###################################################################################
  def search_nearby(self, objectid, feed, objectregion, from_feed, \
                            fetch_size = DEFAULT_FETCH_SIZE):
    """
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      objectregion : type and specification of region around the object
      from_feed: Feed to get objects from
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      Multiple LxObjectLocation or a LxAggregate"""

    if not isinstance(from_feed, str) and not instance(from_feed, unicode):
      raise EXCEPTIONS['InvalidFromFeed']

    query = lql.SelectObjectLocation(from_feed)
    for obj in self._search_nearby(objectid, feed, objectregion, query, fetch_size):
      yield obj

  ###################################################################################
  # query_search_nearby
  #    - search nearby the last known location of the given object. The search returns
  #      results only if location of the object is expired.
  ###################################################################################
  def query_search_nearby(self, objectid, feed, objectregion, query, \
                            fetch_size = DEFAULT_FETCH_SIZE):
    """
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      objectregion : type and specification of region around the object
      query: LQL to execute
      fetch_size: number of objects to return in a batch, optional
        default = 20
    
    Return:
      Multiple LxObjectLocation or a LxAggregate"""

    if not isinstance(query, lql.Query):
      raise EXCEPTIONS['InvalidQuery']

    for obj in self._search_nearby(objectid, feed, objectregion, query, fetch_size):
      yield obj

  ###################################################################################
  # search_region
  #    - search the objects in a given region. The search returns results from those 
  #      objects whose location have not been expired.
  ###################################################################################
  def search_region(self, region, from_feed, fetch_size=DEFAULT_FETCH_SIZE):
    """
    Args:
      region : type and specification of region 
      from_feed: The feed to search
      fetch_size: Number of objects to return in a batch, optional
        default = 20
    
    Return:
      Multiple LxObjectLocation or a LxAggregate"""

    if not isinstance(from_feed, str) and not isinstance(from_feed, unicode):
      raise EXCEPTIONS['InvalidFromFeed']
    
    query = lql.SelectObjectLocation(from_feed)
    for obj in self._search_region(region, query, fetch_size):
      yield obj

  ###################################################################################
  # query_search_region
  #    - query for the objects in a given region. The search returns results from those 
  #      objects whose location have not been expired.
  ###################################################################################
  def query_search_region(self, region, query, fetch_size=DEFAULT_FETCH_SIZE):
    """
    Args:
      region : type and specification of region 
      from_feed: The feed to search
      fetch_size: Number of objects to return in a batch, optional
        default = 20
    
    Return:
      Multiple LxObjectLocation or a LxAggregate"""

    if not isinstance(query, lql.Query):
      raise EXCEPTIONS['InvalidQuery']
    
    for obj in self._search_region(region, query, fetch_size):
      yield obj

  ###################################################################################
  # create_zone
  #    - Create a circular zone around an existing object
  ###################################################################################
  def create_zone(self, zoneid, objectid, feed, region, \
                  trigger, callback, from_feed, name_values={}, deactivate=False, once=False):
    """
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

    if not isinstance(from_feed, str) and not isinstance(from_feed, unicode):
      raise EXCEPTIONS['InvalidFromFeed']

    if not isinstance(region, LocomatixRegion):
      raise EXCEPTIONS['InvalidRegion']

    if isinstance(region, Point):
      raise EXCEPTIONS['InvalidRegion']


    query = lql.From(from_feed)
    self._request('create_zone', zoneid, objectid, feed, \
                    region, trigger, callback, query, name_values, deactivate, once)

  ###################################################################################
  # create_smart_zone
  #    - Create a smart circular zone around an existing object with a query
  ###################################################################################
  def create_smart_zone(self, zoneid, objectid, feed, region, \
                  trigger, callback, query, name_values={}, deactivate=False, once=False):
    """
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

    if not isinstance(query, lql.Query):
      raise EXCEPTIONS['InvalidQuery']

    if not isinstance(region, LocomatixRegion):
      raise EXCEPTIONS['InvalidRegion']

    if isinstance(region, Point):
      raise EXCEPTIONS['InvalidRegion']

    self._request('create_zone', zoneid, objectid, feed, \
                    region, trigger, callback, query._query, name_values, deactivate, once)

  ###################################################################################
  # activate_zone
  #    - Make the zone around an object active
  ###################################################################################
  def activate_zone(self, zoneid, objectid, feed):
    """
    Args:
      zoneid: a unique ID for the new Zone, required
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
    
    Return:
      Nothing"""

    self._request('activate_zone', zoneid, objectid, feed)

  ###################################################################################
  # get_zone
  #    - Get the details of the zone around the object
  ###################################################################################
  def get_zone(self, zoneid, objectid, feed):
    """
    Args:
      zoneid: a unique ID for the new Zone, required
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
    
    Return:
       An LxZone object"""

    response = self._request('get_zone', zoneid, objectid, feed)
    return response.zone
  
  ###################################################################################
  # list_zones
  #    - List all the Zones and its definitions associated with an object.
  ###################################################################################
  def list_zones(self, objectid, feed, fetch_size=DEFAULT_FETCH_SIZE):
    """
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
  
  ###################################################################################
  # deactivate_zone
  #    - Deactivate the zone associated with the object.
  ###################################################################################
  def deactivate_zone(self, zoneid, objectid, feed):
    """
    Args:
      zoneid: a unique ID for the new Zone, required
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
    
    Return:
      Nothing"""

    self._request('deactivate_zone', zoneid, objectid, feed)

  ###################################################################################
  # delete_zone
  #    - Delete the zone associate with the object
  ###################################################################################
  def delete_zone(self, zoneid, objectid, feed):
    """
    Args:
      zoneid: a unique ID for the new Zone, required
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
    
    Return:
      Nothing"""

    self._request('delete_zone', zoneid, objectid, feed)
  
  ###################################################################################
  # create_fence
  #    - Create a fence around a geographical region. The fence can be either circle
  #      rectangle or arbitrary polygon.
  ###################################################################################
  def create_fence(self, fenceid, region, trigger,\
                         callback, from_feed, name_values={}, deactivate=False, once=False):
    """
    Args:
      fenceid: a unique ID for the new Fence, required
      region : type and specification of region 
      callback: type and specification for alerts to be POSTed, required
      from_feed: feed to search, required
      name_values: a dictionary of name-value attribute pairs, optional
    
    Return:
      Nothing"""

    if not isinstance(from_feed, str) and not isinstance(from_feed, unicode):
      raise EXCEPTIONS['InvalidFromFeed']

    if not isinstance(region, LocomatixRegion):
      raise EXCEPTIONS['InvalidRegion']

    if isinstance(region, Point):
      raise EXCEPTIONS['InvalidRegion']

    query = lql.From(from_feed)
    self._request('create_fence', fenceid, region, \
          trigger, callback, query, name_values, deactivate, once)

  ###################################################################################
  # create_smart_fence
  #    - Create a smart fence around a geographical region with a query. The fence 
  #      can be either a circle, rectangle or arbitrary polygon.
  ###################################################################################
  def create_smart_fence(self, fenceid, region, trigger,\
                         callback, query, name_values={}, deactivate=False, once=False):
    """
    Args:
      fenceid: a unique ID for the new Fence, required
      region : type and specification of region 
      callback: type and specification for alerts to be POSTed, required
      query: LQL query to execute, required
      name_values: a dictionary of name-value attribute pairs, optional
    
    Return:
      Nothing"""

    if not isinstance(query, lql.Query):
      raise EXCEPTIONS['InvalidFromFeed']

    if not isinstance(region, LocomatixRegion):
      raise EXCEPTIONS['InvalidRegion']

    if isinstance(region, Point):
      raise EXCEPTIONS['InvalidRegion']

    self._request('create_fence', fenceid, region, \
          trigger, callback, query._query, name_values, deactivate, once)

  ###################################################################################
  # activate_fence
  #    - Make the fence around a geographical region active
  ###################################################################################
  def activate_fence(self, fenceid):
    """Activate an existing Fence.
    
    Args:
      fenceid: a unique ID for the new Fence, required
    
    Return:
      Nothing"""

    self._request('activate_fence', fenceid)

  ###################################################################################
  # get_fence
  #    - Get the details of the fence around a geographical region
  ###################################################################################
  def get_fence(self, fenceid):
    """Get the definition of an existing Fence.
    
    Args:
      fenceid: a unique ID for the new Fence, required
    
    Return:
      A LxFence object"""

    response = self._request('get_fence', fenceid)
    return response.fence
  
  ###################################################################################
  # list_fences
  #    - Fetch all the fences and their definitions.
  ###################################################################################
  def list_fences(self, fetch_size=DEFAULT_FETCH_SIZE):
    """
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
  
  ###################################################################################
  # deactivate_fence
  #    - Deactivate the fence around a geographical region
  ###################################################################################
  def deactivate_fence(self, fenceid):
    """
    Args:
      fenceid: a unique ID for the new Fence, required
    
    Return:
      Nothing"""

    self._request('deactivate_fence', fenceid)

  ###################################################################################
  # delete_fence
  #    - Delete the fence around a geographical region
  ###################################################################################
  def delete_fence(self, fenceid):
    """
    Args:
      fenceid: a unique ID for the new Fence, required
    
    Return:
      Nothing"""

    self._request('delete_fence', fenceid)

  ###################################################################################
  # get_location_history
  #    - Get the location history profile of an object in a feed. Returns the location
  #      profiles of the object between the times.
  ##################################################################################
  def get_location_history(self, objectid, feed, start_time, end_time, \
                         fetch_size=DEFAULT_FETCH_SIZE):
    """
    Args:
      objectid: Key that uniquely identifes the object within the feed, required
      feed: Feed name that contains the object, required
      start_time: start of the time slice to retrieve history
      end_time: end of the time slice to retrieve history
      fetch_size: number of location history to return in a batch, optional
        default = 20

    Return:
      Multiple LxObjectLocation or a LxAggregate"""

    if not isinstance(objectid, str) and not isinstance(objectid, unicode):
      raise EXCEPTIONS['InvalidObjectID']

    if not isinstance(feed, str) and not isinstance(feed, unicode):
      raise EXCEPTIONS['InvalidFeed']

    query = lql.SelectLocation(feed, objectid)
    for loc in self._get_location_history(query, start_time, end_time, fetch_size):
      yield loc

  ###################################################################################
  # query_location_history
  #    - Get the location history profile of an object in a feed. Returns the location
  #      profiles of the object that satisfies the query and between the times.
  ##################################################################################
  def query_location_history(self, query, start_time, end_time, fetch_size=DEFAULT_FETCH_SIZE): 
    """
    Args:
      query: Query for the fetching the location history
      start_time: start of the time slice to retrieve history
      end_time: end of the time slice to retrieve history
      fetch_size: number of location history to return in a batch, optional
        default = 20

    Return:
      Multiple LxObjectLocation or a LxAggregate"""

    if not isinstance(query, lql.Query):
      raise EXCEPTIONS['InvalidQuery']

    for loc in self._get_location_history(query, start_time, end_time, fetch_size):
      yield loc

  ###################################################################################
  # get_space_activity
  #    - Get the location profile of objects in the feed within the given area and 
  #      time.  Returns the location profiles of objects. 
  ##################################################################################
  def get_space_activity(self, feed, region, start_time, end_time, \
                         fetch_size=DEFAULT_FETCH_SIZE):
    """
    Args:
      feed: A feed name, required
      region: specify the region of interest
      start_time: start of the time slice to retrieve history
      end_time: end of the time slice to retrieve history
      fetch_size: number of location history to return in a batch, optional
        default = 20

    Return:
      Multiple LxObjectLocation """

    if not isinstance(feed, str) and not isinstance(feed, unicode):
      raise EXCEPTIONS['InvalidFeed']

    if not isinstance(region, LocomatixRegion):
      raise EXCEPTIONS['InvalidRegion']

    if isinstance(region, Point):
      raise EXCEPTIONS['InvalidRegion']

    query = lql.SelectLocation(feed)
    for loc in self._get_space_activity(query, region, start_time, end_time, fetch_size):
      yield loc

  ###################################################################################
  # query_space_activity
  #    - Get the location profile of objects in the feed within the given area and 
  #      time.  Returns the location profiles of objects that satisfies the query 
  #      and between the times.
  ##################################################################################
  def query_space_activity(self, query, region, start_time, end_time, \
                           fetch_size=DEFAULT_FETCH_SIZE):
    """
    Args:
      query: An LQL query, required
      region: specify the region of interest, required
      start_time: start of the time slice to retrieve history, required.
      end_time: end of the time slice to retrieve history, required
      fetch_size: number of location history to return in a batch, optional
        default = 20

    Return:
      Multiple LxObjectLocation """

    if not isinstance(query, lql.Query):
      raise EXCEPTIONS['InvalidQuery']

    if not isinstance(region, LocomatixRegion):
      raise EXCEPTIONS['InvalidRegion']

    if isinstance(region, Point):
      raise EXCEPTIONS['InvalidRegion']

    for loc in self._get_space_activity(query, region, start_time, end_time, fetch_size):
      yield loc

  ###################################################################################
  # get_histogram 
  #    - Get the count distribution of objects within a specified region and time.
  #      Returns a list of grids and their counts.
  ##################################################################################
  def get_histogram(self, feed, bbox, nhslices, nvslices, etime):
    """
    Args:
      feed: A feed name, required
      bbox: A bounding box that specifies the space of interest 
      nhslices: No. of slices to divide the bbox horizontaly 
      nvslices: No. of slices to divide the bbox vertically 
      etime: earliest time of the objects in the space to include

    Return:
      A list of grid counts"""

    if not isinstance(feed, str) and not isinstance(feed, unicode):
      raise EXCEPTIONS['InvalidFeed']

    if not isinstance(bbox, Rectangle):
      raise EXCEPTIONS['InvalidRegion']

    query = lql.SelectCountLocation(feed)
    response = self._request('get_histogram', query._query, bbox, nhslices, nvslices, etime)
    return response.grid_aggregates

  ###################################################################################
  # query_histogram 
  #    - Get any distribution of objects specified by query within a specified region 
  #      and time. Returns a list of grids and their counts.
  ##################################################################################
  def query_histogram(self, query, bbox, nhslices, nvslices, etime):
    """
    Args:
      query: An LQL query, required
      bbox: A bounding box that specifies the space of interest 
      nhslices: No. of slices to divide the bbox horizontaly 
      nvslices: No. of slices to divide the bbox vertically 
      etime: earliest time of the objects in the space to include

    Return:
      A list of grid aggregates"""

    if not isinstance(query, lql.Query):
      raise EXCEPTIONS['InvalidQuery']

    response = self._request('get_histogram', query._query, bbox, nhslices, nvslices, etime)
    return response.grid_aggregates

  #######################################################
  # Private helper function for list/query objects
  #######################################################
  def _list_objects(self, query, fetch_size):
    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self._request('list_objects', query._query, start_key, fetch_size)
      if len(batch.aggrs) == 0:
        for obj in batch.objects:
          yield obj
      else:
        for aggr in batch.aggrs:
          yield aggr
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

  #######################################################
  # Private helper function for get/query location history
  #######################################################
  def _get_location_history(self, query, start_time, end_time, fetch_size): 
    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self._request('get_location_history', query._query, start_time, \
                            end_time, start_key, fetch_size)
      if len(batch.aggrs) == 0:
        for location in batch.locations:
          yield location
      else:
        for aggr in batch.aggrs:
          yield aggr
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

  #######################################################
  # Private helper function for get/query space activity
  #######################################################
  def _get_space_activity(self, query, region, start_time, end_time, fetch_size):
    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self._request('get_space_activity', query._query, region, start_time, \
                            end_time, start_key, fetch_size)
      if len(batch.aggrs) == 0:
        for objloc in batch.objlocs:
          yield objloc
      else:
        for aggr in batch.aggrs:
          yield aggr
      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

  #######################################################
  # Private helper function for get/query search nearby
  #######################################################
  def _search_nearby(self, objectid, feed, objectregion, query, fetch_size):
    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self._request('search_nearby', objectid, feed, objectregion, query._query, \
                                 start_key, fetch_size)
      if len(batch.aggrs) == 0:
        for objloc in batch.objlocs:
          yield objloc
      else:
        for aggr in batch.aggrs:
          yield aggr

      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key

  #######################################################
  # Private helper function for get/query search region
  #######################################################
  def _search_region(self, region, query, fetch_size):
    start_key = DEFAULT_FETCH_STARTKEY
    while True:
      batch = self._request('search_region', region, query._query, start_key, fetch_size)
      if len(batch.aggrs) == 0:
        for objloc in batch.objlocs:
          yield objloc
      else:
        for aggr in batch.aggrs:
          yield aggr

      if batch.next_key == None:
        break # this is the last batch
      start_key = batch.next_key
  

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
      self._conn = httplib.HTTPSConnection(self._host, self._port, \
                                           timeout=self._timeout)
    else:
      self._conn = httplib.HTTPSConnection(self._host, self._port)

    try:
      self._conn.connect()
    except Exception, ex:
      raise ConnectionFailure(ex, self._host, self._port)

    return # the connection was successful
