usage-analysis
==============

_handset-to-server RPC data usage analysis_

use this to parse and tuple-ize a set of data files containing json/hessian api DATA loglines

* 03-22 15:24:07.599 10708  Hessdroid  D  DATA Sent:698 Recv:999 RTT:2900 Rcode:200 meth:foo()
* 03-22 18:26:04.982 21930  VerizonCNI.JsonApi  D  DATA Sent:251 Recv:10760 RTT:372 Rcode:200 meth:getAssets

and the take the yielded dictionaries and a set of token-processors to 
provides some key stats such as:

* total sent+recv bytes sum
* max rtt
* list of large (>100K) transfers, 
* largest single transfer
* occurrance count of a given method (eg, background update loop)


one way to do this is to generate the DATA via some kind of adb logcat wrapper, ala

```shell
$ ./bin/logcat --network --re .*DATA.* 
```

regardless, once you have the data....

run the script:

```shell
$ bin/count-data.py
[options: {'filespec': '*.DATA', 'grep': 'getAssets', 'dirname': './data'} ]
bytes total: 2063219
max rtt:  11396 ContactsService.getContacts_TAuthToken_long()
largest:  59901 getApplications
occurrences of 'getAssets': 18
```

approach is based on the python generators tutorial: http://www.dabeaz.com/generators-uk/

