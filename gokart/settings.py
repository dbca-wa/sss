import os
import dotenv
import bottle
import re
import pytz
import subprocess
import hashlib
import base64
import json
import osgeo
import datetime
import logging
import logging.config

logging.config.dictConfig({
    "version":1,
    "disable_existing_loggers":False,
    "handlers":{
        "default":{
            "class":"logging.StreamHandler",
            "level":"INFO"
        },
        "shapely_geos":{
            "class":"gokart.loghandlers.MessageHandler",
            "level":"INFO",
            "name":"shapely.geos"
        }
    },
    "loggers":{
        "shapely.geos": {
            "level":"INFO",
            "handlers":["shapely_geos"]
        }
    },
    "root":{
        "level":"INFO",
        "handlers":["default"]
    }
})

dotenv.load_dotenv(dotenv.find_dotenv())

bottle.TEMPLATE_PATH.append('./gokart')
bottle.debug(True)
bottle.BaseRequest.MEMFILE_MAX = 20 * 1024 * 1024

BASE_PATH = os.path.dirname(__file__)
ENV_TYPE = (os.environ.get("ENV_TYPE") or "prod").lower()
DIST_TYPE = (os.environ.get("DIST_TYPE") or "release").lower()
BASE_DIST_PATH = os.path.join(os.path.dirname(BASE_PATH),"dist")
DIST_PATH = os.path.join(os.path.dirname(BASE_PATH), "dist", DIST_TYPE)

KMI_SERVER = os.environ.get("KMI_SERVER") or "https://kmi.dbca.wa.gov.au/geoserver"

CHECK_OVERLAP_IF_CALCULATE_AREA_FAILED = (os.environ.get("CHECK_OVERLAP_IF_CALCULATE_AREA_FAILED") or "false").lower() in ["true","yes","on"]

STATIC_SERVICE=os.environ.get("STATIC_SERVICE") or "https://static.dbca.wa.gov.au"
WEATHERFORECAST_URL=os.environ.get("WEATHERFORECAST_URL") or ""
WEATHERFORECAST_USER=os.environ.get("WEATHERFORECAST_USER") or None
WEATHERFORECAST_PASSWORD=os.environ.get("WEATHERFORECAST_PASSWORD") or None

CALCULATE_AREA_IN_SEPARATE_PROCESS = (os.environ.get("CALCULATE_AREA_IN_SEPARATE_PROCESS") or "true").lower() in ["true","yes","on"]
EXPORT_CALCULATE_AREA_FILES_4_DEBUG = (os.environ.get("EXPORT_CALCULATE_AREA_FILES_4_DEBUG") or "false").lower() in ["true","yes","on"]

PERTH_TIMEZONE = datetime.datetime.now(pytz.timezone('Australia/Perth')).tzinfo

EMAIL_USER = os.environ.get("EMAIL_USER_TRACKING_POINT") 
EMAIL_PWD = os.environ.get("EMAIL_PWD_TRACKING_POINT") 

def get_bool(name,defaultValue=None):
    value = os.environ.get(name)
    if value is None:
        return defaultValue
    else:
        return True if value.lower() in ("true","yes","t","y") else False

def get_string(name,defaultValue=None):
    return os.environ.get(name,defaultValue)

session_key_header = "X-Session-Key"
sso_cookie_names = dict([ name.split(':') for name in (os.environ.get("SSO_COOKIE_NAME") or ".dbca.wa.gov.au:dbca_wa_gov_au_sessionid,.dpaw.wa.gov.au:dpaw_wa_gov_au_sessionid").split(",") ])

def get_request_domain():
    return bottle.request.urlparts[1]

def get_sso_cookie_name():
    domain = get_request_domain()

    try:
        return sso_cookie_names[domain]
    except:
        for key,value in sso_cookie_names.iteritems():
            if domain.endswith(key):
                sso_cookie_names[domain] = value
                return value

        raise "Please configure sso cookie name for domain '{}'".format(domain)

def get_session_cookie(template=None):
    """ 
    Get the session cookie from user request for sso
    if not found, raise 401
    template: cookie string template which has two parameters. 0: cookie  name 1:cookie value; if template is None, return dict object (key is cookie name, value is cookie value)
    """
    try:
        session_key = bottle.request.get_header(session_key_header)
        if session_key:
            if template:
                return template.format(get_sso_cookie_name(),session_key)
            else:
                return {get_sso_cookie_name():session_key}
        else:
            raise bottle.HTTPError(status=401)
    except:
        raise bottle.HTTPError(status=401)

def get_file_md5(f):
    get_md5 = subprocess.Popen(["md5sum",f], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    get_md5_output = get_md5.communicate()

    if get_md5.returncode != 0:
        raise bottle.HTTPError(status=500,body="Generate file md5 failed.{}".format(get_md5_output[1]))

    return get_md5_output[0].split()[0]


def get_md5(data):
    m = hashlib.md5()
    m.update(data)
    data = base64.urlsafe_b64encode(m.digest())
    if data[-3:] == "===":
        return data[0:-3]
    elif data[-2:] == "==":
        return data[0:-2]
    elif data[-1:] == "=":
        return data[0:-1]
    else:
        return data


#get type name from url
typename_re = re.compile("typenames?=\s*(?P<name>[a-zA-Z0-9_\-\:\%]+)\s*",re.DOTALL)
def typename(url):
    m = typename_re.search(url.lower())
    return m.group('name').replace("%3a",":") if m else None

kmiserver_re = re.compile("^(?P<url>[hH][tT][tT][pP][sS]?://[a-zA-Z0-9\-\_\./]+/geoserver)",re.DOTALL)
def kmiserver(url):
    m = kmiserver_re.search(url)
    if m:
        return "{}/".format(m.group('url'))
    else:
        return KMI_SERVER

def datetime_encoder(self,o):
    if isinstance(o,datetime.datetime):
        return o.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(o,osgeo.osr.SpatialReference):
        return str(o)
    else:
        raise TypeError("Unknown type {}".format(type(o)))
json.JSONEncoder.default = datetime_encoder
