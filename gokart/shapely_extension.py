from .loghandlers import MessageHandler

from shapely.geometry import MultiPoint,Point,LineString,MultiLineString
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.collection import GeometryCollection

#customize is_valid

logger = MessageHandler("shapely.geos")
def check_valid(self):
    try:
        logger.restart()
        result = self.is_valid
        if result:
            return (result,None)
        else:
            return (result,logger.messages)
    finally:
        logger.stop()

def method_wrapper(cls,name):
    _original_method = getattr(cls,name)
    def _method(self,*args,**argv):
        try:
            logger.restart()
            return _original_method(self,*args,**argv)
        except Exception as ex:
            messages = logger.messages
            if messages:
                raise ex.__class__("{}({})".format(ex.message,"\r\n".join(logger.messages)))
            else:
                raise

        finally:
            logger.stop()
    return _method

for cls in (MultiPoint,Point,Polygon,MultiPolygon,GeometryCollection,LineString,MultiLineString):
    if hasattr(cls,"is_valid"):
        cls.check_valid = property(check_valid)

    for method_name in ("intersection",):
        setattr(cls,method_name,method_wrapper(cls,method_name))



