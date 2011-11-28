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
import httplib
from response_handlers import *
from exceptions import *
try: import simplejson as json
except ImportError: 
  try: import json
  except ImportError:
    raise ImportError("simplejson is not installed. Please download it from http://code.google.com/p/simplejson/")

class LocomatixResponse(object):
  """This is the base Locomatix Response object from which all Responses are derived.
  
  A Response is initialize with an http_response object (from httplib).  The LocomatixResponse
  gets the status, and body of the http_response.  If the request was successful the LocomatixResponse
  will try to parse the XML using a handler specific to the request type.  Instance variables
  for the specific response type will be set using the handler results.  Descendant Responses
  need only designate a HANDLER class attribute, then do any relevant instance var assigning
  as necessary in their constructor."""
  HANDLER = None
  def __init__(self, http_response):
    self.status = http_response.status
    self.body = http_response.read()
    self.handler = self.__class__.HANDLER.__class__()
    self.request_signature = None
    self.response_meta = LxResponseMetadata()

    if self.status >= httplib.OK:
      data = json.loads(self.body)
      self.response_meta.message = data['Status']
      self.response_meta.response_time = data['ExecutionTime']
      if self.response_meta.message == 'Success':
        self.handler.handle(data)
      self.body = data
    else:
      self.response_meta.message = http_response.reason

  def get_metadata(self):
    return self.response_meta

class CreateFeedResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()

class DeleteFeedResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()

class ListFeedsResponse(LocomatixResponse):
  HANDLER = ListFeedsResponseHandler()
  def __init__(self, http_response):
    super(ListFeedsResponse, self).__init__(http_response)
    if self.response_meta.message == 'Success':
       self.next_key = self.handler.next_key
       self.feeds = self.handler.feeds
    else:
       self.next_key = None
       self.feeds = []

class CreateObjectResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class DeleteObjectResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class ListObjectsResponse(LocomatixResponse):
  HANDLER = ListObjectsResponseHandler()
  def __init__(self, http_response):
    super(ListObjectsResponse, self).__init__(http_response)
    if self.response_meta.message == 'Success':
       self.next_key = self.handler.next_key
       self.objects = self.handler.objects
       self.aggrs = self.handler.aggrs
    else:
       self.next_key = None
       self.aggrs = []
       self.objects = []


class GetAttributesResponse(LocomatixResponse):
  HANDLER = GetAttributesResponseHandler()
  def __init__(self, http_response):
    super(GetAttributesResponse, self).__init__(http_response)
    if self.response_meta.message == 'Success':
       self.object = self.handler.object
    else:
       self.object = None


class UpdateAttributesResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class UpdateLocationResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class GetLocationResponse(LocomatixResponse):
  HANDLER = GetLocationResponseHandler()
  def __init__(self, http_response):
    super(GetLocationResponse, self).__init__(http_response)
    if self.response_meta.message == 'Success':
       self.location = self.handler.location
    else:
       self.location = None


class SearchNearbyResponse(LocomatixResponse):
  HANDLER = SearchResponseHandler()
  def __init__(self, http_response):
    super(SearchNearbyResponse, self).__init__(http_response)
    if self.response_meta.message == 'Success':
       self.objlocs = self.handler.objlocs
       self.aggrs = self.handler.aggrs
       self.next_key = self.handler.next_key
    else:
       self.objlocs = []
       self.aggrs = []
       self.next_key = None
       

class SearchRegionResponse(LocomatixResponse):
  HANDLER = SearchResponseHandler()
  def __init__(self, http_response):
    super(SearchRegionResponse, self).__init__(http_response)
    if self.response_meta.message == 'Success':
       self.objlocs = self.handler.objlocs
       self.aggrs = self.handler.aggrs
       self.next_key = self.handler.next_key
    else:
       self.objlocs = []
       self.aggrs = []
       self.next_key = None


class CreateZoneResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class ActivateZoneResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class GetZoneResponse(LocomatixResponse):
  HANDLER = GetZoneResponseHandler()
  def __init__(self, http_response):
    super(GetZoneResponse, self).__init__(http_response)
    if self.response_meta.message == 'Success':
       self.zone  = self.handler.zone
    else:
       self.zone = None


class ListZonesResponse(LocomatixResponse):
  HANDLER = ListZonesResponseHandler()
  def __init__(self, http_response):
    super(ListZonesResponse, self).__init__(http_response)
    if self.response_meta.message == 'Success':
       self.next_key = self.handler.next_key
       self.zones  = self.handler.zones
    else:
       self.next_key = None
       self.zones  = None


class DeactivateZoneResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class DeleteZoneResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class CreateFenceResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class ActivateFenceResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class GetFenceResponse(LocomatixResponse):
  HANDLER = GetFenceResponseHandler()
  def __init__(self, http_response):
    super(GetFenceResponse, self).__init__(http_response)
    if self.response_meta.message == 'Success':
       self.fence  = self.handler.fence
    else:
       self.fence  = None


class ListFencesResponse(LocomatixResponse):
  HANDLER = ListFencesResponseHandler()
  def __init__(self, http_response):
    super(ListFencesResponse, self).__init__(http_response)
    if self.response_meta.message == 'Success':
       self.next_key = self.handler.next_key
       self.fences = self.handler.fences
    else:
       self.next_key = None
       self.fences = []


class DeactivateFenceResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class DeleteFenceResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class GetLocationHistoryResponse(LocomatixResponse):
  HANDLER = GetLocationHistoryResponseHandler()
  def __init__(self, http_response):
    super(GetLocationHistoryResponse, self).__init__(http_response)
    if self.response_meta.message == 'Success':
       self.locations = self.handler.locations
       self.aggrs = self.handler.aggrs
       self.next_key = self.handler.next_key
    else:
       self.locations = []
       self.aggrs = None
       self.next_key = None


class GetSpaceActivityResponse(LocomatixResponse):
  HANDLER = GetSpaceActivityResponseHandler()
  def __init__(self, http_response):
    super(GetSpaceActivityResponse, self).__init__(http_response)
    if self.response_meta.message == 'Success':
       self.objlocs = self.handler.objlocs
       self.aggrs = self.handler.aggrs
       self.next_key = self.handler.next_key
    else:
       self.objlocs = None
       self.aggrs = None
       self.next_key = None


class GetHistogramResponse(LocomatixResponse):
  HANDLER = GetHistogramResponseHandler()
  def __init__(self, http_response):
    super(GetHistogramResponse, self).__init__(http_response)
    if self.response_meta.message == 'Success':
       self.grid_aggregates = self.handler.grid_aggregates
    else:
       self.grid_aggregates = []
