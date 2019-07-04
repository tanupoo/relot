import datetime

class feeder():

    def __init__(self, csv_files, simple_data=False, repeat=True, debug=False):
        """
        csv_files: a list of csv files. each file contains a list
        of location data of one node.
        a record must include longitude and latitude.
        """
        self.csv_fds = [ (0, f, open(f, "r")) for f in csv_files ]
        self.simple_data = simple_data
        self.repeat_mode = repeat
        self.debug = debug

    def get(self, dev_list=None, before=None):
        """
        dev_list: device list to be searched.
        before: datetime, specifying the record that has a timestamp
        before the timestamp specified here.
        """
        # it doesn't support.
        return '{"gps":[]}'

    def next(self):
        """
        """
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

"""
test code
csv_files = ["sample/mover.csv"]
#csv_files = ["sample2/sample.csv"]
#csv_files = ["sample/x01.csv", "sample/x02.csv",
#             "sample/x03.csv", "sample/x04.csv",
#             "sample/x05.csv", "sample/x06.csv",
#             "sample/x07.csv" ]
"""
if __name__ == '__main__' :
    import sys
    if len(sys.argv) == 1:
        csv_files = ["sample/mover.csv"]
    else:
        csv_files = sys.argv[1]
    feeder = feeder(csv_files)
    for i in range(5):
        msg = feeder.next()
        print(msg)
