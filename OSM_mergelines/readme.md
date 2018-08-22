Merging lines by attributes into linestring.

# Demo

http://trolleway.nextgis.com/resource/2602

# Usage

See __main__.py for usage

* Input file must be Linestring geometry in any format. Convert it by
```
ogr2ogr -nlt Linestring -overwrite /home/trolleway/ssdgis/mergeline/testdata/hi2.gpkg /home/trolleway/ssdgis/mergeline/testdata/hi1.gpkg
```
* Output file must be geopackage.
* Only some fields are keep, some fields are dropped
