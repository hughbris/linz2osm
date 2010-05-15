from django.contrib.gis import geos

from linz2osm.convert.processing.base import BaseProcessor, Error
    
class PolyWindingCW(BaseProcessor):
    """ Wind Polygons clockwise (outer ring) and anti-clockwise (inner rings) """
    
    geom_types = (geos.Polygon, geos.MultiPolygon)
    multi_geometries = False
    cw = True
    
    def handle(self, geometry, fields=None, tags=None, id=None):
        rings = list(geometry.tuple)
        for i in range(len(rings)):
            rings[i] = self.wind_ring(rings[i], i==0)
        
        return geos.Polygon(srid=geometry.srid, *rings)

    def ring_is_clockwise(self, p):
        """
        Returns True if the points in the given ring are in clockwise order,
        or False if they are in anticlockwise order. Calculates a cross product. 
        """
        clen = len(p) - 1
        assert clen >= 3
        total = 0
        for i in xrange(clen):
            x1, y1 = p[i]
            x2, y2 = p[(i + 1) % clen]
            x3, y3 = p[(i + 2) % clen]
            
            # A good cross product tutorial: http://www.netcomuk.co.uk/~jenolive/vect8.html
            
            # We have two vectors U and V such that U = (x2-x1, y2-y1), V = (x3-x2, y3-y2)
            # The cross product `U X V` of 2d vectors is given by UxVy - UyVx
            
            dx1 = x2 - x1
            dy1 = y2 - y1
            dx2 = x3 - x2
            dy2 = y3 - y2
            
            cp = dx1*dy2 - dy1*dx2
            
            # That cross product tells us the angular directionality of the corner 
            # defined by our two vectors U,V (negative means clockwise)
            
            # now we have a vector in the Z dimension with magnitude |U| * |V| * sin(theta)
            # where theta is the angle between U and V
            
            # get vector magnitudes
            u = float(dx1**2 + dy1**2)**0.5
            v = float(dx2**2 + dy2**2)**0.5
            
            # so now if we divide by the length of the vectors, we get sin(theta)
            # adding the sin'd thetas gives us a -ve number for clockwise or +ve for anticlockwise
            total += cp / (u*v)
        return (total <= 0)

    def wind_ring(self, ring, is_outer):
        if self.cw:
            wind_cw = is_outer
        else:
            wind_cw = not is_outer
        
        if self.ring_is_clockwise(ring) != wind_cw:
            ring = list(ring)
            ring.reverse()
        return ring

class PolyWindingCCW(PolyWindingCW):
    """ Wind Polygons anti-clockwise (outer ring) and clockwise (inner rings) """
    cw = False
