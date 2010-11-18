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
    self.from_feeds = []

class LxZone(PrintableAttributes):
  """Represents a locomatix zone."""
  def __init__(self):
    self.zoneid = None
    self.objectid = None
    self.feed = None
    self.object_region = None
    self.trigger = None
    self.callback = None
    self.all_feeds = False
    self.from_feeds = []
