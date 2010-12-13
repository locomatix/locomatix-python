#!/usr/bin/env python

import sys
import string
import time
import socket
import locomatix
try: import simplejson as json
except ImportError: 
  try: import json
  except ImportError:
    raise ImportError("simplejson is not installed. Please download it from http://code.google.com/p/simplejson/")
import cgi
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class CarAlertHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    pass

  def do_POST(self):
    global rootnode

    try:
      ctype, pdict = cgi.parse_header(self.headers.getheader('Content-Type'))
      length = int(self.headers.getheader('Content-Length'))
      
      if ctype == 'application/json' or ctype == 'text/xml':
        qs = self.rfile.read(length)
        self.body = cgi.parse_qs(qs)
 
        self.send_response(200)
        self.send_header("Content-type", 'text/html')
        self.end_headers()
        self.wfile.write("<HTML>POST OK.<BR><BR></HTML>") 

        data = json.loads(self.body['Alert'][0])
        for object in data['Ingress']:
          print "%s received alert for speedtrap %s" % (data['ZoneID'], object['ObjectID'])
    except:
      print "error occurred" 

def main():
  host = socket.gethostname()
  port = 60000
  try:
    httpd = HTTPServer((host, port), CarAlertHandler)
    print 'Speed alerts will be received at the url http://%s:%d' % (host, port)
    httpd.serve_forever()

  except socket.error, (errno, errmsg):
    print 'Could not start web server - %s' % (errmsg)
    sys.exit(1)

  except KeyboardInterrupt:
    print 'shutting down server'
    httpd.socket.close()

if __name__ == '__main__':
  main()
