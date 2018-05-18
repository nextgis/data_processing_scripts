OSRM returns only own JSON, not standart GEOJSON.
Here is example of create GEOJSON from OSRM using bash.
It can be easy ported to python

```bash

# 38.001341,51.554941,1
# 37.987223,51.292056,2
# 37.287875,51.151705,3
# 37.218524,51.059304,4
# 37.193362,50.945776,5

url='0.0.0.0:5000'
#osrm returns only json, not geojson

point1='38.001341,51.554941'
point2='37.987223,51.292056'

#save response to file
curl "$url/route/v1/driving/$point1;$point2?geometries=geojson&steps=true&overview=full" > section.json
#parse json to variables using jq 
DURATION="$(cat section.json | jq '.routes[0].duration')"
DISTANCE="$(cat section.json | jq '.routes[0].distance')"
COORDINATES="$(cat section.json | jq '.routes[0].geometry.coordinates')"
# print string with variables to text file
printf '{\n"type": "FeatureCollection",\n"name": "routing",\n"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },\n"features": [\n{ "type": "Feature", "properties": { "duration": %s, "distance": %s }, "geometry": { "type": "LineString", "coordinates": %s } }\n]\n}
' "$DURATION" "$DISTANCE" "$COORDINATES"  > section.geojson
mv section.geojson section1.geojson

point1='37.987223,51.292056'
point2='37.287875,51.151705'
curl "$url/route/v1/driving/$point1;$point2?geometries=geojson&steps=true&overview=full" > section.json
DURATION="$(cat section.json | jq '.routes[0].duration')"
DISTANCE="$(cat section.json | jq '.routes[0].distance')"
COORDINATES="$(cat section.json | jq '.routes[0].geometry.coordinates')"
printf '{\n"type": "FeatureCollection",\n"name": "routing",\n"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },\n"features": [\n{ "type": "Feature", "properties": { "duration": %s, "distance": %s }, "geometry": { "type": "LineString", "coordinates": %s } }\n]\n}
' "$DURATION" "$DISTANCE" "$COORDINATES"  > section.geojson
mv section.geojson section2.geojson


point1='37.287875,51.151705'
point2='37.218524,51.059304'
curl "$url/route/v1/driving/$point1;$point2?geometries=geojson&steps=true&overview=full" > section.json
DURATION="$(cat section.json | jq '.routes[0].duration')"
DISTANCE="$(cat section.json | jq '.routes[0].distance')"
COORDINATES="$(cat section.json | jq '.routes[0].geometry.coordinates')"
printf '{\n"type": "FeatureCollection",\n"name": "routing",\n"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },\n"features": [\n{ "type": "Feature", "properties": { "duration": %s, "distance": %s }, "geometry": { "type": "LineString", "coordinates": %s } }\n]\n}
' "$DURATION" "$DISTANCE" "$COORDINATES"  > section.geojson
mv section.geojson section3.geojson


point1='37.218524,51.059304'
point2='37.193362,50.945776'
curl "$url/route/v1/driving/$point1;$point2?geometries=geojson&steps=true&overview=full" > section.json
DURATION="$(cat section.json | jq '.routes[0].duration')"
DISTANCE="$(cat section.json | jq '.routes[0].distance')"
COORDINATES="$(cat section.json | jq '.routes[0].geometry.coordinates')"
printf '{\n"type": "FeatureCollection",\n"name": "routing",\n"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },\n"features": [\n{ "type": "Feature", "properties": { "duration": %s, "distance": %s }, "geometry": { "type": "LineString", "coordinates": %s } }\n]\n}
' "$DURATION" "$DISTANCE" "$COORDINATES"  > section.geojson
mv section.geojson section4.geojson

ogrmerge.py -f geojson -single -overwrite_ds -src_layer_field_name order -src_layer_field_content {DS_INDEX} -o routes_each.geojson section1.geojson section2.geojson section3.geojson section4.geojson

# ------------------------


point1='38.001341,51.554941'
point2='37.193362,50.945776'
curl "$url/route/v1/driving/$point1;$point2?geometries=geojson&steps=true&overview=full" > section.json
DURATION="$(cat section.json | jq '.routes[0].duration')"
DISTANCE="$(cat section.json | jq '.routes[0].distance')"
COORDINATES="$(cat section.json | jq '.routes[0].geometry.coordinates')"
printf '{\n"type": "FeatureCollection",\n"name": "routing",\n"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },\n"features": [\n{ "type": "Feature", "properties": { "duration": %s, "distance": %s }, "geometry": { "type": "LineString", "coordinates": %s } }\n]\n}
' "$DURATION" "$DISTANCE" "$COORDINATES"  > section.geojson
mv section.geojson routes_start-finish.geojson
```
