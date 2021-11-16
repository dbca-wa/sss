let GokartListener = function() {
    var vm = this
    this.debug = window.location.search?(window.location.search.toLowerCase().indexOf("debug=true") >= 0):false 
    this.channelNamePrefix = "gokart(" + window.location.origin + window.location.pathname + ")."

    window.addEventListener('storage',function(e){
        if (e.key.startsWith(vm.channelNamePrefix)) {
            var request = JSON.parse(e.newValue)
            if (!request["clientId"] || !request["data"]) {
                if (this.debug) console.log(Date() + " : Request without clientId or request data is received from channel " + e.key + ". request = " + e.newValue)
                return 
            }
            if (request["method"] !== e.key.substring(vm.channelNamePrefix.length)) {
                if (this.debug) console.log(Date() + " : Request with invalid method is received from channel " + e.key + ". request = " + e.newValue)
                return
            }

            request["channel"] = "localStorage"
            vm._processRequest(request,function(response){
                localStorage.setItem(e.key + "status",response)
            })
        }
    })
    
    if (this.debug) console.log(Date() + " : Gokart listener is initialized." )
}

GokartListener.prototype._processRequest = function(request,sentResponse) {
    var vm = this
    var waitingTime = 0
    if (vm.debug) console.log(Date() + " : Receive a request through " + request["channel"] + ". request = " + JSON.stringify(request))
    sentResponse(JSON.stringify(vm.populateResponse(request,"RECEIVED")))

    var setupCalled = false

    var func = function() {
        if (!window.gokart || !window.gokart["loading"].appStatus.isFinished()) {
            if (waitingTime >= 60000) {
                if (vm.debug) console.log(Date() + " : Initialize gokart timeout")
                sentResponse(JSON.stringify(vm.populateResponse(request,"GOKART_FAILED","Initialize gokart timeout.")))
                return
            }
            if (vm.debug) console.log(Date() + " : gokart is loading")
            setTimeout(func,1000)
            waitingTime += 1000
        } else if (!(window.gokart['loading'].appStatus.isSucceed())) {
            sentResponse(JSON.stringify(vm.populateResponse(request,"GOKART_FAILED",window.gokart['loading'].appStatus.failedMessages())))
        } else if (request["method"]) {
            if (!window.gokart[request["data"]['module']]) {
                sentResponse(JSON.stringify(vm.populateResponse(request,"MODULE_NOT_FOUND")))
            } else if (!window.gokart[request["data"]["module"]][request["method"]]) {
                sentResponse(JSON.stringify(vm.populateResponse(request,'METHOD_NOT_SUPPORT')))
            } else {

                if (!setupCalled && window.gokart[request["data"]["module"]].setup) {
                    if (vm.debug) console.log(Date() + " : call setup to initialize module " + request["data"]["module"])
                    window.gokart[request["data"]["module"]].setup()
                    setupCalled = true
                }
                var moduleStatus = window.gokart['loading'].getStatus(request["data"]["module"])
                if (!moduleStatus.isFinished()) {
                    if (waitingTime >= 60000) {
                        sentResponse(JSON.stringify(vm.populateResponse(request,"GOKART_FAILED","Initialize " + request["data"]["module"] + " timeout.")))
                        return
                    }
                    if (vm.debug) console.log(Date() + " : " + request["data"]["module"] + " is initializing")
                    setTimeout(func,1000)
                    waitingTime += 1000
                    return
                } else if (!moduleStatus.isSucceed()) {
                    sentResponse(JSON.stringify(vm.populateResponse(request,"GOKART_FAILED",moduleStatus.failedMessages())))
                    return
                }

                try {
                    window.gokart[request["data"]["module"]][request["method"]](request["data"]['options'])
                    window.focus();
                    sentResponse(JSON.stringify(vm.populateResponse(request,'OK')))
                } catch(ex) {
                    sentResponse(JSON.stringify(vm.populateResponse(request,'METHOD_FAILED',ex)))
                    throw ex
                }
            }
        } else {
            sentResponse(JSON.stringify(vm.populateResponse(request,'METHOD_IS_MISSING')))
        }
    }
    func()
}
GokartListener.prototype.populateResponse = function(request,code,failedReason) {
    var response = {
        clientId:request["clientId"],
        requestId:request["requestId"],
        requestMethod:request["method"],
        time:Date(),
        data:{
            status:"failed",
            code:code,
            message:"",
        }
    }
    var data = response["data"]
    if (code === "RECEIVED") {
        data["message"] = "Request is received from " + request["channel"] + ". data = " + JSON.stringify(request["data"])
        data["status"] = "processing"
    } else if (code === "GOKART_FAILED") {
        data["message"] = failedReason
    } else if (code === "MODULE_NOT_FOUND") {
        data["message"] = "Module(" + window.gokart[request["data"]['module']] + ") is not found."
    } else if (code === "METHOD_NOT_SUPPORT") {
        data["message"] = "Module(" + window.gokart[request["data"]['module']] + ") does not support method " + request["method"] +"."
    } else if (code === "OK") {
        data["message"] = "Succeed to execute method '" + request["method"] + "', data = " + JSON.stringify(request["data"])
        data["status"] = "succeed"
    } else if (code === "METHOD_IS_MISSING") {
        data["message"] = "Rquest method is missing, data = " + JSON.stringify(request["data"])
    } else if (code === "METHOD_FAILED") {
        data["message"] = "Failed to execute method '" + request["method"] + "', data = " + JSON.stringify(request["data"]) + ". Reason = " + failedReason
    }

    if (this.debug) console.log(Date() + " : Send response to client '" + request['clientId'] + "' through " + request["channel"] + " . response = " + JSON.stringify(response))

    return response
}

var gokartListener = new GokartListener()
    
window.addEventListener("message",receiveMessage,false)
function receiveMessage(event) {
    if (event.origin != window.location.origin) {
        return
    }
    var request = JSON.parse(event.data)
    request["channel"] = "postMessage"
    gokartListener._processRequest(request,function(response){
        event.source.postMessage(response,window.location.origin)
    })
}

export default gokartListener
