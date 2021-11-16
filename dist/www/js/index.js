/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
var app = {
    // Application Constructor
    initialize: function() {
        this.bindEvents();
    },
    // Bind Event Listeners
    //
    // Bind any events that are required on startup. Common events are:
    // 'load', 'deviceready', 'offline', and 'online'.
    bindEvents: function() {
        document.addEventListener('deviceready', this.onDeviceReady, false);
    },
    getUserTask :null,
    loginWindow :null,
    // deviceready Event Handler
    //
    // The scope of 'this' is the event. In order to call the 'receivedEvent'
    // function, we must explicitly call 'app.receivedEvent(...);'
    onDeviceReady: function() {
        app.receivedEvent('deviceready');
    },

    getUser: function() {
        app.loginWindow.executeScript({code:"[document.location,document.getElementById(\"whoami\").innerText]"},function(values){
            docLocation = values[0][0];
            if (docLocation.protocol + "//" + docLocation.host != env.staticService) {
                return;
            }
            user = values[0][1].trim();
            if (user.length > 0) {
                try {
                    window.login(JSON.parse(user))
                    app.loginWindow.close()
                } catch(ex) {
                    alert("Login failed");
                }
            } else {
                getUserTask = window.setTimeout(app.getUser,300);
            }
        })
    },
    // Update DOM on a Received Event
    receivedEvent: function(id) {
        app.loginWindow = cordova.InAppBrowser.open(env.staticService + '/pages/login.html', '_blank', "location=no");
        app.loginWindow.addEventListener("loadstop",function() {
            if (app.getUserTask) {
                clearTimeout(app.getUserTask);
                app.getUserTask = null;
            }
            app.getUserTask = window.setTimeout(app.getUser,300);
        });
    }
};

app.initialize();
