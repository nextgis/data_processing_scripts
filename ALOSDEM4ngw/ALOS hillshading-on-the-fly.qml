<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" styleCategories="AllStyleCategories" maxScale="0" minScale="1e+08" version="3.24.0-Tisler">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>0</Searchable>
    <Private>0</Private>
  </flags>
  <temporal enabled="0" fetchMode="0" mode="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option name="WMSBackgroundLayer" value="false" type="bool"/>
      <Option name="WMSPublishDataSourceUrl" value="false" type="bool"/>
      <Option name="embeddedWidgets/count" value="0" type="int"/>
      <Option name="identify/format" value="Value" type="QString"/>
    </Option>
  </customproperties>
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option name="name" value="" type="QString"/>
      <Option name="properties"/>
      <Option name="type" value="collection" type="QString"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling enabled="false" zoomedInResamplingMethod="cubic" maxOversampling="2" zoomedOutResamplingMethod="cubic"/>
    </provider>
    <rasterrenderer azimuth="315" angle="45" nodataColor="" type="hillshade" band="1" zfactor="1" multidirection="0" alphaBand="-1" opacity="0.473">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
    </rasterrenderer>
    <brightnesscontrast contrast="17" brightness="14" gamma="0.7"/>
    <huesaturation colorizeRed="255" colorizeStrength="100" grayscaleMode="0" colorizeGreen="128" saturation="0" colorizeOn="0" invertColors="0" colorizeBlue="128"/>
    <rasterresampler maxOversampling="2" zoomedInResampler="cubic" zoomedOutResampler="cubic"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>5</blendMode>
</qgis>
