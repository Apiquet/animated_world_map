// initialize the map on the "map" div with a given center and zoom
var map = new L.Map('map', {
  zoom: 6,
  minZoom: 3,
});

// create a new tile layer
var tileUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
layer = new L.TileLayer(tileUrl,
{
    attribution: 'Maps © <a href=\"www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors',
    maxZoom: 18
});

// add the layer to the map
map.addLayer(layer);

var parisKievLL = [[48.8567, 2.3508], [50.45, 30.523333]];
var londonParisRomeBerlinBucarest = [[51.507222, -0.1275], [48.8567, 2.3508],
[41.9, 12.5], [52.516667, 13.383333], [44.4166,26.1]];
var londonBrusselFrankfurtAmsterdamLondon = [[51.507222, -0.1275], [50.85, 4.35],
[50.116667, 8.683333], [52.366667, 4.9], [51.507222, -0.1275]];
var barcelonePerpignanPauBordeauxMarseilleMonaco = [
    [41.385064, 2.173403],
    [42.698611, 2.895556],
    [43.3017, -0.3686],
    [44.837912, -0.579541],
    [43.296346, 5.369889],
    [43.738418, 7.424616]
];


map.fitBounds(londonParisRomeBerlinBucarest);



var marker5 = L.Marker.movingMarker(
    barcelonePerpignanPauBordeauxMarseilleMonaco,
    50000, {autostart: true}).addTo(map);

marker5.addStation(1, 2000);
marker5.addStation(2, 2000);
marker5.addStation(3, 2000);
marker5.addStation(4, 2000);

L.polyline(barcelonePerpignanPauBordeauxMarseilleMonaco,
    {color: 'green'}).addTo(map);
