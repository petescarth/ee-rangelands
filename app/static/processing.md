Making JSON Polygons for the app.
---------------------------------

**Grassland polygons from WWF ESRI Shapefile: globalgrasslands_final_082014**

Processed by:

- Projecting to WGS84
- Simplifing to 0.05
- Buffering by -0.1 degrees
- Buffering by 0.05 degrees
- Removing "small"polygons
- Simplifing to 0.05

Field Calculations:

- "id" calculated as replace( trim( lower( "ECO_NAME" )),' ','-')
- Then "ECO_NAME" renamed to "title"

Exported to individual shapefiles:

- Shapefiles converted to geojson using ogr2ogr -f GeoJSON -t_srs crs:84 "%a.geojson" "%a"
- Geojson files processed using "sed -n 6p $f " to select the 6th line in the file
