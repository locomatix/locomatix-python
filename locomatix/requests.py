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


ROUTE_SIGNATURES = {
  'CreateObject':     ( 'POST',   '/feed/%s/object/Create.xml',           ['feed'] ),
  'DeleteObject':     ( 'DELETE', '/feed/%s/object/Delete.xml',           ['feed'] ),
  'ListObjects':      ( 'GET',    '/feed/%s/ListObjects.xml',             ['feed'] ),
  'GetAttributes':    ( 'GET',    '/feed/%s/object/GetAttributes.xml',    ['feed'] ),
  'UpdateAttributes': ( 'PUT',    '/feed/%s/object/UpdateAttributes.xml', ['feed'] ),
  'GetLocation':      ( 'GET',    '/feed/%s/object/GetLocation.xml',      ['feed'] ),
  'UpdateLocation':   ( 'PUT',    '/feed/%s/object/UpdateLocation.xml',   ['feed'] ),
  'SearchRegion':     ( 'GET',    '/search/Region.xml',                   None     ),
  'SearchNearby':     ( 'GET',    '/search/NearbyObject.xml',             None     ),
  'CreateZone':       ( 'POST',   '/zone/%s/Create.xml',                  ['feed'] ),
  'GetZone':          ( 'GET',    '/zone/%s/Get.xml',                     ['feed'] ),
  'ListZones':        ( 'GET',    '/zone/%s/List.xml',                    ['feed'] ),
  'DeleteZone':       ( 'DELETE', '/zone/%s/Delete.xml',                  ['feed'] ),
  'CreateFence':      ( 'POST',   '/fence/Create.xml',                    None     ),
  'GetFence':         ( 'GET',    '/fence/Get.xml',                       None     ),
  'ListFences':       ( 'GET',    '/fence/List.xml',                      None     ),
  'DeleteFence':      ( 'DELETE', '/fence/Delete.xml',                    None     )
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
        uri_params.append(self._params[param_name])
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


class CreateObjectRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['CreateObject']
  def __init__(self, objectid, feed, name_values={}):
    params = { 'feed':feed, 'oid':objectid }
    params.update(name_values)
    super(CreateObjectRequest, self).__init__(params)


class DeleteObjectRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['DeleteObject']
  def __init__(self, objectid, feed):
    params = { 'feed':feed, 'oid':objectid }
    super(DeleteObjectRequest, self).__init__(params)


class ListObjectsRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['ListObjects']
  def __init__(self, feed, fetch_start, fetch_size):
    params = { 'feed':feed, 'fetchstart':fetch_start, 'fetchsize':fetch_size }
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
  def __init__(self, objectid, feed, longitude, latitude, time, name_values={}):
    params = { 'feed':feed, 'oid':objectid, \
               'longitude':longitude, 'latitude':latitude, 'time':time }
    params.update(name_values)
    super(UpdateLocationRequest, self).__init__(params)


class GetLocationRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['GetLocation']
  def __init__(self, objectid, feed):
    params = { 'feed':feed, 'oid':objectid }
    super(GetLocationRequest, self).__init__(params)


class SearchNearbyRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['SearchNearby']
  def __init__(self, objectid, feed, region, from_feeds, fetch_start, fetch_size):
    params = { 'feed':feed, 'oid':objectid, \
               'fetchstart':fetch_start, 'fetchsize':fetch_size }
    if 'type' in region: 
      params['region'] = region['type']
    if 'radius' in region: 
      params['radius'] = region['radius']
    if len(from_feeds) == 0: from_feeds.append(feed)
    params['feeds'] = ','.join(from_feeds)
    super(SearchNearbyRequest, self).__init__(params)


class SearchRegionRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['SearchRegion']
  def __init__(self, region, from_feeds, fetch_start, fetch_size):
    params = {
      'fetchstart':fetch_start, 'fetchsize':fetch_size
    }
    if 'type' in region: 
      params['region'] = region['type']
    if 'radius' in region: 
      params['radius'] = region['radius']
    if 'longitude' in region: 
      params['longitude'] = region['longitude']
    if 'latitude' in region: 
      params['latitude'] = region['latitude']
    if len(from_feeds) > 0:
      params['feeds'] = ','.join(from_feeds)
    super(SearchRegionRequest, self).__init__(params)


class CreateZoneRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['CreateZone']
  def __init__(self, zoneid, objectid, feed, \
               region, trigger, callback, from_feeds=[]):
    params = { 
       'zoneid':zoneid, 'feed':feed, 'oid':objectid, \
       'trigger': trigger, \
    }
    if 'type' in region: 
      params['region'] = region['type']
    if 'radius' in region: 
      params['radius'] = region['radius']
    if 'type' in callback: 
      params['callbacktype'] = callback['type']
    if 'URL' in callback: 
      params['callbackurl'] = callback['URL']
    if len(from_feeds) == 0: from_feeds.append(feed)
    params['feeds'] = ','.join(from_feeds)
    super(CreateZoneRequest, self).__init__(params)


class GetZoneRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['GetZone']
  def __init__(self, zoneid, objectid, feed):
    params = { 'zoneid':zoneid, 'feed':feed, 'oid':objectid }
    super(GetZoneRequest, self).__init__(params)


class ListZonesRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['ListZones']
  def __init__(self, objectid, feed, fetch_start, fetch_size):
    params = { 'feed':feed, 'oid':objectid, \
               'fetchstart':fetch_start, 'fetchsize':fetch_size }
    super(ListZonesRequest, self).__init__(params)


class DeleteZoneRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['DeleteZone']
  def __init__(self, zoneid, objectid, feed):
    params = { 'zoneid':zoneid, 'feed':feed, 'oid':objectid }
    super(DeleteZoneRequest, self).__init__(params)


class CreateFenceRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['CreateFence']
  def __init__(self, fenceid, region, trigger, callback, from_feeds):
    params = { 
        'fenceid':fenceid, \
        'trigger': trigger, \
    }

    if 'type' in region: 
      params['region'] = region['type']
    if 'radius' in region: 
      params['radius'] = region['radius']
    if 'longitude' in region: 
      params['longitude'] = region['longitude']
    if 'latitude' in region: 
      params['latitude'] = region['latitude']
    if 'type' in callback: 
      params['callbacktype'] = callback['type']
    if 'URL' in callback: 
      params['callbackurl'] = callback['URL']
    if len(from_feeds) > 0:
      params['feeds'] = ','.join(from_feeds)
    super(CreateFenceRequest, self).__init__(params)


class GetFenceRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['GetFence']
  def __init__(self, fenceid):
    params = { 'fenceid':fenceid }
    super(GetFenceRequest, self).__init__(params)


class ListFencesRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['ListFences']
  def __init__(self, fetch_start, fetch_size):
    params = { 'fetchstart':fetch_start, 'fetchsize':fetch_size }
    super(ListFencesRequest, self).__init__(params)


class DeleteFenceRequest(LocomatixRequest):
  METHOD, URI_FORMAT, URI_PARAMS = ROUTE_SIGNATURES['DeleteFence']
  def __init__(self, fenceid):
    params = { 'fenceid':fenceid }
    super(DeleteFenceRequest, self).__init__(params)

