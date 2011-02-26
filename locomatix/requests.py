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
from region import LocomatixRegion
from callback import LocomatixCallback


ROUTE_SIGNATURES = {
  'ListFeeds':          ( 'GET',    '/feed/List.json',                          None     ),
  'CreateObject':       ( 'POST',   '/feed/%s/object/Create.json',              ['feed'] ),
  'DeleteObject':       ( 'DELETE', '/feed/%s/object/Delete.json',              ['feed'] ),
  'ListObjects':        ( 'GET',    '/feed/%s/ListObjects.json',                ['feed'] ),
  'GetAttributes':      ( 'GET',    '/feed/%s/object/GetAttributes.json',       ['feed'] ),
  'UpdateAttributes':   ( 'PUT',    '/feed/%s/object/UpdateAttributes.json',    ['feed'] ),
  'GetLocation':        ( 'GET',    '/feed/%s/object/GetLocation.json',         ['feed'] ),
  'UpdateLocation':     ( 'PUT',    '/feed/%s/object/UpdateLocation.json',      ['feed'] ),
  'SearchRegion':       ( 'GET',    '/search/Region.json',                      None     ),
  'SearchNearby':       ( 'GET',    '/search/NearbyObject.json',                None     ),
  'CreateZone':         ( 'POST',   '/zone/%s/Create.json',                     ['feed'] ),
  'ActivateZone':       ( 'POST',   '/zone/%s/Activate.json',                   ['feed'] ),
  'GetZone':            ( 'GET',    '/zone/%s/Get.json',                        ['feed'] ),
  'ListZones':          ( 'GET',    '/zone/%s/List.json',                       ['feed'] ),
  'DeactivateZone':     ( 'POST',   '/zone/%s/DeActivate.json',                 ['feed'] ),
  'DeleteZone':         ( 'DELETE', '/zone/%s/Delete.json',                     ['feed'] ),
  'CreateFence':        ( 'POST',   '/fence/Create.json',                       None     ),
  'ActivateFence':      ( 'POST',   '/fence/Activate.json',                     None     ),
  'GetFence':           ( 'GET',    '/fence/Get.json',                          None     ),
  'ListFences':         ( 'GET',    '/fence/List.json',                         None     ),
  'DeactivateFence':    ( 'POST',   '/fence/DeActivate.json',                   None     ),
  'DeleteFence':        ( 'DELETE', '/fence/Delete.json',                       None     ),
  'GetLocationHistory': ( 'GET',    '/analytics/feed/%s/object/Trail.json',     ['feed'] ),
  'GetSpaceActivity':   ( 'GET',    '/analytics/feed/%s/SpaceActivity.json',    ['feed'] )
}

class LocomatixRequest(object):
  """An abstract request object from which all API requests will be derived.
  
  The parent class implements all the functions necessary to retrieve the http method,
  URI, and body that must be sent to the Locomatix server.  Thus each descendent request type
  need only do two things.  1. define METHOD, URI_FORMAT, and URI_PARAMS class attributes.
  2. implement a constructor that takes whatever args are relevant for the request and 
  assembles them into a _params dictionary."""
  
  # just a convenience constant, used when an http body should be empty
  EMPTY_BODY = ""
  
  """These three class attributes define how the request gets formed into an actual http request.
  METHOD = the actual HTTP method used (GET, PUT, DELETE, POST)
  URI_FORMAT = a printf style format string used to build the uri, e.f. '/feed/%s/object/Create'
  URI_PARAMS = a list of param names that will be inserted into the URI_FORMAT"""
  METHOD, URI_FORMAT, URI_PARAMS = (None, None, None)
  
  def __init__(self, params):
    self._params = params # descendent requests should assemble args into this instance dictionary
    self._set_method()    # sets the _method instance variable
    self._set_uri()       # assembles the final uri into the _uri instance var
    self._set_body()      # assembles the body into the _body instance var
  
  def _set_method(self):
    """Sets the instance _method by simply copying the METHOD class attribute"""
    self._method = self.__class__.METHOD
  
  def _set_uri(self):
    """Inserts uri params into _uri, deletes them from the _params dictionary.
    
    If this is a GET or DELETE request, adds remaining params as query string"""
    uri_params = []
    if self.__class__.URI_PARAMS:
      for param_name in self.__class__.URI_PARAMS:
        uri_params.append(urllib.quote_plus(self._params[param_name]))
        del self._params[param_name]
    self._uri = self.__class__.URI_FORMAT % tuple(uri_params)
    if self.__class__.METHOD in ('GET','DELETE'):
      self._uri += '?' + urllib.urlencode(self._params)
  
  def _set_body(self):
    """If this is a POST or PUT request, adds params as query string to the body."""
    if self.__class__.METHOD in ('POST','PUT'):
      self._body = urllib.urlencode(self._params)
    else:
      self._body = self.__class__.EMPTY_BODY
  
  def dump(self):
    """Returns (method, uri, body) as a tuple."""
    return (self._method, self._uri, self._body)


class ListFeedsRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['ListFeeds']
  def __init__(self, start_key, fetch_size):
    params = { 'startkey' : start_key, 'fetchsize' : fetch_size }
    super(ListFeedsRequest, self).__init__(params)


class CreateObjectRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['CreateObject']
  def __init__(self, objectid, feed, name_values={}, location = None, time = 0, ttl=0):
    params = { 'feed':feed, 'oid':objectid }
    params.update(name_values)
    if location != None:
      params.update(location._params)
      params['time'] = int(time)
      if ttl != 0:
        params['ttl'] = ttl
    super(CreateObjectRequest, self).__init__(params)


class DeleteObjectRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['DeleteObject']
  def __init__(self, objectid, feed):
    params = { 'feed':feed, 'oid':objectid }
    super(DeleteObjectRequest, self).__init__(params)


class ListObjectsRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['ListObjects']
  def __init__(self, feed, start_key, fetch_size):
    params = { 'feed' : feed, 'startkey':start_key, 'fetchsize':fetch_size }
    super(ListObjectsRequest, self).__init__(params)


class GetAttributesRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['GetAttributes']
  def __init__(self, objectid, feed):
    params = { 'feed':feed, 'oid':objectid }
    super(GetAttributesRequest, self).__init__(params)


class UpdateAttributesRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['UpdateAttributes']
  def __init__(self, objectid, feed, name_values={}):
    params = { 'feed':feed, 'oid':objectid }
    params.update(name_values)
    super(UpdateAttributesRequest, self).__init__(params)


class UpdateLocationRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['UpdateLocation']
  def __init__(self, objectid, feed, location, time, name_values={}, ttl=0):
    params = { 'oid' : objectid, 'feed' : feed, 'time': int(time) }
    params.update(location._params)
    params.update(name_values)
    if ttl != 0:
      params['ttl'] = ttl
    super(UpdateLocationRequest, self).__init__(params)


class GetLocationRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['GetLocation']
  def __init__(self, objectid, feed, allow_expired):
    params = { 
      'feed' : feed, 'oid' : objectid \
    }
    if allow_expired == True:
      params['allowexpired'] = True 
    super(GetLocationRequest, self).__init__(params)


class SearchNearbyRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['SearchNearby']
  def __init__(self, objectid, feed, region, predicate, fetch_start, fetch_size):
    params = { 
      'feed' : feed, 'oid' : objectid, \
      'fetchstart':fetch_start, 'fetchsize':fetch_size, \
      'predicate':predicate \
    }
    if not isinstance(region, LocomatixRegion):
      raise ValueError("region is an invalid type (%s) - region must derive from LocomatixRegion" % type(region))
    params.update(region._params)
    super(SearchNearbyRequest, self).__init__(params)


class SearchRegionRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['SearchRegion']
  def __init__(self, region, predicate, fetch_start, fetch_size):
    params = {
      'fetchstart':fetch_start, 'fetchsize':fetch_size, \
      'predicate':predicate \
    }
    if not isinstance(region, LocomatixRegion):
      raise ValueError("Invalid region type (%s) - region must derive from LocomatixRegion" % type(region))
    params.update(region._params)
    super(SearchRegionRequest, self).__init__(params)


class CreateZoneRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['CreateZone']
  def __init__(self, zoneid, objectid, feed, region, trigger, callback, predicate, name_values={}, once=False):
    params = { 
      'zoneid' : zoneid, 'oid' : objectid, \
      'feed' : feed, 'trigger': trigger, \
      'predicate':predicate \
    }
    if once == True:
      params['onetimealert'] = True 
    if not isinstance(region, LocomatixRegion):
      raise ValueError("region is an invalid type (%s) - region must derive from LocomatixRegion" % type(region))
    params.update(region._params)
    if not isinstance(callback, LocomatixCallback):
      raise ValueError("callback is an invalid type (%s) - callback must derive from LocomatixCallback" % type(callback))
    params.update(callback._params)
    params.update(name_values)
    super(CreateZoneRequest, self).__init__(params)


class ActivateZoneRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['ActivateZone']
  def __init__(self, zoneid, objectid, feed):
    params = { 'zoneid' : zoneid, 'feed' : feed, 'oid' : objectid }
    super(ActivateZoneRequest, self).__init__(params)


class GetZoneRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['GetZone']
  def __init__(self, zoneid, objectid, feed):
    params = { 'zoneid' : zoneid, 'oid' : objectid, 'feed' : feed }
    super(GetZoneRequest, self).__init__(params)


class ListZonesRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['ListZones']
  def __init__(self, objectid, feed, start_key, fetch_size):
    params = { \
      'oid' : objectid, 'feed' : feed, \
      'startkey' : start_key, 'fetchsize' : fetch_size  \
    }
    super(ListZonesRequest, self).__init__(params)


class DeactivateZoneRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['DeactivateZone']
  def __init__(self, zoneid, objectid, feed):
    params = { 'zoneid' : zoneid, 'feed' : feed, 'oid' : objectid }
    super(DeactivateZoneRequest, self).__init__(params)


class DeleteZoneRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['DeleteZone']
  def __init__(self, zoneid, objectid, feed):
    params = { 'zoneid' : zoneid, 'feed' : feed, 'oid' : objectid }
    super(DeleteZoneRequest, self).__init__(params)


class CreateFenceRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['CreateFence']
  def __init__(self, fenceid, region, trigger, callback, predicate, name_values={}, once=False):
    params = {  
      'fenceid' : fenceid, 'trigger' : trigger, 'predicate' : predicate \
    }
    if once == True:
      params['onetimealert'] = True 
    if not isinstance(region, LocomatixRegion):
      raise ValueError("Invalid region type (%s) - region must derive from LocomatixRegion" % type(region))
    params.update(region._params)
    if not isinstance(callback, LocomatixCallback):
      raise ValueError("callback is an invalid type (%s) - callback must derive from LocomatixCallback" % type(callback))
    params.update(callback._params)
    params.update(name_values)
    super(CreateFenceRequest, self).__init__(params)


class ActivateFenceRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['ActivateFence']
  def __init__(self, fenceid):
    params = { 'fenceid' : fenceid }
    super(ActivateFenceRequest, self).__init__(params)


class GetFenceRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['GetFence']
  def __init__(self, fenceid):
    params = { 'fenceid' : fenceid }
    super(GetFenceRequest, self).__init__(params)


class ListFencesRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['ListFences']
  def __init__(self, start_key, fetch_size):
    params = { 'startkey' : start_key, 'fetchsize' : fetch_size }
    super(ListFencesRequest, self).__init__(params)


class DeactivateFenceRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['DeactivateFence']
  def __init__(self, fenceid):
    params = { 'fenceid' : fenceid }
    super(DeactivateFenceRequest, self).__init__(params)


class DeleteFenceRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['DeleteFence']
  def __init__(self, fenceid):
    params = { 'fenceid' : fenceid }
    super(DeleteFenceRequest, self).__init__(params)


class GetLocationHistoryRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['GetLocationHistory']
  def __init__(self, objectid, feed, start_time, end_time, start_key, fetch_size):
    params = { 
      'oid' : objectid, 'feed' : feed, \
      'starttime' : int(start_time), 'endtime' : int(end_time), \
      'startkey': start_key, 'fetchsize' : fetch_size
    }
    super(GetLocationHistoryRequest, self).__init__(params)


class GetSpaceActivityRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['GetSpaceActivity']
  def __init__(self, feed, region, start_time, end_time, start_key, fetch_size):
    params = { 
      'feed' : feed, 'starttime' : int(start_time), 'endtime' : int(end_time), \
      'startkey': start_key, 'fetchsize' : fetch_size
    }
    if not isinstance(region, LocomatixRegion):
      raise ValueError("Invalid region type (%s) - region must derive from LocomatixRegion" % type(region))
    params.update(region._params)
    super(GetSpaceActivityRequest, self).__init__(params)

