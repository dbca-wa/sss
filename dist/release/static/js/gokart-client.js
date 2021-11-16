var clientId = new Date().getTime().toString() + Math.random().toString().substring(1)
var requestId = 0
var pendingRequests = {}

function GokartClient(app,module,debug) {
    var vm = this
    this.debug = debug
    this.app = (app || "sss").toLowerCase();
    this.serverUrl = window.location.origin + "/" + this.app;
    this.defaultModule = module;
    this.channelNamePrefix = "gokart(" + this.serverUrl + ")."
    this.timeoutTask = null
    this.gokartWindow = null

    window.addEventListener('storage',function(e){
        if (!e.key.startsWith(vm.channelNamePrefix)) {
            return
        }

        var response = JSON.parse(e.newValue)
        if (e.key !== vm.channelNamePrefix + response["requestMethod"] + "status") {
            if (vm.debug) console.log(Date() + " : Receive a wrong response from channel " + e.key + ". response = " + e.newValue)
            return
        }

        response["channel"] = "localStorage"
        if (!response["requestId"]) {
            if (vm.debug) console.log(Date() + " : RequestId is missing in response. response = " + e.newValue)
            return
        }
        vm._processResponse(response)
    })
}

GokartClient.prototype._processResponse = function (response) {
    try { 
        this._clearTimeoutTask()
        if (response["clientId"] !== clientId) {
            return
        }

        if (this.debug) console.log(Date() + " : Receive response with requestId '" + response["requestId"] + "' through " + response["channel"]  + ". response = " + JSON.stringify(response.data))

        if (response.data["status"] === "failed") {
            alert(response.data["code"] + " : " + response.data["message"])
        }
    } finally{
        if (response.data["status"] !== "processing") {
           delete pendingRequests[response["requestId"].toString()]
        }
    }
}

GokartClient.prototype._clearTimeoutTask = function(){
    if (this.timeoutTask) {
        if (this.debug) console.log(Date() + " : Clear timeout task for app '" + this.app + "'")
        clearTimeout(this.timeoutTask)
        this.timeoutTask = null
    }
}
GokartClient.prototype.populateRequest = function(method,data){
    pendingRequests[(++requestId).toString()] = this
    return {
        method:method,
        clientId:clientId,
        requestId:requestId,
        time:Date(),
        data:data
    }
}

GokartClient.prototype.call = function(method,options,module,ignoreIfNotOpen){
    module = module || this.defaultModule
    ignoreIfNotOpen = ignoreIfNotOpen?true:false
    var vm = this

    var request = JSON.stringify(vm.populateRequest(method,{module:module,options:options}))
    var syncMessageFunc = null

    var sendMessage = null

    var gokartWindowIsActive = function() {
        try {
            if (!vm.gokartWindow) {
                vm.gokartWindow = window.top.opener
            }
            if (!vm.gokartWindow || vm.gokartWindow.closed) {
                return false
            } else if (vm.gokartWindow.location.origin === window.location.origin && vm.gokartWindow.location.pathname === "/" + vm.app) {
                return true
            } else if (!vm.gokartWindow.location || !vm.gokartWindow.location.origin || vm.gokartWindow.location.origin === "null" || vm.gokartWindow.location.origin === "") {
                return null
            } else {
                return false
            }
        } catch(ex) {
            return false
        }
    }

    var postMessageFunc = function() {

        if (vm.debug) console.log(Date() + " : " + vm.app + " is opened and send request to " + vm.app + " through postMessage. request = " + request)
        vm.gokartWindow.postMessage(request,window.location.origin);

        vm._clearTimeoutTask();
        if (vm.debug) console.log(Date() + " : Create a timeout task to resend the request  if postMessage to " + vm.app + " is timeout. timeout = 1 seconds" )
        vm.timeoutTask = setTimeout(function(){
            vm.timeoutTask = null
            if (vm.debug) console.log(Date() + " : post request to " + vm.app + " timeout")
            sendMessage()
        },1000)
    }

    var syncMessageFunc = function() {
        if (vm.debug) console.log(Date() + " : Sent request to " + vm.app + " through localStorage. request = " + request)
        localStorage.setItem(vm.channelNamePrefix + method,request)
        vm._clearTimeoutTask()
        if (ignoreIfNotOpen) {
            return
        }
        if (vm.debug) console.log(Date() + " : Create a timeout task to open " + vm.app + ", and send request to " + vm.app + " if timeout. timeout = 2 seconds" )
        vm.timeoutTask = setTimeout(function() {
            vm.timeoutTask = null
            if (vm.debug) console.log(Date() + " : Send request to " + vm.app + " through localStorage timeout, try to open " + vm.app)
            if (vm.debug) {
                vm.gokartWindow = window.open(vm.serverUrl + "?debug=true")
            } else {
                vm.gokartWindow = window.open(vm.serverUrl )
            }
            postMessageFunc()
        },2000)
    }

    sendMessage = function() {
        var isActive = gokartWindowIsActive()
        if (isActive === null) {
            if (vm.debug) console.log(Date() + " : gokart window is not available, create a timeout task to send message to " + vm.app + " is timeout. timeout = 200 milliseconds" )
            vm._clearTimeoutTask();
            vm.timeoutTask = setTimeout(sendMessage,200)
        } else if (isActive) {
            postMessageFunc()
        } else {
            syncMessageFunc()
        }
    }

    sendMessage()

}

window.addEventListener("message",receiveMessage,false)
function receiveMessage(event) {
    if (event.origin != window.location.origin) {
        return
    }

    var response = JSON.parse(event.data)
    if (!response["requestId"]) {
        return
    }
    response["channel"] = "postMessage"
    if ( pendingRequests[response["requestId"].toString()] ) {
        pendingRequests[response["requestId"].toString()]._processResponse(response)
    }
}
