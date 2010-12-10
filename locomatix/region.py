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

from response_objects import PrintableAttributes

class LocomatixRegion(PrintableAttributes):
  """An abstract region object from which all regions will be derived."""
  def __init__(self, params):
    self._params = params

class Point(LocomatixRegion):
  """An point object that takes in latitude and longitude"""
  def __init__(self, latitude, longitude):
    self.latitude = latitude
    self.longitude = longitude
    params = { 
      'latitude' : self.latitude, 'longitude' : self.longitude \
    }
    super(Point, self).__init__(params)
    
class Circle(LocomatixRegion):
  """An circle region object. A circle can be specified in two ways
     Absolute --- takes in center latitude, longitude and radius
     Relative --- takes in just the radius."""
  def __init__(self, *val):

    absolute = lambda x : len(x) == 3
    relative = lambda x : len(x) == 1

    def _init_relative(*args):
      self.type = 'Circle'
      self.radius = args[0] 
      self.params = {
        'region' : 'Circle', 'radius' : self.radius \
      }
      return True

    def _init_absolute(*args):
      self.type = 'Circle'
      self.latitude = args[0]
      self.longitude = args[1]
      self.radius = args[2]
      self.params = { 
        'region' : 'Circle', 'radius' : self.radius, \
        'latitude' : self.latitude, 'longitude' : self.longitude \
      }
      return True

    success = _init_absolute(*val) if absolute(val) else False

    if not success:
      success = _init_relative(*val) if relative(val) else False

    if not success:
      raise ValueError("mismatch in number of arguments to Circle")

    super(Circle, self).__init__(self.params)
