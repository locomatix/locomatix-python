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

import time

class PrintableAttributes(object):
  """Base class for all objects returned in locomatix responses."""
  def __str__(self):
    """Returns a json-like representation of the object"""
    return str(self.params())
  
  def __repr__(self):
    """Returns a json-like representation of the object"""
    return str(self.params())

  def params(self):
    params = {}
    params.update(self.__dict__)
    if '_params' in params:
      del params['_params']
    return params
  
  def to_map(self):
    """Returns a dictionary representation of the object - nested objects as well"""
    pass

  def from_map(self, params):
    """Constructs a dictionary representation of the object - nested objects as well"""
    pass
