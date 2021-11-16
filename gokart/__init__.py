import json
import hashlib
import re
try:
    import uwsgi
except:
    # ignore uwsgi when profiling
    pass
import base64
import os
import pytz
import subprocess
import tempfile
import requests
import demjson
import datetime
import pytesseract
try:
    from PIL import Image
except:
    import Image

import bottle
import shapely_extension
import settings

import sys
import traceback


from .jinja2settings import settings as jinja2settings

import spatial
bottle.route("/spatial", "POST", spatial.spatial)

import gdal
bottle.route("/gdal/<fmt>", "POST", gdal.gdal)
bottle.route("/ogrinfo", "POST", gdal.ogrinfo)
bottle.route("/download/<fmt>", "POST", gdal.download)

import raster
bottle.route('/outlookmetadata', "GET", raster.outlookmetadata)
bottle.route('/weatheroutlook/<fmt>', "POST", raster.weatheroutlook)

import kmi
bottle.route('/kmi/layer', "GET", kmi.layermetadata)

import hotspot_emails
bottle.route("/hotspot_email_list", "GET", hotspot_emails.get_email_addresses)
bottle.route("/send_hotspot_email/<recipient>/<msg_text>/<flights>/<cql_filter>", "GET", hotspot_emails.send_email)

@bottle.route('/client')
def server_static():
    return bottle.static_file('client.html', root=settings.BASE_PATH)

profile_re = re.compile("gokartProfile\s*=\s*(?P<profile>\{.+\})\s*;?\s*exports.+default.+gokartProfile", re.DOTALL)
def _get_profile(app):
    # get app profile
    profile = None
    appPath = os.path.join(settings.DIST_PATH, "{}.js".format(app))
    if not os.path.exists(appPath):
        raise Exception("Application({}) Not Found".format(app))
    key = "{}_profile".format(app)
    profileChanged = False
    if uwsgi.cache_exists(key):
        profile = uwsgi.cache_get(key)
    if profile:
        profile = json.loads(profile)
        if repr(os.path.getmtime(appPath)) != profile["mtime"] or os.path.getsize(appPath) != profile["size"]:
            profileChanged = True
            profile = None
    if not profile:
        file_data = None
        with open(appPath, "rb") as f:
            file_data = f.read()
        m = profile_re.search(file_data)
        profile = {
            'mtime': repr(os.path.getmtime(appPath)),
            'size': os.path.getsize(appPath),
            'profile': demjson.decode(m.group("profile") if m else "{}")
        }
        m = hashlib.md5()
        m.update(file_data)
        profile['profile']['build']['md5'] = base64.urlsafe_b64encode(m.digest()).rstrip("=")
        file_data = None
        if profileChanged:
            uwsgi.cache_update(key, json.dumps(profile))
        else:
            uwsgi.cache_set(key, json.dumps(profile))

    profile["profile"]["dependents"] = {}
    # get vendor md5
    vendorPath = os.path.join(settings.DIST_PATH, "vendor.js")
    if not os.path.exists(vendorPath):
        raise Exception("Vendor library Not Found")
    key = "{}_profile".format("vendor")
    profileChanged = False
    vendorProfile = None
    if uwsgi.cache_exists(key):
        vendorProfile = uwsgi.cache_get(key)
    if vendorProfile:
        vendorProfile = json.loads(vendorProfile)
        if repr(os.path.getmtime(vendorPath)) != vendorProfile["mtime"] or os.path.getsize(vendorPath) != vendorProfile["size"]:
            profileChanged = True
            vendorProfile = None
    if not vendorProfile:
        m = hashlib.md5()
        with open(vendorPath, "rb") as f:
            m.update(f.read())
        vendorProfile = {
            'mtime': repr(os.path.getmtime(vendorPath)),
            'size': os.path.getsize(vendorPath),
            'vendorMD5': base64.urlsafe_b64encode(m.digest()).rstrip("=")
        }
        if profileChanged:
            uwsgi.cache_update(key, json.dumps(vendorProfile))
        else:
            uwsgi.cache_set(key, json.dumps(vendorProfile))
    profile["profile"]["dependents"]["vendorMD5"] = vendorProfile["vendorMD5"]
    # get env profile
    envPath = os.path.join(settings.BASE_DIST_PATH, 'release', 'static', 'js', "{}.env.js".format(settings.ENV_TYPE))
    if not os.path.exists(envPath):
        raise Exception("'{}.env.js' is missing.".format(settings.ENV_TYPE))
    else:
        key = "{}_{}_profile".format("env", settings.ENV_TYPE)
        profileChanged = False
        envProfile = None
        if uwsgi.cache_exists(key):
            envProfile = uwsgi.cache_get(key)
        if envProfile:
            envProfile = json.loads(envProfile)
            if repr(os.path.getmtime(envPath)) != envProfile["mtime"] or os.path.getsize(envPath) != envProfile["size"]:
                profileChanged = True
                envProfile = None
        if not envProfile:
            m = hashlib.md5()
            with open(envPath,"rb") as f:
                m.update(f.read())

            envProfile = {
                'mtime': repr(os.path.getmtime(envPath)),
                'size': os.path.getsize(envPath),
                'envMD5':base64.urlsafe_b64encode(m.digest()).rstrip("=")
            }
            if profileChanged:
                uwsgi.cache_update(key, json.dumps(envProfile))
            else:
                uwsgi.cache_set(key, json.dumps(envProfile))

        profile["profile"]["dependents"]["envMD5"] = envProfile["envMD5"]
        profile["profile"]["envType"] = settings.ENV_TYPE
    # get style profile
    stylePath = os.path.join(settings.BASE_DIST_PATH, 'release', 'static', 'css', "style.css")
    if not os.path.exists(stylePath):
        raise Exception("'style.css' is missing.")
    else:
        key = "style_profile"
        profileChanged = False
        styleProfile = None
        if uwsgi.cache_exists(key):
            styleProfile = uwsgi.cache_get(key)
        if styleProfile:
            styleProfile = json.loads(styleProfile)
            if repr(os.path.getmtime(stylePath)) != styleProfile["mtime"] or os.path.getsize(stylePath) != styleProfile["size"]:
                profileChanged = True
                styleProfile = None
        if not styleProfile:
            m = hashlib.md5()
            with open(stylePath,"rb") as f:
                m.update(f.read())
            styleProfile = {
                'mtime': repr(os.path.getmtime(stylePath)),
                'size': os.path.getsize(stylePath),
                'styleMD5':base64.urlsafe_b64encode(m.digest()).rstrip("=")
            }
            if profileChanged:
                uwsgi.cache_update(key, json.dumps(styleProfile))
            else:
                uwsgi.cache_set(key, json.dumps(styleProfile))
        profile["profile"]["dependents"]["styleMD5"] = styleProfile["styleMD5"]
    return profile["profile"]

@bottle.route("/profile/<app>")
def profile(app):
    #get app profile
    try:
        profile = _get_profile(app)
        bottle.response.set_header("Content-Type", "application/json")
        return profile
    except:
        bottle.response.status = 400
        bottle.response.set_header("Content-Type","text/plain")
        traceback.print_exc()
        return traceback.format_exception_only(sys.exc_type,sys.exc_value)

# serve up map apps
@bottle.route('/<app>')
def index(app):
    try:
        profile = _get_profile(app)
        if profile["dependents"]["vendorMD5"] != profile["build"]["vendorMD5"]:
            raise Exception("Application was built based on outdated vendor library, please build application again.")
        return bottle.template('index.html',template_adapter=bottle.Jinja2Template,template_settings=jinja2settings, app=app,envType=settings.ENV_TYPE,profile=profile,weatherforecast_url=settings.WEATHERFORECAST_URL)
    except:
        bottle.response.status = 400
        bottle.response.set_header("Content-Type","text/plain")
        #if app.isalnum():
        #   traceback.print_exc()
        return traceback.format_exception_only(sys.exc_type,sys.exc_value)

@bottle.route("/weatherforecast",method="POST")
def weatherforecast():
    #weather forecast
    try:
        if settings.WEATHERFORECAST_URL:
            requestData = bottle.request.forms.get("data")
            if requestData:
                requestData = json.loads(requestData)
            else:
                raise Exception("Request data are missing")
            requestData["weatherforecast_url"] = settings.WEATHERFORECAST_URL
            requestData["weatherforecast_user"] = settings.WEATHERFORECAST_USER
            requestData["weatherforecast_password"] = settings.WEATHERFORECAST_PASSWORD
            return bottle.template('weatherforecast.html',template_adapter=bottle.Jinja2Template,template_settings=jinja2settings,envType=settings.ENV_TYPE,request_time=datetime.datetime.now(settings.PERTH_TIMEZONE), **requestData)
        else:
            bottle.response.status = 404
            bottle.response.set_header("Content-Type","text/plain")
            return "Path '/weatherforecast' Not Found"
    except:
        bottle.response.status = 400
        bottle.response.set_header("Content-Type","text/plain")
        traceback.print_exc()
        return traceback.format_exception_only(sys.exc_type,sys.exc_value)

# saveas
@bottle.route("/saveas", method="POST")
def saveas():
    user = bottle.request.get_header("Remote-User", "anonymous")

    f = bottle.request.files.get("file")
    filename = f.raw_filename
    f.raw_filename = "_{}_{}".format(user, bottle.request.remote_addr).join(os.path.splitext(f.raw_filename))
    workdir = os.path.join(settings.BASE_PATH, "tmp")
    if not os.path.exists(workdir):
        # create dir if required.
        os.mkdir(workdir)
    path = os.path.join(workdir, f.filename)
    if os.path.exists(path):
        try:
            os.remove(path)
        except:
            pass
    f.save(workdir, overwrite=True)
    bottle.response.set_header("Content-Type", "text/plain")
    return bottle.request.url.replace("/saveas", "/fetch") + "/" + f.filename + "?filename=" + filename

# WMS shim for Himawari 8
# Landgate tile servers, round robin
FIREWATCH_SERVICE = "/mapproxy/firewatch/service"
FIREWATCH_GETCAPS = FIREWATCH_SERVICE + "?service=wms&request=getcapabilities"
FIREWATCH_HTTPS_VERIFY = settings.get_bool("FIREWATCH_HTTPS_VERIFY", True)


@bottle.route("/hi8/<target>")
def himawari8(target):
    last_updatetime = bottle.request.query.get("updatetime")
    baseUrl = bottle.request.url[0:bottle.request.url.find("/hi8")]
    key = "himawari8.{}".format(target)
    result = None
    getcaps = None
    if uwsgi.cache_exists("himawari8"):
        if uwsgi.cache_exists(key):
            result = json.loads(uwsgi.cache_get(key))
        else:
            getcaps = uwsgi.cache_get("himawari8")
    else:
        res = requests.get("{}{}".format(baseUrl,FIREWATCH_GETCAPS),verify=FIREWATCH_HTTPS_VERIFY)
        res.raise_for_status()
        getcaps = res.content
        getcaps = getcaps.decode("utf-8")
        uwsgi.cache_set("himawari8", getcaps, 60*10)  # cache for 10 mins

    if not result:
        layernames = re.findall("\w+HI8\w+{}\.\w+".format(target), getcaps)
        layers = []
        for layer in layernames:
            layers.append([settings.PERTH_TIMEZONE.localize(datetime.datetime.strptime(re.findall("\w+_(\d+)_\w+", layer)[0], "%Y%m%d%H%M")), layer])
        layers = sorted(layers,key=lambda layer:layer[0])
        for layer in layers:
            layer[0] = (layer[0]).strftime("%a %b %d %Y %H:%M:%S AWST")
        result = {
            "servers": [baseUrl + FIREWATCH_SERVICE],
            "layers": layers,
            "updatetime":layers[len(layers) - 1][0]
        }
        uwsgi.cache_set(key, json.dumps(result), 60*10)  # cache for 10 mins

    if len(result["layers"]) == 0:
        return bottle.HTTPResponse(status=404)
    elif last_updatetime and last_updatetime == result["updatetime"]:
        bottle.response.status = 290
        return "{}"
    else:
        return result

basetime_url = os.environ.get("BOM_BASETIME_URL") or "https://kmi.dbca.wa.gov.au/geoserver/bom/wms?service=WMS&version=1.1.0&request=GetMap&styles=&bbox=70.0,-55.0, 195.0, 20.0&width=768&height=460&srs=EPSG:4283&format=image%2Fgif&layers={}"
basetime_re = re.compile("(\d{4})-(\d{2})-(\d{2})\s*(\d{2})\D*(\d{2})\s*(UTC)")


def getTimelineFromWmsLayer(current_timeline, layerIdFunc):
    basetimeLayer = bottle.request.query.get("basetimelayer")
    timelineSize = bottle.request.query.get("timelinesize")
    layerTimespan = bottle.request.query.get("layertimespan")  # in seconds
    if not basetimeLayer or not timelineSize or not layerTimespan:
        return None
    timelineSize = int(timelineSize)
    layerTimespan = int(layerTimespan)
    # import ipdb;ipdb.set_trace()
    localfile = None
    try:
        # import ipdb;ipdb.set_trace()
        localfile = tempfile.NamedTemporaryFile(mode='w+b', delete=False, prefix=basetimeLayer.replace(":", "_"), suffix=".gif").name
        subprocess.check_call(["curl", "-G", "--cookie", settings.get_session_cookie(template="{0}={1}"), basetime_url.format(basetimeLayer), "--output", localfile])
        md5 = settings.get_file_md5(localfile)
        if current_timeline and current_timeline["md5"] == md5:
            return current_timeline
        else:
            img = Image.open(localfile)
            img.load()
            basetimestr = pytesseract.image_to_string(img, lang="bom")
            m = basetime_re.search(basetimestr, re.I)
            if not m:
                raise bottle.HTTPError(status=500, body="Can't extract the base time from base time layer.")
            basetime = datetime.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)), 0, 0, tzinfo=pytz.timezone(m.group(6)))
            now = datetime.datetime.now(pytz.timezone('UTC'))
            if basetime > now:
                raise bottle.HTTPError(status=500, body="Extract the wrong base time from base time layer.")
            if (now - basetime).seconds > 86400:
                raise bottle.HTTPError(status=500, body="Extract the wrong base time from base time layer.")
            if basetime.year != int(m.group(1)) or basetime.month != int(m.group(2)) or basetime.day != int(m.group(3)) or basetime.hour != int(m.group(4)) or basetime.minute != int(m.group(5)):
                raise bottle.HTTPError(status=500, body="Extract the wrong base time from base time layer.")
            basetime = basetime.astimezone(pytz.timezone("Australia/Perth"))
            layers = []
            layertime = None
            layerId = None
            for i in xrange(0, timelineSize):
                layertime = basetime + datetime.timedelta(seconds=layerTimespan * i)
                layerId = layerIdFunc(i, layerTimespan)
                layers.append([layertime.strftime("%a %b %d %Y %H:%M:%S AWST"), layerId, None])
            return {"refreshtime": datetime.datetime.now().strftime("%a %b %d %Y %H:%M:%S"), "layers": layers, "md5": md5, "updatetime": basetime.strftime("%a %b %d %Y %H:%M:%S AWST")}
    except:
        traceback.print_exc()
        if localfile:
            #keep the file in tmp folder if failed
            print("Can't extract base time from file '{}'".format(localfile))
            localfile = None
        raise
    finally:
        if localfile:
            os.remove(localfile)


def bomLayerIdFunc(layeridpattern):
    def _func(i, timespan):
        if timespan >= 86400:
            # unit is day
            return layeridpattern.format(i * int(timespan / 86400))
        else:
            # unit is hour
            return layeridpattern.format(i * int(timespan / 3600))
    return _func

start_date = datetime.datetime(1970, 1, 1, 0, 0, tzinfo=pytz.timezone("UTC")).astimezone(pytz.timezone("Australia/Perth"))


@bottle.route("/bom/<target>")
def bom(target):
    last_updatetime = bottle.request.query.get("updatetime")
    layeridpattern = bottle.request.query.get("layeridpattern")
    if layeridpattern:
        layeridpattern = "bom:{}".format(layeridpattern)
    else:
        layeridpattern = "bom:{}{{:0>3}}".format(target)
    current_timeline = None
    try:
        current_timeline = json.loads(uwsgi.cache_get(target))
    except:
        current_timeline = None

    bottle.response.set_header("Content-Type", "application/json")
    bottle.response.status = 200
    if current_timeline and datetime.datetime.now() - datetime.datetime.strptime(current_timeline["refreshtime"], "%a %b %d %Y %H:%M:%S") < datetime.timedelta(minutes=5):
        # data is refreshed within 5 minutes, use the result directly
        if current_timeline["updatetime"] == last_updatetime:
            # return 304 cause "No element found" error, so return a customized code to represent the same meaning as 304
            bottle.response.status = 290
            return "{}"
        else:
            return {"layers": current_timeline["layers"], "updatetime": current_timeline["updatetime"]}

    timeline = getTimelineFromWmsLayer(current_timeline, bomLayerIdFunc(layeridpattern))

    if not timeline:
        raise "Missing some of http parameters 'basetimelayer', 'timelinesize', 'layertimespan'."

    if not current_timeline or id(timeline) != id(current_timeline):
        uwsgi.cache_set(target, json.dumps(timeline), 0)

    if timeline["updatetime"] == last_updatetime:
        bottle.response.status = 290
        return "{}"
    else:
        return {"layers": timeline["layers"], "updatetime": timeline["updatetime"]}


application = bottle.default_app()
