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
import time, calendar
import logging
from locomatix import logger

log = logging.getLogger('locomatix')

def dprint(args, response, alt_message):
  if args.get('raw'):
    log.log(logger.RAW, '\nResponse:\n%s' % response)
  else:
    if alt_message:
      print alt_message

def convert_time(sometime):
  if isinstance(sometime, (int, float)):
    return sometime

  try:
    stime = int(sometime)
  except ValueError:
    try:
      stime = float(sometime)
    except ValueError:
      st = time.strptime(sometime, "%m/%d/%Y:%H:%M:%S")
      stime = calendar.timegm(st)

  return stime

def form_nvpairs(argnvpairs):
  nvpairs = dict()
  for anv in argnvpairs:
    nv = anv.split('=')
    name = nv[0].strip()
    value = nv[1].strip()

    if name in nvpairs and isinstance(nvpairs[name], list):
      nvpairs[name].append(value)
    elif name in nvpairs:
      nvlist = [nvpairs[name], value]
      nvpairs[name] = nvlist
    else:
      nvpairs[name] = value

  return nvpairs

