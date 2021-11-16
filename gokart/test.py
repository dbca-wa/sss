import json
import os
import tempfile
import math
import traceback
from shutil import copyfile
from collections import OrderedDict
from datetime import datetime

from shapely.geometry import shape,MultiPoint,Point
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.linestring import LineString
from shapely.geometry.multilinestring import MultiLineString
from shapely.geometry import LinearRing,mapping,LineString
from shapely.geometry.collection import GeometryCollection

from gokart.spatial import calculateFeatureArea,calculateGeometryArea,extractPolygons,transform,exportGeojson

def mergeGeometry(geom1,geom2):
    if not geom2:
        return geom1
    elif not geom1:
        return geom2
    else:
        if isinstance(geom1,Point):
            if isinstance(geom2,Point):
                return MultiPoint([geom1,geom2])
            elif isinstance(geom2,MultiPoint):
                geoms = [geom1]
                for p in geom2.geoms:
                    geoms.append(p)
                return MultiPoint(geoms)
            elif isinstance(geom2,(LineString,Polygon)):
                return GeometryCollection([geom1,geom2])
            elif isinstance(geom2,(MultiLineString,MultiPolygon)):
                geoms = [geom1]
                for p in geom2.geoms:
                    geoms.append(p)
                return GeometryCollection(geoms)
            else:
                raise Exception("Unsupported geometry type({}.{})".format(geom2.__class__.__module__,geom2.__class__.__name__))
        elif isinstance(geom1,LineString):
            if isinstance(geom2,LineString):
                return MultiLineString([geom1,geom2])
            elif isinstance(geom2,MultiLineString):
                geoms = [geom1]
                for p in geom2.geoms:
                    geoms.append(p)
                return MultiLineString(geoms)
            elif isinstance(geom2,(Point,Polygon)):
                return GeometryCollection([geom1,geom2])
            elif isinstance(geom2,(MultiPoint,MultiPolygon)):
                geoms = [geom1]
                for p in geom2.geoms:
                    geoms.append(p)
                return GeometryCollection(geoms)
            else:
                raise Exception("Unsupported geometry type({}.{})".format(geom2.__class__.__module__,geom2.__class__.__name__))
        elif isinstance(geom1,Polygon):
            if isinstance(geom2,Polygon):
                return MultiPolygon([geom1,geom2])
            elif isinstance(geom2,MultiPolygon):
                geoms = [geom1]
                for p in geom2.geoms:
                    geoms.append(p)
                return MultiPolygon(geoms)
            elif isinstance(geom2,(Point,LineString)):
                return GeometryCollection([geom1,geom2])
            elif isinstance(geom2,(MultiPoint,MultiLineString)):
                geoms = [geom1]
                for p in geom2.geoms:
                    geoms.append(p)
                return GeometryCollection(geoms)
            else:
                raise Exception("Unsupported geometry type({}.{})".format(geom2.__class__.__module__,geom2.__class__.__name__))
        elif isinstance(geom1,MultiPoint):
            geoms = list(geom1.geoms)
            if isinstance(geom2,Point):
                geoms.append(geom2)
                return MultiPoint(geoms)
            elif isinstance(geom2,MultiPoint):
                for p in geom2.geoms:
                    geoms.append(p)
                return MultiPoint(geoms)
            elif isinstance(geom2,(Polygon,LineString)):
                geoms.append(geom2)
                return GeometryCollection(geoms)
            elif isinstance(geom2,(MultiPolygon,MultiLineString)):
                for p in geom2.geoms:
                    geoms.append(p)
                return GeometryCollection(geoms)
            else:
                raise Exception("Unsupported geometry type({}.{})".format(geom2.__class__.__module__,geom2.__class__.__name__))
        elif isinstance(geom1,MultiLineString):
            geoms = list(geom1.geoms)
            if isinstance(geom2,LineString):
                geoms.append(geom2)
                return MultiLineString(geoms)
            elif isinstance(geom2,MultiLineString):
                for p in geom2.geoms:
                    geoms.append(p)
                return MultiLineString(geoms)
            elif isinstance(geom2,(Point,Polygon)):
                geoms.append(geom2)
                return GeometryCollection(geoms)
            elif isinstance(geom2,(MultiPolygon,MultiPoint)):
                for p in geom2.geoms:
                    geoms.append(p)
                return GeometryCollection(geoms)
            else:
                raise Exception("Unsupported geometry type({}.{})".format(geom2.__class__.__module__,geom2.__class__.__name__))
        elif isinstance(geom1,MultiPolygon):
            geoms = list(geom1.geoms)
            if isinstance(geom2,Polygon):
                geoms.append(geom2)
                return MultiPolygon(geoms)
            elif isinstance(geom2,MultiPolygon):
                for p in geom2.geoms:
                    geoms.append(p)
                return MultiPolygon(geoms)
            elif isinstance(geom2,(Point,LineString)):
                geoms.append(geom2)
                return GeometryCollection(geoms)
            elif isinstance(geom2,(MultiLineString,MultiPoint)):
                for p in geom2.geoms:
                    geoms.append(p)
                return GeometryCollection(geoms)
            else:
                raise Exception("Unsupported geometry type({}.{})".format(geom2.__class__.__module__,geom2.__class__.__name__))
        else:
            raise Exception("Unsupported geometry type({}.{})".format(geom1.__class__.__module__,geom1.__class__.__name__))

def symmetric_difference(geom1,geom2,split=False):
    if not split:
        try:
            return extractPolygons(geom1.symmetric_difference(geom2))
        except:
            return symmetric_difference(geom1,geom2,split=True)
    if isinstance(geom1,Polygon):
        if isinstance(geom2,Polygon):
            return extractPolygons(geom1.symmetric_difference(geom2))
        else:
            for g in geom2.geoms:
                geom1 = extractPolygons(symmetric_difference(geom1,g))
                if not geom1:
                    return None

            return geom1
    else:
        diff_geom = None
        for g in geom1.geoms:
            diff_g = symmetric_difference(g,geom2)
            if not diff_g:
                continue
            diff_geom = mergeGeometry(diff_geom,diff_g)
        return diff_geom


def difference(geom1,geom2,split=False):
    if not split:
        try:
            return extractPolygons(geom1.difference(geom2))
        except:
            return difference(geom1,geom2,split=True)
    if isinstance(geom1,Polygon):
        if isinstance(geom2,Polygon):
            return extractPolygons(geom1.difference(geom2))
        else:
            for g in geom2.geoms:
                geom1 = extractPolygons(difference(geom1,g))
                if not geom1:
                    return None

            return geom1
    else:
        diff_geom = None
        for g in geom1.geoms:
            diff_g = difference(g,geom2)
            if not diff_g:
                continue
            diff_geom = mergeGeometry(diff_geom,diff_g)
        return diff_geom


def intersects(geom1,geom2,split=False):
    if not split:
        try:
            return geom1.intersects(geom2)
        except:
            return intersects(geom1,geom2,split=True)
    if isinstance(geom1,Polygon):
        if isinstance(geom2,Polygon):
            return geom1.intersects(geom2)
        else:
            for g in geom2.geoms:
                if intersects(geom1,g):
                    return True

            return False
    else:
        for g in geom1.geoms:
            if intersects(g,geom2):
                return True
        return False

def default_print_progress_status(print_timestamp=True):
    print_timestamp = print_timestamp
    def _default_print_progress_status(msg):
        if print_timestamp:
            if msg:
                print("{} : {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),msg))
            else:
                print("{}".format(msg))
        else:
            print("{}".format(msg))

    return _default_print_progress_status

def getShapelyGeometry(feature):
    if not feature["geometry"]:
        return None
    elif feature["geometry"]["type"] == "GeometryCollection":
        return GeometryCollection([shape(g) for g in feature["geometry"]["geometries"]])
    else:
        return shape(feature["geometry"])

#return polygon or multipolygons if have, otherwise return None
class PolygonUtil(object):
    FIX_RING_ORIENT = int(math.pow(2,0))
    FIX_SELFINTERSECT_LINES = int(math.pow(2,1))
    FIX_SELFINTERSECT_POINTS = int(math.pow(2,2))
    FIX_ORPHAN_RINGS = int(math.pow(2,3))
    FIX_ORPHAN_RING_AS_INTERIOR_RING = int(math.pow(2,4))
    FIX_ORPHAN_RING_AS_ISLAND = int(math.pow(2,5))
    REMOVE_DUPLICATE_POINT = int(math.pow(2,6))
    SPLIT_EXTERIOR_RING_2_EXTERIOR_HOLE = int(math.pow(2,7))
    SPLIT_INTERIOR_HOLE_2_INTERIOR_RING = int(math.pow(2,8))
    SPLIT_EXTERIOR_HOLE_2_EXTERIOR_RING = int(math.pow(2,9))
    SPLIT_INTERIOR_RING_2_INTERIOR_HOLE = int(math.pow(2,10))
    SPLIT_EXTERIOR_RING = int(math.pow(2,11))
    SPLIT_INTERIOR_HOLE = int(math.pow(2,12))
    SPLIT_EXTERIOR_HOLE = int(math.pow(2,13))
    SPLIT_INTERIOR_RING = int(math.pow(2,14))
    SPLIT_ORPHAN_RING = int(math.pow(2,15))


    FIX_TYPES = OrderedDict([
        (FIX_RING_ORIENT,"Fix ring orient"),
        (FIX_SELFINTERSECT_LINES , "Fix selfintersected lines"),
        (FIX_SELFINTERSECT_POINTS, "Fix selfintersected points"),
        (FIX_ORPHAN_RINGS,"Fix orphan rings"),
        (FIX_ORPHAN_RING_AS_INTERIOR_RING,"Fix orphan ring as interior ring"),
        (FIX_ORPHAN_RING_AS_ISLAND ,"Fix orphan ring as island"),
        (REMOVE_DUPLICATE_POINT ,"Remove duplicate point"),
        (SPLIT_EXTERIOR_RING_2_EXTERIOR_HOLE,"Split exterior ring to exterior ring and exterior hole"),
        (SPLIT_INTERIOR_HOLE_2_INTERIOR_RING,"Split interior hole to interior hole and interior ring"),
        (SPLIT_EXTERIOR_HOLE_2_EXTERIOR_RING,"Split exterior hole to exterior hole and exterior ring"),
        (SPLIT_INTERIOR_RING_2_INTERIOR_HOLE,"Split interior ring to interior ring and interior hole"),
        (SPLIT_EXTERIOR_RING,"Split exterior rint to 2 exterior rings"),
        (SPLIT_INTERIOR_HOLE,"Split interior hole to 2 interior holes"),
        (SPLIT_EXTERIOR_HOLE,"Split exterior hole to 2 exterior holes"),
        (SPLIT_INTERIOR_RING,"Split interior ring to 2 interior rings"),
        (SPLIT_ORPHAN_RING,"Split orphan ring to 2 orphan rings")

    ])
    def __init__(self,name,geom,parentPath=None,print_progress_status=None,properties=None):
        self.geom = geom
        self.parentPath = parentPath
        self.pos = 0
        self.name = name
        self.properties = properties
        self.print_progress_status = print_progress_status or default_print_progress_status()

    @classmethod 
    def fix_type_names(cls,fix_type):
        return [name for t,name in cls.FIX_TYPES.items() if t & fix_type == t]

    def polygons(self,refresh=False):
        """
        Return all polygons included in the geometry  as a list of (path,polygon).
        """
        def getGeomPath():
            curPos = self.pos
            self.pos += 1
            if self.parentPath:
                return "{}.{}".format(self.parentPath,curPos)
            else:
                return str(curPos)

        if refresh or (not hasattr(self,"_polygons")):
            self.pos = 0
            if isinstance(self.geom,Polygon):
                self._polygons = [(getGeomPath(),self.geom)]
            elif isinstance(self.geom,MultiPolygon):
                self._polygons = [(getGeomPath(),geom1) for geom1 in self.geom.geoms]
            elif isinstance(self.geom,GeometryCollection):
                polygonList = None
                for g in self.geom:
                    sublist = PolygonUtil(self.name,g,parentPath=getGeomPath(),print_progress_status=self.print_progress_status,properties=self.properties).polygons
                    if not p:
                        continue
                    elif not polygonList:
                        polygonList = sublist
                    else:
                        polygonList += sublist
                self._polygons = polygonList
            else:
                self._polygons = None

        return self._polygons

    def expandGeom(self,geom=None):
        """
        Expand the geometry as a tree structure 
        """
        geom = geom or self.geom
        if isinstance(geom,Polygon):
            return ['polygon',self.geom]
        elif isinstance(geom,MultiPolygon):
            return ["multipolygon",[['polygon',g] for g in geom.geoms]]
        elif isinstance(self.geom,GeometryCollection):
            return ['geometrycollection',[self.expandGeom(g) for g in geom]]
        else:
            return ['other',self.geom]

    def addOrphanRing(self,expandedGeom,orphanRings):
        """
        Try to add orphan interior ring into one of the poylgon,
        if this ring is contained by one polygon, then add it to the polygon as interior ring 
        if this ring is not contained by any polygon, then add it as indenpendent polygon
        """
        fix_types = 0
        def _addAsInteriorRing(expandedGeom,orphanPoly):
            if expandedGeom[0] == 'polygon':
                if expandedGeom[1].contains(orphanPoly):
                    #the polygon contains the orphan polygon, add the orphan polygon as a interior ring.
                    expandedGeom[1] = Polygon(expandedGeom[1].exterior,[r for r in expandedGeom[1].interiors] + [LinearRing([c for c in reversed(orphanPoly.exterior.coords)])])
                    return True
                else:
                    return False
            elif expandedGeom[0] == 'other':
                return False
            elif expandedGeom[0] == 'multipolygon':
                for g in expandedGeom[1]:
                    if _addAsInteriorRing(g,orphanPoly):
                        return True
                return False
            elif expandedGeom[0] == 'geometrycollection':
                for g in expandedGeom[1]:
                    if _addAsInteriorRing(g,orphanPoly):
                        return True
                return False
            else:
                return False
        index = len(orphanRings) - 1
        while index >= 0:
            orphanRing = LinearRing(orphanRings[index])
            if orphanRing.is_ccw:
                orphanPoly = Polygon(LinearRing(reversed(orphanRing.coords)))
            else:
                orphanPoly = Polygon(orphanRing)
            if _addAsInteriorRing(expandedGeom,orphanPoly):
                fix_types |= self.FIX_ORPHAN_RING_AS_INTERIOR_RING
                del orphanRings[index]
            index -= 1

        if orphanRings:
            fix_types |= self.FIX_ORPHAN_RING_AS_ISLAND
            self.print_progress_status("Still have some orphan rings are not contained by polygon, added them as independent polygons")
            if expandedGeom[0] == 'polygon':
                expandedGeom = ["multipolygon",[expandedGeom]]
                for orphanRing in orphanRings:
                    orphanRing = LinearRing(orphanRing)
                    if orphanRing.is_ccw:
                        orphanPoly = Polygon(LinearRing(reversed(orphanRing.coords)))
                    else:
                        orphanPoly = Polygon(orphanRing)
                    expandedGeom[1].append(['polygon',orphanPoly])
            elif expandedGeom[0] in ("multipolygon","geometrycollection"):
                for orphanRing in orphanRings:
                    orphanRing = LinearRing(orphanRing)
                    if orphanRing.is_ccw:
                        orphanPoly = Polygon(LinearRing(reversed(orphanRing.coords)))
                    else:
                        orphanPoly = Polygon(orphanRing)
                    expandedGeom[1].append(['polygon',orphanPoly])
            else:
                raise Exception("Doesn't support expanded geometry type ({})".format("expandedGeom[0]"))

        return fix_types

    def collapseGeom(self,expandedGeom):
        """
        Collapse a expanded tree structure as a single geometry
        """
        if expandedGeom[0] == 'polygon':
            return expandedGeom[1]
        elif expandedGeom[0] == 'other':
            return expandedGeom[1]
        elif expandedGeom[0] == 'multipolygon':
            return MultiPolygon([self.collapseGeom(g) for g in expandedGeom[1]]) 
        elif expandedGeom[0] == 'geometrycollection':
            return GeometryCollection([self.collapseGeom(g) for g in expandedGeom[1]]) 
        else:
            raise Exception("Unsupported geometry type {}".format(expandedGeom[0]))
            
    def first_selfintersect_point(self,ring_coords):
        """
        return the first selfintersect point
        """
        index = 0
        coord_map = {}
        for coord in ring_coords:
            if coord in coord_map:
                if index not in [0,len(ring_coords) - 1]:
                    return (coord,coord_map[coord],index)
            else:
                coord_map[coord] = index
            index += 1
    
        return None


    def selfintersect_points(self,ring):
        index = 0
        coord_map = {}
        duplicate_coords = []
        for coord in ring.coords:
            if coord in coord_map:
                coord_map[coord].append(index)
                if coord not in duplicate_coords:
                    duplicate_coords.append(coord)
            else:
                coord_map[coord] = [index]
            index += 1
    
        result = []
        duplicate_coords.sort(key=lambda coord:coord_map[coord][0])
    
        for coord in duplicate_coords:
            if any([i for i in coord_map[coord] if i != 0 and  i != len(ring.coords) - 1]):
                result.append((coord,coord_map[coord]))
    
        return result

    def split_intersectlines(self,ring):
        """
        find intersectlines 
        if find, split the line into two lines, and return new ring;otherwise return False
        """
        index = 0
        coords_len = len(ring.coords)
        lines = []
        #genarte all lines
        while index < coords_len - 1:
            lines.append(LineString(ring.coords[index:index+2]))
            index += 1
        self.print_progress_status("have {} lines for processing ".format(len(lines)))
        index = 0
        lines_len = len(lines)
        changed = False
        intersected_lines = []
        while index < lines_len - 2:
            #self.print_progress_status("check line {}/{}".format(index + 1,len(lines)))
            subindex = index + 2
            while subindex < lines_len:
                intersected_point = lines[index].intersection(lines[subindex])
                if intersected_point:
                    intersected_coord = intersected_point.coords[0]
                    if intersected_coord not in lines[subindex].coords or intersected_coord not in lines[index].coords:
                        intersected_lines.append(((index,intersected_coord not in lines[index].coords),(subindex,intersected_coord not in lines[subindex].coords),intersected_coord))
                    if intersected_coord not in lines[subindex].coords:
                        lines.insert(subindex + 1,LineString([intersected_coord,lines[subindex].coords[1]]))
                        lines[subindex] = LineString([lines[subindex].coords[0],intersected_coord])
                        lines_len += 1
                        changed = True
                        self.print_progress_status("Split the intersected lines into two lines.  index={} ,coords={}".format(subindex,intersected_coord))

                    if intersected_coord not in lines[index].coords:
                        lines.insert(index + 1,LineString([intersected_coord,lines[index].coords[1]]))
                        lines[index] = LineString([lines[index].coords[0],intersected_coord])
                        lines_len += 1
                        changed = True
                        self.print_progress_status("Split the intersected lines into two lines. index={} ,coords={}".format(index,intersected_coord))


                subindex += 1

            index += 1

        if changed:
            ring = LinearRing([l.coords[0] for l in lines] + [lines[-1].coords[1]])
            if ring.coords[0] != ring.coords[-1]:
                raise Exception("The first and last coords of the Ring after splitting intersectlines are not same")
            return ring

        return None

    def check_ring(self,feat):
        if feat["geometry"]["type"] == "Polygon":
            polygonlist = [feat["geometry"]["coordinates"]]
        elif feat["geometry"]["type"] == "MultiPolygon":
            polygonlist = feat["geometry"]["coordinates"]
        elif feat["geometry"]["type"] == "GeometryCollection":
            raise Exception("{} Not Support".format(feat["geometry"["type"]]))
        else:
            return None

        if not polygonlist:
            return None

        nonclosed_polygons = []
        index = 0
        while index < len(polygonlist):
            try:
                poly = polygonlist[index]
                nonclosed_rings = []
                ring_index = 0
                for ring in poly:
                    if ring[0] != ring[-1]:
                        nonclosed_rings.append((ring_index,(ring[0],ring[-1])))
                    ring_index += 1
                    
                if nonclosed_rings:
                    nonclosed_polygons.append((index,nonclosed_rings))
            finally:
                index += 1

        return nonclosed_polygons

    def check_intersect(self):
        polygonList = self.polygons()
    
        if not polygonList:
            return None

        intersect_polygons = []
        index = 0
        while index < len(polygonList) - 1:
            subindex = index + 1
            path1,poly1 = polygonList[index]
            index += 1
            while subindex < len(polygonList):
                path2,poly2 = polygonList[subindex]
                subindex += 1
                if poly1.contains(poly2):
                    intersect_polygons.append( ((path1,poly1),(path2,poly2),('contain',poly2)) )
                elif poly2.contains(poly1):
                    intersect_polygons.append( ((path2,poly2),(path1,poly1),('contain',poly1)) )
                else:
                    intersections = extractPolygons(poly1.intersection(poly2))
                    if intersections:
                        intersect_polygons.append( ((path2,poly2),(path1,poly1),('intersect',intersections)) )
        return intersect_polygons


    def check_selfintersect(self):
        polygonList = self.polygons()
    
        if not polygonList:
            return None

        selfintersect_polygons = []
        for path,poly in polygonList:
            selfintersect_rings = []
            index = 0
            for ring in [poly.exterior] + list(poly.interiors):
                selfintersects = self.selfintersect_points(ring)
                if selfintersects:
                    selfintersect_rings.append((index,selfintersects))
                index += 1
                    
            if selfintersect_rings:
                selfintersect_polygons.append((path,selfintersect_rings))

        return selfintersect_polygons

    def exportPolygon(self):
        polygons = self.polygons(True)
        for path,polygon in polygons:
            exportGeojson(polygon,os.path.join(tempfile.gettempdir(),"{}_{}.geojson".format(self.name,path.replace('.','-'))))

    def fix_selfintersect(self,check_selfintersectlines=False):
        polygonList = self.polygons()
        if not polygonList:
            return None
        #import ipdb;ipdb.set_trace()
        expandedGeom = self.expandGeom()
        geom_fix_types = 0
        fixed_polygons = []
        #contain all orphan rings
        orphan_rings = []
        #one selfintersected will be replaced with multiple fixed polygons, so the path of the afterward polygon will be changed after one selfintersected polygon is replaced. 
        #this is the reason why we need to reverse the polygonList when fixing.
        for path,polygon in reversed(polygonList):
            fixed_polygons = []
            #contain all non self-intersected exterior rings 
            exterior_rings = []
            #contain all non self-intersected interior rings 
            interior_rings = []
            #import ipdb;ipdb.set_trace()
            #contain all rings which require self-intersection detection and fixing
            all_rings = []
            fix_types = 0
            #add exterior rings to all_rings as exterior ring and also make sure the ring is  clock-wise direction.
            if polygon.exterior.is_ccw:
                all_rings.append([exterior_rings,0,LinearRing(reversed(polygon.exterior.coords))])
                fix_types |= self.FIX_RING_ORIENT
            else:
                all_rings.append([exterior_rings,0,polygon.exterior])

            #add interior rings contained by exterior ring to all_rings as interior rings, and also make sure the rings are  counter clockwise direction.
            #add interior rings not contained by exterior ring to all_rings as orphan rings, and also make sure the rings are  counter clockwise direction.
            i = 1
            exterior_polygon = Polygon(all_rings[0][2])
            for r in polygon.interiors:
                polygon_r = Polygon(r)
                if exterior_polygon.contains(polygon_r):
                    if r.is_ccw:
                        all_rings.append([interior_rings,i,r])
                    else:
                        all_rings.append([interior_rings,i,LinearRing(reversed(r.coords))])
                        fix_types |= self.FIX_RING_ORIENT
                elif intersects(exterior_polygon,polygon_r) and difference(symmetric_difference(polygon_r,exterior_polygon),exterior_polygon):
                    exportGeojson((self.geom,self.properties),"/tmp/invalid_feature.geojson")
                    exportGeojson((polygon,self.properties),"/tmp/invalid_feature_polygon_{}.geojson".format(path))
                    exportGeojson((exterior_polygon,self.properties),"/tmp/invalid_feature_polygon_{}_exterior.geojson".format(path))
                    exportGeojson((polygon_r,self.properties),"/tmp/invalid_feature_polygon_{}_interior.geojson".format(path))
                    exportGeojson((difference(symmetric_difference(polygon_r,exterior_polygon),exterior_polygon),self.properties),"/tmp/invalid_feature_polygon_{}_invalid.geojson".format(path))
                    raise Exception("The exterior ring of the polygon({}) is intersected with interior ring".format(path))
                else:
                    fix_types |= self.FIX_ORPHAN_RINGS
                    if r.is_ccw:
                        all_rings.append([orphan_rings,i,r])
                    else:
                        all_rings.append([orphan_rings,i,LinearRing(reversed(r.coords))])

                i += 1

            #detect and fix intersect lines
            if check_selfintersectlines:
                i = 0
                while i < len(all_rings):
                    self.print_progress_status("processing ring {}/{}".format(i + 1,len(all_rings)))
                    fixed_ring = self.split_intersectlines(all_rings[i][2])
                    if fixed_ring:
                        fix_types |= self.FIX_SELFINTERSECT_LINES
                        all_rings[i][2] = fixed_ring
                    i += 1


            #Repopulate the polygon, which has exterior ring with clock-wise direction, and interior rings with counter clockwise direction, 
            #and also interior rings not contained by exterior ring are removed from original polygon,
            polygon = Polygon(LinearRing(all_rings[0][2]),[LinearRing(r[2]) for r in all_rings[1:]])

            #detect and fix selfintersection rings 
            while all_rings:
                rings,ring_index,ring = all_rings[0]
                del all_rings[0]

                check_rings = [ring.coords]
                #detect and fix the current ring and the rings splitted from the current ring.
                while check_rings:
                    check_ring = check_rings[0]
                    del check_rings[0]

                    first_selfintersect_point = self.first_selfintersect_point(check_ring)
                    if not first_selfintersect_point:
                        #no self-intersection found, add it to fixed rings(exterior_rings or interior_rings or orphan_rings)
                        rings.append(check_ring)
                        continue
                    coord,start_pos,end_pos  = first_selfintersect_point

                    """
                    if ring_index == 0:
                        self.print_progress_status("Split the exterior ring of the polygon({}) as {} :coord = {}, start_pos = {}, end_pos = {}".format(path,"exterior ring" if exterior else "interior ring",coord,start_pos,end_pos))
                    else:
                        self.print_progress_status("Split the interior({}) ring of the polygon({}) as {} :coord = {}, start_pos = {}, end_pos = {}".format(ring_index - 1,path,"exterior ring" if exterior else "interior ring",coord,start_pos,end_pos))
                    """
                    if start_pos + 1 == end_pos:
                        #duplicate points 
                        fix_types |= self.REMOVE_DUPLICATE_POINT
                        ring1 = check_ring[0:start_pos] + check_ring[end_pos:]
                        check_rings.insert(0,ring1)
                        continue
                    elif start_pos == 0 and end_pos + 1 == len(check_ring) - 1:
                        #duplicate points 
                        fix_types |= self.REMOVE_DUPLICATE_POINT
                        ring1 = check_ring[:end_pos + 1]
                        check_rings.insert(0,ring1)
                        continue


                    if start_pos == 0:
                        #first point is the self-intersected point, split it into two rings in the middle
                        ring1 = check_ring[:end_pos + 1 ]
                        ring2 = check_ring[end_pos:]
                    else:
                        #The two self-intersected points are in the middle, extract the self-intersected section as a ring , and the remain points including one self-intersected point as the other ring.
                        ring1 = check_ring[0:start_pos] + check_ring[end_pos:]
                        ring2 = check_ring[start_pos:end_pos + 1 ]
                    #validate the splitted two rings
                    for r in (ring1,ring2):
                        if len(r) < 4:
                            if ring_index == 0:
                                raise Exception("Fix the exterior ring of the polygon({}) failed, the splitted ring only has {} points ".format(path, len(r)))
                            else:
                                raise Exception("Fix the interior ring ({}) of the polygon({}) failed, the splitted ring only has {} points ".format(ring_index - 1,path, len(r)))

                        if r[0] != r[-1]:
                            if ring_index == 0:
                                raise Exception("Fix the exterior ring of the polygon({}) failed, the fist point of the splitted ring is not the same point as the last point.({} <> {}) ".format(path, r[0], r[-1] ))
                            else:
                                raise Exception("Fix the interior ring ({}) of the polygon({}) failed, the fist point of the splitted ring is not the same point as the last point.({} <> {}) ".format(ring_index - 1,path, r[0],r[-1] ))

                    #detect the right type(exterior,interior or orphan) and add them into check_rings or all_rings
                    if Polygon(ring1).contains(Polygon(ring2)):
                        if rings == exterior_rings:
                            check_rings.insert(0,ring1)
                            all_rings.insert(0,(interior_rings,ring_index,LinearRing(ring2)))
                            if ring_index == 0:
                                fix_types |= self.SPLIT_EXTERIOR_RING_2_EXTERIOR_HOLE
                            else:
                                fix_types |= self.SPLIT_INTERIOR_HOLE_2_INTERIOR_RING
                        elif rings == interior_rings:
                            #this is a island,add ring2 as another exterior ring.
                            check_rings.insert(0,ring1)
                            all_rings.insert(0,(exterior_rings,ring_index,LinearRing(ring2)))
                            if ring_index == 0:
                                fix_types |= self.SPLIT_EXTERIOR_HOLE_2_EXTERIOR_RING
                            else:
                                fix_types |= self.SPLIT_INTERIOR_RING_2_INTERIOR_HOLE
                        else:
                            if ring_index == 0:
                                raise Exception("Fix the exterior ring of the polygon({}) failed, found island in orphan ring".format(path))
                            else:
                                raise Exception("Fix the interior ring({}) of the polygon({}) failed, found island in orphan ring".format(ring_index - 1,path))
                        continue
                    elif Polygon(ring2).contains(Polygon(ring1)):
                        if rings == exterior_rings:
                            check_rings.insert(0,ring2)
                            all_rings.insert(0,(interior_rings,ring_index,LinearRing(ring1)))
                            if ring_index == 0:
                                fix_types |= self.SPLIT_EXTERIOR_RING_2_EXTERIOR_HOLE
                            else:
                                fix_types |= self.SPLIT_INTERIOR_HOLE_2_INTERIOR_RING
                        elif rings == interior_rings:
                            #this is a island,add ring1 as another exterior ring.
                            check_rings.insert(0,ring2)
                            all_rings.insert(0,(exterior_rings,ring_index,LinearRing(ring1)))
                            if ring_index == 0:
                                fix_types |= self.SPLIT_EXTERIOR_HOLE_2_EXTERIOR_RING
                            else:
                                fix_types |= self.SPLIT_INTERIOR_RING_2_INTERIOR_HOLE
                        else:
                            if ring_index == 0:
                                raise Exception("Fix the exterior ring of the polygon({}) failed, found island in orphan ring".format(path))
                            else:
                                raise Exception("Fix the interior ring({}) of the polygon({}) failed, found island in orphan ring".format(ring_index - 1,path))
                    elif extractPolygons(Polygon(ring1).intersection(Polygon(ring2))):
                        if ring_index == 0:
                            raise Exception("Fix the exterior ring of the polygon({}) failed, found intersection between the splitted two rings".format(path))
                        else:
                            raise Exception("Fix the interior ring({}) of the polygon({}) failed, found intersection between the splitted two rings".format(ring_index - 1,path))
                    else:
                        check_rings.insert(0,ring1)
                        check_rings.insert(1,ring2)
                        if rings == exterior_rings:
                            if ring_index == 0:
                                fix_types |= self.SPLIT_EXTERIOR_RING
                            else:
                                fix_types |= self.SPLIT_INTERIOR_HOLE
                        elif rings == interior_rings:
                            if ring_index == 0:
                                fix_types |= self.SPLIT_EXTERIOR_HOLE
                            else:
                                fix_types |= self.SPLIT_INTERIOR_RING
                        else:
                            fix_types |= self.SPLIT_ORPHAN_RING

                        #import ipdb;ipdb.set_trace()
            #save the current polygon as a independent feature for testing if the current polygon is not changed.
            if not fix_types :
                continue
            #import ipdb;ipdb.set_trace()
            #try to populate the polygons from fixed exterior rings and interior rings.
            #import ipdb;ipdb.set_trace()
            geom_fix_types |= fix_types
            if interior_rings:
                for exterior_ring_coords in exterior_rings:
                    exterior_ring = Polygon(LinearRing(exterior_ring_coords))
                    interior_index = len(interior_rings) - 1
                    interior_rings_coords = []
                    while interior_index >= 0:
                        interior_ring = Polygon(LinearRing(interior_rings[interior_index]))
                        if exterior_ring.contains(interior_ring):
                            interior_rings_coords.append(interior_rings[interior_index])
                            del interior_rings[interior_index]
                        interior_index -= 1

                    if interior_rings_coords:
                        fixed_polygons.append(Polygon(exterior_ring_coords,interior_rings_coords))
                    else:
                        fixed_polygons.append(Polygon(exterior_ring_coords))

                if interior_rings:
                    #import ipdb;ipdb.set_trace()
                    raise Exception("Some interior rings are not in polygon.")
            else:
                for exterior_ring_coords in exterior_rings:
                    fixed_polygons.append(Polygon(exterior_ring_coords))

            polygon_area = calculateGeometryArea(polygon)
            fixed_polygon_area = calculateGeometryArea(MultiPolygon(fixed_polygons))
            self.print_progress_status("Original polygon area = {}, fixed polygon area = {},fix types = {}".format(polygon_area,fixed_polygon_area,self.fix_type_names(fix_types)))
            #replace the selfintersected polygon in the expanded geom

            #replace the current polygon with fixed polygon
            paths = [int(i) for i in path.split(".")]
            #find the parent geometry
            parentGeom = expandedGeom
            for p in paths[0:-1]:
                if parentGeom[0] not in ('multipolygon','geometrycollection'):
                    raise Exception("container geometry is not multipolygon and geometrycollection")
                parentGeom = parentGeom[1][p]
            #remove the current polygon from parent geometry and add the fixed polygons to parent geometry
            if paths[-1] == 0:
                if parentGeom[0] == 'polygon':
                    parentGeom[0] = 'multipolygon'
                    parentGeom[1] = [["polygon",p] for p  in fixed_polygons]
                elif parentGeom[0] == 'other':
                    raise Exception("Replaced geometry type is 'other', can't be replaced by a polygon")
                else:
                    del parentGeom[1][paths[-1]]
                    for poly in reversed(fixed_polygons):
                        parentGeom[1].insert(paths[-1],['polygon',poly])
            else:
                del parentGeom[1][paths[-1]]
                for poly in reversed(fixed_polygons):
                    parentGeom[1].insert(paths[-1],['polygon',poly])


        if geom_fix_types:
            #the current geometry is selfintersected and already fixed.
            #import ipdb;ipdb.set_trace()
            if orphan_rings:
                #found some orphan ring , add the orphan rings to geometry
                geom_fix_types |= self.addOrphanRing(expandedGeom,orphan_rings)

            
            fixed_geom = self.collapseGeom(expandedGeom)
            #PolygonUtil(self.name,fixed_geom,print_progress_status=self.print_progress_status,properties=self.properties).exportPolygon()
            return (fixed_geom,geom_fix_types)
        else:
            return None


def check_geometry(geojsonfile,src_proj="EPSG:4326",target_proj='EPSG:4326',print_progress_status=None,print_result=False,print_timestamp=True):
    print_progress_status = print_progress_status or default_print_progress_status(print_timestamp)
    with open(geojsonfile) as f:
        geojson = json.loads(f.read())

    features = geojson["features"]

    selfintersect_features = []
    for feat in features:
        geom = getShapelyGeometry(feat)
        if not geom:
            continue
        geometry = transform(geom,src_proj,target_proj)
        polygonutil = PolygonUtil("check_feature",geometry,print_progress_status=print_progress_status,properties=feat.get('properties'))
        checkresult = {}
        result = polygonutil.check_selfintersect()
        if result:
            checkresult["selfintersect_polygons"] = result

        result = polygonutil.check_ring(feat)
        if result:
            checkresult["nonclosed_polygons"] = result

        try:
            result = polygonutil.check_intersect()
            if result:
                checkresult["intersected_polygons"] = result
        except:
            pass

        if checkresult:
            selfintersect_features.append((feat,checkresult))

    if print_result:
        if selfintersect_features:
            print_progress_status("Checking file '{}'".format(geojsonfile))
            print_checkresult(selfintersect_features,print_progress_status = print_progress_status)
            print_progress_status("")


    return selfintersect_features

def print_checkresult(selfintersect_features,properties=None,print_progress_status=None,print_timestamp=True):
    print_progress_status = print_progress_status or default_print_progress_status(print_timestamp)
    if selfintersect_features:
        new_line = False
        for feat,checkresult in selfintersect_features:
            print_progress_status("======================The following feature is invalid==============================")
            if properties:
                feat_properties = feat.get("properties") or {}
                for key in properties:
                    print_progress_status("{}={}".format(key,feat_properties.get(key) ))
            else:
                for key,value in (feat.get("properties") or {}).items():
                    print_progress_status("{}={}".format(key,value))
            print_progress_status("")
            

            nonclosed_polygons = checkresult.get("nonclosed_polygons")
            if nonclosed_polygons:
                new_line = True
                for path,nonclosed_rings in nonclosed_polygons:
                    print_progress_status("The {} polygon has non closed rings".format(path))
                    for index,coords in nonclosed_rings:
                        if index == 0:
                            print_progress_status("  The exterior ring is not closed.start coord={},end coord={}".format(coords[0],coords[1]))
                        else:
                            print_progress_status("  The interior ring({}) is not closed. start coord={}, end coord={}".format(index - 1,coords[0],coords[1]))

            selfintersect_polygons = checkresult.get("selfintersect_polygons")
            if selfintersect_polygons:
                if new_line:
                    print_progress_status("")
                new_line = True

                for path,selfintersect_rings in selfintersect_polygons:
                    print_progress_status("The {} polygon is self-intersected".format(path))
                    for index,selfintersects in selfintersect_rings:
                        if index == 0:
                            print_progress_status("  The exterior ring is self-intersected")
                        else:
                            print_progress_status("  The interior ring({}) is self-intersected".format(index - 1))
                        for coord,indexes in selfintersects:
                            print_progress_status("    Coordinate({}) is self-intersected at position({})".format(coord,indexes))

            intersected_polygons = checkresult.get("intersected_polygons")
            if intersected_polygons:
                if new_line:
                    print_progress_status("")
                new_line = True

                for poly1,poly2,intersection in intersected_polygons:
                    if intersection[0] == 'contain':
                        print_progress_status("The {} polygon contains the {} polygon. {} {}".format(poly1[0],poly2[0],os.linesep,intersection[1]))
                    else:
                        print_progress_status("The {} polygon is intersected with {} polygon,intersection is:{} {}".format(poly1[0],poly2[0],os.linesep,intersection[1]))

def fix_selfintersect(geojson,check_selfintersectlines=False,print_progress_status=None,fixed_file=None,id_property=None,print_timestamp=True):
    """
    if geojson can be a geojson file or geojson string
    if some the polygon fetures in this geosjon string or geojson file are selfintersected, a new file or geojson string  will be created to contain the fixed features and the other features and return the caller; 

    otherwise , return the same geojson file or geojson string.
    """
    print_progress_status = print_progress_status or default_print_progress_status(print_timestamp)
    isfile = None
    if geojson[-8:].lower() == ".geojson":
        with open(geojson) as f:
            geojsonFeatures = json.loads(f.read())
        isFile = True
    else:
        geojsonFeatures = json.loads(geojson)
        isFile = False

    features = geojsonFeatures["features"]
    index = 0
    changed = False
    #import ipdb;ipdb.set_trace()
    def basename(index):
        if isFile:
            if len(features) == 1:
                return os.path.split(geojson)[1][:-8]
            else:
                return "{}_{}".format(os.path.split(geojson)[1][:-8],index)
        else:
            if len(features) == 1:
                return "fixed_feature"
            else:
                return "fixed_feature_{}".format(index)


    fix_status = []
    if features and callable(id_property):
        id_property = id_property(features[0])


    while index < len(features):
        fixed_geom = None
        featureArea = None
        fixedFeatureArea = None
        feat = features[index]
        check_msg = None
        try:
            failed = False

            featureArea = calculateFeatureArea(feat)

            geom = getShapelyGeometry(feat)
            if not geom:
                continue
            fixed_geom = PolygonUtil(basename(index),geom,print_progress_status=print_progress_status,properties=feat.get('properties')).fix_selfintersect(check_selfintersectlines=check_selfintersectlines)
            if not fixed_geom:
                continue

            #PolygonUtil(basename(index),fixed_geom,print_progress_status=print_progress_status).exportPolygon()
            changed = True
            feat["geometry"].update(mapping(fixed_geom[0]))
            fixedFeatureArea = calculateFeatureArea(feat)
            print_progress_status("feature area = {},fixed feature area = {}, fix types = {}".format(featureArea,fixedFeatureArea,PolygonUtil.fix_type_names(fixed_geom[1])))


            selfintersect_polygons = PolygonUtil("check_feature",fixed_geom,print_progress_status=print_progress_status,properties=feat.get('properties')).check_selfintersect()
            if selfintersect_polygons:
                print_checkresult([(feat,selfintersect_features)],print_progress_status=print_progress_status)
                check_msg  = "Fix failed, still have selfintersection after fixing "
            else:
                check_msg  = "OK"

        except Exception as ex:
            failed = True
            raise
        finally:
            if failed:
                pass
            elif fixed_geom:
                if id_property:
                    fix_status.append((feat["properties"][id_property],{
                        "origin_feature_area":featureArea,
                        "fixed_feature_area":fixedFeatureArea,
                        "area_changed":abs(featureArea - fixedFeatureArea),
                        "fix_types":fixed_geom[1],
                        "fix_types_desc":" , ".join(PolygonUtil.fix_type_names(fixed_geom[1])),
                        "check_msg":check_msg

                        }))
                else:
                    fix_status.append((index,{
                        "origin_feature_area":featureArea,
                        "fixed_feature_area":fixedFeatureArea,
                        "area_changed":abs(featureArea - fixedFeatureArea),
                        "fix_types":fixed_geom[1],
                        "fix_types_desc":" , ".join(PolygonUtil.fix_type_names(fixed_geom[1])),
                        "check_msg":check_msg
                        }))
            else:
                if id_property:
                    fix_status.append((feat["properties"][id_property],{"fix_types":0,"fix_types_desc":"No change","origin_feature_area":featureArea}))
                else:
                    fix_status.append((index,{"fix_types":0,"fix_types_desc":"No change","origin_feature_area":featureArea}))
            index += 1

    if not changed:
        return (geojson,fix_status)

    if isFile or fixed_file:
        filename = fixed_file or os.path.join(tempfile.gettempdir(),"{}_fixed.geojson".format(os.path.split(geojson)[1][:-8]))
        with open(filename,'w') as f:
            f.write(json.dumps(geojsonFeatures,indent=True))
        return (filename,fix_status)
    else:
        return (features,fix_status)


def batch_fix(folder,check_selfintersectlines=False,clean=False,print_timestamp=True):
    if not os.path.exists(folder):
        raise Exception("The folder '{}' doesn't exist".format(folder))

    if not os.path.isdir(folder):
        raise Exception("The path '{}' is not a folder".format(folder))

    log_folder = os.path.join(folder,'log')
    processed_folder = os.path.join(folder,'processed')
    fixed_folder = os.path.join(folder,'fixed')
    status_folder = os.path.join(folder,'status')

    if not os.path.exists(log_folder):
        os.mkdir(log_folder)

    if not os.path.exists(processed_folder):
        os.mkdir(processed_folder)

    if not os.path.exists(fixed_folder):
        os.mkdir(fixed_folder)

    if not os.path.exists(status_folder):
        os.mkdir(status_folder)
    
    status_file = os.path.join(status_folder,'process_status.txt')
    failed_process_file = os.path.join(status_folder,'failed.txt')
    for f in (status_file,failed_process_file):
        try:
            #create the file if not  exist
            fd = os.open(f, os.O_CREAT|os.O_EXCL|os.O_RDWR)
            os.close(fd)
        except OSError as e:
            continue


    geojson_files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".geojson")])

    basename = lambda f:f[:len(".geojson") * -1]


    f_logfile = lambda f:os.path.join(log_folder,"{}.log".format(basename(f)))
    f_source_file = lambda f:os.path.join(folder,f)
    f_processed_file = lambda f:os.path.join(processed_folder,f)
    f_fixed_file = lambda f:os.path.join(fixed_folder,f)

    if clean:
        #try to remove the log file whose geojson file processing is not finished.
        for geojson_file in geojson_files:
            logfile = f_logfile(geojson_file)
            if os.path.exists(logfile):
                #processed
                if not os.path.exists(os.path.join(processed_folder,geojson_file)):
                    #process not finished
                    os.remove(logfile)

    logfile_fd = None
    def _print_process_status(msg):
        if logfile_fd:
            if print_timestamp:
                if msg:
                    os.write(logfile_fd,"{} : {}{}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),msg,os.linesep))
                else:
                    os.write(logfile_fd,"{}".format(os.linesep))
            else:
                if msg:
                    os.write(logfile_fd,"{}{}".format(msg,os.linesep))
                else:
                    os.write(logfile_fd,"{}".format(os.linesep))


    def _write_fix_status(geojson_file,fix_status):
        with open(status_file,'a') as f:
            f.write("{} = {}{}".format(geojson_file,json.dumps(fix_status),os.linesep))

    def _write_failed(geojson_file,msg):
        with open(failed_process_file,'a') as f:
            f.write("{} : {} = {}{}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),geojson_file,msg,os.linesep))

    #processing
    for geojson_file in geojson_files:
        logfile_fd = None
        logfile = f_logfile(geojson_file)
        source_file = f_source_file(geojson_file)
        fixed_file = f_fixed_file(geojson_file)
        processed_file = f_processed_file(geojson_file)
        try:
            try:
                logfile_fd = os.open(logfile, os.O_CREAT|os.O_EXCL|os.O_RDWR)
            except OSError as e:
                continue

            print("Processing '{}'".format(source_file))

            _print_process_status("Processing '{}'".format(geojson_file))

            selfintersected_features = check_geometry(source_file)
            if selfintersected_features:
                print_checkresult(selfintersected_features,print_progress_status=_print_process_status)

            fixed_file,fix_status = fix_selfintersect(source_file,check_selfintersectlines=check_selfintersectlines,print_progress_status=_print_process_status,fixed_file=fixed_file,id_property=lambda feat:[p for p in ["fire_number","ogc_fid",None] if p is None or p in feat["properties"]][0])
            _print_process_status("End to process '{}'".format(geojson_file))

            _write_fix_status(geojson_file,fix_status)
            copyfile(source_file,processed_file)
        except Exception as ex:
            traceback.print_exc()
            _write_failed(geojson_file,ex.message)

        finally:
            if logfile_fd:
                try:
                    os.close(logfile_fd)
                    logfile_fd = None
                except:
                    pass
 
def process_status_report(folder):
    status_folder = os.path.join(folder,'status')
    process_status_file = os.path.join(status_folder,'process_status.txt')
    merged_process_status_file = os.path.join(status_folder,'process_status_merged.txt')
    fixed_status_file = os.path.join(status_folder,'fixed_status.txt')
    if not os.path.exists(process_status_file):
        raise Exception("The process status file '{}' does not exist".format(process_status_file))
    #read all lines from process_status.txt
    lines = []
    with open(process_status_file) as f:
        while True:
            line = f.readline()
            if line:
                lines.append(line)
            else:
                break
    
    #get all files from process_status.txt
    files = [l.split('=')[0].strip() for l in lines]
    
    #detect the duplicate file items in process_status.txt
    file_map = {}
    duplicate_files=[]
    index = 0
    while index < len(files):
        f = files[index]
        if f in file_map:
            if f not in duplicate_files:
                duplicate_files.append(f)
            file_map[f].append(index)
        else:
            file_map[f] = [index]
        index += 1
    
    #remove the duplicate file items, only keep the last item for a single file
    new_lines = []
    index  = 0
    while index < len(lines):
        try:
            f = files[index]
            if f in duplicate_files:
                if index == file_map[f][-1]:
                    new_lines.append(lines[index])
                else:
                    continue
            else:
                new_lines.append(lines[index])
        finally:
            index += 1
    
    #write to the fixed process status file
    with open(merged_process_status_file,'wb') as f:
        for l in new_lines:
            f.write(l)
    print("check the process status in new file '{}'".format(merged_process_status_file))
    
    #write to the fixed process status file
    with open(fixed_status_file,'wb') as f:
        for l in new_lines:
            if "fixed_feature_area" in l:
                f.write(l)
    print("check the fixed status in new file '{}'".format(fixed_status_file))

    area_not_changed = 0
    area_changed = 0
    max_area_diff = 0
    fix_type_report = {}

    failed_map = {}
    features = 0
    fixed_features = []

    for key in PolygonUtil.FIX_TYPES.keys():
        fix_type_report[key] = []

    for l in new_lines:
        f,f_status = [s.strip() for s in l.strip().split("=")]
        feature_status_list = json.loads(f_status)
        for featureid,status in feature_status_list:
            features += 1
            if status["fix_types"] > 0:
                fixed_features.append(feature_key)

            if len(feature_status_list) == 1:
                feature_key = f
            else:
                feature_key = "{}.{}".format(f,featureid)

            if status["fix_types"] > 0:
                if status["area_changed"] == 0:
                    area_not_changed += 1
                else:
                    area_changed += 1
                    if max_area_diff < status["area_changed"]:
                        max_area_diff = status["area_changed"]

                for key in PolygonUtil.FIX_TYPES.keys():
                    if key & status["fix_types"] == key:
                        fix_type_report[key].append(feature_key)

                if "check_msg" in status:
                    if status["check_msg"] != "OK":
                        failed_map[feature_key] = status["check_msg"]


    print("=========================================================")
    print("{} features are processed,{} features are fixed,area not changed features:{}, area changed features:{}, max area difference:{}".format(features,len(fixed_features),area_not_changed,area_changed,max_area_diff))
    print("Fix type report")
    for t,features in fix_type_report.items():
        if features:
            print("    {}: {}".format(PolygonUtil.FIX_TYPES[t],len(features)))
    if failed_map:
        print("After fixed, the following features still have issues.")
        for f,msg in failed_map:
            print("    {} : {}".format(f,msg))

    #find the files not included in process status file
    new_files = [l.split("=")[0].strip() for l in new_lines]
    
    first = False
    geojson_files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".geojson")])
    for f in geojson_files:
        if f not in new_files:
            if first:
                first = False
                print("The following files are not processed.")
            print("    {}".format(f))
    print("=========================================================")

def merge_geometries(geojsonfiles,crs="EPSG:4326",calculate_area=False,merged_file=None,merged_properties=None):
    if isinstance(geojsonfiles,str):
        geojsonfiles = [geojsonfiles]

    merged_geom = None
    feat_count = 0
    properties = {}
    for geojsonfile in geojsonfiles:
        with open(geojsonfile) as f:
            features = json.loads(f.read())
        for feat in features["features"]:
            feat_count += 1
            if merged_properties:
                for prop in merged_properties:
                    if prop in feat["properties"]:
                        merged_prop = "merged_{}".format(prop)
                        if feat["properties"][prop] is None:
                            continue;
                        elif isinstance(feat["properties"][prop],(int,float)):
                            properties[merged_prop] = properties.get(merged_prop,0) + feat["properties"][prop]
                        else:
                            raise Exception("Unsupported property type ({}.{})".format(feat["properties"][prop].__class__.__module__,feat["properties"][prop].__class__.__name__))
            if merged_geom:
                merged_geom = mergeGeometry(merged_geom,getShapelyGeometry(feat))
            else:
                merged_geom = getShapelyGeometry(feat)

    properties["merged_features"] = feat_count

    if calculate_area:
        properties["area"] = calculateGeometryArea(merged_geom,src_proj=crs)

    exportGeojson((merged_geom,properties),merged_file or '/tmp/feature_merged.geojson')

    return merged_file


def subtract_geometries(mainfile,subtract_files,crs="EPSG:4326",calculate_area=False,diff_file=None,print_timestamp=True):
    print_progress_status = default_print_progress_status(print_timestamp)

    diff_file = diff_file or '/tmp/feature_diff.geojson'
    if isinstance(subtract_files,str):
        subtract_files = [subtract_files]

    properties = {}
    features = []

    with open(mainfile) as f:
        main_features = json.loads(f.read())
    for main_feat in main_features["features"]:
        main_geom = extractPolygons(getShapelyGeometry(main_feat))
        subtract_count = 0
        for subtract_file in subtract_files:
            if not main_geom:
                break
            with open(subtract_file) as f:
                subtract_features = json.loads(f.read())
            print(subtract_file)
            for subtract_feat in subtract_features["features"]:
                """
                if "other_tenures" in subtract_file and subtract_feat["properties"]["ogc_fid"] == 296326:
                    #ignore one tenure
                    continue
                """
                subtract_geom = getShapelyGeometry(subtract_feat)
                if subtract_feat["properties"]["ogc_fid"] == 61039:
                    fixed_geom = PolygonUtil("subtract_geom",subtract_geom,print_progress_status=print_progress_status,properties=subtract_feat.get('properties')).fix_selfintersect(check_selfintersectlines=True)
                    if fixed_geom:
                        subtract_geom = fixed_geom[0]


                if intersects(main_geom,subtract_geom):
                    print(subtract_feat["properties"])
                    subtract_count += 1
                    symmetric_g = symmetric_difference(main_geom,subtract_geom)
                    main_geom = difference(symmetric_g,subtract_geom)

                    if not main_geom:
                        break
        if main_geom:
            properties = main_feat["properties"]
            if "area" in properties:
                properties["original_area"] = properties["area"]
            properties["area"] = calculateGeometryArea(main_geom,src_proj=crs)
            properties["subtract_features"] = subtract_count

            features.append((main_geom,properties))


    if features:
        exportGeojson(features,diff_file or '/tmp/feature_diff.geojson')

    return diff_file

"""
merge_geometries([
    "./tmp/bf_2017_ekm_019/feature_area_in_legislated_lands_and_waters.geojson",
    "./tmp/bf_2017_ekm_019/feature_area_in_sa_nt_burntarea.geojson",
    "./tmp/bf_2017_ekm_019/feature_area_in_dept_interest_lands_and_waters.geojson",
    "./tmp/bf_2017_ekm_019/feature_area_in_other_tenures.geojson"
    ],crs='aea',calculate_area=True,merged_file="./tmp/bf_2017_ekm_019/feature_merged.geojson",merged_properties=['area'])
"""
"""
subtract_geometries("./tmp/bf_2017_ekm_019/feature_total_area.geojson",
    [
    "./tmp/bf_2017_ekm_019/feature_area_in_legislated_lands_and_waters.geojson",
    "./tmp/bf_2017_ekm_019/feature_area_in_sa_nt_burntarea.geojson",
    "./tmp/bf_2017_ekm_019/feature_area_in_dept_interest_lands_and_waters.geojson",
    "./tmp/bf_2017_ekm_019/feature_area_in_other_tenures.geojson"
    ],crs='aea',calculate_area=True,diff_file="./tmp/bf_2017_ekm_019/feature_diff.geojson")

"""

"""
subtract_geometries("./tmp/bf_2018_ekm_036/feature.geojson",
    [    
    "./tmp/bf_2018_ekm_036/feature_area_in_legislated_lands_and_waters.geojson",
    "./tmp/bf_2018_ekm_036/feature_area_in_sa_nt_burntarea.geojson",
    #"./tmp/bf_2018_ekm_036/feature_area_in_dept_interest_lands_and_waters.geojson",
    "./tmp/bf_2018_ekm_036/feature_area_in_other_tenures.geojson"
    ],crs='aea',calculate_area=True,diff_file="./tmp/bf_2018_ekm_036/feature_diff5.geojson")
"""

#check_geometry("./tmp/bfrs2018/BF_2018_EKM_029.geojson")


#folder='/home/rockyc/work/gokart/tmp/batch'
#folder='/home/rockyc/work/gokart/tmp/bfrs2017'
#batch_fix(folder,clean=True)



#filename='/home/rockyc/work/gokart/tmp/BF_2017_PIL_018_2018-06-29_033027.geojson'
#filename="/home/rockyc/work/gokart/tmp/bf_2017_ekm_024.geojson"

#process_status_report(folder)

#selfintersected_features = check_geometry(filename)
#print_checkresult(selfintersected_features)
#fixed_file,fix_status = fix_selfintersect(filename)
#print(fixed_file)

#print("Check whether the fixed features have selfintersection ")
#selfintersected_features = check_geometry(fixed_file)
#if selfintersected_features:
#    print_checkresult(selfintersected_features)
#else:
#    print("No selfintersection found")

#print_progress_status("Check whether the fixed features have selfintersection in aea projection")
#selfintersected_features = check_geometry(fixed_file,target_proj='aea')
#if selfintersected_features:
#    print_checkresult(selfintersected_features)
#else:
#    print_progress_status("No selfintersection found")
#selfintersected_features = check_geometry("/home/rockyc/work/gokart/tmp/BF_2017_EKM_024.geojson")
#print_checkresult(selfintersected_features)

#selfintersected_features = check_geometry("/home/rockyc/work/gokart/tmp/BF_2017_EKM_024_EPSG_4326.geojson")
#print_checkresult(selfintersected_features)
