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
from objects import PrintableAttributes

class LocomatixRegion(PrintableAttributes):
  """An abstract region object from which all regions will be derived."""
  def __init__(self, rtype, params):
    self.type = rtype
    self._params = params

class Point(LocomatixRegion):
  """An point object that takes in latitude and longitude"""
  def __init__(self, latitude, longitude):
    self.latitude = latitude
    self.longitude = longitude
    params = { 
      'region' : 'Point', 'latitude' : self.latitude, 'longitude' : self.longitude \
    }
    super(Point, self).__init__('Point', params)

  def to_map(self):
    params = dict()
    params['lxtype'] = 'LxRegion'
    params['type'] = self.type
    params['latitude'] = self.latitude
    params['longitude'] = self.longitude

    return params

class Polygon(LocomatixRegion):

  def __init__(self, *args):
      """
      Initializes using a boundary of coordinates

      Example where a tuple parameters are used:
      >>> poly = Polygon([(lat1, long1), (lat2, long2), (lat3, long3), (lat4, long4), (lat1, long1)])
      """
      if not args:
        raise TypeError('Must provide a list of points to initialize a Polygon.')

      if not isinstance(args[0], list):
        raise TypeError('Argument must be a list of points to initialize a Polygon.')

      self.points = args[0]

      pt_list = '|'.join([str(pt[0]) + ',' + str(pt[1]) for pt in self.points])
      params = {
        'region' : 'Polygon', 'points' : pt_list \
      }
      super(Polygon, self).__init__('Polygon', params)

  def to_map(self):
    params = dict()
    params['lxtype'] = 'LxRegion'
    params['type'] = self.type
    params['points'] = self.points

    return params

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
    self.type = 'Rectangle'

  def to_map(self):
    params = dict()
    params['lxtype'] = 'LxRegion'
    params['type'] = self.type

    params['sw_lat'] = self.sw_lat
    params['sw_long'] = self.sw_long
    params['ne_lat'] = self.ne_lat
    params['ne_long'] = self.ne_long

    return params

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

    super(Circle, self).__init__('Circle', params)

  def to_map(self):
    params = dict()
    params['lxtype'] = 'LxRegion'
    params['type'] = self.type

    params['radius'] = self.radius
    if 'latitude' in self.__dict__:
      params['latitude'] = self.latitude

    if 'longitude' in self.__dict__:
      params['longitude'] = self.longitude

    return params

def createRegion(params):
  ''' Create an instance of the appropriate region provided a map'''
  if params['type'] == 'Point':
    return Point(params['latitude'], params['longitude'])

  elif params['type'] == 'Polygon':
    points = params['points']
    pt_list = [(pt['latitude'], pt['longitude']) for pt in points]
    return Polygon(pt_list)
  
  elif params['type'] == 'Circle':
    if 'latitude' in params and 'longitude' in params:
      return Circle(params['latitude'], params['longitude'], params['radius'])
    else:
      return Circle(params['radius'])

  return None
