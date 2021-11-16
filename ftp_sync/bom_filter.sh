#!/bin/bash

list_file=$1

tmp_file="/tmp/bom_filter_$(($(date +'%s * 1000 + %-N / 1000000')))"
file_name=""
file_ext=""
file_path=""
file=""
previous_file_name=""
previous_file_ext=""
index=-1

if [[ -a "$tmp_file" ]]; then
    error "${tmp_file} already exist"
    exit 1
fi
cp "${list_file}" "${tmp_file}"

while read -r f; do
    file_path=${f%/*}
    if [[ "${file_path}" == "${f}" ]]; then
        #${f} doesn't include any path
        file_path=""
        file="${f}"
    else
        file=${f#${file_path}/}
        file_path="${file_path}/"
    fi
    file_name=${file%%.*}
    file_ext=${file#${file_name}.}

#    if [[ "${file_ext}" == "csv" ]]; then
#        #csv file,
#        continue
#    fi
    if [[ "$previous_file_name" != "${file_path}${file_name}" ]]; then
        #new file, add to the file list
        index=$(($index+1))
        files[$index]="$f"
        previous_file_name="${file_path}${file_name}"
        previous_file_ext=$file_ext
    elif [[ $file_ext != "grb" ]]; then
        #current file is not a grb file, a prefered format
        files[$index]="$f"
        previous_file_ext=$file_ext
    fi
done < ${tmp_file}

files_length=$(($index + 1))
#write the bom files into file .bom_files.txt
rm -f "${list_file}"
while read -r f; do
    index=0
    found=0
    while [[ $found -eq 0 ]] && [[ $index -lt $files_length ]]; do
        if [[ "${files[$index]}" == "$f" ]]; then
            found=1
        fi
        index=$(($index+1))
    done
    if [[ $found -eq 0 ]]; then
        #no need to synchronize
        echo "#$f" >> "${list_file}"
    else
        #need to synchronize
        echo "$f" >> "${list_file}"
    fi
done < ${tmp_file}
#remove temp file
rm -f "${tmp_file}"

