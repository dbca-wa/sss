let gokartProfile=  {
    "name": $app,
    "version":$version,
    "distributionType":$distributionType,
    "description":$description,
    "repositoryBranch":$repository_branch,
    "lastCommit":$commit,
    "commitDate":$commit_date,
    "commitMessage":$commit_message,
    "commitAuthor":$commit_author,
    "build":{
        "datetime":$build_datetime,
        "date":$build_date,
        "time":$build_time,
        "platform":$build_platform,
        "host":$build_host,
        "vendorMD5":$vendor_md5
    }
}
export default gokartProfile
