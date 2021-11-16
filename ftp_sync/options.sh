#!/bin/bash
usage="Synchronize the files from ftp server to local folder

This program will create two invisible folder in root folder
1. .sync folder for synchronizing files from ftp server
2. .data folder to hold another copy of the files which guarantee the file is still available during syncing.

The file will be available by creating a soft link which point to a folder under .data at most time, and will temporary point to a folder under .sync folder during synchroning file from .sync to .data.

This program will use four steps to perform synchronization.
1. Synchronize the data from ftp server into a .sync folder in local dir 
2. Recreate the soft link to point to .sync folder as the workspace
3. Synchronize the data from .cache folder in local dir to local dir
4. Recreate the soft link to point to .data as the workspace

So this program will consume double space in local in order to guarantee a valid copy is always available; by using soft link,minmise the unavailable time during synchronization 

Usage ftp_sync [OPTIONS]
FTP Server options:
    -s,--server=server  ftp server
    -u,--user=user      ftp user account
    -p,--password       ftp user password
    --secure            enable sftp
    -d,--remote-dir=dir relative folder in user's home folder in ftp server to synchronize from; can't start with '/'

Local options:
    -r,--root-dir=dir   folder in local system to contain the files synchronized from ftp server; it is a absolute path or a file path to the file 'ftp_sync.sh'
    -l,--local-dir=dir  relative folder in root dir to syncrhoize the files from remote dir to; default is same as remote-dir

Syncrhonize options:
    --parallel[=N]      download N files in parallel
    --only-existing     only synchronize the file already exists in the client side
    --not-sync          don't perfrom synchronization.
    --sync-list-filter  a script to filter the file list returned from remote dir, only valid when --only-existing is enabled.
                         it is a absolute file or a file relative to the file 'ftp_sync.sh'
                        script parameters
                        1: a file contained all the files returned from ftp server, this script should remove the unwanted files, or comment them with '#'

other options:
    -e,--env-file       the environment file used to setup the options; it is a absolute file or a file relative to the file 'ftp_sync.sh'
    --log-level         log level. error,warning,info,debug; default is warning
    --log-file          log file; it is a absolute file or a file relative to the file 'ftp_sync.sh'
    --log-files         how many files need to be kept in file system, one file per day, default 14 files
"

#a special value represents a option has no default value and also not specified in the command line and environment file if have
null_value='!@nil@!'

#supported log levels and its value
declare -A log_levels=()
log_levels["error"]=1
log_levels["warning"]=2
log_levels["info"]=3
log_levels["debug"]=4


#all the options can be configured in command line or environment file 
declare -a all_options=("server" "user" "password" "secure" "remote-dir" "root-dir" "local-dir" "only-existing" "log-level" "log-file" "log-files" "help" "sync-list-filter" "not-sync" "parallel")

#all bool type options
#bool type option has two value, default is 0
#  0: false
#  1: true
declare -A bool_options=()
bool_options["all"]=1
bool_options["secure"]=1
bool_options["help"]=1
bool_options["only-existing"]=1
bool_options["not-sync"]=1

#initialize the options array
#bool option is set to 0
#other option is set to null_value
declare -A options=()
for op in ${all_options[@]}; do
   env_var="$( echo -e "$op" | tr '-' '_' )"
   env_var="ftpsync_${env_var}"
   #echo "options=${op}  env_var_name=${env_var}  env_var_value=${!env_var}"
   if [[ -v "${env_var}" ]]; then
       if [[ ${bool_options[$op]} -eq 1 ]]; then
           env_value=${!env_var}
           #convert to lower case
           env_value=${env_value,,}
           if [[ "${env_value}" =~ ^(true|yes|on|1|t|y)$ ]]; then
               options[$op]=1
           else
               options[$op]=0
           fi

       else
           options[$op]="${!env_var}"
       fi
   elif [[ "$op" == "remote-dir"  ]]; then
        options["remote-dir"]=""
   elif [[ "$op" == "sync-list-filter"  ]]; then
        options["sync-list-filter"]=""
   elif [[ "$op" == "log-level"  ]]; then
        options["log-level"]="warning"
   elif [[ "$op" == "parallel"  ]]; then
        options["parallel"]="5"
   elif [[ "$op" == "log-file"  ]]; then
        options["log-file"]="/var/log/ftp_sync.log"
   elif [[ "$op" == "log-files"  ]]; then
        options["log-files"]="14"
   elif [[ ${bool_options[$op]} -eq 1 ]]; then
       options[$op]=0
   else
       options[$op]=$null_value
   fi
done

#set the default option value
#if [[ -f "./env.sh" ]]; then
#    options["env-file"]="./env.sh"
#else
#    options["env-file"]=$null_value
#fi

#decalre IEEE option
declare -A options_ieee=()
options_ieee["server"]="-s"
options_ieee["user"]="-u"
options_ieee["password"]="-p"
options_ieee["remote-dir"]="-d"

options_ieee["root-dir"]="-r"
options_ieee["local-dir"]="-l"

options_ieee["env-file"]="-e"

options_ieee["help"]="-h"

#decalre gnu option
declare -A options_gnu=()
options_gnu["server"]="--server"
options_gnu["user"]="--user"
options_gnu["password"]="--password"
options_gnu["secure"]="--secure"
options_gnu["remote-dir"]="--remote-dir"

options_gnu["root-dir"]="--root-dir"
options_gnu["local-dir"]="--local-dir"

options_gnu["only-existing"]="--only-existing"
options_gnu["sync-list-filter"]="--sync-list-filter"
options_gnu["not-sync"]="--not-sync"
options_gnu["parallel"]="--parallel"

options_gnu["log-level"]="--log-level"
options_gnu["log-file"]="--log-file"
options_gnu["log-files"]="--log-files"
options_gnu["env-file"]="--env-file"

options_gnu["help"]="--help"

#declare the option whose value can be the same value as other option if not configured
declare -A options_ref=()
options_ref["local-dir"]="remote-dir"

#declare the option which contain credential data, should not print to stdout or stderr
declare -A credential_options=()
credential_options["password"]=1

#try to parse env-file option first
index=0
next_index=0
while [[ $index -lt $# ]]; do
    index=$(($index + 1))
    op="env-file"
    if [[ ${options_ieee[$op]} == "${!index}" ]]; then
        #check whether the next parameter is another option
        found=0
        next_index=$(($index + 1))
        for op1 in ${all_options[@]}; do
            if [[ ${options_ieee[$op1]} == "${!next_index}" ]]; then
                found=1
                break
            elif [[ "${bool_options[$op1]}" -eq 1 ]] && [[ ${options_gnu[$op1]} == "${!next_index}" ]]; then
                found=1
                break
            elif [[ ! "${bool_options[$op1]}" -eq 1 ]] && [[ ${!next_index} =~ ^${options_gnu[$op1]}=.* ]]; then
                found=1
                break
            fi
        done
        if [[ $found -eq 0 ]]; then
            #not a option
            options[$op]=${!next_index}
            index=$next_index
        fi
        break
    elif [[ ${!index} =~ ^${options_gnu[$op]}=.* ]]; then
        options[$op]=${!index#${options_gnu[$op]}=*}
        break
    fi
done

#if env-file is configured, execute it first
if [[ ${options["env-file"]} != $null_value ]] && [[ ${options["env-file"]} != "" ]]; then
    #env file is specified, execute it
    options["env-file"]=`get_absolute_path "${options["env-file"]}" "${script_dir}"`
    source ${options["env-file"]}
fi

#parse the all other options from command 
index=0
next_index=0
while [[ $index -lt $# ]]; do
    index=$(($index + 1))
    for op in ${all_options[@]}; do
        if [[ "$op" == "env-file" ]]; then
            continue
        fi
        if [[ ${options_ieee[$op]} == "${!index}" ]]; then
            if [[ "${bool_options[$op]}" -eq 1 ]]; then
                options[$op]=1
            else
                #check whether the next parameter is another option
                found=0
                next_index=$(($index + 1))
                for op1 in ${all_options[@]}; do
                    if [[ ${options_ieee[$op1]} == "${!next_index}" ]] && [[ ${options_ieee[$op1]} != "" ]]; then
                        found=1
                        break
                    elif [[ "${bool_options[$op1]}" -eq 1 ]] && [[ ${options_gnu[$op1]} == "${!next_index}" ]] && [[ ${options_gnu[$op1]} != "" ]]; then
                        found=1
                        break
                    elif [[ ! "${bool_options[$op1]}" -eq 1 ]] && [[ ${!next_index} =~ ^${options_gnu[$op1]}=.* ]] && [[ ${options_gnu[$op1]} != "" ]]; then
                        found=1
                        break
                    fi
                done
                if [[ $found -eq 0 ]]; then
                    #not a option
                    options[$op]=${!next_index}
                    index=$next_index
                else
                    options[$op]=""
                fi
            fi
            break
        elif [[ "${bool_options[$op]}" -eq 1 ]] && [[ ${options_gnu[$op]} == "${!index}" ]]; then
            options[$op]=1
            break
        elif [[ ! "${bool_options[$op]}" -eq 1 ]] && [[ ${!index} =~ ^${options_gnu[$op]}=.* ]]; then
            options[$op]=${!index#${options_gnu[$op]}=*}
            break
        fi
    done
done

#process the log-level 
options["_log-level"]=${log_levels[${options["log-level"]}]}
if [[ "${options["_log-level"]}" == "" ]]; then
    options["_log-level"]=${log_levels["warning"]}
    options["log-level"]="warning"
fi

#if in help mode, display the usage
if [[ ${options["help"]} -eq 1 ]]; then
    echo "$usage"
    exit 0
fi

#assign the options to the value of other option declared in array options_ref, if not specified in command
for op in ${all_options[@]}; do 
    if [[ "${options[$op]}" == "$null_value"  ]] && [[ "${options_ref[$op]}" != "" ]]; then
        options[$op]=${options[${options_ref[$op]}]}
    fi
done

#if remote-dir is "./", change it to ""
if [[  "${options["remote-dir"]}" == "./" ]]; then
    options["remote-dir"]=""
fi

#if log_files less then 1, reset to 1
if [[ ${options["log-files"]} -lt 1 ]]; then
    options["log-files"]=1
fi

if [[ "${options["log-file"]}" != "" ]]; then
    options["log-file"]=`get_absolute_path "${options["log-file"]}" "${script_dir}"`
fi
#initialize logging file
source ${script_dir}/logging.sh

#check whether all options have value, the value can be default value, specified in command or come from other option
missing_option=0
for op in ${all_options[@]}; do 
    if [[ "${options[$op]}" == "$null_value" ]]; then
        missing_option=1
        if [[ "${options_ieee[$op]}" != "" ]] && [[ "${options_gnu[$op]}" != "" ]]; then
            error "Missing parameter '$op', using options '${options_ieee[$op]}' or '${options_gnu[$op]}'"
        elif [[ "${options_ieee[$op]}" != "" ]] ; then
            error "Missing parameter '$op', using option '${options_ieee[$op]}'"
        else
            error "Missing parameter '$op', using option '${options_gnu[$op]}'"
        fi
    fi
done

if [[ $missing_option -eq 1 ]]; then
    error ""
    error "$usage"

    for op in ${all_options[@]}; do
        if [[ "${options[$op]}" == "$null_value" ]]; then
            error "$op Not Declared"
        elif [[ ! ${credential_options[$op]} -eq 1 ]]; then
            if [[ ${bool_options[$op]} -eq 1  ]]; then
                if [[ ${options[$op]} -eq 0  ]]; then
                    error "$op = false"
                else
                    error "$op = true"
                fi
            else
                error "$op = ${options[$op]}"
            fi
        else
            error "$op = ********"
        fi
    done

    exit 1
fi

if [[ ${options["parallel"]} -lt 1 ]]; then
    ${options["parallel"]} = 1
fi

#get ftp url
if [[ ${options["secure"]} -eq 1 ]]; then
    options["ftp-url"]="ftps://${options["server"]}"
else
    options["ftp-url"]="ftp://${options["server"]}"
fi

#initialize options or create other options used by program
options["root-dir"]=`get_absolute_path "${options["root-dir"]}" "${script_dir}"`
#if [[ ${options["root-dir"]} =~ ^(/)|(/etc/.*)|(/root/.*)|(/bin/.*)|(/sbin/.*)|(/lib/.*)$ ]]; then
if [[ ${options["root-dir"]} =~ ^/$|^/etc(/.*)?$|^/root(/.*)?$|^/bin(/.*)?$|^/sbin(/.*)?$|^/lib(/.*)?$ ]]; then
    error "root dir can't be '/', also can't be in system folder '/etc','/root','/bin','/sbin','lib'"
    exit 1
fi
create_dir ${options["root-dir"]}
return_code=$?; if [[ ! $return_code -eq 0 ]]; then  exit $return_code; fi

if [[ "${options["local-dir"]}" =~ ^/.* ]]; then
    #is a absolute path, but its root path is options["root-dir"], change it to relative path 
    options["local-dir"]=`echo ${options["local-dir"]} | sed -e 's/^\/\+//'`
fi
#local sync dir
options["sync-dir"]=`get_absolute_path "${options["local-dir"]}" "${options["root-dir"]}/.sync"`

create_dir ${options["sync-dir"]}
return_code=$?; if [[ ! $return_code -eq 0 ]]; then  exit $return_code; fi

#local data dir
options["data-dir"]=`get_absolute_path "${options["local-dir"]}" "${options["root-dir"]}/.data"`

create_dir ${options["data-dir"]}
return_code=$?; if [[ ! $return_code -eq 0 ]]; then  exit $return_code; fi

#local-dir, the accessing point, this is a soft link
options["local-dir"]=`get_absolute_path "${options["local-dir"]}" "${options["root-dir"]}"`
if [[ "${options["local-dir"]}" == "${options["root-dir"]}" ]]; then
    error "local-dir can't be the same dir as root-dir"
    exit 1
fi

parent_dir=`get_parent_path "${options["local-dir"]}"`
return_code=$?; if [[ ! $return_code -eq 0 ]]; then  error "$parent_dir"; exit $return_code; fi

create_dir "$parent_dir"
return_code=$?; if [[ ! $return_code -eq 0 ]]; then  exit $return_code; fi

if [[ -a "${options["local-dir"]}" ]] && [[ ! -h "${options["local-dir"]}" ]]; then
    error "${options["local-dir"]} is not a symbolic link."
    exit 1
fi

if [[ ${options["only-existing"]} -eq 1 ]]; then
    #synchronize the file in only-existing mode
    options["sync-list-file"]="${options["local-dir"]}.synclist"
    if [[ -a "${options["sync-list-file"]}" ]] && [[ ! -f "${options["sync-list-file"]}" ]]; then
        error "${options["sync-list-file"]} is not a file."
        exit 1
    fi
    if [[ "${options["sync-list-filter"]}" != "" ]]; then
        options["sync-list-filter"]=`get_absolute_path "${options["sync-list-filter"]}" "${script_dir}"`
        if [[ ! -a "${options["sync-list-filter"]}" ]]; then
            error "Sync file list filter script '${options["sync-list-filter"]}' does not exist."
            exit 1
        elif [[ -d "${options["sync-list-filter"]}" ]]; then
            error "Sync file list filter script '${options["sync-list-filter"]}' is a directory"
            exit 1
        fi
    fi
fi
#print all options if debug is enabled
if [[ "${options["_log-level"]}" -ge "${log_levels["debug"]}" ]]; then
    for op in "${!options[@]}"; do 
        if [[ "$op" =~ ^_.* ]]; then
            continue
        elif [[ ! ${credential_options[$op]} -eq 1 ]]; then
            if [[ ${bool_options[$op]} -eq 1  ]]; then
                if [[ ${options[$op]} -eq 0  ]]; then
                    debug "$op = false"
                else
                    debug "$op = true"
                fi
            else
                debug "$op = ${options[$op]}"
           fi
        else
            debug "$op = ******"
        fi
    done
fi

