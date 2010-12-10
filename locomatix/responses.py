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
import httplib, urllib
from response_handlers import *
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
  def __init__(self, http_response, *args):
    self.status = http_response.status
    self.body = http_response.read()
    self.handler = self.__class__.HANDLER.__class__()
    self.request_signature = None
    if self.status >= httplib.OK:
      data = json.loads(self.body)
      status = data['Status']
      if status != 'Success':
        self.message = status
      else:
        self.handler.handle(data)
        self.message = self.handler.message
      self.body = json.dumps(data, indent=4)
    else:
      self.message = http_response.reason


class ListFeedsResponse(LocomatixResponse):
  HANDLER = ListFeedsResponseHandler()
  def __init__(self, http_response, *args):
    super(ListFeedsResponse, self).__init__(http_response)
    self.next_key = self.handler.next_key
    self.feeds = self.handler.feeds


class CreateObjectResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class DeleteObjectResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class ListObjectsResponse(LocomatixResponse):
  HANDLER = ListObjectsResponseHandler()
  def __init__(self, http_response, *args):
    super(ListObjectsResponse, self).__init__(http_response)
    self.next_key = self.handler.next_key
    self.objects = self.handler.objects


class GetAttributesResponse(LocomatixResponse):
  HANDLER = GetAttributesResponseHandler()
  def __init__(self, http_response, *args):
    super(GetAttributesResponse, self).__init__(http_response)
    self.object = self.handler.object


class UpdateAttributesResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class UpdateLocationResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class GetLocationResponse(LocomatixResponse):
  HANDLER = GetLocationResponseHandler()
  def __init__(self, http_response, *args):
    super(GetLocationResponse, self).__init__(http_response)
    self.object = self.handler.object


class SearchNearbyResponse(LocomatixResponse):
  HANDLER = SearchResponseHandler()
  def __init__(self, http_response, *args):
    super(SearchNearbyResponse, self).__init__(http_response)
    self.objects = self.handler.objects
    self.next_key = self.handler.next_key


class SearchRegionResponse(LocomatixResponse):
  HANDLER = SearchResponseHandler()
  def __init__(self, http_response, *args):
    super(SearchRegionResponse, self).__init__(http_response)
    self.objects = self.handler.objects
    self.next_key = self.handler.next_key


class CreateZoneResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class GetZoneResponse(LocomatixResponse):
  HANDLER = GetZoneResponseHandler()
  def __init__(self, http_response, *args):
    super(GetZoneResponse, self).__init__(http_response)
    self.zone  = self.handler.zone


class ListZonesResponse(LocomatixResponse):
  HANDLER = ListZonesResponseHandler()
  def __init__(self, http_response, *args):
    super(ListZonesResponse, self).__init__(http_response)
    self.next_key = self.handler.next_key
    self.zones  = self.handler.zones


class DeleteZoneResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class CreateFenceResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class GetFenceResponse(LocomatixResponse):
  HANDLER = GetFenceResponseHandler()
  def __init__(self, http_response, *args):
    super(GetFenceResponse, self).__init__(http_response)
    self.fence  = self.handler.fence


class ListFencesResponse(LocomatixResponse):
  HANDLER = ListFencesResponseHandler()
  def __init__(self, http_response, *args):
    super(ListFencesResponse, self).__init__(http_response)
    self.next_key = self.handler.next_key
    self.fences = self.handler.fences


class DeleteFenceResponse(LocomatixResponse):
  HANDLER = StatusResponseHandler()


class GetLocationHistoryResponse(LocomatixResponse):
  HANDLER = GetLocationHistoryResponseHandler()
  def __init__(self, http_response, objectid = None, feed = None, *args):
    super(GetLocationHistoryResponse, self).__init__(http_response)
    self.objectid = objectid
    self.feed = feed
    self.locations = self.handler.locations
    self.next_key = self.handler.next_key


class GetSpaceActivityResponse(LocomatixResponse):
  HANDLER = GetSpaceActivityResponseHandler()
  def __init__(self, http_response, *args):
    super(GetSpaceActivityResponse, self).__init__(http_response)
    self.objects = self.handler.objects
    self.next_key = self.handler.next_key
