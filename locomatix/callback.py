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

class LocomatixCallback(PrintableAttributes):
  """An abstract callback object from which all callbacks are derived."""
  def __init__(self, params):
    self._params = params
  
class URLCallback(LocomatixCallback):
  def __init__(self, url):
    self.type = 'url'
    self.url = url
    params = { 'callbacktype':'url', 'callbackurl': url }
    super(URLCallback, self).__init__(params)

  def to_map(self):
    params = dict()
    params['lxtype'] = 'LxCallback'
    params['type'] = self.type
    params['url'] = self.url

class ApplePushCallback(LocomatixCallback):
  def __init__(self, message, sound, token):
    self.type = 'applepushnotification'
    self.message = message
    self.sound = sound
    self.token = token
    params = { 
               'callbacktype':'applepushnotification', \
               'applepushmessage' : message,  \
               'applepushsound' : sound,  \
               'applepushtoken' : token  \
             }

    super(ApplePushCallback, self).__init__(params)

  def to_map(self):
    params = dict()
    params['lxtype'] = 'LxCallback'
    params['type'] = self.type
    params['message'] = self.message
    params['sound'] = self.sound
    params['token'] = self.token

def createCallback(params):
  ''' Create the appropriate instance of the callback from the map'''
  if params['type'] == 'url':
    return URLCallback(params['url'])

  elif params['type'] == 'applepushnotification':
    return ApplePushCallback(params['message'], params['sound'], params['token'])

  return None
