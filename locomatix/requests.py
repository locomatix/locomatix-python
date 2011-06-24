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
import urllib
from region import *
from callback import *


ROUTE_SIGNATURES = {
  'CreateFeed':         ( 'POST',    '/feed/Create.json',                       None     ),
  'DeleteFeed':         ( 'DELETE',  '/feed/Delete.json',                       None     ),
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
  'GetSpaceActivity':   ( 'GET',    '/analytics/feed/%s/SpaceActivity.json',    ['feed'] ),
  'GetHistogram':       ( 'GET',    '/analytics/feed/%s/ObjectGrid.json',       ['feed'] )
}

def tnvs(name_values):
  nvs = dict()
  for n, v in name_values.items():
    if isinstance(v, list):
      nl = []
      for val in v: 
        vs = val.encode("utf-8") if isinstance(val, unicode) else val
        nl.append(vs)
      nvs[n] = nl
    else:
      nvs[n] = v.encode("utf-8") if isinstance(v, unicode) else v
  return nvs

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
  
  def __init__(self, params):
    self._params = params # descendent requests should assemble args into this instance dictionary
    self._set_method()    # sets the _method instance variable
    self._set_uri()       # assembles the final uri into the _uri instance var
    self._set_body()      # assembles the body into the _body instance var
  
  def _set_method(self):
    """Sets the instance _method by simply copying the METHOD class attribute"""
    self._method = self.METHOD
  
  def _set_uri(self):
    """Inserts uri params into _uri, deletes them from the _params dictionary.
    
    If this is a GET or DELETE request, adds remaining params as query string"""
    uri_params = []
    if self.URI_PARAMS:
      for param_name in self.URI_PARAMS:
        uri_params.append(urllib.quote_plus(self._params[param_name]))
        del self._params[param_name]
    self._uri = self.URI_FORMAT % tuple(uri_params)
    if self.METHOD in ('GET','DELETE'):
      self._uri += '?' + urllib.urlencode(self._params)
  
  def _set_body(self):
    """If this is a POST or PUT request, adds params as query string to the body."""
    if self.METHOD in ('POST','PUT'):
      nvseq = []
      for param, values in self._params.iteritems():
        if isinstance(values, list):
          nvseq.extend([(param, value) for value in values])
        else:
          nvseq.append((param, values))
      self._body = urllib.urlencode(nvseq)
    else:
      self._body = self.__class__.EMPTY_BODY
  
  def dump(self):
    """Returns (method, uri, body) as a tuple."""
    return (self._method, self._uri, self._body)


class CreateFeedRequest(LocomatixRequest):
  def __init__(self, feed, name_values={}):
    self.METHOD, self.URI_FORMAT, self.URI_PARAMS = ROUTE_SIGNATURES['CreateFeed']
    params = dict({ 'feed' : feed })
    params.update(tnvs(name_values))
    super(CreateFeedRequest, self).__init__(params)

class DeleteFeedRequest(LocomatixRequest):
  def __init__(self, feed):
    self.METHOD, self.URI_FORMAT, self.URI_PARAMS = ROUTE_SIGNATURES['DeleteFeed']
    params = { 'feed' : feed }
    super(DeleteFeedRequest, self).__init__(params)

class ListFeedsRequest(LocomatixRequest):
  def __init__(self, start_key, fetch_size):
    self.METHOD, self.URI_FORMAT, self.URI_PARAMS = ROUTE_SIGNATURES['ListFeeds']
    params = { 'startkey' : start_key, 'fetchsize' : fetch_size }
    super(ListFeedsRequest, self).__init__(params)


class CreateObjectRequest(LocomatixRequest):
  def __init__(self, objectid, feed, name_values={}, location = None, time = 0, ttl=0):
    self.METHOD,   self.URI_FORMAT,  self.URI_PARAMS = ROUTE_SIGNATURES['CreateObject']
    params = dict({ 'feed':feed, 'oid':objectid })
    params.update(tnvs(name_values))
    if location != None:
      params.update(location._params)
      params['time'] = int(time)
      if ttl != 0:
        params['ttl'] = ttl
    super(CreateObjectRequest, self).__init__(params)


class DeleteObjectRequest(LocomatixRequest):
  def __init__(self, objectid, feed):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['DeleteObject']
    params = { 'feed':feed, 'oid':objectid }
    super(DeleteObjectRequest, self).__init__(params)


class ListObjectsRequest(LocomatixRequest):
  def __init__(self, feed, start_key, fetch_size):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['ListObjects']
    params = { 'feed' : feed, 'startkey':start_key, 'fetchsize':fetch_size }
    super(ListObjectsRequest, self).__init__(params)


class GetAttributesRequest(LocomatixRequest):
  def __init__(self, objectid, feed):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['GetAttributes']
    params = { 'feed':feed, 'oid':objectid }
    super(GetAttributesRequest, self).__init__(params)


class UpdateAttributesRequest(LocomatixRequest):
  def __init__(self, objectid, feed, name_values={}):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['UpdateAttributes']
    params = dict({ 'feed':feed, 'oid':objectid })
    params.update(tnvs(name_values))
    super(UpdateAttributesRequest, self).__init__(params)


class UpdateLocationRequest(LocomatixRequest):
  def __init__(self, objectid, feed, location, time, name_values={}, ttl=0):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['UpdateLocation']
    params = dict({ 'oid' : objectid, 'feed' : feed, 'time': int(time) })
    params.update(location._params)
    params.update(tnvs(name_values))
    if ttl != 0:
      params['ttl'] = ttl
    super(UpdateLocationRequest, self).__init__(params)


class GetLocationRequest(LocomatixRequest):
  def __init__(self, objectid, feed, allow_expired):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['GetLocation']
    params = { 
      'feed' : feed, 'oid' : objectid \
    }
    if allow_expired:
      params['allowexpired'] = True 
    super(GetLocationRequest, self).__init__(params)


class SearchNearbyRequest(LocomatixRequest):
  def __init__(self, objectid, feed, region, predicate, fetch_start, fetch_size):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['SearchNearby']
    params = dict({ 
      'feed' : feed, 'oid' : objectid, \
      'startkey':fetch_start, 'fetchsize':fetch_size, \
      'predicate':predicate \
    })
    if not isinstance(region, LocomatixRegion):
      raise ValueError("region is an invalid type (%s) - region must derive from LocomatixRegion" % type(region))
    params.update(region._params)
    super(SearchNearbyRequest, self).__init__(params)


class SearchRegionRequest(LocomatixRequest):
  def __init__(self, region, predicate, fetch_start, fetch_size):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['SearchRegion']
    params = dict({
      'startkey':fetch_start, 'fetchsize':fetch_size, \
      'predicate':predicate \
    })
    if not isinstance(region, LocomatixRegion):
      raise ValueError("Invalid region type (%s) - region must derive from LocomatixRegion" % type(region))
    params.update(region._params)
    super(SearchRegionRequest, self).__init__(params)


class CreateZoneRequest(LocomatixRequest):
  def __init__(self, zoneid, objectid, feed, region, trigger, callback, predicate, \
               name_values={}, deactivate=False, once=False):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['CreateZone']
    params = dict({ 
      'zoneid' : zoneid, 'oid' : objectid, \
      'feed' : feed, 'trigger': trigger, \
      'predicate':predicate \
    })
    if once:
      params['onetimealert'] = True 
    if deactivate:
      params['state'] = 'inactive'
    if not isinstance(region, LocomatixRegion):
      raise ValueError("region is an invalid type (%s) - region must derive from LocomatixRegion" % type(region))
    params.update(region._params)
    if not isinstance(callback, LocomatixCallback):
      raise ValueError("callback is an invalid type (%s) - callback must derive from LocomatixCallback" % type(callback))
    params.update(callback._params)
    params.update(tnvs(name_values))
    super(CreateZoneRequest, self).__init__(params)


class ActivateZoneRequest(LocomatixRequest):
  def __init__(self, zoneid, objectid, feed):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['ActivateZone']
    params = { 'zoneid' : zoneid, 'feed' : feed, 'oid' : objectid }
    super(ActivateZoneRequest, self).__init__(params)


class GetZoneRequest(LocomatixRequest):
  def __init__(self, zoneid, objectid, feed):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['GetZone']
    params = { 'zoneid' : zoneid, 'oid' : objectid, 'feed' : feed }
    super(GetZoneRequest, self).__init__(params)


class ListZonesRequest(LocomatixRequest):
  def __init__(self, objectid, feed, start_key, fetch_size):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['ListZones']
    params = { \
      'oid' : objectid, 'feed' : feed, \
      'startkey' : start_key, 'fetchsize' : fetch_size  \
    }
    super(ListZonesRequest, self).__init__(params)


class DeactivateZoneRequest(LocomatixRequest):
  def __init__(self, zoneid, objectid, feed):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['DeactivateZone']
    params = { 'zoneid' : zoneid, 'feed' : feed, 'oid' : objectid }
    super(DeactivateZoneRequest, self).__init__(params)


class DeleteZoneRequest(LocomatixRequest):
  def __init__(self, zoneid, objectid, feed):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['DeleteZone']
    params = { 'zoneid' : zoneid, 'feed' : feed, 'oid' : objectid }
    super(DeleteZoneRequest, self).__init__(params)


class CreateFenceRequest(LocomatixRequest):
  def __init__(self, fenceid, region, trigger, callback, predicate, name_values={}, deactivate=False, once=False):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['CreateFence']
    params = dict({  
      'fenceid' : fenceid, 'trigger' : trigger, 'predicate' : predicate \
    })
    if once:
      params['onetimealert'] = True 
    if deactivate:
      params['state'] = 'inactive'
    if not isinstance(region, LocomatixRegion):
      raise ValueError("Invalid region type (%s) - region must derive from LocomatixRegion" % type(region))

    params.update(region._params)
    if not isinstance(callback, LocomatixCallback):
      raise ValueError("callback is an invalid type (%s) - callback must derive from LocomatixCallback" % type(callback))
    params.update(callback._params)
    params.update(tnvs(name_values))
    super(CreateFenceRequest, self).__init__(params)


class ActivateFenceRequest(LocomatixRequest):
  def __init__(self, fenceid):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['ActivateFence']
    params = { 'fenceid' : fenceid }
    super(ActivateFenceRequest, self).__init__(params)


class GetFenceRequest(LocomatixRequest):
  def __init__(self, fenceid):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['GetFence']
    params = { 'fenceid' : fenceid }
    super(GetFenceRequest, self).__init__(params)


class ListFencesRequest(LocomatixRequest):
  def __init__(self, start_key, fetch_size):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['ListFences']
    params = { 'startkey' : start_key, 'fetchsize' : fetch_size }
    super(ListFencesRequest, self).__init__(params)


class DeactivateFenceRequest(LocomatixRequest):
  def __init__(self, fenceid):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['DeactivateFence']
    params = { 'fenceid' : fenceid }
    super(DeactivateFenceRequest, self).__init__(params)


class DeleteFenceRequest(LocomatixRequest):
  def __init__(self, fenceid):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['DeleteFence']
    params = { 'fenceid' : fenceid }
    super(DeleteFenceRequest, self).__init__(params)


class GetLocationHistoryRequest(LocomatixRequest):
  def __init__(self, objectid, feed, start_time, end_time, start_key, fetch_size):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['GetLocationHistory']
    params = { 
      'oid' : objectid, 'feed' : feed, \
      'starttime' : int(start_time), 'endtime' : int(end_time), \
      'startkey': start_key, 'fetchsize' : fetch_size
    }
    super(GetLocationHistoryRequest, self).__init__(params)


class GetSpaceActivityRequest(LocomatixRequest):
  def __init__(self, feed, region, start_time, end_time, start_key, fetch_size):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['GetSpaceActivity']
    params = dict({ 
      'feed' : feed, 'starttime' : int(start_time), 'endtime' : int(end_time), \
      'startkey': start_key, 'fetchsize' : fetch_size
    })
    if not isinstance(region, LocomatixRegion):
      raise ValueError("Invalid region type (%s) - region must derive from LocomatixRegion" % type(region))
    params.update(region._params)
    super(GetSpaceActivityRequest, self).__init__(params)


class GetHistogramRequest(LocomatixRequest):
  def __init__(self, feed, bbox, nhslices, nvslices, etime):
    self.METHOD,   self.URI_FORMAT,   self.URI_PARAMS = ROUTE_SIGNATURES['GetHistogram']
    params = dict({ 
      'feed' : feed, 'grid_horizontal_slices' : str(nhslices),  \
      'grid_vertical_slices' : str(nvslices), 'grid_starttime' : int(etime) \
    })
    if not isinstance(bbox, Rectangle):
      raise ValueError("Invalid region type (%s) - should be a rectangle" % type(bbox))

    cr_low  = str(bbox.sw_lat) + ',' + str(bbox.sw_long) 
    cr_high = str(bbox.ne_lat) + ',' + str(bbox.ne_long)

    pt_list = '|'.join((cr_low, cr_high))
    rparams = {
      'grid_bbox' : pt_list \
    }

    params.update(rparams)
    super(GetHistogramRequest, self).__init__(params)
