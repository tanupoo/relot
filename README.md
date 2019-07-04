Realtime Location Tracker
=========================

relot is a REaltime LOcation Tracker.

## Platform

MacOSX and Linux

## Requirements

- OpenLayers-2.13.1
- mongodb (option)

## goal

### Browser

- n秒毎に定期的に自動更新する。(n > 10)
- マーカーは n 個 (n > 5)
- マーカーが動く。
- 指定したマーカーを中心に地図が動く。
- マーカーの値がなければ過去の値を引き継ぐ。

### GPS Data Server + DB

- マーカー毎の過去 n秒間の最新値を返す。
- 値がなければ対応するjsonオブジェクトを送らない。
- longitude, latitudeの変位が半径 n以下ならjsonオブジェクトを送らない。

## Basic Architecture

            | input somehow                       
            v      
         +------------+       +-----------+  Start Page  +---------+
         | GPS DB     |       |           | 65482        |         |
         |   CSV      |       | relots.py | <----------> |         |
         |   MongoDB  |       |           | -----------> |         |
         |   etc...   |       |           |              |         |
         +------------+       |           |              |         |
            A |               |           |              |         |
    polling | | res.          +-----------+              | Browser |
            | |                     |                    |         |
            | V                     v                    |         |
         +----------+         +-----------+ 65483        |         |
         | GPS Data |         |           | <===(WS)===> |         |
         |  Server  | ------> | websocket | -----------> |         |
         +----------+  Send   +-----------+     Send     +---------+
                     GPS data                 GPS data

## sample data

GPS Visualizer のKML形式のサンプルデータを拝借。
http://www.ic.daito.ac.jp/~mizutani/gps/data/2013_aug26_toyara.kml

CSV(経度,緯度,高度の順)で保存する。

## relots

This is the GPS data server.

    cd relots
    ln -sf if_mongodb.py if_db.py

    % python relots.py -d 49001 127.0.0.1

### feeder

You have to choice one of feeders.
There are two feeders in this package.

- if_mongodb.py: interface for mongodb
- if_csv.py: interface for csv files.

And, you have to make a symbolic link to if_db.py like below.

    e.g.
    % ln -fs if_test.py if_db.py
    % rm if_db.pyc

### GPS data file

- csvファイルから配る。
- csvファイルのフォーマットは、lon,lat,alt
- 名前はファイル名から取る。

### WebSocketでPUSHするメッセージ形式

e.g.

    {
      "gps": [
        {
          "name":"maker01",
          "date": "2017-03-21T07:01:23.124296",
          "lon": "139.753998",
          "lat": "35.677380",
          "alt": "15"
        },
        {
          "name":"maker02",
          "date": "2017-03-21T07:01:23.124296",
          "lon": "139.753998",
          "lat": "35.677380",
          "alt": "15"
        }
      ]
    }

## browswer

http://localhost:48080/relot/relots.html

- modeは2つ。移動体のマーカーは動かさないで地図を動かす。

