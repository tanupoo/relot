var ws;
var ol_map;
var ol_markers;
var epsg4326;
var epsg900913;
var zoom = 17; 
var lon_center = 0;
var lat_center = 0;
var mdb = {}; /* marker database. */
var view_mode = 2; /* 1: sticky map, 2: sticky marker */
var tracing_mode = 0; /* 0: move, 1: trace */

function map_init()
{
  ol_map = new OpenLayers.Map("basicMap");
  epsg4326 = new OpenLayers.Projection("EPSG:4326");
  epsg900913 = new OpenLayers.Projection("EPSG:900913");
  var mapnik = new OpenLayers.Layer.OSM();
  ol_markers = new OpenLayers.Layer.Markers("Markers");

  ol_map.addLayer(mapnik);
  ol_map.addLayer(ol_markers);
  ol_map.setCenter([], zoom);
}

/*
 * put the marker into the new position.
 * put the new position into db.pos_new.
 */
function marker_put(m)
{
  var pos = new OpenLayers.Marker(
      new OpenLayers.LonLat(m.lon, m.lat).transform(epsg4326, epsg900913));
  ol_markers.addMarker(pos);
  mdb[m.name].pos_new = pos;
}

/*
 * check whether the marker moves more than N meters.
 */
function marker_is_significant_move(m) {
  //XXX TBD
  return 1;
}

/*
 * remove the marker at the old position.
 */
function marker_remove_old(m)
{
  if (mdb[m.name].pos_current) {
    ol_markers.removeMarker(mdb[m.name].pos_current);
  }
}

/*
 * update the marker's info.
 */
function marker_update(m)
{
  mdb[m.name].date= m.date;
  mdb[m.name].lon = m.lon;
  mdb[m.name].lat = m.lat;
  mdb[m.name].alt = m.alt;
  mdb[m.name].pos_current = mdb[m.name].pos_new;
}

/*
 * if the marker does not exist in the db, create one.
 */
function marker_setone(m)
{
  if (!mdb[m.name])
    mdb[m.name] = {};
}

function marker_move(m)
{
  marker_setone(m);
  if (marker_is_significant_move(m)) {
    marker_put(m);
    if (!tracing_mode)
      marker_remove_old(m);
  }
  marker_update(m);
}

function marker_center(lon, lat)
{
  var pos = new OpenLayers.LonLat(lon, lat).transform(epsg4326, epsg900913);
  ol_map.setCenter(pos);
}

function ws_open()
{
  ws = new WebSocket("ws://127.0.0.1:49002/relot/feed");

  ws.onopen = function(ev)
  {
    document.getElementById("boxRes").innerHTML = "ws has been opened";
  };

  ws.onmessage = function(ev)
  {
    var msg = JSON.parse(ev.data);
    // XXX need to check the reponse message.
    for (var i = 0; i < msg.gps.length; i++) {
      /*
       * if you want to draw the trace of the marker, call marker_put() below
       * instead of marker_move().
       * marker_put(msg.gps[i].lon, msg.gps[i].lat);
       */
      marker_move(msg.gps[i]);
    }
    if (msg.gps.length > 0 && lon_center == 0 && lat_center == 0) {
      lon_center = msg.gps[0].lon;  /* need to be dynamically set someway */
      lat_center = msg.gps[0].lat;  /* need to be dynamically set someway */
    }
    if (view_mode == 2) {
      marker_center(lon_center, lat_center);
    }
  };

  ws.onerror = function(ev) {
    console.log("ERROR: something error happened on WebSocket");
  };
}

function ev_click_start()
{
  var msg = {
    cmd: "start",
    id: document.getElementById("boxClientID").value,
    interval: document.getElementById("boxInterval").value,
    date: Date.now()
  };
  ws.send(JSON.stringify(msg));
}

function ev_click_stop()
{
  var msg = {
    cmd: "stop",
  };
  ws.send(JSON.stringify(msg));
}

window.addEventListener('load', ev_load, false);

function ev_load()
{
  document.getElementById("btnStart").addEventListener("click", ev_click_start, false);
  document.getElementById("btnStop").addEventListener("click", ev_click_stop, false);
  document.getElementById("boxInterval").value = "1";
  document.getElementById("boxClientID").value = "admin";
  document.getElementById("boxZoomLevel").value = zoom;
  map_init();
  ws_open();
}

