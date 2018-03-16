var mymap = L.map('mapid').setView([37.0902, -95.7129], 4);
var currMarker = null;
var allPatientMarkers = null;
var allResultMarkers = null;
var allPatients = null;
L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox.light',
    accessToken: 'pk.eyJ1Ijoid2lsbGFkdSIsImEiOiJjamVxOGJ6djgzOHltMndtZXZ1b3ZtdWNpIn0.hofKqreauFjGLkr0lncKUQ'
}).addTo(mymap);


$("#validate").click(function() {
    baseurl = "https://maps.googleapis.com/maps/api/geocode/json?address=";
    data = $("#loc").val();
    key = "&key=AIzaSyD9H6AHtwno1O3FDqULTZMbQOEa4-4cEtk";
    q_url = baseurl + encodeURI(data) + key;
    console.log(q_url);
    $.ajax({
        url: q_url,
    }).done(function( data ) {
        if (data.results.length == 0){
            $('.address-validation').html('<div class="alert alert-danger" role="alert">Could not find an appropriate location.</div>');
        } else {
            if (currMarker != null){
                mymap.removeLayer(currMarker)
            }
            address = data.results[0].formatted_address;
            lat = data.results[0].geometry.location.lat;
            long = data.results[0].geometry.location.lng;
            html = '<div class="alert alert-success" role="alert"><p id="address"><strong>'+ address + '</strong></p><p id="lat_long">' + lat + ", "  + long + '</p></div>';
            html += '<input type="hidden" name="lat" value="'+ lat +'">'
            html += '<input type="hidden" name="long" value="'+ long +'">'
            $('.address-validation').html(html);
            var latlng = L.latLng(lat, long);
            currMarker = L.marker([lat, long]).addTo(mymap);
            mymap.flyTo(latlng, 8);
        }
    });
});

$("#reset").click(function() {
    if (allResultMarkers != null) allResultMarkers.clearLayers();
    if (allPatientMarkers != null) allPatientMarkers.clearLayers();
    console.log("RESET");
    placeAllPatients(allPatients);
});

$("form").on("submit", function(event) {
    var resultsMarkers = []
    count = 0
    lat = 0
    long = 0
    event.preventDefault();
    console.log($(this).serialize());
    params = $(this).serialize();
    q_url = "/find-matches?" + params;
    $.get(q_url, function(data) {
        allPatientMarkers.clearLayers()
        if (allResultMarkers != null){
            allResultMarkers.clearLayers()
        }
        for (var i = 0; i < data.kidney.length; i++){
            count += 1
            pat = data.kidney[i]
            long += pat.long
            lat += pat.lat
            resultsMarkers.push(L.circleMarker(L.latLng(pat.lat, pat.long), {"color": "red", "radius": 1}).bindTooltip("Rank: " + (i + 1) + " -  Name: " + pat.name + " -  Age: " + pat.age + " -  Blood: " + pat.bloodtype + " -  HLA: " + pat.hla_dr + " -  Wait in Days: " + pat.wait ));
        }
        for (var i = 0; i < data.liver.length; i++){
            count += 1
            pat = data.liver[i]
            long += pat.long
            lat += pat.lat
            resultsMarkers.push(L.circleMarker(L.latLng(pat.lat, pat.long), {"color": "blue", "radius": 1}).bindTooltip("Rank: " + (i + 1) + " -  Name: " + pat.name + " -  Age: " + pat.age + " -  Blood: " + pat.bloodtype + " -  HLA: " + pat.hla_dr + " -  Wait in Days: " + pat.wait ));
        }
        allResultMarkers = L.layerGroup(resultsMarkers).addTo(mymap);
        console.log(lat/count, long/count)
        mymap.flyTo(L.latLng(lat/count, long/count), 5);
        console.log(data);
    });
});



function placeAllPatients(data) {
    var markers = [];
    for (var i = 0; i < data.length; i++) {
        patient = data[i];
        lat = patient.loc.lat;
        long = patient.loc.lng;
        col = "#f8babe";
        if (patient.organ == "liver") col = "#7076db";
        markers.push(L.circleMarker(L.latLng(lat, long), {"color": col, "radius": 1}));
    }
    allPatientMarkers = L.layerGroup(markers).addTo(mymap);
}


$(document).ready(function() {
    console.log("PPOP");
    $.ajax({
        url: "/list-patients",
    }).done(function( data ) {
        if (data.length == 0){
            console.log("NO PATIENT MATCH")
        } else {
            allPatients = data;
            placeAllPatients(allPatients);
        }
    });
});