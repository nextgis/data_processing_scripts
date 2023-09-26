<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="0" minScale="1e+08" hasScaleBasedVisibilityFlag="0" version="3.24.0-Tisler" styleCategories="AllStyleCategories">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>

  <pipe>
    <provider>
      <resampling zoomedOutResamplingMethod="cubicSpline" enabled="true" maxOversampling="2" zoomedInResamplingMethod="cubicSpline"/>
    </provider>
    <rasterrenderer opacity="1" band="1" classificationMin="-28" type="singlebandpseudocolor" nodataColor="" alphaBand="-1" classificationMax="2921">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>MinMax</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader classificationMode="1" clip="0" colorRampType="DISCRETE" maximumValue="2921" minimumValue="-28" labelPrecision="0">
          <item alpha="255" color="#71abd8" value="-4000" label="altitude -10"/>
          <item alpha="255" color="#79b2de" value="-2000" label="altitude -9"/>
          <item alpha="255" color="#84b9e3" value="-1000" label="altitude -8"/>
          <item alpha="255" color="#8dc1ea" value="-750" label="altitude -7"/>
          <item alpha="255" color="#96c9f0" value="-500" label="altitude -6"/>
          <item alpha="255" color="#a1d2f7" value="-250" label="altitude -5"/>
          <item alpha="255" color="#acdbfb" value="-100" label="altitude -4"/>
          <item alpha="255" color="#b9e3ff" value="-50" label="altitude -3"/>
          <item alpha="255" color="#c6ecff" value="-20" label="altitude -2"/>
          <item alpha="255" color="#d8f2fe" value="0" label="altitude -1"/>
          <item alpha="255" color="#acd0a5" value="1" label="altitude 1"/>
          <item alpha="255" color="#94bf8b" value="20" label="altitude 2"/>
          <item alpha="255" color="#a8c68f" value="50" label="altitude 3"/>
          <item alpha="255" color="#bdcc96" value="100" label="altitude 4"/>
          <item alpha="255" color="#d1d7ab" value="150" label="altitude 5"/>
          <item alpha="255" color="#e1e4b5" value="200" label="altitude 6"/>
          <item alpha="255" color="#efebc0" value="300" label="altitude 7"/>
          <item alpha="255" color="#e8e1b6" value="400" label="altitude 8"/>
          <item alpha="255" color="#ded6a3" value="600" label="altitude 9"/>
          <item alpha="255" color="#d3ca9d" value="800" label="altitude 10"/>
          <item alpha="255" color="#cab982" value="1000" label="altitude 11"/>
          <item alpha="255" color="#c3a76b" value="1500" label="altitude 12"/>
          <item alpha="255" color="#b9985a" value="2000" label="altitude 13"/>
          <item alpha="255" color="#aa8753" value="3000" label="altitude 14"/>
          <item alpha="255" color="#ac9a7c" value="4000" label="altitude 15 eternal snow"/>
          <item alpha="255" color="#baae9a" value="5000" label="altitude 16 eternal snow"/>
          <item alpha="255" color="#cac3b8" value="6000" label="altitude 17 eternal snow"/>
          <item alpha="255" color="#e0ded8" value="7000" label="altitude 18 eternal snow"/>
          <item alpha="255" color="#f5f4f2" value="8000" label="altitude 19 eternal snow"/>
         <item alpha="255" color="#f5f4f2" value="9000" label="altitude 19 eternal snow"/>
         <item alpha="0" color="#f5f4f2" value="10000" label="nodata"/>
          <rampLegendSettings direction="0" suffix="" useContinuousLegend="1" minimumLabel="" prefix="" orientation="2" maximumLabel="">
            <numericFormat id="basic">
              <Option type="Map">
                <Option name="decimal_separator" type="QChar" value=""/>
                <Option name="decimals" type="int" value="6"/>
                <Option name="rounding_type" type="int" value="0"/>
                <Option name="show_plus" type="bool" value="false"/>
                <Option name="show_thousand_separator" type="bool" value="true"/>
                <Option name="show_trailing_zeros" type="bool" value="false"/>
                <Option name="thousand_separator" type="QChar" value=""/>
              </Option>
            </numericFormat>
          </rampLegendSettings>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0" gamma="1"/>
    <huesaturation invertColors="0" colorizeStrength="100" grayscaleMode="0" colorizeOn="0" colorizeRed="255" colorizeBlue="128" saturation="0" colorizeGreen="128"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>provider</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
