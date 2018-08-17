import unittest

class TestStringMethods(unittest.TestCase):


    def test_compare_geom(self):
        from osgeo import ogr, osr
        import mergelines    
        
        processor = mergelines.Processor()

        etalon_point1 = ogr.Geometry(ogr.wkbPoint)
        etalon_point1.AddPoint_2D(37.1, 55.1)
        
        etalon_point2 = ogr.Geometry(ogr.wkbPoint)
        etalon_point2.AddPoint_2D(37.1, 55.1)
        
        compare_result = processor.compareGeom(etalon_point1,etalon_point2)
        self.assertTrue(compare_result)
        etalon_point1 = None         
        etalon_point2 = None     
        
        
        etalon_point1 = ogr.Geometry(ogr.wkbPoint)
        etalon_point1.AddPoint_2D(37.2, 55.1)
        
        etalon_point2 = ogr.Geometry(ogr.wkbPoint)
        etalon_point2.AddPoint_2D(37.1, 55.1)
        
        compare_result = processor.compareGeom(etalon_point1,etalon_point2)
        self.assertFalse(compare_result)
        etalon_point1 = None         
        etalon_point2 = None         
        
 
        etalon_point1 = ogr.Geometry(ogr.wkbPoint)
        etalon_point1.AddPoint_2D(-37.1, 55.1)
        
        etalon_point2 = ogr.Geometry(ogr.wkbPoint)
        etalon_point2.AddPoint_2D(-37.1, 55.1)
        
        compare_result = processor.compareGeom(etalon_point1,etalon_point2)
        self.assertTrue(compare_result)
        etalon_point1 = None         
        etalon_point2 = None     
        
    def test_get_frist_point(self):
        from osgeo import ogr, osr
        import mergelines
        
        # set up the shapefile driver
        driver = ogr.GetDriverByName("MEMORY")
        # create the data source
        data_source = driver.CreateDataSource("memData")
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        layer = data_source.CreateLayer("memData", srs, ogr.wkbLineString)
        
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint(37.1, 55.1)
        line.AddPoint(37.2, 55.2)
        line.AddPoint(37.3, 55.3)
        line.AddPoint(37.4, 55.4)
        line.AddPoint(37.5, 55.5)
        line.AddPoint(37.6, 55.6)
        

        featureDefn = layer.GetLayerDefn()
        feature = ogr.Feature(featureDefn)
        feature.SetGeometry(line)
        
        processor = mergelines.Processor()
        frist_point = processor.getFristPointOfLine(feature.GetGeometryRef())
        
        # GetPoint returns a tuple not a Geometry
        etalon_point = ogr.Geometry(ogr.wkbPoint)
        etalon_point.AddPoint_2D(37.1, 55.1)
        compare_result = processor.compareGeom(frist_point,etalon_point)
        self.assertTrue(compare_result)
        etalon_point = None        
        
        etalon_point = ogr.Geometry(ogr.wkbPoint)
        etalon_point.AddPoint_2D(37.2, 55.1)
        compare_result = processor.compareGeom(frist_point,etalon_point)
        self.assertFalse(compare_result)
        etalon_point = None
        

        
    def test_get_last_point(self):
        from osgeo import ogr, osr
        import mergelines
        
        driver = ogr.GetDriverByName("MEMORY")
        data_source = driver.CreateDataSource("memData")
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        layer = data_source.CreateLayer("memData", srs, ogr.wkbLineString)
        
        line = ogr.Geometry(ogr.wkbLineString)
        #line.AddPoint(37.0, 55.0)
        line.AddPoint(37.1, 55.1)
        line.AddPoint(37.2, 55.2)
        line.AddPoint(37.3, 55.3)
        line.AddPoint(37.4, 55.4)
        line.AddPoint(37.5, 55.5)
        line.AddPoint(37.6, 55.6)

        featureDefn = layer.GetLayerDefn()
        feature = ogr.Feature(featureDefn)
        feature.SetGeometry(line)
        
        processor = mergelines.Processor()
       
        
        last_point = processor.getLastPointOfLine(feature.GetGeometryRef())   
        
        etalon_point = ogr.Geometry(ogr.wkbPoint)
        etalon_point.AddPoint_2D(37.6, 55.6)
        compare_result = processor.compareGeom(last_point,etalon_point)
        self.assertTrue(compare_result)
        etalon_point = None       
        feature = None 
        
        etalon_point = ogr.Geometry(ogr.wkbPoint)
        etalon_point.AddPoint_2D(37.9, 55.9)
        compare_result = processor.compareGeom(last_point,etalon_point)
        self.assertFalse(compare_result)
        etalon_point = None       
        feature = None
        
    def test_filterIsolateFeatures_5features_3x2_return(self):
        from osgeo import ogr, osr, gdal
        import mergelines
        processor = mergelines.Processor()


        dataSource = gdal.OpenEx('unittest/test_filter_isolate.geojson')
        layer = dataSource.GetLayer()
        source_features = list()
        for feature in layer:
            source_features.append(feature)
        
        non_isolated_features,isolated_features = processor.filterIsolateFeatures(source_features)
        self.assertEqual(len(non_isolated_features),3)
        self.assertEqual(len(isolated_features),2)
        
        self.assertNotEqual(len(isolated_features),6)
        layer = None
        dataSource = None
                
    def test_filterIsolateFeatures_manyfeatures_6x2_return(self):
        from osgeo import ogr, osr, gdal
        import mergelines
        processor = mergelines.Processor()


        dataSource = gdal.OpenEx('unittest/test_filter_isolate_many.geojson')
        layer = dataSource.GetLayer()
        source_features = list()
        for feature in layer:
            source_features.append(feature)
        
        non_isolated_features,isolated_features = processor.filterIsolateFeatures(source_features)
        self.assertEqual(len(non_isolated_features),6)
        self.assertEqual(len(isolated_features),2)
        
        self.assertNotEqual(len(isolated_features),68)
        layer = None
        dataSource = None
        
    def test_filterIsolateFeatures_1features_0x1_return(self):
        from osgeo import ogr, osr, gdal
        import mergelines
        processor = mergelines.Processor()
        layer = None
        dataSource = None
        
        dataSource = gdal.OpenEx('unittest/test_filter_isolate_1.geojson')
        layer = dataSource.GetLayer()
        source_features = list()
        for feature in layer:
            source_features.append(feature)
        
        non_isolated_features,isolated_features = processor.filterIsolateFeatures(source_features)
        self.assertEqual(len(non_isolated_features),0)
        self.assertEqual(len(isolated_features),1)

        layer = None
        dataSource = None
        
    def test_withClusterTouchingFeature_standart(self):
        from osgeo import ogr, osr, gdal
        import mergelines
        processor = mergelines.Processor()
        
        clusters_geometry = dict()
        #dict of geometry of linestrings
        
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint(37.1, 55.1)
        line.AddPoint(37.2, 55.2)
        line.AddPoint(37.3, 55.3)
        line.AddPoint(37.4, 55.4)
        line.AddPoint(37.5, 55.5)
        line.AddPoint(37.6, 55.6)
        
        clusters_geometry[0] = line
        line = None   
        
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint(38.1, 55.1)
        line.AddPoint(38.2, 55.2)
        line.AddPoint(38.3, 55.3)
        line.AddPoint(38.4, 55.4)
        line.AddPoint(38.5, 55.5)
        line.AddPoint(38.6, 55.6)
        
        clusters_geometry[1] = line
        line = None
        
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint(38.6, 55.6)
        line.AddPoint(38.7, 55.7)
        testing_line = line
        line = None
        self.assertEqual(processor.withClusterTouchingGeometry(clusters_geometry,testing_line),1)
                
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint(37.6, 55.6)
        line.AddPoint(38.7, 55.7)
        testing_line = line
        line = None
        self.assertEqual(processor.withClusterTouchingGeometry(clusters_geometry,testing_line),0)
        
        line = None
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint(38.8, 55.6)
        line.AddPoint(38.7, 55.7)
        testing_line = line
        line = None
        self.assertNotEqual(processor.withClusterTouchingGeometry(clusters_geometry,testing_line),1)        


    def test_geometryMerge_case1(self):
        from osgeo import ogr, osr, gdal
        import mergelines
        processor = mergelines.Processor()
        
        line = ogr.Geometry(type=ogr.wkbLineString)
        line.AddPoint_2D(37.1, 55.1)
        line.AddPoint_2D(37.2, 55.2)
        line.AddPoint_2D(37.3, 55.3)
        line.AddPoint_2D(37.4, 55.4)
        line.AddPoint_2D(37.5, 55.5)
        line.AddPoint_2D(37.6, 55.6)
        
        source_line = line
        line = None        
        
        line = ogr.Geometry(type=ogr.wkbLineString)
        line.AddPoint_2D(37.6, 55.6)
        line.AddPoint_2D(37.75, 55.75)
        
        append_line_1 = line
        line = None       
         
        line = ogr.Geometry(type=ogr.wkbLineString)
        line.AddPoint_2D(37.1, 55.1)
        line.AddPoint_2D(37.2, 55.2)
        line.AddPoint_2D(37.3, 55.3)
        line.AddPoint_2D(37.4, 55.4)
        line.AddPoint_2D(37.5, 55.5)
        line.AddPoint_2D(37.6, 55.6)
        line.AddPoint_2D(37.75, 55.75)
        
        etalon_line = line
        line = None    

        
        
        merge_result = processor.geometry_merge(source_line,append_line_1)
        compare_result = processor.compareGeom(merge_result,etalon_line)

        self.assertTrue(compare_result)
        source_line = None         
        append_line_1 = None     
        merge_result = None     
        etalon_line = None     
        
    def test_geometryMerge_case2(self):
        from osgeo import ogr, osr, gdal
        import mergelines
        processor = mergelines.Processor()
        
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint_2D(37.1, 55.1)
        line.AddPoint_2D(37.2, 55.2)
        line.AddPoint_2D(37.3, 55.3)
        line.AddPoint_2D(37.4, 55.4)
        line.AddPoint_2D(37.5, 55.5)
        line.AddPoint_2D(37.6, 55.6)
        
        source_line = line
        line = None        
        
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint_2D(37.85, 55.85)
        line.AddPoint_2D(37.75, 55.75)
        line.AddPoint_2D(37.6, 55.6)
        
        append_line_1 = line
        line = None       
         
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint_2D(37.1, 55.1)
        line.AddPoint_2D(37.2, 55.2)
        line.AddPoint_2D(37.3, 55.3)
        line.AddPoint_2D(37.4, 55.4)
        line.AddPoint_2D(37.5, 55.5)
        line.AddPoint_2D(37.6, 55.6)
        line.AddPoint_2D(37.75, 55.75)
        line.AddPoint_2D(37.85, 55.85)
        
        etalon_line = line
        line = None    
        
        merge_result = processor.geometry_merge(source_line,append_line_1)
        compare_result = processor.compareGeom(merge_result,etalon_line)
        self.assertTrue(compare_result)
        source_line = None         
        append_line_1 = None     
        merge_result = None     
        etalon_line = None            
        
    def test_geometryMerge_case3(self):
        from osgeo import ogr, osr, gdal
        import mergelines
        processor = mergelines.Processor()
        
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint_2D(37.6, 55.6)
        line.AddPoint_2D(37.5, 55.5)
        line.AddPoint_2D(37.4, 55.4)
        line.AddPoint_2D(37.3, 55.3)
        line.AddPoint_2D(37.2, 55.2)
        line.AddPoint_2D(37.1, 55.1)
        
        source_line = line
        line = None        
        
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint_2D(37.6, 55.6)
        line.AddPoint_2D(37.75, 55.75)
        line.AddPoint_2D(37.85, 55.85)
        
        append_line_1 = line
        line = None       
         
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint_2D(37.85, 55.85)
        line.AddPoint_2D(37.75, 55.75)
        line.AddPoint_2D(37.6, 55.6)
        line.AddPoint_2D(37.5, 55.5)
        line.AddPoint_2D(37.4, 55.4)
        line.AddPoint_2D(37.3, 55.3)
        line.AddPoint_2D(37.2, 55.2)
        line.AddPoint_2D(37.1, 55.1)
        
        etalon_line = line
        line = None    
        
        merge_result = processor.geometry_merge(source_line,append_line_1)

        compare_result = processor.compareGeom(merge_result,etalon_line)
        self.assertTrue(compare_result)
        source_line = None         
        append_line_1 = None     
        merge_result = None     
        etalon_line = None     
                
    def test_geometryMerge_case4(self):
        from osgeo import ogr, osr, gdal
        import mergelines
        processor = mergelines.Processor()
        
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint_2D(37.6, 55.6)
        line.AddPoint_2D(37.5, 55.5)
        line.AddPoint_2D(37.4, 55.4)
        line.AddPoint_2D(37.3, 55.3)
        line.AddPoint_2D(37.2, 55.2)
        line.AddPoint_2D(37.1, 55.1)
        
        source_line = line
        line = None        
        
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint_2D(37.75, 55.75)
        line.AddPoint_2D(37.6, 55.6)
        
        append_line_1 = line
        line = None       
         
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint_2D(37.75, 55.75)
        line.AddPoint_2D(37.6, 55.6)
        line.AddPoint_2D(37.5, 55.5)
        line.AddPoint_2D(37.4, 55.4)
        line.AddPoint_2D(37.3, 55.3)
        line.AddPoint_2D(37.2, 55.2)
        line.AddPoint_2D(37.1, 55.1)
        
        etalon_line = line
        line = None    
        
        merge_result = processor.geometry_merge(source_line,append_line_1)

        compare_result = processor.compareGeom(merge_result,etalon_line)
        self.assertTrue(compare_result)
        source_line = None         
        append_line_1 = None     
        merge_result = None     
        etalon_line = None     
        
        
    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()