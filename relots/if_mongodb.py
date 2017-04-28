#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import json
import pymongo
from datetime import datetime

'''

## The pipeline of the aggregate() to mongodb

    query = [
        { "$group": {
            "_id":"$DevEUI_uplink.DevEUI",
            "latest": { "$last":"$DevEUI_uplink" },
        }},
        { "$project": {
            "_id":0,
            "DevEUI":"$_id",
            "latest":"$latest"
        }}
        ]

if you call interested() method, it's going to be like below.

    query = [
        { "$match":
            { "$or":[
            { "DevEUI_uplink.DevEUI":"000DB53114683543" },
            { "DevEUI_uplink.DevEUI":"BEEF0D0000000001" }
        ]}},
        { "$group": {
            "_id":"$DevEUI_uplink.DevEUI",
            "latest": { "$last":"$DevEUI_uplink" },
        }},
        { "$project": {
            "_id":0,
            "DevEUI":"$_id",
            "latest":"$latest"
        }}
        ]

## The response expected from mongodb

    {
       "latest" : {
          "mic_hex" : "ad8b10fc",
          "DevEUI" : "000DB53114683543",
          "ModelCfg" : "0",
          "Lrrid" : "080E005C",
          "LrrLON" : "139.762070",
          "CustomerData" : {
             "alr" : {
                "pro" : "ADRF/DEMO",
                "ver" : "1"
             }
          },
          "CustomerID" : "100000778",
          "payload_hex" : "000261022039c508541e9b",
          "SpFact" : "12",
          "ADRbit" : "1",
          "Late" : "0",
          "Lrcid" : "00000201",
          "Lrrs" : {
             "Lrr" : {
                "Lrrid" : "080E005C",
                "LrrESP" : "-132.331039",
                "LrrRSSI" : "-115.000000",
                "LrrSNR" : "-17.250000",
                "Chain" : "0"
             }
          },
          "Channel" : "LC1",
          "LrrRSSI" : "-115.000000",
          "Time" : "2017-04-05T12:27:58.523+02:00",
          "LrrSNR" : "-17.250000",
          "MType" : "2",
          "DevLrrCnt" : "1",
          "FCntUp" : "10332",
          "SubBand" : "G0",
          "FPort" : "2",
          "FCntDn" : "667",
          "LrrLAT" : "35.663242",
          "DevAddr" : "14683543"
       },
       "DevEUI" : "000DB53114683543"
    }

'''

class gpsdata_feed_with_mongodb():

    conn = None
    db = None
    dev_list = []
    query = [
        { "$group": {
            "_id":"$DevEUI_uplink.DevEUI",
            "latest": { "$last":"$DevEUI_uplink" },
        }},
        { "$project": {
            "_id":0,
            "DevEUI":"$_id",
            "latest":"$latest"
        }}
        ]

    def __init__(self, port=27017):
        try:
            self.conn = pymongo.MongoClient(port=port)
        except BaseException as e:
            print("ERROR: ", e)
        self.db = self.conn.lorawan # XXX should be passed from the config
        self.coll = self.db.app     # XXX should be passed from the config

    def interested(self, dev_list):
        ''' set the list of DevEUI you are interested in.
        '''
        self.dev_list = dev_list
        if len(dev_list) == 0:
            return
        elif len(dev_list) == 1:
            self.query[0].append({"$match":{
                    "DevEUI_uplink.DevEUI":dev_list[0] }})
            return
        self.query[0].append({"$match":{ "$or": [
                { "DevEUI_uplink.DevEUI":n } for n in dev_list ] }})

    def get_latest(self):
        if self.debug_level >= 3 :
            print("DEBUG: MONGODB: BEGIN OF QUERY")
            print(self.query)
            print("DEBUG: MONGODB: END OF QUERY")
        res = list(self.coll.aggregate(self.query))
        if self.debug_level >= 3 :
            print("DEBUG: MONGODB: BEGIN OF RESPONSE")
            print(res)
            print("DEBUG: MONGODB: END OF RESPONSE")
        # make a response
        msg_list = []
        for r in res:
            # parse the line
            if not r.get("latest") or not r["latest"].get("__app_data"):
                print("ERROR: invalid response (no latest nor __app_data) from mongodb")
                return ""
            name = r.get("DevEUI")
            lon = r["latest"]["__app_data"].get("longitude")
            lat = r["latest"]["__app_data"].get("latitude")
            alt = r["latest"]["__app_data"].get("altitude")
            if not lon or not lat:
                print("ERROR: invalid app message (no longitude nor latitude) from mongodb")
                return ""
            msg_list.append(
                '{"name":"%s","date":"%s","lon":"%s","lat":"%s","alt":"%s"}'
                % (name, datetime.now().isoformat(), lon, lat, alt))
        return '{"gps":[' + ','.join(msg_list) + ']}'

class feeder(gpsdata_feed_with_mongodb):

    def __init__(self, debug_level=0):
        self.debug_level = debug_level
        gpsdata_feed_with_mongodb.__init__(self)

'''
test code
'''
if __name__ == '__main__' :
    feeder = feeder(debug_level=3)
    feeder.interested(["2000000000000002"])
    for i in range(5):
        msg = feeder.get_latest()
        print(msg)
