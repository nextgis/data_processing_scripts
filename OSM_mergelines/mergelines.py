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
        logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]      %(message)s', level = logging.DEBUG)

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
                
        

    def compareValues(self,ngw_value, wfs_value):
        if (ngw_value == '' or ngw_value == None) and (wfs_value == '' or wfs_value == None):
            return True
        
        if isinstance(ngw_value, float) and isinstance(wfs_value, float):              
            return abs(ngw_value - wfs_value) < self.delta 
            
        if ngw_value != wfs_value:      
            return False
        return True
        
    def comparePoints(self,ngw_pt, wfs_pt):
        return (abs(ngw_pt[0] - wfs_pt[0]) < self.delta) and (abs(ngw_pt[1] - wfs_pt[1]) < self.delta)
        
    def compareLines(self,ngw_line, wfs_line):
        if ngw_line.GetPointCount() != wfs_line.GetPointCount():
            return False
        for i in range(ngw_line.GetPointCount()):
            

            if not self.comparePoints(ngw_line.GetPoint(i), wfs_line.GetPoint(i)):
                return False
            
        return True
        
    def comparePolygons(self,ngw_poly, wfs_poly):
        ngw_poly_rings = ngw_poly.GetGeometryCount()
        wfs_poly_rings = wfs_poly.GetGeometryCount()
        if ngw_poly_rings != wfs_poly_rings:
            return False

        for i in range(ngw_poly_rings):
            if not self.compareLines(ngw_poly.GetGeometryRef(i), wfs_poly.GetGeometryRef(i)):
                return False 





        for i in range(ngw_poly.GetPointCount()):
            if not self.comparePoints(ngw_poly.GetGeometryRef(i), wfs_poly.GetGeometryRef(i)):
                return False

        return True                 
        
    def compareGeom(self,ngw_geom, wfs_geom):  

        if ngw_geom.GetGeometryCount() <> wfs_geom.GetGeometryCount():
            return False    #Diffirent geometry count
        elif ngw_geom.GetGeometryType() is ogr.wkbPoint:              
            return self.comparePoints(ngw_geom.GetPoint(), wfs_geom.GetPoint())  
        elif ngw_geom.GetGeometryType() is ogr.wkbLineString:
            return self.compareLines(ngw_geom, wfs_geom)  
        elif ngw_geom.GetGeometryType() is ogr.wkbPolygon:
            return self.comparePolygons(ngw_geom, wfs_geom)  
        elif ngw_geom.GetGeometryType() is ogr.wkbMultiPoint:
            for i in range(ngw_geom.GetGeometryCount()):
                if not self.comparePoints(ngw_geom.GetGeometryRef(i).GetPoint(0), wfs_geom.GetGeometryRef(i).GetPoint(0)):
                    return False
        elif ngw_geom.GetGeometryType() is ogr.wkbMultiLineString:
            for i in range(ngw_geom.GetGeometryCount()):
                if not self.compareLines(ngw_geom.GetGeometryRef(i), wfs_geom.GetGeometryRef(i)):
                    return False
        elif ngw_geom.GetGeometryType() is ogr.wkbMultiPolygon:
            for i in range(ngw_geom.GetGeometryCount()):
                if not self.comparePolygons(ngw_geom.GetGeometryRef(i), wfs_geom.GetGeometryRef(i)):
                    return False
        else:
            print 'ngw_geom.GetGeometryCount() <> wfs_geom.GetGeometryCount()'
            print ngw_geom.GetGeometryCount() <> wfs_geom.GetGeometryCount()
            
            print 'ngw_geom.GetGeometryType() is ogr.wkbPoint:'
            print ngw_geom.GetGeometryType() is ogr.wkbPoint
            raise ValueError('compareGeom get unexpected geometry')
            return True # this is unexpected

        return True     
        
        
        

        
    def mergelines(self,DifferentFeaturesList=('NAME','HIGHWAY')):
    

        logging.debug( 'Layer name: ' + self.srclayer.GetName() )
        
        #sort features gruoping by attributes
        fields = u''
        DifferentFeaturesList = ['"'+item+'"' for item in DifferentFeaturesList]
        sql = '''SELECT * FROM {layername} ORDER BY {fields} '''.format(fields = ','.join(DifferentFeaturesList), layername = self.srclayer.GetName())
        
        logging.debug(sql)

        ResultSet = self.srcdataSource.ExecuteSQL(sql)
        layer = self.srcdataSource.GetLayer()
        features_list = list()
        for feature in ResultSet:
            a = feature.GetField("NAME")
            logging.debug(a)
            if fields <> prev_fields:
                new_features = self.splitFeaturesBlock(features_list) #return list of features
                new_layer.addFeatures(new_features)
                features_list = list()
                features_list.append(feature)
            else:
                features_list.append(feature)
            
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
        
        -----> -> a_b b_a
        -----> <- a_b b_b
        <----- -> a_a b_a
        <----- <- a_a b_b
        
        '''
        point_a_a = self.getFristPointOfLine(geometry_a)
        point_a_b = self.getLastPointOfLine(geometry_a)        
        point_b_a = self.getFristPointOfLine(geometry_b)
        point_b_b = self.getLastPointOfLine(geometry_b)
        

        
        if self.compareGeom(point_a_b,point_b_a):
            for p in xrange(geometry_b.GetPointCount()):
                if p == 0:
                    continue
                lon, lat, z = geometry_b.GetPoint(p)
                geometry_a.AddPoint_2D(lon,lat)
            return geometry_a
        elif self.compareGeom(point_a_b,point_b_b):
            p = geometry_b.GetPointCount()-1
            while p > 0:
                p = p - 1
                lon, lat, z = geometry_b.GetPoint(p)
                geometry_a.AddPoint_2D(lon,lat)
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
            return new_geometry        
        elif self.compareGeom(point_a_a,point_b_b):            
            new_geometry = ogr.Geometry(ogr.wkbLineString)
            p = geometry_b.GetPointCount()-1
            while p > 0:
                p = p - 1
                lon, lat, z = geometry_b.GetPoint(p)
                new_geometry.AddPoint_2D(lon,lat)
            for p in xrange(geometry_a.GetPointCount()):
                if p == 0:
                    pass
                lon, lat, z = geometry_a.GetPoint(p)
                new_geometry.AddPoint_2D(lon,lat)
            return new_geometry
        
        return None
        
    def splitFeaturesBlock(self,features_list,featureDefn):
        #take a list with features with simlar attributes.
        #Return a list of features, features from same street will merged to continous LINESTRING
        
        non_isolated_features,isolated_features = self.filterIsolateFeatures(features_list)
                

                    
        #isolated_features - ready for output
        #non_isolated_features - ready for alalysis
        merged_features = list()
        clusters_count = 0
        features_state = dict()
        features_in_clusters = dict()
        clusters_geometry = dict()
        
        
        #Сравнение по координатам с тем кластером, куда эта линия уже включена
        #Если включена в кластер, то пропускаем
        
        clusters_geometry[clusters_count] = non_isolated_features[0].GetGeometryRef()
        features_in_clusters[0] = 0
        
        for a in range(0,len(non_isolated_features)):
            #С каким кластером соприкасается фича a?

            with_cluster_touching_feature = self.withClusterTouchingGeometry(clusters_geometry,non_isolated_features[a].GetGeometryRef())
            if with_cluster_touching_feature is None:
                clusters_count=+1
                clusters_geometry[clusters_count] = non_isolated_features[a].GetGeometryRef()
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
            
        for cluster_number in range(0,clusters_count+1):
            for key, value in features_in_clusters.items():
                if value == cluster_number:
                    feature = ogr.Feature(featureDefn)
                    feature.SetGeometry(clusters_geometry[cluster_number])
                    result.append(feature)
                    feature = None

                    break
                    
        for i in isolated_features:
            result.append(i)
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