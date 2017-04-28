#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import datetime

csv_files = ["sample/mover.csv"]
#csv_files = ["sample2/sample.csv"]
#csv_files = ["sample/x01.csv", "sample/x02.csv",
#             "sample/x03.csv", "sample/x04.csv",
#             "sample/x05.csv", "sample/x06.csv",
#             "sample/x07.csv" ]

class gpsdata_feed_with_csv_file():

    def __init__(self, csv_files, repeat=True):
        self.repeat_mode = repeat
        self.csv_fds = [ (0, f, open(f, "r")) for f in csv_files ]

    def interested(self, dev_list):
        '''
        not used
        '''
        pass

    def get_latest(self):
        msg_list = []
        for i in range(0, len(self.csv_fds)):
            disabled, name, fd = self.csv_fds[i]
            if disabled:
                continue
            line = fd.readline()
            if not line:
                # seek(0) if repeat mode.  otherwise, close and disables it.
                if not self.repeat_mode:
                    fd.close()
                    self.csv_fds[i] = (1,f,)
                    continue
                fd.seek(0)
                line = fd.readline()
            # parse the line
            v = [ d.strip() for d in line.split(",") ]
            msg_list.append(
                '{"name":"%s","date":"%s","lon":"%s","lat":"%s","alt":"%s"}'
                % (name, datetime.datetime.now().isoformat(), v[0], v[1], v[2]))
        return '{"gps":[' + ','.join(msg_list) + ']}'

class feeder(gpsdata_feed_with_csv_file):

    def __init__(self, debug_level=0):
        self.debug_level = debug_level
        gpsdata_feed_with_csv_file.__init__(self, csv_files, repeat=True)

'''
test code
'''
if __name__ == '__main__' :
    feeder = feeder()
    for i in range(5):
        msg = feeder.get_latest()
        print(msg)
