
var browser_config = { 
    non_match_policy : "confirm",
    non_match_timeout: 43200,
    non_match_message:function(refuse,uaName,uaVersion,browserRequirements) {
       var requirementsMessage = "";
        for (var browser in browserRequirements) {
            requirement = browserRequirements[browser]
            if (requirement.message && requirement.message.length > 0) {
                requirementsMessage = requirementsMessage + "\r\n\t" + browser + "(" + requirement.message + ")";
            } else {
                requirementsMessage = requirementsMessage + "\r\n\t" + browser ;
            }
        }
        if (refuse) {
            return "Your browser is not supported for use with the spatial support system please use/install one of the following:" + requirementsMessage;
        } else {
            return "Your browser is not supported for use with the spatial support system please use/install one of the following:" + requirementsMessage + ".\r\n\r\nDo you want to continue?";
        }
    },

    browser_match_policy: "confirm",
    browser_match_timeout:43200,
    browser_match_message:function(refuse,uaName,uaVersion,uaRequirement,browserRequirements) {
        return browser_config["non_match_message"](refuse,uaName,uaVersion,browserRequirements);
    },

    full_match_timeout:604800,

    requirements:{
        firefox:">=48",
        chrome:">=50",
        chromium:">=50",
        safari:">=9.1",
        "mobile safari":">=5.0.2"
    }
}

