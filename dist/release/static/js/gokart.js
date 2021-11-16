var Gokart = (function() {
    var _Gokart = function (url,app,module) {
        this.url = url;
        this.app = app;
        this.module = module;
        this.gokartWindow = null;
        this.status = "loading";
        this.message = "Gokart client is loading";
    
        this.gokartFrame = document.createElement("iframe");
        this.gokartFrame.setAttribute('id','gokartclient');
        this.gokartFrame.setAttribute('height','0px');
        this.gokartFrame.setAttribute('width','0px');
        this.gokartFrame.setAttribute('src',this.url + '/client');
        this.gokartFrame.setAttribute('style',"display:none")
        this.debug = window.location.search?(window.location.search.toLowerCase().indexOf("debug=true") >= 0):false;
    
        var vm = this
        this.gokartFrame.onload = function(){
            vm.gokartFrame.contentWindow.postMessage(JSON.stringify({method:"create",options:{origin:window.location.origin,module:vm.module,app:vm.app,debug:vm.debug}}),vm.url);
        }
        window.addEventListener("message",function (event) {
            if (vm.status === "closed") return;
            var response = JSON.parse(event.data);
            if (response.requestId === "create") {
                if (response.data.status === "OK") {
                    vm.gokartWindow = vm.gokartFrame.contentWindow;
                    vm.status = "ready";
                } else {
                    vm.message = response.data.status + ":" + response.data.message;
                    alert(vm.message)
                    vm.status = "failed";
                }
            }
        },false)
    
        document.body.appendChild(this.gokartFrame);
    }
    
    _Gokart.prototype.call = function(method,options,ignoreIfNotOpen) {
        var vm = this
        var func = function() {
            if (vm.status === "ready")  {
                ignoreIfNotOpen = ignoreIfNotOpen?true:false
                vm.gokartWindow.postMessage(JSON.stringify({method:method,data:{module:vm.module,options:options},ignoreIfNotOpen:ignoreIfNotOpen}),vm.url);
            } else if (vm.status === "loading") {
                setTimeout(func,100)
            } else {
                alert(vm.message);
            }
        }
        func()
    }
    _Gokart.prototype.close = function() {
        if  (this.gokartFrame && this.gokartFrame.parentNode) {
            this.gokartFrame.parentNode.removeChild(this.gokartFrame)
        }
        this.gokartFrame = null;
        this.gokartWindow = null;
        this.status = "closed";
        this.message = "Gokart client is closed";
        if (this.debug) console.log(this.message)
    }

    var instance = null;

    return {
        get:function(module,url,app) {
            var url = url || "https://sss.dbca.wa.gov.au";
            if (url.endsWith("/")) {
                url = url.substring(0,url.length - 1)
            }
            var app = app || "sss";
            var module = module;

            if (instance) {
                if (instance.url === url && instance.app === app) {
                    instance.module = module;
                } else {
                    instance.close();
                    instance = new _Gokart(url,app,module)
                }
            } else {
                instance = new _Gokart(url,app,module)
            }
            return instance
        }
    }
})();
    
