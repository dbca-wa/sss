// module for packaging up gokart's third-party dependencies

// produce some terrifying CSS at runtime using browserify-css
import 'tether-shepherd/dist/css/shepherd-theme-dark.css'
import 'foundation-sites/dist/foundation-flex.css'
import 'foundation-datepicker/css/foundation-datepicker.css'
import 'openlayers/dist/ol-debug.css'
import 'dragula/dist/dragula.css'

// jQuery v2, the krazy glue of the internet
import $ from 'jquery'
// jCanvas mod to canvas operations
require('jcanvas')($, window)
// Cross-browser support for saving blobs from a webpage
import { saveAs as fileSaveAs} from 'filesaverjs'
// Cross-browser polyfill for canvas.toBlob
require('blueimp-canvas-to-blob')
// Cross-browser polyfill for ES6
import 'babel-polyfill'
// OpenLayers 3 map widget, including our extensions
import ol from 'src/ol-extras.js'
// proj4 reprojection lib
import proj4 from 'proj4'
// Vue.js template engine
import Vue from 'vue'
// Extension for easy cross-component sharing
import VueStash from 'vue-stash'
// Foundation 6 CSS framework
import 'foundation-sites'
import 'foundation-datepicker'
// IE9+ support for SVG sprites
import svg4everybody from 'svg4everybody'
//emailer(s)
//import emailjs from 'emailjs-com'
import nodemailer from 'nodemailer'
import postmark from 'postmark'
import * as Msal from 'msal'
// QR code generator
import kjua from 'kjua'
import qs from 'qs'
import axios from 'axios'
// Timestamp parsing library
//import moment from 'moment'
import moment from 'moment-timezone'
// Drag and drop support
import dragula from 'dragula'
// Data storage engine
import localforage from 'localforage'
// attach elements to eachother
import Tether from 'tether'
// Guided tour lib
import Shepherd from 'tether-shepherd'
//pdf generator
import jsPDF from 'jspdf'
import interact from 'interact.js'
import hash from "object-hash"
import utils from './utils.js'
import turf from 'turf'

var saveAs = function (blob, name, no_auto_bom) {
    if (env.appType == "cordova") {
        var formData = new window.FormData();
        formData.append('file', blob, name);
        var req = new window.XMLHttpRequest();
        req.open('POST', gokartService + '/saveas');
        req.withCredentials = true;
        req.responseType = 'text';
        req.onload = function (event) {
            var fetchUrl = req.responseText;
            window.open(fetchUrl,"_system");
        };
        req.send(formData);
    } else {
        fileSaveAs(blob,name,no_auto_bom);
    }
}

ol.control.FullScreen.getChangeType_ = (function() {
    var originFunc = ol.control.FullScreen.getChangeType_
    return function() {
        return originFunc() || ""
    }
})()

ol.control.FullScreen.isFullScreenSupported = (function() {
    var originFunc =  ol.control.FullScreen.isFullScreenSupported
    return function() {
        return (env.appType == "cordova")?false:originFunc()
    }    
})()

ol.control.FullScreen.prototype.handleFullScreenChange_ = function() {
    var originalFunc = ol.control.FullScreen.prototype.handleFullScreenChange_;
    return function() {
        originalFunc.call(this)
        this.setMap(this.getMap())
    }
}()
//improve freehand drawing by
//1. Remove the consectuive same points.
//2. Guarantee the pixels between two points must be not less than the value of the property 'minDistance' if configured
ol.interaction.Draw.prototype.addToDrawing_ = function() {
    var originFunc = ol.interaction.Draw.prototype.addToDrawing_;
    return function(event) {
        if (this.freehand_) {
          var coordinates = null
          if (this.mode_ === ol.interaction.Draw.Mode.LINE_STRING) {
            coordinates = this.sketchCoords_;
          } else if (this.mode_ === ol.interaction.Draw.Mode.POLYGON) {
            coordinates = this.sketchCoords_[0];
          }
          if (coordinates.length >= 2) {
              if (coordinates[coordinates.length - 2][0] === event.coordinate[0] && coordinates[coordinates.length - 2][1] === event.coordinate[1]) {
                  return
              }
              if (this.get('minDistance')) {
                  var lastPoint = event.map.getPixelFromCoordinate(coordinates[coordinates.length - 2])
                  if (Math.sqrt(Math.pow(event.pixel[0] - lastPoint[0],2) + Math.pow(event.pixel[1] - lastPoint[1],2)) <= this.get('minDistance')) {
                      return
                  }
              }
          }
        }
        originFunc.call(this,event)
    }
}();

//Configure the snapTolerance for freehand drawing
ol.interaction.Draw.prototype.atFinish_ = function(event) {
  var at = false;
  if (this.sketchFeature_) {
    var potentiallyDone = false;
    var potentiallyFinishCoordinates = [this.finishCoordinate_];
    if (this.mode_ === ol.interaction.Draw.Mode.LINE_STRING) {
      potentiallyDone = this.sketchCoords_.length > this.minPoints_;
    } else if (this.mode_ === ol.interaction.Draw.Mode.POLYGON) {
      potentiallyDone = this.sketchCoords_[0].length >
          this.minPoints_;
      potentiallyFinishCoordinates = [this.sketchCoords_[0][0],
        this.sketchCoords_[0][this.sketchCoords_[0].length - 2]];
    }
    if (potentiallyDone) {
      var map = event.map;
      for (var i = 0, ii = potentiallyFinishCoordinates.length; i < ii; i++) {
        var finishCoordinate = potentiallyFinishCoordinates[i];
        var finishPixel = map.getPixelFromCoordinate(finishCoordinate);
        var pixel = event.pixel;
        var dx = pixel[0] - finishPixel[0];
        var dy = pixel[1] - finishPixel[1];
        var snapTolerance = this.freehand_ ? (this.get('freehandSnapTolerance') || 1) : this.snapTolerance_;
        at = Math.sqrt(dx * dx + dy * dy) <= snapTolerance;
        if (at) {
          this.finishCoordinate_ = finishCoordinate;
          break;
        }
      }
    }
  }
  return at;
};


//customize thie method to avoid cyclic object value
JSON.stringify = (function(){
    var originFunc = JSON.stringify
    return function(obj,replacer,space) {
        try {
            return originFunc(obj,replacer,space)
        } catch(err) {
            //failed
            return "(" + err + ")"
        }
    }
})()

moment.fn.toLocaleString = function(){
    return this.tz("Australia/Perth").format('ddd MMM DD YYYY HH:mm:ss [AWST]')
}
moment.fromLocaleString = function(datestr){
    return moment.tz(datestr,'ddd MMM DD YYYY HH:mm:ss [AWST]','Australia/Perth')
}

//config Vue
//three call formats:
//1. list, prop ,value : check whether objects'property is equal with value
//2. list, prop : check whether object's property is true
//3. list, func : check whether return value of func(o) is true
Vue.filter('filterIf', function (list) {
  if (!list) { return }
  if (arguments.length === 2) {
      if (typeof arguments[1] === "string") {
          var prop = arguments[1];
          return list.filter(function (val) {
            return val && val[prop];
          })
      } else {
          var func = arguments[1];
          return list.filter(function (val) {
            return func(val);
          })
      }
  } else if(arguments.length === 3) {
      var prop = arguments[1];
      var value = arguments[2];
      return list.filter(function (val) {
        return val && val[prop] === value;
      })
  } else {
      return ;
  }
})

export {
  $,
  ol,
  proj4,
  Vue,
  VueStash,
  svg4everybody,
  saveAs,
  postmark,
  Msal,
  qs,
  axios,
  kjua,
  nodemailer,
  moment,
  dragula,
  localforage,
  Tether,
  Shepherd,
  jsPDF,
  interact,
  hash,
  turf,
  utils
}
