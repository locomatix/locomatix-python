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

class LocomatixObjectRegion(PrintableAttributes):
  """An abstract object region from which all object regions will be derived."""
  def __init__(self, params):
    self._params = params
  
class CircleObjectRegion(LocomatixObjectRegion):
  def __init__(self, radius):
    self.type = 'Circle'
    self.radius = radius
    params = { 'region':'Circle', 'radius': radius }
    super(CircleObjectRegion, self).__init__(params)

