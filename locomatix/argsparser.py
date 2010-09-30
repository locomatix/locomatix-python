import os
import sys
import getopt

from defaults import * 

class ArgsParser:

      def __init__(self):

          self.pargs = []
          self.description = ''

          self.oargs = []
          self.opts  = dict()

          self.rargs = []
          self.ropts  = dict()

          self.args = dict()

          self.args['use-ssl'] = True
          self.args['host'] = DEFAULT_LOCOMATIX_HOST
          self.args['port'] = DEFAULT_LOCOMATIX_PORTS[self.args['use-ssl']]

          # Add the standard set of options
          self.add_roption('custid',     'c:', 'custid=',    'Customer ID for authentication')
          self.add_roption('key',        'k:', 'key=',       'Key for authentication')
          self.add_roption('secret-key', 's:', 'secret-key=','Secret key for authentication')
          self.add_option('help',       'h',  'help',       'Print help message')

          # Read the credentials from the locomatix startup file, if it exists
          myhome = os.path.expanduser('~')
          config_file = os.path.join(myhome, '.lxrc')
          try:
              handle = open(config_file, 'r')

          except IOError :
              pass
          else:
              igot = handle.readlines()
              for line in igot:
                  about = line.split()
                  if about == [] or len(about) < 3:
                     continue
                  if about[0] == 'custid':
                     self.args['custid'] = about[2]
                  elif about[0] == 'key':
                     self.args['key'] = about[2]
                  elif about[0] == 'secret_key':
                     self.args['secret-key'] = about[2]
                  elif about[0] == 'host':
                     self.args['host'] = about[2]
                  elif about[0] == 'port':
                     self.args['port'] = int(about[2])
                  elif about[0] == 'use_ssl':
                     option = about[2].lower()
                     self.args['use-ssl'] = True if option in ('yes','true') else False
              handle.close()

      def add_option(self, option, sopt, lopt, help, multiple=False):
          hsopt = '' if sopt == '' else '-' + sopt.split(':')[0]
          hlopt = '' if lopt == '' else '--' + lopt.split('=')[0]

          self.oargs.append(option)
          self.opts[option] = [ sopt, hsopt, lopt, hlopt, help, multiple]
          self.args[option] = [] if multiple else ''

      def add_roption(self, option, sopt, lopt, help, multiple=False):
          hsopt = '' if sopt == '' else '-' + sopt.split(':')[0]
          hlopt = '' if lopt == '' else '--' + lopt.split('=')[0]

          self.rargs.append(option)
          self.ropts[option] = [ sopt, hsopt, lopt, hlopt, help, multiple ]
          self.args[option] = [] if multiple else ''

      def add_arg(self, arg, help):
          self.pargs.append([arg, help])

      def add_description(self, desc):
          self.description = desc

      def parse_args(self, sysargs):

          opargs = self.args

          all_sopts = ''.join([i[0] for i in self.opts.values()] + \
                              [i[0] for i in self.ropts.values()])

          all_lopts = [i[2] for i in self.opts.values()] + \
                      [i[2] for i in self.ropts.values()]

          try:
              opts, args = getopt.gnu_getopt(sysargs[1:], all_sopts, all_lopts) 
              for o, a in opts:
                  for i in range(len(self.oargs)):
                      if o in (self.opts[self.oargs[i]][1], self.opts[self.oargs[i]][3]): 
                         if self.opts[self.oargs[i]][5]:
                            opargs[self.oargs[i]].append(a)
                         else:
                            opargs[self.oargs[i]] = a

                  for i in range(len(self.rargs)):
                      if o in (self.ropts[self.rargs[i]][1], self.ropts[self.rargs[i]][3]):  
                         if self.ropts[self.rargs[i]][5]:
                            opargs[self.rargs[i]].append(a)
                         else:
                            opargs[self.rargs[i]] = a

          except getopt.GetoptError, err:
              print str(err)
              self.usage(sysargs)
              sys.exit(1)

          if len(args) < len(self.pargs):
             self.usage(sysargs)
             sys.exit(1)
          
          for arg in self.rargs:
            if arg not in opargs or opargs[arg] == '' or len(opargs[arg]) < 1:
              print 'Missing required argument %s' % (arg)
              self.usage(sysargs)
              sys.exit(1)

          if 'custid' not in opargs or 'key' not in opargs or 'secret-key' not in opargs:
             print 'Missing security credentials. You can do one of the following ', '\n'
             print '  a) Setup .lxrc with security credentials in your home dir'
             print '  b) Pass the security credentials as command line options', '\n'
             self.usage(sysargs)
             sys.exit(1)

          ipargs = [x[0] for x in self.pargs]
          opargs.update(dict(zip(ipargs, args)))
          return opargs

      def usage(self, sysargs):
          print 'usage: ', sysargs[0], '[OPTIONS]', 

          for i in range(len(self.rargs)):
              rargs = self.ropts[self.rargs[i]]
              print '[', rargs[1]+' |', rargs[3], ']', self.rargs[i],

          for i in range(len(self.pargs)):
              print self.pargs[i][0], 

          print '\n\n', self.description, '\n'

          if len(self.rargs) > 0: print 'Required arguments:'
          for i in range(len(self.rargs)):
              rargs = self.ropts[self.rargs[i]]
              print '  ', rargs[1]+',', rargs[3].ljust(20, ' '), rargs[4]

          # if len(self.pargs) > 0: print 'Positional arguments:'
          for i in range(len(self.pargs)):
              print '  ', self.pargs[i][0].ljust(24, ' '), self.pargs[i][1]

          if len(self.oargs) > 0: print '\nOptional arguments:'
          for i in range(len(self.oargs)):
              oargs = self.opts[self.oargs[i]]
              print '  ', oargs[1]+',', oargs[3].ljust(20, ' '), oargs[4]
