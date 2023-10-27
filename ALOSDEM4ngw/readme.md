
Convert ALOS DEM for NextGIS.com 

- filter by GeoJSON file. GeoJSON file contains tiles. You need to make a subset of those tiles to pass to the script.
- merge
- convert for optimal format
- write benchmark file

```
python3 dem4country.py set-of-tiles.geojson /mnt/alpha/backups/data/dem-sources/alos2012dem ./caucasus.tif
```
Upload of huge rasters to NextGIS Web is recomended via NextGIS Connect plugin for QGIS.
- Update to latest version of NextGIS Connect plugin. There is not very latest version installed via NextGIS QGIS installation.
- Ensure stable net connection from QGIS to NextGIS Web while layer upload and processing. At this time raster layer creation process on server will ended if QGIS disconnected/
