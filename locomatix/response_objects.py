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

class PrintableAttributes(object):
  """Base class for all objects returned in locomatix responses."""
  def __str__(self):
    """Returns a json-like representation of the object"""
    params = self.__dict__
    if '_params' in params:
      del params['_params']
    return str(params)

  def __repr__(self):
    """Returns a json-like representation of the object"""
    params = self.__dict__
    if '_params' in params:
      del params['_params']
    return str(params)


class LxObject(PrintableAttributes):
  """Represents a locomatix object."""
  def __init__(self):
    self.objectid = None
    self.feed = None
    self.name_values = dict()
    self.location = None

class LxLocation(PrintableAttributes):
  """Represents a locomatix location."""
  def __init__(self):
    self.objectid = None
    self.feed = None
    self.name_values = dict()
    self.longitude = None
    self.latitude = None
    self.time = None
    self.name_values = dict()

class LxFence(PrintableAttributes):
  """Represents a locomatix fence."""
  def __init__(self):
    self.fenceid = None
    self.region = None
    self.trigger = None
    self.callback = None
    self.all_feeds = False
    self.predicate = None
    self.name_values = dict()
    self.state = None

class LxZone(PrintableAttributes):
  """Represents a locomatix zone."""
  def __init__(self):
    self.zoneid = None
    self.objectid = None
    self.feed = None
    self.region = None
    self.trigger = None
    self.callback = None
    self.all_feeds = False
    self.predicate = None
    self.name_values = dict()
    self.state = None
