import { $, moment } from 'src/vendor.js'


let FeatureTask = function(manager,scope,taskId,description,status,message) {
    this.manager = manager
    this.scope = scope
    this.taskId = taskId
    this.description = description
    this.icon = ""
    this.statusText = ""
    this.message = ""
    this.setStatus(status,message)
}

FeatureTask.FAILED = -1
FeatureTask.FAIL_CONFIRMED = -2
FeatureTask.WAITING = 1
FeatureTask.RUNNING = 2
FeatureTask.SUCCEED = 3
FeatureTask.WARNING = 4
FeatureTask.IGNORED =  5
FeatureTask.MERGED =  6

FeatureTask.prototype._getIcon = function() {
    if (this.status === FeatureTask.FAILED || this.status === FeatureTask.FAIL_CONFIRMED) {
        return "fa-close"
    } else if (this.status === FeatureTask.WAITING) {
        return "fa-pause"
    } else if (this.status === FeatureTask.RUNNING) {
        return "fa-spinner"
    } else if (this.status === FeatureTask.SUCCEED) {
        return "fa-check"
    } else if (this.status === FeatureTask.WARNING) {
        return "fa-warning"
    } else if (this.status === FeatureTask.IGNORED) {
        return "fa-minus"
    } else if (this.status === FeatureTask.MERGED) {
        return "fa-link"
    }  else {
        return "fa-spinner"
    }
}

FeatureTask.prototype._getStatusText = function() {
    if (this.status === FeatureTask.FAILED) {
        return "Failed"
    } else if (this.status === FeatureTask.WAITING) {
        return "Waiting"
    } else if (this.status === FeatureTask.RUNNING) {
        return "Running"
    } else if (this.status === FeatureTask.SUCCEED) {
        return "OK"
    } else if (this.status === FeatureTask.WARNING) {
        return "Warning"
    } else if (this.status === FeatureTask.IGNORED) {
        return "Ignored"
    } else if (this.status === FeatureTask.MERGED) {
        return "Merged"
    } else if (this.status === FeatureTask.FAIL_CONFIRMED) {
        return "Failed"
    }  else {
        return "Running"
    }
}

FeatureTask.prototype.setStatus = function(status,message) {
    this.status = status
    this.message = message || ""
    this.statusText = this._getStatusText()
    this.icon = this._getIcon()
    if (this.manager && this.manager.changeCallback) this.manager.changeCallback()
}

let FeatureTaskManager = function(changeCallback) {
    //call when feature's tasks changed.
    this.changeCallback = changeCallback
}

//return true if init succeed; otherwise return false
FeatureTaskManager.prototype.initTasks = function(feat) {
    if (this.changeCallback) this.changeCallback()
    if (feat.tasks && feat.tasks.length > 0) {
        if (feat.tasks.find(function(t){return t.status === FeatureTask.WAITING || t.status === FeatureTask.RUNNING})) {
            alert("Feature still has running jobs.")
            return false
        }
    }
    feat.tasks = []
    return true
}
FeatureTaskManager.prototype.clearTasks = function(feat) {
    var vm = this
    var tasks = feat.tasks
    if (!tasks || tasks.length === 0) {
        return
    }
    var delay = 1000
    if (this.allTasksSucceed(feat)) {
        delay = 1000
    } else if(this.allTasksNotFailed(feat)) {
        delay = 10000
    } else {
        delay = 60000
    }
    setTimeout(function(){
        if (vm.changeCallback) vm.changeCallback()
        if (tasks) {
            tasks.length = 0
        }
    },delay)
}
FeatureTaskManager.prototype.getTasks = function(feat) {
    return feat.tasks || []
}
FeatureTaskManager.prototype.getTask = function(feat,scope,taskId) {
    return feat.tasks?(feat.tasks.find(function(t) {return t.id === taskId && t.scope === scope})):null
}
//status should be "waiting","running","succeed","failed"
FeatureTaskManager.prototype.addTask = function(feat,scope,taskId,description,status) {
    if (this.changeCallback) this.changeCallback()
    var task = new FeatureTask(this,scope,taskId,description,status)
        
    feat.tasks.push(task)
    return task
}

FeatureTaskManager.prototype.allTasksSucceed = function(feat,scope) {
    return feat.tasks.find(function(t) {return (!scope || t.scope === scope) && [FeatureTask.SUCCEED,FeatureTask.IGNORED,FeatureTask.MERGED].indexOf(t.status) === -1 })?false:true;
}

FeatureTaskManager.prototype.allTasksNotFailed = function(feat,scope) {
    return feat.tasks.find(function(t) {return (!scope || t.scope === scope) && [FeatureTask.SUCCEED,FeatureTask.IGNORED,FeatureTask.MERGED,FeatureTask.WARNING].indexOf(t.status) === -1 })?false:true;
}

FeatureTaskManager.prototype.allTasksFinished = function(feat,scope) {
    return feat.tasks.find(function(t) {return (!scope || t.scope === scope) && [FeatureTask.RUNNING,FeatureTask.WAITING].indexOf(t.status) >= 0 })?false:true;
}

FeatureTaskManager.prototype.errorMessages = function(feat,scope) {
    return feat.tasks.filter(function(t) {return (!scope || t.scope === scope) && [FeatureTask.FAILED,FeatureTask.WARNING].indexOf(t.status) >= 0 && t.message }).map(function(t){return t.message;})
}

let Utils = function() {
}

Utils.prototype.importSpatialFileTypes = "";//".json,.geojson,.gpx,.gpkg"
Utils.prototype.importSpatialFileTypeDesc = "Support GeoJSON(.geojson .json), GPS data(.gpx), GeoPackage(.gpkg), 7zip(.7z), TarFile(.tar.gz,tar.bz,tar.xz),ZipFile(.zip)"

Utils.prototype.SUCCEED = FeatureTask.SUCCEED
Utils.prototype.FAILED = FeatureTask.FAILED
Utils.prototype.WAITING = FeatureTask.WAITING
Utils.prototype.RUNNING = FeatureTask.RUNNING
Utils.prototype.WARNING = FeatureTask.WARNING
Utils.prototype.IGNORED = FeatureTask.IGNORED
Utils.prototype.MERGED = FeatureTask.MERGED
Utils.prototype.FAIL_CONFIRMED = FeatureTask.FAIL_CONFIRMED

Utils.prototype.getFeatureTaskManager = function(changeCallback) {
    return new FeatureTaskManager(changeCallback)
}

Utils.prototype.checkPermission = function(url, method, callback) {
    method = method || "GET"
    var pos = url.indexOf('?')
    if  (pos >= 0) {
        if (pos === url.length - 1) {
            url = url + "checkpermission=true"
        } else {
            url = url + "&checkpermission=true"
        }
    } else {
        url = url + "?checkpermission=true"
    }
    var parameters = null
    if (arguments.length > 3) {
        parameters = []
        for(var index = 3; index < arguments.length; index++) {
            parameters.push(arguments[index])
        }
    }
    var ajaxSetting = {
        xhrFields:{
            withCredentials: true
        },
        method:method,
        success:function(data, status, jqXHR) {
            if (parameters) {
                parameters.splice(0, 0, true)
                callback.apply(null,parameters)
            } else {
                callback(true)
            }
        },
        error:function(jqXHR) {
            if (parameters) {
                if (jqXHR.status === 401) {
                    parameters.splice(0, 0 ,false)
                } else if(jqXHR.status >= 500) {
                    parameters.splice(0, 0 ,false)
                } else {
                    parameters.splice(0, 0, true)
                }
                callback.apply(null,parameters)
            } else {
                if (jqXHR.status === 401) {
                    callback(false)
                } else if(jqXHR.status >= 500) {
                    callback(false)
                } else {
                    callback(true)
                }
            }
        }
        
    }
    if (["POST","PATCH","PUT"].indexOf(method) >= 0) {
        ajaxSetting["contentType"] = "application/json"
        ajaxSetting["data"] = JSON.stringify({})
    }
    $.ajax(url, ajaxSetting)
}
var defaultWinOptions = [
    ["scrollbars","yes"],
    ["locationbar","no"],
    ["menubar","no"],
    ["statusbar","yes"],
    ["toolbar","no"],
    ["personalbar","no"],
    ["centerscreen","yes"],
    ["width",function(){return Math.floor(window.innerWidth * 0.95)}],
    ["height",function(){return Math.floor(window.innerHeight * 0.95)}]
]
Utils.prototype.editResource = function(event,options,url,target,reopen) {
    if (!url) {
        var targetElement = (event.target.nodeName == "A")?event.target:event.target.parentNode;
        url = targetElement.href
        target = targetElement.target
    }
    if (!target) {
        target = "_blank"
    }
    if (env.appType == "cordova") {
        window.open(url,"_system");
    } else {
        options = options || {}
        var winOptions = defaultWinOptions.map(function(option){return option[0] + "=" + (options[option[0]] || ((typeof option[1] === "function")?option[1]():option[1]) )}).join(",")
        if (reopen) {
            var win = window.open("",target,winOptions)
            try{
                if (win.location.href !== "about:blank") {
                    //already opened before, close it first
                    win.close()
                }
            } catch (ex) {
                //already opened before, close it first
                win.close()
            }
            window.open(url,target,winOptions)
        } else {
            var  win = window.open(url,target,winOptions);
            setTimeout(function(){win.focus()},500)
        }
    }
}

Utils.prototype.submitForm = function(formid,options,reopen) {
    var form = $("#" + formid)

    if (env.appType == "cordova") {
        form.submit()
    } else {
        var target = form.attr("target") || "_blank"
        options = options || {}
        var winOptions = defaultWinOptions.map(function(option){return option[0] + "=" + (options[option[0]] || ((typeof option[1] === "function")?option[1]():option[1]) )}).join(",")
        var win = window.open("",target,winOptions);
        if (reopen) {
            try{
                if (win.location.href !== "about:blank") {
                    //already opened before, close it first
                    win.close()
                    win = null
                }
            } catch (ex) {
                //already opened before, close it first
                win.close()
                win = null
            }
            if (win === null) {
                win = window.open("",target,winOptions);
            }
        }
        form.submit()
        if (target === "_blank"  || !reopen) {
            setTimeout(function(){win.focus()},500)
        }
    }
}

Utils.prototype.getWindowTarget = function(target){
    return (env.appType === "cordova")?"_system":target
}

var proxyCache = {}
Utils.prototype.proxy = function(classname,object,attrs){
    if (!object) {return null;}
    if (!(classname in proxyCache)) {
        var properties = []
        var methods = []
        var ProxyClass = null
        for (var key in object) {
            if (key[0] === "_") {
                continue
            } else if (typeof object[key] !== 'function') {
                properties.push(key)
            } else if (object.hasOwnProperty(key)){
                methods.push(key)
            }
        }
        var key = null
        if (properties.length > 0 || methods.length > 0) {
            ProxyClass = function(object) {
                this._object = object
                this._objectPrototype = Object.getPrototypeOf(this._object)
                for(var i = 0;i < properties.length;i++) {
                    key = properties[i]
                    eval("Object.defineProperty(this,\"" + key + "\",{ \
                        get:function(){return this._object[\"" + key + "\"]}, \
                        set:function(value){this._object[\"" + key + "\"] = value}, \
                    })")
                }
            }
        } else {
            ProxyClass  = function(object) {
            }
        }
        //proxy all the method
        ProxyClass.prototype = Object.create(Object.getPrototypeOf(object))
        ProxyClass.prototype.constructor = ProxyClass
        ProxyClass.prototype.getWrappedObject = function() {
            return this._object
        }
        for (var key in Object.getPrototypeOf(object)) {
            if (["constructor"].indexOf(key) < 0 && (!attrs || !(key in attrs))) {
                eval("ProxyClass.prototype[\"" + key + "\"] = function() { \
                    return this._objectPrototype[\"" + key + "\"].apply(this._object,arguments); \
                }")
            }
        }

        for(var i = 0;i < methods.length;i++) {
            key = methods[i]
            eval("ProxyClass.prototype[\"" + key + "\"] = function() { \
                return this._object[\"" + key + "\"]?this._object[\"" + key + "\"].apply(this._object,arguments) : undefined; \
            }")
        }

        for (var key in attrs) {
            eval("ProxyClass.prototype[\"" + key + "\"] = function() { \
                return attrs[\"" + key + "\"].apply(this._object,arguments); \
            }")
        }

        ProxyClass.prototype.constructor = ProxyClass
        proxyCache[classname] = ProxyClass
    }
    return new proxyCache[classname](object)

}
//verify the user input date string.
//event, the dom event trigger this verification
//inputPattern: the array of input patterns 
//pattern: the pattern to normialize the user input 
//if correct, format the date with pattern
//if failed, set focus to the date element
//return true if correct;otherwise return false
Utils.prototype.verifyDate = function(event,inputPattern,pattern) {
    var element = event.target;
    element.value = element.value.trim()
    if (element.value.length > 0) {
        var m = moment(element.value,inputPattern,true)
        if (!m.isValid()) {
            setTimeout(function() {
                element.focus()
            },10);
            return false
        } else {
            element.value = m.format(pattern)
            $(element).trigger('change')
            return true
        }
    } else {
        return true
    }
}

//Return a list of moment object whose time is specified in timesInDay array
//timesInDay: specify the time part in format "HH:mm:ss" ,required
//size: the number of the datetimes , required
//stragegy: the way to get the first datetime, default is 2
//  1: The first datetime is consisted with current date and first time in timesInDay
//  2: The first datetime is consisted with current date and the nearest time before current time in timesInDay 
//  3: The first datetime is consisted with current date and the nearest time after current time in timesInDay 
//startDate: the start datetime of the forecast,if missing, current datetime will be used
Utils.prototype.getDatetimes = function(timesInDay,size,strategy,startDate) {
    startDate = startDate || moment().tz("Australia/Perth");
    var currentDate = startDate.format("YYYY-MM-DD");
    strategy = strategy || 2;

    var result = [];
    var timeIndex = -1;
    if (strategy === 2 || strategy === 3) {
        $.each(timesInDay,function(index,time){
            if (strategy === 2 && startDate < moment.tz(currentDate + " " + time,"Australia/Perth") ) {
                if (index === 0) {
                    timeIndex = timesInDay.length - 1;
                    startDate.date(startDate.date() - 1);
                } else {
                    timeIndex = index - 1;
                }
                return false;
            } else if (strategy === 3 && startDate < moment.tz(currentDate + " " + time,"Australia/Perth") ) {
                furstIndex = index;
                return false;
            }
        })
        if (strategy === 3 && timeIndex === -1) {
            timeIndex = 0;
            startDate.date(startDate.date() + 1);
        }
    } else {
        timeIndex = 0;
    }
    var result = [];
    while (result.length < size) {
        result.push( moment.tz(startDate.format("YYYY-MM-DD") + " " + timesInDay[timeIndex],"Australia/Perth") );
        timeIndex += 1;
        if (timeIndex >= timesInDay.length) {
            timeIndex = 0;
            startDate.date(startDate.date() + 1);
        }
    }
    return result
}
var _precisionMap = {}
Utils.prototype.getDateFormatPrecision = function(format) {
    var precision = _precisionMap[format]
    if (!precision) {
        var d = moment("2018-02-02 01:01:01.001","YYYY-MM-DD HH:mm:ss.SSS")
        var d2 = moment(d.format(format),format)
        var diff = d - d2
        if (diff === 0) {
            precision = "milliseconds"
        } else if (diff === 1) {
            precision = "seconds"
        } else if (diff === 1001) {
            precision = "minutes"
        } else if (diff === 61001) {
            precision = "hours"
        } else if (diff === 3661001) {
            precision = "days"
        } else if (diff === 90061001) {
            precision = "months"
        } else if (diff === 2768461001) {
            precision = "years"
        } else {
            throw "Precision time interval (" + precision + ") Not Support"
        }
        _precisionMap[format] = precision
    }
    return precision
}
Utils.prototype.nextDate = function(d,format) {
    var precision = this.getDateFormatPrecision(format)
    return moment(d).add(1,precision)
}
//dateRange consists of 5 digits XXXXX or 6 digits XXXXXX
//The sixth digit(optional) is the precision type; 1 : minute; 2: hour; 3: day; 4:week; 5: month; 6: year,7:financial year, 8:seconds, 9 milliseconds
//The fifth digit is the range type; 1 : minute; 2: hour; 3: day; 4:week; 5: month; 6: year,7:financial year
//The fourth digit is the range mode: 0: current ; 1: last
//the first three digit is the range value
//For example last 24 hours; dateRange is 21024
//return an array [startDate(inclusive),endDate(inclusive)], if endDate is current time, set endDate to null
Utils.prototype.getDateRange = function(range, format) {
    var dateRange = parseInt(range)
    if (dateRange === -1) {
        //customized
        return null
    } else if (isNaN(dateRange)) {
        throw "Invalid date range '" + range + "'."
    } else if (dateRange >= 1000000 || dateRange < 10000) {
        throw "Range (" + range + ") Not Support" 
    }

    format = format || "YYYY-MM-DD"
    var resultFormat = null
    var precision = null
    if (dateRange >= 100000) {
        //precision type is specified
        precision = Math.floor(dateRange / 100000)
        dateRange = dateRange % 100000
        resultFormat = format || null
        if (precision === 1) {
            precision = "minutes"
            format = "YYYY-MM-DD HH:mm"
        } else if (precision === 2) {
            precision = "hours"
            format = "YYYY-MM-DD HH"
        } else if (precision === 3) {
            precision = "days"
            format = "YYYY-MM-DD"
        } else if (precision === 5) {
            precision = "months"
            format = "YYYY-MM"
        } else if (precision === 6) {
            precision = "years"
            format = "YYYY"
        } else if (precision === 8) {
            precision = "seconds"
            format = "YYYY-MM-DD HH:mm:ss"
        } else if (precision === 9) {
            precision = "milliseconds"
            format = "YYYY-MM-DD HH:mm:ss.SSS"
        } else {
            throw "Precision type (" + precision + ") Not Support"
        }
        if (!resultFormat) {
            resultFormat = format
        }
    } else {
        format = format || "YYYY-MM-DD"
        resultFormat = format
        precision = this.getDateFormatPrecision(format)
    }
    var startDate = null
    var endDate = null
    if (dateRange > 21000 && dateRange <= 21999) {
        //Last XX hours
        endDate = moment(moment().format(format),format)
        if (precision === "hours") {
            startDate = moment(endDate).subtract(dateRange - 21000 - 1,"hours")
        } else if (["milliseconds","seconds","minutes"].indexOf(precision) >= 0) {
            startDate = moment(endDate).subtract(dateRange - 21000,"hours")
        } else {
            startDate = moment(endDate).subtract(dateRange - 21000,"hours")
        }
        endDate = null
    } else if (dateRange === 30001) {
        //today
        startDate = moment().startOf('day')
        endDate = null
    } else if (dateRange > 31000 && dateRange <= 31999) {
        //last XXX days
        endDate = moment(moment().format(format),format)
        if (precision === "days") {
            startDate = moment(endDate).subtract(dateRange - 31000 - 1,"days")
        } else if (["milliseconds","seconds","minutes","hours"].indexOf(precision) >= 0) {
            startDate = moment(endDate).subtract(dateRange - 31000,"days")
        } else {
            startDate = moment(endDate).subtract(dateRange - 31000,"days")
        }
        endDate = null
    } else if (dateRange === 40001) {
        //current week
        startDate = moment().startOf('week')
        endDate = null
    } else if (dateRange > 41000 && dateRange <= 41999) {
        //last XXX weeks
        endDate = moment(moment().format(format),format)
        if (precision === "days") {
            startDate = moment(endDate).subtract((dateRange - 41000) * 7 - 1,"days")
        } else if (["milliseconds","seconds","minutes","hours"].indexOf(precision) >= 0) {
            startDate = moment(endDate).subtract((dateRange - 41000) * 7,"days")
        } else {
            startDate = moment(endDate).subtract((dateRange - 41000) * 7,"days")
        }
        endDate = null
    } else if (dateRange === 70001) {
        //current financial year
        var startDate = moment(moment().format("YYYY-MM-DD"),"YYYY-MM-DD")
        if (startDate.month() >= 6) {
            startDate.month(6)
            startDate.date(1)
        } else {
            startDate.year(startDate.year() - 1)
            startDate.month(6)
            startDate.date(1)
        }
        endDate = null
    }  else {
        throw "Date range (" + dateRange + ") Not Support"
    }
    return [startDate?startDate.format(resultFormat):null,endDate?endDate.format(resultFormat):null]
    
}

//like jquery.extend, but is a deep extend version
Utils.prototype.extend = function() {
    if (arguments.length === 0) {
        return {}
    } else if (arguments.length === 1) {
        return arguments[0]
    } else {
        var o = arguments[0]
        var _arguments = arguments
        var index = 1
        var vm = this
        while (index < arguments.length) {
            $.each(arguments[index],function(key,value) {
                if (value === undefined) {
                    return
                }
                if (key in o) {
                    //key exist in the result object
                    if (value !== null && value !== undefined && typeof(value) === "object" && !Array.isArray(value)) {
                        //is a json object
                        if (o[key] !== null && o[key] !== undefined && typeof(o[key]) === "object" && !Array.isArray(o[key])) {
                            //the same key in result object is a json object
                            o[key] = vm.extend(o[key],value)
                        } else {
                            //the same key in result object is not a json object,overrite it
                            o[key] = value
                        }
                    } else {
                        //is not a json object 
                        //overrite it
                        o[key] = value
                    }
                } else {
                    //key does not exist in the result object
                    o[key] = value
                }

            })
            index += 1
        }
        return o
    }
}
//extract the property value from a json object and set to json object template
//if a property in json object template does not exist in json object, the property's value will be removed from the result
//if a property in json object template has a undefined value in json object, the property will be removed from the result
//if a property whose value is a non empty json object in json object template, recusive call extract method with property value in json object template and json object.
Utils.prototype.extract = function(jsonTemplate,obj) {
    var result = {}
    var vm = this
    $.each(jsonTemplate,function(key,value){
        if (value !== null && value !== undefined && typeof(value) === "object" && !Array.isArray(value)) {
            //is a json object
            if (obj[key] === undefined) {
                return
            } else if (obj[key] === null) {
                result[key] = null
            } else if (Object.keys(value).length === 0) {
                //is a empty json object, use the value from obj 
                result[key] = obj[key]
            } else {
                //contain some properties in json object template, only extract the predefined property's value
                result[key] = vm.extract(jsonTemplate[key],obj[key])
            }
        } else if (obj[key] !== undefined){
            result[key] = obj[key]
        }
    })
    return result
}


function toInt(str) {
    try {
        var result = parseInt(str)
        return Number.isNaN(result)?0:result
    } catch(ex) {
        return 0
    }
}

Utils.prototype.getWidth = function(element) {
    return element.width() 
        + toInt(element.css("padding-left")) + toInt(element.css("padding-right")) 
        + toInt(element.css("margin-left")) + toInt(element.css("margin-right")) 
        + toInt(element.css("border-width"))
}

Utils.prototype.getHeight = function(element,unit) {
    return element.height() 
        + toInt(element.css("padding-top")) + toInt(element.css("padding-bottom")) 
        + toInt(element.css("margin-top")) + toInt(element.css("margin-bottom")) 
        + toInt(element.css("border-width"))
}

var utils = new Utils()

export default utils
