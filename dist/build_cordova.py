#!/usr/bin/env python
# Takes one argument, the name of the app to build.
# Needs dev server running on port 8080 to pull rendered index file from
import subprocess
import sys
import os
import dotenv
import json
import re
import shutil

#import ipdb;ipdb.set_trace()
base_dir = os.path.dirname(__file__)
dotenv.load_dotenv(os.path.join(base_dir,"build_cordova.env"))

patch_file = "js/patch.js"
patch_file_abs = os.path.join(base_dir,"www",patch_file)

gokart_url = os.environ.get("GOKART_URL","") or "http://127.0.0.1:8080/"
if gokart_url[-1:] != "/":
    gokart_url = "{}/".format(gokart_url)

keystore,keystore_password,key_alias,key_password = [os.environ.get(f,"").strip() or None for f in ["KEYSTORE","KEYSTORE_PASSWORD","KEY_ALIAS","KEY_PASSWORD"]]
platforms = [p.strip().lower() for p in (os.environ.get("PLATFORMS","").strip() or "android,ios").split(",") if p.strip()]

cordova_gokart_file = os.path.join(base_dir,"www/gokart.html")
cordova_dist_dir = os.path.join(base_dir,"www/dist")
build_sh = os.path.join(base_dir,".build_cordova.sh")

platforms_file = os.path.join(base_dir,"platforms","platforms.json")
config_file = os.path.join(base_dir,"config.xml")
engine_re = re.compile("<engine[ \t]+name=[\"\'](?P<platform>[a-zA-Z0-9]+)[\"\'][ \t]+spec=[\"\'](?P<spec>[^\"\']+)[\"\'][ \t]*/>")

env_re = re.compile("<script[ \t]+src=[\"\']/?dist/static/js/(?P<env_type>[a-zA-Z0-9]+)\.env\.js[\"\'][ \t]*((/>)|(>[ \t]*</script>))",re.I)


cordova_cmd = "run"
app = "sss"
def setUp():
    #retrieve the gokart html from local server;
    print "Begin to load gokart.html form web server"
    returncode = subprocess.call(['wget', 'localhost:8080/{}'.format(app), '-O', cordova_gokart_file])
    if returncode != 0:
        raise "Fail to load gokart.html from web server"
    print "Succeed to load gokart.html from web server"

    #get  env type of gokart service
    with open(cordova_gokart_file,'rb') as f:
        file_content = f.read()
    
    #get  env type of gokart service
    env_type = None
    for m in env_re.finditer(file_content):
        env_type = m.group("env_type")

    if not env_type:
        raise "Can't get the env type from gokart.html"
    code_base = "release" if env_type == "prod" else "dev"
    build_type = "release" if env_type == "prod" else "debug"

    print "env type = {}, code base = {}, build type = {}".format(env_type,code_base,build_type)

    cordova_js = """
        <script type="text/javascript" src="cordova.js"></script>
    </body>
    """
    file_content = file_content.replace("</body>",cordova_js)
    print "Add cordova javascript files"

    #Add javascript patch for cordova app
    if os.path.exists(patch_file_abs):
        patch_js = """
          <script type="text/javascript" src="{}"></script>
        </body>
        """.format(patch_file)
        file_content = file_content.replace("</body>",patch_js)
        print "Add the patch file '{}'".format(patch_file_abs)
    
    
    with open(cordova_gokart_file,'wb') as f:
        f.write(file_content)

    print "Begin to remove outdated gokart static resource from cordova project."
    source_dist_dir = os.path.join(base_dir,code_base)
    #copy related javascript files, staic files and 
    returncode = subprocess.call(["rm","-rf" ,cordova_dist_dir])
    if returncode != 0:
        raise "Fail to remove outdated gokart static resource from cordova project."
    print "Succeed to remove outdated gokart static resource from cordova project."

    print "Begin to copy gokart static resource into cordova project."
    returncode = subprocess.call(["rsync","-vpogtIrk","--progress","{}/".format(source_dist_dir), "{}/".format(cordova_dist_dir),"--exclude","node_modules".format(source_dist_dir)])
    if returncode != 0:
        raise "Fail to copy gokart static resource into cordova project."

    shutil.copyfile(os.path.join(source_dist_dir,"static","js","{}.env.js".format(env_type)),os.path.join(cordova_dist_dir,"env.js"))
    print "Succeed to copy gokart static resource into cordova project."

    #populate build command file
    #load all installed platforms
    if os.path.exists(platforms_file):
        with open(platforms_file,'rb') as f:
            installed_platforms = json.load(f)
    else:
        installed_platforms = {}

    #load all saved platforms
    config_file = os.path.join(base_dir,"config.xml")
    if not os.path.exists(config_file):
        raise Exception("config file({}) does not exist.".format(config_file))
    engines = {}
    with open(config_file,'rb') as f:
        for m in engine_re.finditer(f.read()):
            if m.group("platform"):
                engines[m.group("platform")] = m.group("spec")

    with open(build_sh,"wb") as f:
        #add and save platform if required
        platform_save_cmd = None
        for platform in platforms:
            if platform in engines and platform in installed_platforms:
                #platform installed
                continue
            elif platform in engines:
                #platform not installed, but already in config.xml
                cmd = ['cordova','platform','add',platform]
            elif platform in installed_platforms:
                #platform already installed ,but not in config.xml
                platform_save_cmd = ['cordova','platform','save']
                continue
            else:
                #platform not installed and not in config.xml
                cmd = ['cordova','platform','add',platform,"--save"]

            f.write(" ".join(cmd))
            f.write("\n")


        if platform_save_cmd:
            f.write(" ".join(platform_save_cmd))
            f.write("\n")

        #build
        for platform in platforms:
            cmd = ['cordova',cordova_cmd,platform]
            if build_type == "release":
                cmd.append("--release")
            else:
                cmd.append("--debug")
            if keystore and key_alias:
                cmd += ["--","--keystore",keystore,"--alias",key_alias]
                if keystore_password:
                    cmd += ["--storePassword",keystore_password]
                if key_password:
                    cmd += ["--password",key_password]
            cmd.append("--stacktrace")
            f.write(" ".join(cmd))
            f.write("\n")
    
    subprocess.call(["chmod","733",build_sh])

def tearDown():
    if os.path.exists(build_sh):
        os.remove(build_sh)

if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[3] not in ["setUp",'tearDown'] or sys.argv[1] not in ["run","build"]:
        raise Exception("python build.py ((run)|(build)) (app) ((setUp)|(tearDown))")

    cordova_cmd = sys.argv[1]
    app = sys.argv[2]

    if sys.argv[3] == 'setUp':
        setUp()
    else:
        tearDown()
