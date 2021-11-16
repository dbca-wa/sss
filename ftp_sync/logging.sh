#!/bin/bash

#get and prepare the log file first.
init_log_file(){
    local log_file=${options["log-file"]}
    local log_file_name=${log_file%%.*}
    local log_file_ext=""
    if [[ "${log_file_name}" != ${log_file} ]]; then
        log_file_ext=${log_file#${log_file_name}.}
    fi
    local log_file_pattern=""
    if [[ "${log_file_ext}" == "" ]]; then
        options["_log-file"]="${log_file_name}_`date +%F`"
        log_file_pattern="${log_file_name}_*"
    else
        options["_log-file"]="${log_file_name}_`date +%F`.${log_file_ext}"
        log_file_pattern="${log_file_name}_*.${log_file_ext}"
    fi
    if [[ -a "${log_file}" ]] && [[ ! -f "${log_file}" ]]; then
        #log_file exists, but not a file
        echo "${log_file} is not a regular file."
        exit 1
    fi
    if [[ ! -f "${log_file}" ]]; then
        #create dir for log file if required
        local log_dir=`get_parent_path "${options["_log-file"]}"`
        return_code=$?; if [[ $return_code -ne 0 ]]; then  echo "$parent_dir"; exit $return_code; fi
        create_dir "${log_dir}"
        return_code=$?; if [[ $return_code -ne 0 ]]; then  exit $return_code; fi
        #create log file
        touch "${options["_log-file"]}"
        return_code=$?; if [[ $return_code -ne 0 ]]; then  exit $return_code; fi
        #remove outdated files
        local file_index=0
        for log_file in `ls -r ${log_file_pattern}`; do
            file_index=$((${file_index}+1))
            if [[ ${file_index} -gt ${options["log-files"]} ]]; then
                rm "${log_file}"
                return_code=$?; if [[ $return_code -ne 0 ]]; then  warning "Failed to remove the log file '${log_file}'"; fi
            fi
        done
    fi
}

debug(){
    if [[ "${options["_log-level"]}" -ge "${log_levels["debug"]}" ]]; then
        logging "debug" "$1"
    fi
}
info(){
    if [[ "${options["_log-level"]}" -ge "${log_levels["info"]}" ]]; then
        logging "info" "$1"
    fi
}
warning(){
    if [[ "${options["_log-level"]}" -ge "${log_levels["warning"]}" ]]; then
        logging "warning" "$1"
    fi
}
error(){
    logging "error" "$1"
}

logging(){
    if [[ "$2" == "" ]]; then echo ""; else  echo "`date` : $2"; fi
    if [[ "${options["log-file"]}" != "" ]]; then
        if [[ "$2" == "" ]]; then echo "" >> ${options["_log-file"]}; else  echo "`date` $1 : $2" >> ${options["_log-file"]}; fi
    fi
}

if [[ "${options["log-file"]}" != "" ]] && [[ "${options["_log-file"]}" == "" ]]; then
    init_log_file 
    return_code=$?; if [[ $return_code -ne 0 ]]; then  echo exit $return_code; fi
fi

