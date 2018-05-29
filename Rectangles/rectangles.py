#!/usr/bin/env python3
# encoding: utf-8

import argparse
from math import sqrt

import ogr
import osr
import gdal

from shapely.geometry import Polygon, LineString
from shapely.affinity import affine_transform


parser = argparse.ArgumentParser()
parser.add_argument("--long", type=int, help="Size of the long side", default=10)
parser.add_argument("--short", type=int, help="Size of the short side", default=5)
parser.add_argument("--sq_size", type=int, help="Length of square side in meters", default=1000)

parser.add_argument("--lon1", type=float, help="Longitude for 1st point")
parser.add_argument("--lon2", type=float, help="Longitude for 2nd point")
parser.add_argument("--lat1", type=float, help="Latitude for 1st point")
parser.add_argument("--lat2", type=float, help="Latitude for 2nd point")

parser.add_argument('--lines', dest='lines', action='store_true')
parser.add_argument('--polygones', dest='lines', action='store_false')

parser.add_argument("--output", help="Name of result file", default='net.shp')

def gdal_error_handler(err_class, err_num, err_msg):
    errtype = {
            gdal.CE_None:'None',
            gdal.CE_Debug:'Debug',
            gdal.CE_Warning:'Warning',
            gdal.CE_Failure:'Failure',
            gdal.CE_Fatal:'Fatal'
    }
    err_msg = err_msg.replace('\n',' ')
    err_class = errtype.get(err_class, 'None')
    print('Error Number: %s' % (err_num))
    print('Error Type: %s' % (err_class))
    print('Error Message: %s' % (err_msg))

def get_projected_epsg(lon, lat):
    zone = ((lon + 180) // 6 ) % 60 + 1

    if lat > 0:
        epsg = 32600 + zone
    else:
        epsg = 32700 + zone
    
    return int(epsg)

def reproj(lon, lat, epsg):
    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)
    
    target = osr.SpatialReference()
    target.ImportFromEPSG(epsg)
    
    transform = osr.CoordinateTransformation(source, target)
    
    point = ogr.CreateGeometryFromWkt("POINT (%s %s)" % (lon, lat))
    point.Transform(transform)

    return (point.GetX(), point.GetY())

def get_transform(x1, y1, x2, y2):
    dist = sqrt((x2-x1)**2 + (y2-y1)**2)
    sinA = (y2-y1) / dist
    cosA = (x2-x1) / dist

    return [cosA, -sinA, sinA, cosA, x1, y1]


def make_net(x_count, y_count, dist, lines=False):
    geoms = dict()
    for i in range(x_count):
        for j in range(y_count):
            c1 = (i*dist, j*dist)
            c2 = ((i+1)*dist, j*dist)
            c3 = ((i+1)*dist, (j+1)*dist)
            c4 = (i*dist, (j+1)*dist)
            if lines:
                geoms[(i, j)] = LineString([c1, c4])
            else:
                geoms[(i, j)] = Polygon([c1, c2 ,c3, c4])
    
    return geoms

def transform_net(polys, transform):
    for k, geom in polys.items():
        polys[k] = affine_transform(geom, transform)
    
    return polys

def save(polygones, name, epsg):
    driver = ogr.GetDriverByName('Esri Shapefile')
    ds = driver.CreateDataSource(name)

    srs = ogr.osr.SpatialReference()
    srs.ImportFromEPSG(epsg)

    geom = polygones[(0, 0)]  # (0, 0) object is presented always
    if geom.geom_type == 'Polygon':
        geom_type = ogr.wkbPolygon
    elif geom.geom_type == 'LineString':
        geom_type = ogr.wkbLineString
    else:
        raise NotImplementedError("Unknown geometry type %s" % (geom.geom_type, ))

    layer = ds.CreateLayer('', srs, geom_type)
    layer.CreateField(ogr.FieldDefn('col', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('row', ogr.OFTInteger))
    defn = layer.GetLayerDefn()
    
    for (col, row), poly in polygones.items():
        feat = ogr.Feature(defn)
        feat.SetField('col', col)
        feat.SetField('row', row)
        
        
        geom = ogr.CreateGeometryFromWkb(poly.wkb)
        feat.SetGeometry(geom)
        
        layer.CreateFeature(feat)
        feat = geom = None
    
    ds = layer = feat = geom = None

def main():
    args = parser.parse_args()

    gdal.PushErrorHandler(gdal_error_handler)

    epsg = get_projected_epsg(args.lon1, args.lat1)

    x1, y1 = reproj(args.lon1, args.lat1, epsg)
    x2, y2 = reproj(args.lon2, args.lat2, epsg)

    net = make_net(args.long, args.short, args.sq_size, lines=args.lines)
    trans = get_transform(x1, y1, x2, y2)
    net = transform_net(net, trans)

    save(net, args.output, epsg)



if __name__ == "__main__":
    main()
