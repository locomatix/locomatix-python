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


class Polygon(LocomatixRegion):

  def __init__(self, *args):
      """
      Initializes using a boundary of coordinates

      Examples of initialization, where shell is a valid sequence of points geometry:
      >>> poly = Polygon(shell)

      Example where a tuple parameters are used:
      >>> poly = Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])
      """
      if not args:
        raise TypeError('Must provide a list of points to initialize a Polygon.')

      if not isinstance(args[0], list):
        raise TypeError('Argument must be a list of points to initialize a Polygon.')

      self.type = 'Polygon'
      self.points = args[0]

      pt_list = '|'.join([str(pt[0]) + ',' + str(pt[1]) for pt in self.points])
      params = {
        'region' : 'Polygon', 'points' : pt_list \
      }
      super(Polygon, self).__init__(params)

class Rectangle(Polygon):
  """A bounding box object that takes south west corner and north east corner"""
  def __init__(self, sw_lat, sw_long, ne_lat, ne_long):
    self.sw_lat = sw_lat
    self.sw_long = sw_long

    self.ne_lat = ne_lat
    self.ne_long = ne_long

    bbox = [(sw_lat, sw_long), (sw_lat, ne_long), (ne_lat, ne_long), \
             (ne_lat, sw_long), (sw_lat, sw_long)]

    super(Rectangle, self).__init__(bbox)

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
      params = {
        'region' : 'Circle', 'radius' : args[0] \
      }
      return params

    def _init_absolute(*args):
      self.type = 'Circle'
      self.latitude = args[0]
      self.longitude = args[1]
      self.radius = args[2]
      params = { 
        'region' : 'Circle', 'radius' : args[2], \
        'latitude' : args[0], 'longitude' : args[1] \
      }
      return params

    params = _init_absolute(*val) if absolute(val) else None

    if params == None:
      params = _init_relative(*val) if relative(val) else None

    if params == None:
      raise ValueError("mismatch in number of arguments to Circle")

    super(Circle, self).__init__(params)
