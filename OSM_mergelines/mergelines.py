#!/usr/bin/env python
# -*- coding: utf-8 -*-

from osgeo import gdal
from osgeo import ogr
import os
import errno

import logging



class Processor:

    def __init__(self,filename=None):


        self.delta = 0.00000001 #Using in compare points 
        #logging.basicConfig(level = logging.DEBUG)
        logging.basicConfig(format = u'%(filename)s;[LINE:%(lineno)d]# ; %(levelname)-8s ; [%(asctime)s]      ; %(message)s', level = logging.DEBUG)

        '''
        logging.debug( u'This is a debug message' )
        logging.info( u'This is an info message' )
        logging.warning( u'This is a warning' )
        logging.error( u'This is an error message' )
        logging.critical( u'FATAL!!!' )
        '''


        if filename is not None:
    
            if not os.path.exists(filename):
                raise IOError(filename)
            ogr.UseExceptions()
        

            self.srcdataSource = gdal.OpenEx(filename)
            layer_count = self.srcdataSource.GetLayerCount()
            logging.debug('Layer count: ' + str(layer_count))
            if layer_count < 1:
                raise ValueError('layer_count should be >= 1')
            self.srclayer = self.srcdataSource.GetLayer()
            
            for feature in self.srclayer:
                geom = feature.GetGeometryRef()
                if geom.IsValid() <> True:
                    raise ValueError('Invalid geometry')
        logging.info('initialization complete')
        

    def compareValues(self,left_value, right_value):
        if (left_value == '' or left_value == None) and (right_value == '' or right_value == None):
            return True
        
        if isinstance(left_value, float) and isinstance(right_value, float):              
            return abs(left_value - right_value) < self.delta 
            
        if left_value != right_value:      
            return False
        return True
        
    def comparePoints(self,left_pt, right_pt):
        return (abs(left_pt[0] - right_pt[0]) < self.delta) and (abs(left_pt[1] - right_pt[1]) < self.delta)
        
    def compareLines(self,left_line, right_line):
        if left_line.GetPointCount() != right_line.GetPointCount():
            return False
        for i in range(left_line.GetPointCount()):
            
            if not self.comparePoints(left_line.GetPoint(i), right_line.GetPoint(i)):
                return False
        return True
        
    def comparePolygons(self,left_poly, right_poly):
        left_poly_rings = left_poly.GetGeometryCount()
        right_poly_rings = right_poly.GetGeometryCount()
        if left_poly_rings != right_poly_rings:
            return False

        for i in range(left_poly_rings):
            if not self.compareLines(left_poly.GetGeometryRef(i), right_poly.GetGeometryRef(i)):
                return False 
        for i in range(left_poly.GetPointCount()):
            if not self.comparePoints(left_poly.GetGeometryRef(i), right_poly.GetGeometryRef(i)):
                return False

        return True                 
        
    def compareGeom(self,left_geom, right_geom):  

        if left_geom.GetGeometryCount() <> right_geom.GetGeometryCount():
            return False    #Diffirent geometry count
        elif left_geom.GetGeometryType() is ogr.wkbPoint:              
            return self.comparePoints(left_geom.GetPoint(), right_geom.GetPoint())  
        elif left_geom.GetGeometryType() is ogr.wkbLineString:
            return self.compareLines(left_geom, right_geom)  
        elif left_geom.GetGeometryType() is ogr.wkbPolygon:
            return self.comparePolygons(left_geom, right_geom)  
        elif left_geom.GetGeometryType() is ogr.wkbMultiPoint:
            for i in range(left_geom.GetGeometryCount()):
                if not self.comparePoints(left_geom.GetGeometryRef(i).GetPoint(0), right_geom.GetGeometryRef(i).GetPoint(0)):
                    return False
        elif left_geom.GetGeometryType() is ogr.wkbMultiLineString:
            for i in range(left_geom.GetGeometryCount()):
                if not self.compareLines(left_geom.GetGeometryRef(i), right_geom.GetGeometryRef(i)):
                    return False
        elif left_geom.GetGeometryType() is ogr.wkbMultiPolygon:
            for i in range(left_geom.GetGeometryCount()):
                if not self.comparePolygons(left_geom.GetGeometryRef(i), right_geom.GetGeometryRef(i)):
                    return False
        else:
            print 'left_geom.GetGeometryCount() <> right_geom.GetGeometryCount()'
            print left_geom.GetGeometryCount() <> right_geom.GetGeometryCount()
            
            print 'left_geom.GetGeometryType() is ogr.wkbPoint:'
            print left_geom.GetGeometryType() is ogr.wkbPoint
            raise ValueError('compareGeom get unexpected geometry')
        return True     
         

    def create_output_layer(self,inLayer,output_filename):
        from osgeo import ogr, osr

        outShapefile = output_filename
        outDriver = ogr.GetDriverByName("GPKG")
        
        # Remove output shapefile if it already exists
        if os.path.exists(outShapefile):
            outDriver.DeleteDataSource(outShapefile)

        # Create the output shapefile
        outDataSource = outDriver.CreateDataSource(outShapefile)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        outLayer = outDataSource.CreateLayer("mergelines", srs, geom_type=ogr.wkbLineString)
        
        
        # Add input Layer Fields to the output Layer
        inLayerDefn = inLayer.GetLayerDefn()
        for i in range(0, inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            logging.debug(fieldDefn.GetName())
            outLayer.CreateField(fieldDefn)
           

        # Get the output Layer's Feature Definition
        #outLayerDefn = outLayer.GetLayerDefn()
        return outDataSource

    def mergelines(self,output_filename,DifferentFeaturesList=('NAME','HIGHWAY')):
    
        src_layer = self.srclayer
        logging.debug( 'Layer name: ' + self.srclayer.GetName() )
        
        #sort features gruoping by attributes
        fields = u''
        DifferentFeaturesList = ['"'+item+'"' for item in DifferentFeaturesList]
        sql = '''SELECT * FROM {layername} WHERE NAME IS NOT NULL  ORDER BY {fields} '''.format(fields = ','.join(DifferentFeaturesList), layername = self.srclayer.GetName())

        logging.debug(sql)
        
        ogr.UseExceptions()
        
        outDataSource = self.create_output_layer(self.srclayer, output_filename)
        outLayer = outDataSource.GetLayer()
        logging.debug('out layer created')
        out_featureDefn = outLayer.GetLayerDefn()
        logging.debug('layer defn get')

        ResultSet = self.srcdataSource.ExecuteSQL(sql)
        logging.debug('sql executed')
        layer = self.srcdataSource.GetLayer()
        
        logging.debug('getlayer ok')
        
        features_list = list()
        i = 1
        result_count = ResultSet.GetFeatureCount()
        for feature in ResultSet:
            a = feature.GetField("NAME")
            fields = a
            if i == 1:
                fields = a
                prev_fields = fields
            logging.debug('feature '+str(i) + ' / ' + str(result_count))
            if (fields <> prev_fields) or (i == result_count):
                logging.debug('new street')
                if i == result_count: #for last
                    features_list.append(feature)
                logging.debug('len features_list before sent '+str(len(features_list))) 
                new_features = self.splitFeaturesBlock(features_list,layer.GetLayerDefn()) #return list of features
                logging.debug('len new_features:'+str(len(new_features)))
                
                #copy calculated features to output file
                for new_feature in new_features:
                    out_feature = ogr.Feature(out_featureDefn)
                    
                    p = features_list[0].GetGeometryRef()
                    wkt = p.ExportToWkt()
                                        
                    p = new_feature.GetGeometryRef()
                    wkt = p.ExportToWkt()
                    
                    out_feature.SetGeometry(new_feature.GetGeometryRef())
                    out_feature.SetField( "NAME", prev_fields ) #take attributes from previsious feature from sql
                    outLayer.CreateFeature(out_feature)

                features_list = list()
                features_list.append(feature)
            else:
                features_list.append(feature)
            fid = feature.GetField("OSM_ID")    
            logging.debug(str(fid).decode('utf-8') + '  ' +str(a).decode('utf-8'))
            prev_fields = fields
            i = i+1
            #logging.debug(a.decode('utf-8'))
                
    def getFristPointOfLine(self,geom):
        #accept feature
        #return POINT geometry


        # GetPoint returns a tuple not a Geometry
        firstpoint = ogr.Geometry(ogr.wkbPoint)
        firstpoint.AddPoint_2D(geom.GetPoint(0)[0], geom.GetPoint(0)[1])
        return firstpoint    
    
    def getLastPointOfLine(self,geom):
        #accept feature
        #return POINT geometry


        # GetPoint returns a tuple not a Geometry
        lastpoint = ogr.Geometry(ogr.wkbPoint)
        lastpoint.AddPoint_2D(geom.GetPoint(geom.GetPointCount()-1)[0], geom.GetPoint(geom.GetPointCount()-1)[1])
        return lastpoint
        
    def withClusterTouchingGeometry(self,clusters_geometry,test_geometry):
        #accept: dict of geometry, ogrfeature
        #returns key of dict (integer) or None if feature not touching anything geometry in dict
        #if featute touching more than one cluster, return anything one number
        for key, cluster_geometry in clusters_geometry.iteritems():        
            if self.is_lines_touching_ends(cluster_geometry,test_geometry):
                return key
        
        return None
        
    def is_lines_touching_ends(self,geometry_a,geometry_b):
        point_a_a = self.getFristPointOfLine(geometry_a)
        point_a_b = self.getLastPointOfLine(geometry_a)    
       
        point_b_a = self.getFristPointOfLine(geometry_b)
        point_b_b = self.getLastPointOfLine(geometry_b)
        if self.compareGeom(point_a_a,point_b_a) or self.compareGeom(point_a_a,point_b_b) or self.compareGeom(point_a_b,point_b_a) or self.compareGeom(point_a_b,point_b_b):
            return True
        
        return False
        

        
    def filterIsolateFeatures(self,features_list):
        #take a list with features with simlar attributes.
        #returns a list of non_isolated_features and list of non_isolated_features
        
            
        
        isolated_features = list()
        non_isolated_features = list()
        non_isolated_features_ids = dict()
        
        if len(features_list)==1:
            return non_isolated_features, features_list


        for a in range(0,len(features_list)):
            point_a_a = self.getFristPointOfLine(features_list[a].GetGeometryRef())
            point_a_b = self.getLastPointOfLine(features_list[a].GetGeometryRef())
            a_is_isolated = True
            for b in range(0,len(features_list)):
                point_b_a = self.getFristPointOfLine(features_list[b].GetGeometryRef())
                point_b_b = self.getLastPointOfLine(features_list[b].GetGeometryRef())
                if a == b:
                    continue
                #compare point coordnates using float point stuff
                if self.compareGeom(point_a_a,point_b_a) or self.compareGeom(point_a_a,point_b_b) or self.compareGeom(point_a_b,point_b_a) or self.compareGeom(point_a_b,point_b_b):
                    a_is_isolated = False
                    non_isolated_features_ids[a] = True
            if a_is_isolated:
                isolated_features.append(features_list[a])
        

        #move
        for a in range(0,len(features_list)):
            if a in non_isolated_features_ids:
                non_isolated_features.append(features_list[a])
        
        return non_isolated_features,isolated_features
        
    def geometry_merge(self,geometry_a,geometry_b):
        #WITCH POINTS LINES CONNECTED BY
        '''
        CASES
        
        -----> -> a_b b_a
        -----> <- a_b b_b
        <----- -> a_a b_a
        <----- <- a_a b_b
        
        '''
        point_a_a = self.getFristPointOfLine(geometry_a)
        point_a_b = self.getLastPointOfLine(geometry_a)        
        point_b_a = self.getFristPointOfLine(geometry_b)
        point_b_b = self.getLastPointOfLine(geometry_b)
        
        debug_line = ogr.Geometry(ogr.wkbLineString)
        
        '''
        print geometry_a.GetPointCount()
        print int(round(geometry_a.GetPointCount()/2))
        debug_lon, debug_lat,debug_z = geometry_b.GetPoint(int(round(geometry_a.GetPointCount()/2)))
        debug_line.AddPoint_2D(debug_lon, debug_lat)         
        '''
        debug_lon, debug_lat,debug_z = geometry_b.GetPoint(int(round(geometry_b.GetPointCount()/2)))
        debug_line.AddPoint_2D(debug_lon, debug_lat)
        
        #debug_wkt = debug_line.ExportToWkt()
        
        if self.compareGeom(point_a_b,point_b_a):
            for p in xrange(geometry_b.GetPointCount()):
                if p == 0:
                    continue
                lon, lat, z = geometry_b.GetPoint(p)
                geometry_a.AddPoint_2D(lon,lat)
            logging.debug('merge case 1;'+str(debug_lon) + ';' + str(debug_lat))
            return geometry_a
        elif self.compareGeom(point_a_b,point_b_b):
            p = geometry_b.GetPointCount()-1
            while p > 0:
                p = p - 1
                lon, lat, z = geometry_b.GetPoint(p)
                geometry_a.AddPoint_2D(lon,lat)
            logging.debug('merge case 2;'+str(debug_lon) + ';' + str(debug_lat))
            return geometry_a
        elif self.compareGeom(point_a_a,point_b_a):
            
            new_geometry = ogr.Geometry(ogr.wkbLineString)
            p = geometry_b.GetPointCount()
            while p > 0:
                p = p - 1
                lon, lat, z = geometry_b.GetPoint(p)
                new_geometry.AddPoint_2D(lon,lat)

            for p in xrange(geometry_a.GetPointCount()):
                if p == 0:
                    continue
                lon, lat, z = geometry_a.GetPoint(p)
                new_geometry.AddPoint_2D(lon,lat)
            logging.debug('merge case 3;'+str(debug_lon) + ';' + str(debug_lat))
            return new_geometry        
        elif self.compareGeom(point_a_a,point_b_b):            
            new_geometry = ogr.Geometry(ogr.wkbLineString)
            p = geometry_b.GetPointCount()-1
            for p in xrange(geometry_b.GetPointCount()-1):
                lon, lat, z = geometry_b.GetPoint(p)
                new_geometry.AddPoint_2D(lon,lat)
            for p in xrange(geometry_a.GetPointCount()):
                if p == 0:
                    pass
                lon, lat, z = geometry_a.GetPoint(p)
                new_geometry.AddPoint_2D(lon,lat)
            logging.debug('merge case 4;'+str(debug_lon) + ';' + str(debug_lat))
            return new_geometry
        
        return None
        
    def splitFeaturesBlock(self,features_list,featureDefn):
        #take a list with features with simlar attributes.
        #Return a list of features, features from same street will merged to continous LINESTRING
        
        if len(features_list)==1:
            result = list()
            result.append(features_list[0])
            return result
        
        non_isolated_features,isolated_features = self.filterIsolateFeatures(features_list)
        logging.debug('len features_list '+str(len(features_list)))        
        logging.debug('len non_isolated '+str(len(non_isolated_features)))        
        logging.debug('len isolated '+str(len(isolated_features)))        

                    
        #isolated_features - ready for output
        #non_isolated_features - ready for alalysis
        merged_features = list()
        clusters_count = 0
        features_state = dict()
        features_in_clusters = dict()
        clusters_geometry = dict()
        
        
        #Сравнение по координатам с тем кластером, куда эта линия уже включена
        #Если включена в кластер, то пропускаем
        

        
        if (len(non_isolated_features) == 0):   
            #has many streets with same name, but they all not touching by ends
            result = list()
            for i in isolated_features:
                result.append(i) 
            return result
            
            
            
        clusters_geometry[clusters_count] = non_isolated_features[0].GetGeometryRef()
        features_in_clusters[0] = 0
        
        for a in range(0,len(non_isolated_features)):
            #С каким кластером соприкасается фича a?

            with_cluster_touching_feature = self.withClusterTouchingGeometry(clusters_geometry,non_isolated_features[a].GetGeometryRef())
            
            logging.debug('a='+str(a))
            logging.debug('with_cluster_touching_feature='+str(with_cluster_touching_feature))
            
            if with_cluster_touching_feature is None:
                clusters_count= clusters_count+1
                clusters_geometry[clusters_count] = non_isolated_features[a].GetGeometryRef()
                features_in_clusters[a]=clusters_count
                continue
            current_cluster = with_cluster_touching_feature
            #point_a_a = getFristPointOfLine(clusters_geometry[current_cluster].GetGeometryRef())
            #point_a_b = getLastPointOfLine(clusters_geometry[current_cluster].GetGeometryRef())
            for b in range(0,len(non_isolated_features)):
                #point_b_a = getFristPointOfLine(non_isolated_features[b].GetGeometryRef())
                #point_b_b = getLastPointOfLine(non_isolated_features[b].GetGeometryRef())
                
                if self.is_lines_touching_ends(clusters_geometry[current_cluster],non_isolated_features[b].GetGeometryRef()):
                #if self.compareGeom(point_a_a,point_b_a) or self.compareGeom(point_a_a,point_b_b) or self.compareGeom(point_a_b,point_b_a) or self.compareGeom(point_a_b,point_b_b):
                    if b in features_in_clusters:
                        continue
                    clusters_geometry[current_cluster] = self.geometry_merge(clusters_geometry[current_cluster],non_isolated_features[b].GetGeometryRef())
                    features_in_clusters[b]=current_cluster

        
        result = list()
        
        print features_in_clusters
        for cluster_number in range(0,clusters_count+1):
            logging.debug('compute cluster ='+str(cluster_number))
            for key, value in features_in_clusters.items():
                if value == cluster_number:
                    feature = ogr.Feature(featureDefn)
                    feature.SetGeometry(clusters_geometry[cluster_number])
                    result.append(feature)
                    feature = None

                    break
                    
        for i in isolated_features:
            result.append(i)
            #logging.debug(i.GetField("NAME").decode('utf-8'))
        #result = result + isolated_features
        
        return result
        
        #iterate in each group
            #if this feature not connected with any other feature in group:
                #move this feature to new group
        #at this line we have clusterised gropus (see fig.2)
        #append to each group count of objects
        #Use only groups when more 1 count
        #order group by X(Centroid) (not neccesary)
        #iterate in each group
            #create new LINESTRING geometry from frist feature
            
            #find other unused feature in this group
                #create new geometry as copy of this feature
                #add to this geometry points from connected feature, using right order
                #add attributes from frist points
                
        #export as file