#!/usr/bin/env python
#
# use this to parse a set of data files containing json/hessian api DATA loglines
#
#03-22 15:24:07.599 10708  Hessdroid  D  DATA Sent:698 Recv:999 RTT:2900 Rcode:200 meth:foo()
#03-22 18:26:04.982 21930  VerizonCNI.JsonApi  D  DATA Sent:251 Recv:10760 RTT:372 Rcode:200 meth:getAssets
#
# generate them via
#   ./bin/logcat --network --re .*DATA.* 
#
# generators tutorial: http://www.dabeaz.com/generators-uk/
#

from optparse import OptionParser
import sys, os, fnmatch
import gzip, bz2
import re

def trace(source):
   for item in source:
      print item
      yield item

def gen_find(filepat,top):
   for path, dirlist, filelist in os.walk(top):
      #for name in filelist:
      for name in fnmatch.filter(filelist,filepat):
         #print os.path.join(path,name)
         yield os.path.join(path,name)

def gen_open(filenames):
   for name in filenames:
      if name.endswith(".gz"):
         yield gzip.open(name)
      elif name.endswith(".bz2"):
         yield bz2.BZ2File(name)
      else:
         yield open(name)

def gen_cat(sources):
   for s in sources:
      for item in s:
         yield item

def gen_grep(pat, lines):
   patc = re.compile(pat)
   for line in lines:
      if patc.search(line): 
         yield line


# get lines from file regex in directory
def lines_from_dir(filepat, dirname):
   names = gen_find(filepat, dirname)
   #names = trace(gen_find(filepat, dirname))
   files = gen_open(names)
   lines = gen_cat(files)
   return lines


# sum bytes transferred; grep on entire line, parse via rsplit()
def sum_bytes_loglines(pattern, lines):
   patlines = gen_grep(pattern, lines)
   bytecolumn = (line.rsplit(None,1)[1] for line in patlines)
   bytes = (int(x) for x in bytecolumn if x != '-')
   print "bytes total:", sum(bytes)


def field_map(dictseq,name,func):
   for d in dictseq:
      d[name] = func(d[name])
      yield d

# parse DATA log lines into dicts
# 03-22 15:24:07.599 10708             Hessdroid  D  DATA Sent:698 Recv:999 RTT:2900 Rcode:200 meth:com.wavemarket.finder.core.v2.api.AuthService.auth_TCredentialContainer_string()
def data_logs_to_dict(lines):
   logpats = r'(\S+) (\S+) (\S+) *(\S+)  [VDIWE]  DATA Sent:(\S+) Recv:(\S+) RTT:(\S+) Rcode:(\S+) meth:(\S+)'
   logpat = re.compile(logpats)
   #for line in lines: print line;
   groups = (logpat.match(line) for line in lines)
   tuples = (g.groups() for g in groups if g)
   colnames = ('date','timestamp','threadid','transport','sent','recv','rtt','rcode','method')
   log = (dict(zip(colnames,t)) for t in tuples)
   log = field_map(log, "sent", lambda s: int(s) if s != '-' else 0)
   log = field_map(log, "recv", lambda s: int(s) if s != '-' else 0)
   log = field_map(log, "rtt", lambda s: int(s) if s != '-' else 0)
   log = field_map(log, "rcode", int)
   return log


# tuple-processors
#

def sum_bytes(dicts):
   print "bytes total:", sum(r['sent'] + r['recv'] for r in dicts)

def print_large_transfers(dicts):
   large = (r for r in dicts if r['sent']+r['recv'] > 100000)
   for r in large: print r['method'], r['sent']+r['recv']

def print_largest(dicts):
   print "largest:  %d %s" % max((r['sent']+r['recv'],r['method']) for r in dicts)

def print_maxrtt(dicts):
   print "max rtt:  %d %s" % max((r['rtt'],r['method']) for r in dicts)

def count_occurances(methodname, dicts):
   return sum(1 for r in dicts if methodname in r['method'])



# main
#
def main(args=sys.argv):
   parser = OptionParser()
   parser.add_option("-f", "--filespec",
                     action="store", type="string", dest="filespec",
                     default="*.DATA")
   parser.add_option("-d", "--dir",
                     action="store", type="string", dest="dirname",
                     default="./data")
   parser.add_option("-g", "--grep",
                     action="store", type="string", dest="grep",
                     default="getAssets")
   (options, args) = parser.parse_args(args)
   print "options:", options



   ## tuple-ize, work with tuples: easy

   loglines = lines_from_dir(options.filespec, options.dirname)
   dicts = data_logs_to_dict(loglines)
   sum_bytes(dicts)

   loglines = lines_from_dir(options.filespec, options.dirname)
   dicts = data_logs_to_dict(loglines)
   print_maxrtt(dicts)

   loglines = lines_from_dir(options.filespec, options.dirname)
   dicts = data_logs_to_dict(loglines)
   print_largest(dicts)

   loglines = lines_from_dir(options.filespec, options.dirname)
   dicts = data_logs_to_dict(loglines)
   print_large_transfers(dicts)

   loglines = lines_from_dir(options.filespec, options.dirname)
   dicts = data_logs_to_dict(loglines)
   print "Occurrences of '"+options.grep+ "':", count_occurances(options.grep, dicts)


   ## sum w/ our rsplit parser: fast
   #loglines = lines_from_dir(options.filespec, options.dirname)
   #sum_bytes_loglines(options.grep, loglines)



if __name__ == '__main__':
    main()

