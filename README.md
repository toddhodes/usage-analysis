usage-analysis
==============

handset to server RPC data usage analysis

use this to parse a set of data files containing json/hessian api DATA loglines

* 03-22 15:24:07.599 10708  Hessdroid  D  DATA Sent:698 Recv:999 RTT:2900 Rcode:200 meth:foo()
* 03-22 18:26:04.982 21930  VerizonCNI.JsonApi  D  DATA Sent:251 Recv:10760 RTT:372 Rcode:200 meth:getAssets

provides total bytes sum, max rtt, largest single, list of large (>100K) transfers, 
and occurrances of a given key method (eg, background update loop)


generate them via the adb logcat wrapper

   ./bin/logcat --network --re .*DATA.* 

then run the script:
```shell
$ bin/count-data.py
[options: {'filespec': '*.DATA', 'grep': 'getAssets', 'dirname': './data'} ]
bytes total: 2063219
max rtt:  11396 com.wavemarket.finder.core.v2.api.ContactsService.getContacts_TAuthToken_long()
largest:  59901 getApplications
occurrences of 'getAssets': 18
```

approach is based on the python generators tutorial: http://www.dabeaz.com/generators-uk/

