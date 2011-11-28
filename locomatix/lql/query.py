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
class Query(object):
  """An base query class."""
  def __init__(self, query):
    self._query = query

def From(*val):

  with_objectids = lambda x : len(x) > 2
  with_objectid = lambda x : len(x) == 2
  with_feed = lambda x : len(x) == 1

  def _init_with_objectid(*args):
    feed = args[0]
    oid = args[1]
    query = 'FROM %s WITH oid "%s"' % (args[0], args[1])
    return query

  def _init_with_objectids(*args):
    feed = args[0]
    oids = '","'.join(args[1:])
    query = 'FROM %s WITH oid IN ("%s")' % (args[0], oids)
    return query

  def _init_with_feed(*args):
    feed = args[0]
    query = 'FROM %s' % (args[0])
    return query

  query = _init_with_objectids(*val) if with_objectids(val) else None

  if query == None:
    query = _init_with_objectid(*val) if with_objectid(val) else None

  if query == None:
    query = _init_with_feed(*val) if with_feed(val) else None

  if query == None:
    raise ValueError("mismatch in number of arguments")
  
  return query

class SelectObject(Query):
  def __init__(self, *args):
    query = 'SELECT * %s ' % (From(*args))
    super(SelectObject, self).__init__(query)

class SelectLocation(Query):
  def __init__(self, *args):
    query = 'SELECT LOCATION.* %s ' % (From(*args))
    super(SelectLocation, self).__init__(query)

class SelectCountLocation(Query):
  def __init__(self, *args):
    query = 'SELECT COUNT(LOCATION.*) %s ' % (From(*args))
    super(SelectCountLocation, self).__init__(query)

class SelectObjectLocation(Query):
  def __init__(self, *args):
    query = 'SELECT *, LOCATION.* %s ' % (From(*args))
    super(SelectObjectLocation, self).__init__(query)

class LqlQueryZone(Query):
  """A zone query"""
  def __init__(self, query):
    super(LqlQueryZone, self).__init__(query)

class LqlQueryFence(Query):
  """A fence query"""
  def __init__(self, query):
    super(LqlQueryFence, self).__init__(query)
