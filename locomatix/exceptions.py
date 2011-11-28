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

class LxException(Exception):
  def __init__(self, message):
    self.message = message

  def __str__(self):
    return self.message

class ConnectionFailure(LxException):
  """Raised when the Client fails to establish a connection with the remote Locomatix server."""
  def __init__(self, parent_exception, host, port):
    self.ex = parent_exception
    self.host = host
    self.port = port
  def __str__(self):
    return "Failed to establish connection with %s:%d\n%s" % (self.host, self.port, self.ex)

class RequestFailed(LxException):
  """Raised when the Client fails to establish a connection with the remote Locomatix server."""
  def __init__(self, parent_exception, host, port, req_type):
    super(RequestFailed, self).__init__(self.__class__.__name__)
    self.ex = parent_exception
    self.req_type = req_type
    self.host = host
    self.port = port
  def __str__(self):
    return "Locomatix %s could not be completed on %s:%d\n%s" % (self.req_type, self.host, self.port, self.ex)

class UnknownError(LxException):
  """Raised when the client is unable to recognize the error by the server."""
  def __init__(self):
    super(UnknownError, self).__init__(self.__class__.__name__)

class BadRequest(LxException):
  """Raised when the request is not valid."""
  def __init__(self):
    super(BadRequest, self).__init__(self.__class__.__name__)

class InvalidRequest(LxException):
  """Raised when the request is malformed."""
  def __init__(self):
    super(InvalidRequest, self).__init__(self.__class__.__name__)

class UnknownRequest(LxException):
  """Raised when Locomatix Server does not recognize the request.""" 
  def __init__(self):
    super(UnknownRequest, self).__init__(self.__class__.__name__)

class TooBigRequest(LxException):
  """Raised when the incoming request is too big to process in the Locomatix Server.""" 
  def __init__(self):
    super(TooBigRequest, self).__init__(self.__class__.__name__)

class UnauthorizedRequest(LxException):
  """Raised if the credentials provided are not allowed to perform the request.""" 
  def __init__(self):
    super(UnauthorizedRequest, self).__init__(self.__class__.__name__)

class AuthenticationFailed(LxException):
  """Raised if the credentials provided are invalid.""" 
  def __init__(self):
    super(AuthenticationFailed, self).__init__(self.__class__.__name__)

class MissingVersion(LxException):
  """Raised when the http header does not contain version.""" 
  def __init__(self):
    super(MissingVersion, self).__init__(self.__class__.__name__)

class MissingObjectID(LxException):
  """Raised when the request does not contain the required object identifier.""" 
  def __init__(self):
    super(MissingObjectID, self).__init__(self.__class__.__name__)

class MissingFeed(LxException):
  """Raised when the request does not contain the required feed name.""" 
  def __init__(self):
    super(MissingFeed, self).__init__(self.__class__.__name__)

class MissingZoneID(LxException):
  """Raised when the request does not contain the required zone identifier.""" 
  def __init__(self):
    super(MissingZoneID, self).__init__(self.__class__.__name__)

class MissingFenceID(LxException):
  """Raised when the request does not contain the required fence identifier.""" 
  def __init__(self):
    super(MissingFenceID, self).__init__(self.__class__.__name__)

class MissingCallbackType(LxException):
  """Raised when the request does not contain the required callback type.""" 
  def __init__(self):
    super(MissingCallbackType, self).__init__(self.__class__.__name__)

class MissingCallbackURL(LxException):
  """Raised when the request does not contain the required callback URL.""" 
  def __init__(self):
    super(MissingCallbackURL, self).__init__(self.__class__.__name__)

class MissingLongitude(LxException):
  """Raised when the request does not contain the required longitude.""" 
  def __init__(self):
    super(MissingLongitude, self).__init__(self.__class__.__name__)

class MissingLatitude(LxException):
  """Raised when the request does not contain the required longitude.""" 
  def __init__(self):
    super(MissingLatitude, self).__init__(self.__class__.__name__)

class MissingTime(LxException):
  """Raised when the request does not contain the required time.""" 
  def __init__(self):
    super(MissingTime, self).__init__(self.__class__.__name__)

class MissingStartTime(LxException):
  """Raised when the request does not contain the required start time.""" 
  def __init__(self):
    super(MissingStartTime, self).__init__(self.__class__.__name__)

class MissingEndTime(LxException):
  """Raised when the request does not contain the required end time.""" 
  def __init__(self):
    super(MissingEndTime, self).__init__(self.__class__.__name__)

class MissingRegion(LxException):
  """Raised when the request does not contain the required region.""" 
  def __init__(self):
    super(MissingRegion, self).__init__(self.__class__.__name__)

class MissingRadius(LxException):
  """Raised when the request does not contain the required radius.""" 
  def __init__(self):
    super(MissingRadius, self).__init__(self.__class__.__name__)

class MissingQuery(LxException):
  """Raised when the request does not contain the required query.""" 
  def __init__(self):
    super(MissingQuery, self).__init__(self.__class__.__name__)

class MissingFetchParams(LxException):
  """Raised when the request does not contain the required fetch parameters.""" 
  def __init__(self):
    super(MissingFetchParams, self).__init__(self.__class__.__name__)

class MissingNameValuePairs(LxException):
  """Raised when the request does not contain the required name value pairs.""" 
  def __init__(self):
    super(MissingNameValuePairs, self).__init__(self.__class__.__name__)

class MissingCustomerID(LxException):
  """Raised when the request does not contain the customer ID authentication.""" 
  def __init__(self):
    super(MissingCustomerID, self).__init__(self.__class__.__name__)

class MissingCustomerKey(LxException):
  """Raised when the request does not contain the customer key authentication.""" 
  def __init__(self):
    super(MissingCustomerKey, self).__init__(self.__class__.__name__)

class MissingSecretKey(LxException):
  """Raised when the request does not contain the secret key authentication.""" 
  def __init__(self):
    super(MissingSecretKey, self).__init__(self.__class__.__name__)

class MissingTrigger(LxException):
  """Raised when the request does not contain the required condition for trigger.""" 
  def __init__(self):
    super(MissingTrigger, self).__init__(self.__class__.__name__)

class InvalidVersion(LxException):
  """Raised when the request contains a version that is invalid.""" 
  def __init__(self):
    super(InvalidVersion, self).__init__(self.__class__.__name__)

class InvalidLongitude(LxException):
  """Raised when the request contains a longitude that is invalid.""" 
  def __init__(self):
    super(InvalidLongitude, self).__init__(self.__class__.__name__)

class InvalidLatitude(LxException):
  """Raised when the request contains a latitude that is invalid.""" 
  def __init__(self):
    super(InvalidLatitude, self).__init__(self.__class__.__name__)

class InvalidTime(LxException):
  """Raised when the request contains an invalid time.""" 
  def __init__(self):
    super(InvalidTime, self).__init__(self.__class__.__name__)

class InvalidTTL(LxException):
  """Raised when the request contains an invalid TTL.""" 
  def __init__(self):
    super(InvalidTTL, self).__init__(self.__class__.__name__)

class ParameterValueExceeded(LxException):
  """Raised when the request contains an invalid TTL.""" 
  def __init__(self):
    super(ParameterValueExceeded, self).__init__(self.__class__.__name__)

class InvalidParameterValue(LxException):
  """Raised when the request contains an invalid parameter value.""" 
  def __init__(self):
    super(InvalidParameterValue, self).__init__(self.__class__.__name__)

class InvalidObjectID(LxException):
  """Raised when the request contains an invalid object identifier .""" 
  def __init__(self):
    super(InvalidObjectID, self).__init__(self.__class__.__name__)

class InvalidFeed(LxException):
  """Raised when the request contains an invalid feed name.""" 
  def __init__(self):
    super(InvalidFeed, self).__init__(self.__class__.__name__)

class InvalidZoneID(LxException):
  """Raised when the request contains an invalid zone identifier.""" 
  def __init__(self):
    super(InvalidZoneID, self).__init__(self.__class__.__name__)

class InvalidFenceID(LxException):
  """Raised when the request contains an invalid fence identifier.""" 
  def __init__(self):
    super(InvalidFenceID, self).__init__(self.__class__.__name__)

class TooBigRegion(LxException):
  """Raised when the request does not contain the required callback type.""" 
  def __init__(self):
    super(TooBigRegion, self).__init__(self.__class__.__name__)

class InvalidRegion(LxException):
  """Raised when the request has an invalid type of region.""" 
  def __init__(self):
    super(InvalidRegion, self).__init__(self.__class__.__name__)

class InvalidRadius(LxException):
  """Raised when the request has an invalid radius for the circle region.""" 
  def __init__(self):
    super(InvalidRadius, self).__init__(self.__class__.__name__)

class InvalidPolygon(LxException):
  """Raised when the request has an invalid polygon.""" 
  def __init__(self):
    super(InvalidPolygon, self).__init__(self.__class__.__name__)

class InvalidCallbackType(LxException):
  """Raised when the request has an invalid callback type.""" 
  def __init__(self):
    super(InvalidCallbackType, self).__init__(self.__class__.__name__)

class InvalidCallbackURL(LxException):
  """Raised when the request has an invalid callback URL.""" 
  def __init__(self):
    super(InvalidCallbackURL, self).__init__(self.__class__.__name__)

class InvalidQuery(LxException):
  """Raised when the request does not contain a valid query.""" 
  def __init__(self):
    super(InvalidQuery, self).__init__(self.__class__.__name__)

class InvalidTrigger(LxException):
  """Raised when the request contains invalid trigger condition.""" 
  def __init__(self):
    super(InvalidTrigger, self).__init__(self.__class__.__name__)

class TooBigFetch(LxException):
  """Raised when the fetch request is too big.""" 
  def __init__(self):
    super(TooBigFetch, self).__init__(self.__class__.__name__)

class InvalidMimeType(LxException):
  """Raised when the mime type is invalid.""" 
  def __init__(self):
    super(InvalidMimeType, self).__init__(self.__class__.__name__)

class ObjectAlreadyExists(LxException):
  """Raised when an object already exists in the feed."""
  def __init__(self):
    super(ObjectAlreadyExists, self).__init__(self.__class__.__name__)

class ObjectDoesNotExist(LxException):
  """Raised when an object does not exist in the feed."""
  def __init__(self):
    super(ObjectDoesNotExist, self).__init__(self.__class__.__name__)

class ZoneAlreadyExists(LxException):
  """Raised when a zone already exists for the object."""
  def __init__(self):
    super(ZoneAlreadyExists, self).__init__(self.__class__.__name__)

class ZoneDoesNotExist(LxException):
  """Raised when a zone does not exist for the object."""
  def __init__(self):
    super(ZoneDoesNotExist, self).__init__(self.__class__.__name__)

class FenceAlreadyExists(LxException):
  """Raised when a fence already exists."""
  def __init__(self):
    super(FenceAlreadyExists, self).__init__(self.__class__.__name__)

class FenceDoesNotExist(LxException):
  """Raised when a fence does not exist."""
  def __init__(self):
    super(FenceDoesNotExist, self).__init__(self.__class__.__name__)

class ObjectDoesNotHaveLocation(LxException):
  """Raised when an object does not have location."""
  def __init__(self):
    super(ObjectDoesNotHaveLocation, self).__init__(self.__class__.__name__)

class FenceAlreadyInactive(LxException):
  """Raised when a fence is already in inactive state."""
  def __init__(self):
    super(FenceAlreadyInactive, self).__init__(self.__class__.__name__)

class FenceAlreadyActive(LxException):
  """Raised when a fence is already in active state."""
  def __init__(self):
    super(FenceAlreadyActive, self).__init__(self.__class__.__name__)

class ZoneAlreadyInactive(LxException):
  """Raised when a zone is already in inactive state."""
  def __init__(self):
    super(ZoneAlreadyInactive, self).__init__(self.__class__.__name__)

class ZoneAlreadyActive(LxException):
  """Raised when a zone is already in active state."""
  def __init__(self):
    super(ZoneAlreadyActive, self).__init__(self.__class__.__name__)

class InvalidGridBoundingBox(LxException):
  """Raised when an invalid grid bounding box is provided for heatmap computation."""
  def __init__(self):
    super(InvalidGridBoundingBox, self).__init__(self.__class__.__name__)

class InvalidStartKey(LxException):
  """Raised when an invalid start key is provided for iteration."""
  def __init__(self):
    super(InvalidStartKey, self).__init__(self.__class__.__name__)

class InternalSystemError(LxException):
  """Raised when the server sends internal system error.""" 
  def __init__(self):
    super(InternalSystemError, self).__init__(self.__class__.__name__)

class FeedAlreadyExists(LxException):
  """Raised when a feed already exists."""
  def __init__(self):
    super(FeedAlreadyExists, self).__init__(self.__class__.__name__)

class FeedDoesNotExist(LxException):
  """Raised when a feed does not exist."""
  def __init__(self):
    super(FeedDoesNotExist, self).__init__(self.__class__.__name__)

class FeedNotEmpty(LxException):
  """Raised when a delete feed finds that the feed is not empty."""
  def __init__(self):
    super(FeedNotEmpty, self).__init__(self.__class__.__name__)


class GEOMIndexError(LxException):
  pass

class GEOMException(LxException):
  pass

EXCEPTIONS = {
  'BadRequest':                  BadRequest, 
  'InvalidRequest':              InvalidRequest, 
  'UnknownRequest':              UnknownRequest,
  'TooBigRequest':               TooBigRequest, 
  'UnAuthorizedRequest':         UnauthorizedRequest,
  'AuthenticationFailed':        AuthenticationFailed,

  'MissingVersion':              MissingVersion,
  'MissingObjectID':             MissingObjectID,
  'MissingFeed':                 MissingFeed,
  'MissingZoneID':               MissingZoneID,
  'MissingFenceID':              MissingFenceID,
  'MissingCallbackType':         MissingCallbackType,
  'MissingCallbackURL':          MissingCallbackURL,
  'MissingLongitude':            MissingLongitude,
  'MissingLatitude':             MissingLatitude,
  'MissingTime':                 MissingTime,
  'MissingStartTime':            MissingStartTime,
  'MissingEndTime':              MissingEndTime,
  'MissingRegion':               MissingRegion,
  'MissingRadius':               MissingRadius,
  'MissingPredicate':            MissingQuery,
  'MissingBatchFetchParams':     MissingFetchParams,
  'MissingNameValuePairs':       MissingNameValuePairs,
  'MissingCustomerID':           MissingCustomerID,
  'MissingCustomerKey':          MissingCustomerKey,
  'MissingSecretKey':            MissingSecretKey,
  'MissingTrigger':              MissingTrigger,

  'InvalidVersion':              InvalidVersion,
  'InvalidTime':                 InvalidTime,
  'InvalidLongitude':            InvalidLongitude,
  'InvalidLatitude':             InvalidLatitude,
  'InvalidTTL':                  InvalidTTL,
  'ParameterValueExceeded':      ParameterValueExceeded,
  'InvalidParameterValue':       InvalidParameterValue,
  'InvalidObjectID':             InvalidObjectID,
  'InvalidFeed':                 InvalidFeed,
  'InvalidZoneID':               InvalidZoneID,
  'InvalidFenceID':              InvalidFenceID,
  'TooBigRegion':                TooBigRegion,
  'InvalidRegion':               InvalidRegion,
  'InvalidRadius':               InvalidRadius,
  'InvalidPolygon':              InvalidPolygon,
  'InvalidCallbackType':         InvalidCallbackType,
  'InvalidCallbackURL':          InvalidCallbackURL,
  'InvalidPredicate':            InvalidQuery,
  'InvalidQuery':                InvalidQuery,
  'InvalidTrigger':              InvalidTrigger,
  'TooBigFetch':                 TooBigFetch,
  'InvalidMimeType':             InvalidMimeType,
  'InvalidStartKey':             InvalidStartKey,

  'ObjectAlreadyExists':         ObjectAlreadyExists,
  'ObjectDoesNotExist':          ObjectDoesNotExist,
  'ZoneAlreadyExists':           ZoneAlreadyExists,
  'ZoneDoesNotExist':            ZoneDoesNotExist,
  'FenceAlreadyExists':          FenceAlreadyExists,
  'FenceDoesNotExist':           FenceDoesNotExist,
  'ObjectDoesNotHaveLocation':   ObjectDoesNotHaveLocation,
  'FenceAlreadyInActive':        FenceAlreadyInactive,
  'FenceAlreadyActive':          FenceAlreadyActive,
  'ZoneAlreadyInActive':         ZoneAlreadyInactive,
  'ZoneAlreadyActive':           ZoneAlreadyActive,

  'FeedAlreadyExists':           FeedAlreadyExists,
  'FeedDoesNotExist':            FeedDoesNotExist,
  'FeedNotEmpty':                FeedNotEmpty,
  'InvalidGridBoundingBox':      InvalidGridBoundingBox,

  'InternalSystemError':         InternalSystemError
}
