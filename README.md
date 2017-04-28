Realtime Location Tracker
=========================

relot is a REaltime LOcation Tracker.

## Platform

MacOSX and Linux

## Requirements

- OpenLayers-2.13.1
- lighttpd
- mod_websocket
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
         | GPS DB     |       |           | <----------- |         |
         |   CSV      |       |           | -----------> |         |
         |   MongoDB  |       |  lighttpd |              |         |
         |   etc...   |       |           | GET Start WS |         |
         +------------+       |    +------|------------- |         |
            A |               |    |      |              |         |
    polling | | res.          +-----------+              | Browser |
            | |                    |                     |         |
            | V                    V                     |         |
         +----------+         +-----------+              |         |
         | GPS Data |         |    mod    | <===(WS)===> |         |
         |  Server  | ------> | websocket | -----------> |         |
         +----------+  Send   +-----------+     Send     +---------+
                     GPS data                 GPS data

## mod websocket

lighttpd の websocket module.

https://github.com/nori0428/mod_websocket

    % git clone --recursive git://github.com/nori0428/mod_websocket.git 

### How to build mod_websocket

    apt-get install -y autoconf libtool

makeとか設定方法など。

https://github.com/nori0428/mod_websocket/blob/master/INSTALL

conrtib/lighttpd にあるバージョン以外を使う場合は lighttpd 1.4 のソースが必要になる。

<s>makefile が mod_websocket 以下の一部にディレクトリを作るので、</s>
<s>root で make install すると、後から一般ユーザで make できなくなる。</s>

    % cd mod_websocket
    % ./bootstrap
    % ./configure --with-websocket=all --with-test
    % make clean check
    ============================================================================
    Testsuite summary for mod_websocket 3.5
    ============================================================================
    # TOTAL: 4
    # PASS:  4
    # SKIP:  0
    # XFAIL: 0
    # FAIL:  0
    # XPASS: 0
    # ERROR: 0
    ============================================================================

    % ./configure --with-lighttpd=`pwd`/contrib/lighttpd1.4
    % make install
        :
    Target Lighttpd version: lighttpd-1.4.46
    do patch? [y/n]

で y と答える。

    % cd contrib/lighttpd1.4
    % apt-get install -y libssl-dev libbz2-dev zlib1g-dev libpcre3-dev

お好みで --prefix でディレクトリを変える。
以降、BASEDIR で参照する。

    e.g.
    % BASEDIR=${HOME}/lorawan/local

    % ./configure --with-websocket=all --with-openssl --prefix=${BASEDIR}
    % make
    % make install

    % mkdir -p ${BASEDIR}/etc/lighttpd
    % cp doc/config/lighttpd.conf ${BASEDIR}/etc/lighttpd/
    % cp doc/config/modules.conf ${BASEDIR}/etc/lighttpd/
    % cp -r doc/config/conf.d ${BASEDIR}/etc/lighttpd/

起動に必要なディレクトリを作っておく。

    % mkdir -p ${BASEDIR}/var/log/lighttpd
    % mkdir -p ${BASEDIR}/var/run
    % mkdir -p ${BASEDIR}/www

### パッチがあたらないバージョンの場合

    % git clone https://github.com/lighttpd/lighttpd1.4.git
    % ./configure --with-lighttpd=`pwd`/lighttpd1.4
    % make install
        :
    Target Lighttpd version: lighttpd-1.4.46
    do patch? [y/n]

で n と答えて、がんばって手で当ててから、lighttpd をmakeする。

### lighttpd.conf

ディレクトリを合わせる。
websocket.server を設定する。
XXX host は...

    % vi lighttpd.conf
    websocket.server = ( "/demo" => ( "host" => "127.0.0.1", "port" => 49001 ) )

    --- lighttpd.conf.orig  2017-04-28 10:41:21.385166150 +0900
    +++ lighttpd.conf       2017-04-28 10:46:18.913172134 +0900
    @@ -13,11 +13,12 @@
     ## if you add a variable here. Add the corresponding variable in the
     ## chroot example aswell.
     ##
    -var.log_root    = "/var/log/lighttpd"
    -var.server_root = "/srv/www"
    -var.state_dir   = "/var/run"
    -var.home_dir    = "/var/lib/lighttpd"
    -var.conf_dir    = "/etc/lighttpd"
    +var.base_dir    = "/home/takumori/lorawan/local"
    +var.log_root    = base_dir + "/var/log/lighttpd"
    +var.server_root = base_dir + "/www"
    +var.state_dir   = base_dir + "/var/run"
    +var.home_dir    = base_dir + "/lib/lighttpd"
    +var.conf_dir    = base_dir + "/etc/lighttpd"
     
     ## 
     ## run the server chrooted.
    @@ -85,7 +86,7 @@
     ##  Basic Configuration
     ## ---------------------
     ##
    -server.port = 80
    +server.port = 49002
     
     ##
     ## Use IPv6?
    @@ -446,3 +447,6 @@
     #include_shell "cat /etc/lighttpd/vhosts.d/*.conf"
     ##
     #######################################################################
    +
    +websocket.server = ( "/demo" => ( "host" => "127.0.0.1", "port" => 49001 ) )
    +

### 起動

    起動。/usr/local/lighttpd/sbin にインストールしている場合。

    ${BASEDIR}/sbin/lighttpd -f ${BASEDIR}/etc/lighttpd/lighttpd.conf -D

"-D" はバックグラウンドで起動*しない*。

    > tcp6       0      0 :::49002       :::*        LISTEN

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

