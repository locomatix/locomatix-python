#!/usr/bin/env python
import logging

RAW = 5
REQUEST = 6

class RawResponseFilter(logging.Filter):
  def filter(self, record):
    if record.levelno in [RAW, REQUEST]:
        return True
    return False

logging.basicConfig(format='%(message)s')
logging.addLevelName(RAW, "RAW")
logging.addLevelName(REQUEST, "REQUEST")
logging.getLogger('locomatix').setLevel(logging.INFO)

