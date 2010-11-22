#!/usr/bin/env python

import sys
import string
import time
import socket
import xml.sax
import locomatix

import cgi
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class AlertResponseHandler(xml.sax.ContentHandler):

  def __init__(self):
    self.zone = None
    self.objects = []
    self.curr_object = None
    self.curr_text = ''

  def startElement(self, name, attrs):
    if name == 'Object':
      self.curr_object = locomatix.LxObject() 

  def endElement(self, name):
    if name == 'ZoneID':
      self.zone = self.curr_text 
    elif name == 'Action':
      self.action = self.curr_text
    elif name == 'Feed':
      self.curr_object.feed = self.curr_text
    elif name == 'ObjectID':
      self.curr_object.objectid = self.curr_text 
    elif name == 'Object':
      self.objects.append(self.curr_object)

    self.curr_text = ''

  def characters(self, content):
    self.curr_text += content.strip()

class AlertErrorHandler(xml.sax.ErrorHandler):
  def __init__(self):
    pass

  def error(self, exception):
    import sys
    print "Error, exception: %s\n" % exception

  def fatalError(self, exception):
    print "Fatal Error, exception: %s\n" % exception

class CarAlertHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    pass

  def do_POST(self):
    global rootnode

    try:
      ctype, pdict = cgi.parse_header(self.headers.getheader('Content-Type'))
      length = int(self.headers.getheader('Content-Length'))
        
      if ctype == 'text/xml':
        qs = self.rfile.read(length)
        self.body = cgi.parse_qs(qs)
        alertxml = self.body['Alert'][0] 
 
        self.send_response(200)
        self.send_header("Content-type", 'text/html')
        self.end_headers()
        self.wfile.write("<HTML>POST OK.<BR><BR></HTML>") 

        handler = AlertResponseHandler()
        xml.sax.parseString(alertxml, handler, AlertErrorHandler()) 
        print "%s received alert for speedtrap %s" % \
            (handler.zone, handler.objects[0].objectid)

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
