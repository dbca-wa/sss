import os
import sys
import string
import datetime
import pytz
import socket
import json
import platform
import subprocess
import hashlib
import base64

base_path = os.path.abspath(os.path.dirname(__file__))
base_dist_path = os.path.join(base_path,"dist")

def generate_app_profile():
    profile_template_file = os.path.join(base_path,"src/apps/profile-template.js")
    package_json_file = os.path.join(base_path,"package.json")

    with open(package_json_file) as f:
        package = json.loads(f.read())

    with open(profile_template_file) as f:
        profile_template = string.Template(f.read())

    app_name = package["config"]["app"]
    profile_name = os.path.join(base_path,"src/apps","{}-profile.js".format(app_name))

    now = datetime.datetime.now(pytz.timezone('Australia/Perth'))

    package.update(package['config'])
    package["distributionType"] = sys.argv[1] if len(sys.argv) >= 2 else "unknown"

    vendor_file = os.path.join(base_dist_path,package["distributionType"],"vendor.js")

    if not os.path.exists(vendor_file):
        raise Exception("Vendor file({}) is missing".format(vendor_file))

    m = hashlib.md5()
    with open(vendor_file,"rb") as f:
        m.update(f.read())

    vendor_md5 = base64.urlsafe_b64encode(m.digest()).rstrip("=")

    package.update({
        "build_datetime":now.strftime("%Y-%m-%d %H:%M:%S %Z(%z)"),
        "build_date":now.strftime("%Y-%m-%d %Z(%z)"),
        "build_time":now.strftime("%H-%M-%S %Z(%z)"),
        "build_platform":platform.system(),
        "build_host":socket.gethostname(),
        "vendor_md5":vendor_md5
    })


    #get the latest git commit.
    latest_commit = subprocess.check_output(["git","log","-n","1"]).splitlines()
    commit_info = {}
    for line in latest_commit:
        for k,v in [(b"commit","commit"),(b"Author:","commit_author"),(b"Merge:",""),(b"Date:","commit_date"),(b"","commit_message")]:
            if line[:len(k)] == k:
                if v and line[len(k):].strip() :
                    text = remove_non_ascii(line[len(k):])
                    if v in commit_info:
                        #commit_info[v] =  "{}\\n{}".format(commit_info[v],line[len(k):].strip().decode('utf-8'))
                        commit_info[v] =  "{}\\n{}".format(commit_info[v],text.strip().decode('utf-8'))
                    else:
                        #commit_info[v] = line[len(k):].strip().decode('utf-8')
                        commit_info[v] = text.strip().decode('utf-8')
                break
    if 'commit' in commit_info:
        commit_info['commit'] = commit_info['commit'][:7]

    package.update(commit_info)

    #get the branch info
    branch = [b for b in subprocess.check_output(["git", "branch"]).splitlines() if b.strip().startswith(b"*")][0].strip()[1:].strip().decode('utf-8')
    
    #if branch.startswith("(detached from"):
    #    branch = branch[len("(detached from"):len(branch) - 1].strip()

    package["repository_branch"]=branch



    #tranform value to json string
    for k,v in package.items():
        package[k] = json.dumps(v)

    for key, val in package.items():
        print('{}: {}'.format(key, val))

    profile = profile_template.safe_substitute(package)

    print('\nPROFILE:')
    print(profile)

    with open(profile_name,'w') as f:
        f.write(profile)
        
def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

if __name__ == "__main__":
    generate_app_profile()



