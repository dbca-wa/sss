<template>
  <div class="tabs-panel" id="layers-export" v-cloak>
    <div id="map-export-controls">
      <div id="settings-fixpart">  
      <!--div class="tool-slice row collapse">
        <div class="small-3">
          <label class="tool-label">Vector format:</label>
        </div>
        <div class="small-9">
          <select name="select" v-model="vectorFormat">
            <option value="json" selected>GeoJSON (web GIS)</option> 
            <option value="kml">KML (Google Earth)</option>
            <option value="geopkg">Geopackage (high performance)</option>
            <option value="shapefile">Shapefile (legacy desktop GIS)</option>
            <option value="csv">CSV (Spreadsheet/Excel)</option>
          </select>
        </div>
      </div-->
      <div class="tool-slice row collapse">
        <div class="small-3">
          <label class="tool-label">Name:</label>
        </div>
        <div class="small-9">
          <input id="export-name" type="text" v-model="title" placeholder="Map Name"/>
        </div>
      </div>
      <div class="tool-slice row collapse">
        <div class="small-3">
          <label class="tool-label">Paper size:</label>
        </div>
        <div class="small-9">
          <select v-model="paperSize">
                    <option v-for="size in paperSizes" v-bind:value="$key">{{ $key }} ({{ size[0] }}mm &times; {{ size[1] }}mm)</option>
                  </select>
        </div>
      </div>

      <div class="tool-slice row collapse">
        <div class="small-3">
          <label class="tool-label">Download:</label>
        </div>
        <div class="small-9">
          <div class="expanded button-group">
            <a class="button" title="JPG for quick and easy printing" @click="print('jpg')"><i class="fa fa-file-image-o"></i><br>JPG</a>
            <a class="button" title="Geospatial PDF for use in PDF Maps and Adobe Reader" @click="print('pdf')"><i class="fa fa-print"></i><br>PDF</a>
            <a class="button" title="GeoTIFF for use in QGIS on the desktop" @click="print('tif')"><i class="fa fa-picture-o"></i><br>GeoTIFF</a>
            <a class="button" title="Legends of active layers" @click="layerlegends.toggleLegends()"><i class="fa fa-file-pdf-o"></i><br>Legend</a>
          </div>
        </div>
      </div>

      <div class="tool-slice row collapse">
        <div class="small-3">
          <div class="switch tiny">
            <input class="switch-input" id="toggleRetainBoundingbox" type="checkbox" v-bind:checked="settings.print.retainBoundingbox" @change="toggleRetainBoundingbox"/>
            <label class="switch-paddle" for="toggleRetainBoundingbox">
              <span class="show-for-sr">Fit to screen bounding box</span>
            </label>
          </div>
        </div>
        <div class="small-9">
          <label for="toggleRetainBoundingbox" >Fit to screen bounding box</label>
        </div>
      </div>
      
      <div class="tool-slice row collapse">
        <div class="small-3">
          <div class="switch tiny">
            <input class="switch-input" id="toggleSnapToFixedScale" type="checkbox" v-bind:checked="settings.print.snapToFixedScale" @change="toggleSnapToFixedScale"/>
            <label class="switch-paddle" for="toggleSnapToFixedScale">
              <span class="show-for-sr">Snap to nearest fixed scale</span>
            </label>
          </div>
        </div>
        <div class="small-9">
          <label for="toggleSnapToFixedScale" >Snap to nearest fixed scale</label>
        </div>
      </div>
      
      <hr class="row"/>
      <div class="tool-slice row collapse">
        <div class="small-3">
          <label class="tool-label">Info:</label>
        </div>
        <div class="small-9 columns">
          <div class="expanded button-group">
            <label class="button expanded" for="spatialInfo" title="{{utils.importSpatialFileTypeDesc}}">
                <i class="fa fa-info"></i> Spatial Info
            </label>
            <input type="file" id="spatialInfo" class="show-for-sr" name="spatialinfofile" v-el:spatialinfofile @change="getSpatialInfo()" accept="{{utils.importSpatialFileTypes}}"/>
          </div>
        </div>

        <div class="small-3">
          <label class="tool-label">Transform:</label>
        </div>
        <div class="small-9 columns">
          <div class="expanded button-group">
            <label class="button expanded convertbutton" for="togeojson" 
                title="{{utils.importSpatialFileTypeDesc}}">
                <i class="fa fa-exchange"></i><br>Transform<br>(geojson)
            </label>
            <input type="file" id="togeojson" class="show-for-sr" name="convertfile" v-el:togeojson @change="convertFormat('geojson',$event)" 
                accept="{{utils.importSpatialFileTypes}}"/>

            <label class="button expanded convertbutton" for="togpkg" 
                title="{{utils.importSpatialFileTypeDesc}}">
                <i class="fa fa-exchange"></i><br>Transform<br>(gpkg)
            </label>
            <input type="file" id="togpkg" class="show-for-sr" name="convertfile" v-el:togpkg @change="convertFormat('gpkg',$event)" 
                accept="{{utils.importSpatialFileTypes}}"/>

            <label class="button expanded convertbutton" for="toshp" 
                title="{{utils.importSpatialFileTypeDesc}}">
            <i class="fa fa-exchange"></i><br>Transform<br>(shp)
            </label>
            <input type="file" id="toshp" class="show-for-sr" name="convertfile" v-el:toshp @change="convertFormat('shp',$event)" 
                accept="{{utils.importSpatialFileTypes}}"/>

            <label class="button expanded convertbutton" for="tocsv" 
                title="{{utils.importSpatialFileTypeDesc}}">
            <i class="fa fa-exchange"></i><br>Transform<br>(csv)
            </label>
            <input type="file" id="tocsv" class="show-for-sr" name="convertfile" v-el:tocsv @change="convertFormat('csv',$event)" 
                accept="{{utils.importSpatialFileTypes}}"/>

          </div>
        </div>
      </div>

      <hr class="row"/>
      <div class="tool-slice row collapse">
        <div class="small-3">
          <label class="tool-label">Save view:</label>
        </div>
        <div class="small-9 columns">
          <div class="input-group">
            <input v-el:savestatename class="input-group-field" type="text" placeholder="Name for saved view"/>
            <div class="input-group-button">
              <a class="button" @click="saveStateButton()">Save</a>
            </div>
          </div>
        </div>
      </div>
      <div class="tool-slice row collapse">
        <div class="small-3">
          <label class="tool-label">Export view:</label>
        </div>
        <div class="small-9 columns">
          <div class="expanded button-group">
            <a class="button expanded" @click="download()"><i class="fa fa-download"></i> Download current view</a>
          </div>
        </div>
      </div>
      <div class="tool-slice row collapse">
        <div class="small-3">
          <label class="tool-label">Load view:</label>
        </div>
        <div class="small-9 columns">
          <div class="expanded button-group">
            <label class="button expanded" for="uploadFile"><i class="fa fa-upload"></i> Upload view file</label><input type="file" id="uploadFile" class="show-for-sr" name="statefile" accept="application/json" v-model="statefile" v-el:statefile @change="load()"/>
          </div>
        </div>
      </div>
      </div>

      <div class="tool-slice row collapse scroller" id="settings-flexible">
        <div class="small-3">
          <label class="tool-label"></label>
        </div>
        <div class="small-9 columns">
          <div v-for="state in states" class="feature-row" style="overflow: hidden">
            <div class="float-right button-group small">
              <a class="button" title="Open view" @click="open(state)"><i class="fa fa-folder-open"></i></a>
              <a class="button" title="Download view" @click="download(state)"><i class="fa fa-download"></i></a>
              <a class="button alert" title="Delete view" @click="remove(state)">✕</a>
            </div>
            {{ state }}
          </div>
          <div v-if="states.length == 0" class="feature-row">
            No saved views yet
          </div>
        </div>
      </div>

      <div class="hide" v-el:legendsvg>
        <gk-legend></gk-legend>
      </div>

      <img id="map-disclaimer" class="hide" src="/dist/static/images/map-disclaimer.svg"/>

      <gk-layerlegends v-ref:layerlegends></gk-layerlegends>
    </div>

    <div class="small reveal" id="spatialInfoDialog" data-reveal data-close-on-click='false'> 
        <h3 >{{spatialInfo.title}}</h3>
        <div class="row feature-row" >
            <div class="small-5 columns">Layer</div>
            <div class="small-2 columns">SRS</div>
            <div class="small-2 columns">Geometry</div>
            <div class="small-2 columns">Features</div>
            <div class="small-1 columns"></div>
        </div>
        <template v-for="dslayers in spatialInfo['datasources']" class="row feature-row"  track-by="$index">
            <div class="row" v-if="spatialInfo['datasourceCount'] > 1">
                <div class="small-12 columns datasource"><a>{{dslayers["datasource"]}}</a></div>
            </div>
            <div v-for="l in dslayers['layers']" class="row feature-row"  track-by="$index">
                <div class="small-5 columns">{{l.layer}}</div>
                <div class="small-2 columns">{{l.srs}}</div>
                <div class="small-2 columns">{{l.geometry}}</div>
                <div class="small-2 columns">{{l.features}}</div>
                <div class="small-1 columns">
                    <a class="button tiny secondary float-right" v-if="spatialInfo.upload" @click="importLayer(dslayers['datasource'],l)"><i class="fa fa-upload"></i></a>
                </div>
            </div>
        </template>

        <button class="close-button" data-close aria-label="Close modal" type="button">
            <span aria-hidden="true">&times;</span>
        </button>
    </div>

  </div>
</template>
<style>
.datasource {
    font-size: 18px;
    font-weight: bold;
    font-style: italic;
    background-color: #266f78;
}
.convertbutton {
    padding-left:2px;
    padding-right:2px;
}
</style>
<script>
  import { kjua, saveAs, moment, $, localforage,hash} from 'src/vendor.js'
  import gkLegend from './legend.vue'
  import gkLayerlegends from './layerlegends.vue'
  export default {
    store: {
        whoami:'whoami', 
        dpmm:'dpmm', 
        view:'view', 
        mmPerInch:'mmPerInch',
        settings:'settings',
        displayResolution:'displayResolution',
        activeMenu:'activeMenu',
        activeSubmenu:'activeSubmenu',
        screenHeight:'layout.screenHeight',
        hintsHeight:'layout.hintsHeight',
        leftPanelHeadHeight:'layout.leftPanelHeadHeight'
    },
    components: { gkLegend,gkLayerlegends },
    data: function () {
      return {
        spatialInfo:{},
        minDPI: 150,
        paperSizes: {
          A0: [1189, 841],
          A1: [841, 594],
          A2: [594, 420],
          A3: [420, 297],
          A4: [297, 210]
        },
        paperSize: 'A3',
        printStatus: {
            oldLayout: {},
            layout:{},
            overviewMap:{},
            jobs:0
        },
        title: '',
        statefile: '',
        vectorFormat: 'geojson',
        states: [],
        vectorFormats:[
            {format:"geojson",title:"GeoJSON (web GIS)",name:"GeoJSON"},
            {format:"sqlite",title:"SQLite",name:"SQLite"},
            {format:"gpkg",title:"GeoPackage",name:"GeoPackage"},
            {format:"csv",title:"CSV (Spreadsheet/Excel)",name:"CSV"}
        ]
      }
    },
    // parts of the template to be computed live
    computed: {
      loading: function () { return this.$root.loading },
      env: function () { return this.$root.env },
      annotations: function () { return this.$root.annotations },
      utils: function () { return this.$root.utils },
      layerlegends:function() {return this.$refs.layerlegends},
      map:function() {return this.$root.map},
      olmap: function () {
        return this.$root.map.olmap
      },
      shortUrl: {
        cache: false,
        get: function () {
          if (!this.olmap) { return }
          var lonlat = this.olmap.getView().getCenter()
          return $.param({ lon: lonlat[0], lat: lonlat[1], scale: Math.round(this.$root.map.getScale() * 1000) })
        }
      },
      finalTitle:function() {
        this.title = this.title.trim()
        return (this.title.length == 0)?"Quick Print":this.title
      },
      bucketKey: function() {
        return hash.MD5({
            'extent':this.printStatus.layout.extent.join(' '),
            'author': this.legendInfo().author,
            'filename':this.finalTitle,
            'time': Date.now()
        })
      },
    },
    // methods callable from inside the template
    methods: {
      adjustHeight:function() {
        if (this.activeMenu === "layers" && this.activeSubmenu === "export") {
            //console.log("screenHeight=" + this.screenHeight)
            //console.log("fixedHeight=" + $("#settings-fixpart").height() )
            $("#settings-flexible").height(this.screenHeight - this.leftPanelHeadHeight -16 - $("#settings-fixpart").height() - this.hintsHeight)
        }
      },
      toggleRetainBoundingbox:function(ev) {
        this.settings.print.retainBoundingbox = !this.settings.print.retainBoundingbox
        this.saveState()
      },
      toggleSnapToFixedScale:function(ev) {
        this.settings.print.snapToFixedScale = !this.settings.print.snapToFixedScale
        this.saveState()
      },
      // info for the legend block on the print raster
      legendInfo: function () {
        if (!this.$root.map || !this.$root.map.olmap) {
            return {}
        }
        var result = {
          title: this.finalTitle,
          author: "Produced by the Department of Parks and Wildlife", //this.whoami.email,
          date: 'Map last amended ' + moment().toLocaleString()
        }
        if (this.$root.map) {
          result.km = (Math.round(this.$root.map.getScale() * 40) / 1000).toLocaleString()
          result.scale = this.paperSize + ' ' + this.$root.scales.scaleString
        }
        return result
      },
      exportVector: function(features, name,format) {
        var vm = this
        //add applicaiton name and timestamp
        var name = (name || '') + "." + this.$root.profile.name + "_export_" + moment().format("YYYYMMDD_HHmmss")
        var result = this.$root.geojson.writeFeatures(features)
        format = format || this.vectorFormat
        if (format === 'geojson') {
          var blob = new window.Blob([result], {type: 'application/json;charset=utf-8'})
          saveAs(blob, name + '.geojson')
        } else {
          this.downloadVector(format,{
            filename:name,
            datasources : {
                parameter:"features",
                default_geometry_type:"auto",
                default_srs:"EPSG:4326"
            },
            features:result,
            srs:"EPSG:4326"
          })
        }
      },
      getFileFormat:function(filename) {
        return this._fileformats.find(function(f){return filename.substring(filename.length - f[1].length).toLowerCase() === f[1]})
      },
      convertFormat:function(format,ev) {
        var file = (ev.currentTarget.files.length > 0)?ev.currentTarget.files[0]:null
        ev.currentTarget.value = null
        if (!file) {
            return
        }
        
        var fileFormat = this.getFileFormat(file.name)
        if (!fileFormat) {
            alert("Unsupported file format(" + file.name + ")")
            return
        }
        if (fileFormat[0] === format) {
            alert("Target format is the same as source format.")
            return
        }

        this.downloadVector(format,{
            datasources : {
                parameter:"datafile",
                default_geometry_type:"auto",
            },
            files: {
                datafile:file
            },
            srs:"EPSG:4326"
        })
      },
      downloadVector:function(format,options,callback) {
        var vm = this
        var formData = new window.FormData()
        var tasks = 1
        var defaultFileName = null
        if (!callback) {
            callback = function(status,msg) {
                if (msg) {
                    alert(msg)
                }
            }
        }
        var sendRequest = function() {
            if (tasks > 0) {
                return
            }
            try{
                var req = new window.XMLHttpRequest()
                req.open('POST', vm.env.gokartService + '/download/' + format)
                req.responseType = 'blob'
                req.withCredentials = true
                req.onload = function (event) {
                    try{
                        if (req.status >= 400) {
                            var reader = new FileReader()
                            reader.addEventListener("loadend",function(e){
                                callback(false,e.target.result)
                            })
                            reader.readAsText(req.response)
                        } else {
                            var filename = null
                            if (req.getResponseHeader("Content-Disposition")) {
                                var matches = vm._filename_re.exec(req.getResponseHeader("Content-Disposition"))
                                filename = (matches && matches[1])? matches[1]: null
                            }
                            if (!filename) {
                                filename = files[0].name.substring(0,files[0].name.length - fileFormat[1].length) + "." + format
                            }
                            if (!filename) {
                                filename = "download." + format
                            }
                            saveAs(req.response, filename)
                            callback(true)
                        }
                    } catch(ex) {
                        callback(false,ex.message || ex)
                    }
                }
                req.send(formData)
            }catch(ex) {
                callback(false,ex.message || ex)
            }
        }
        try {
            $.each(options,function(key,value){
                if (key === "layers") {
                    formData.append('layers', JSON.stringify(options["layers"]))
                } else if (key === "datasources") {
                    formData.append('datasources', JSON.stringify(options["datasources"]))
                } else if (key === "files") {
                    $.each(value,function(name,file){
                        tasks += 1
                        var fileFormat = vm.getFileFormat(file.name)
                        if (!fileFormat) {
                            throw ("Unsupported file format(" + file.name + ")")
                        }
                        if (!defaultFileName) {
                            defaultFileName = file.name.substring(0,file.name.length - fileFormat[1].length) + "." + format
                        }
    
                        var reader = new window.FileReader()
                        reader.onload = function(){
                            var parameter = name
                            var fmt = fileFormat[2]
                            var filename = file.name
                            return function(e) {
                                formData.append(parameter, new window.Blob([e.target.result],{type:fmt}), filename)
                                tasks -= 1
                                sendRequest()
                            }
                        }()
                        reader.readAsArrayBuffer(file)
                    })
                } else {
                    formData.append(key, value)
                }
            })
    
            tasks -= 1
            sendRequest()
        }catch(ex) {
            callback(false,ex.message || ex)
        }
      },
      getSpatialInfo: function(){
        var file = (this.$els.spatialinfofile.files.length > 0)?this.$els.spatialinfofile.files[0]:null
        this.$els.spatialinfofile.value = null
        if (!file) {
            return
        }
        var fileFormat = this.getFileFormat(file.name)
        if (!fileFormat) {
            alert("Unsupported file format(" + file.name + ")")
            return
        }
        var vm = this
        var reader = new window.FileReader()
        reader.onload = function (e) {
            try{
                var formData = new window.FormData()
                formData.append('datasource', new window.Blob([e.target.result],{type:fileFormat[2]}), file.name)
                var req = new window.XMLHttpRequest()
                req.open('POST', vm.env.gokartService + '/ogrinfo')
                req.responseType = 'blob'
                req.withCredentials = true
                req.onload = function (event) {
                    try{
                        if (req.status >= 400) {
                            var reader = new FileReader()
                            reader.readAsText(req.response)
                            reader.addEventListener("loadend",function(e){
                                alert(e.target.result)
                            })
                            delete vm._importData
                        } else {
                            var reader = new FileReader()
                            reader.readAsText(req.response)
                            reader.addEventListener("loadend",function(e){
                                if (!e.target.result) {
                                    alert("No spatial data")
                                    return
                                }
                                var spatialInfo = JSON.parse(e.target.result)
                                if (!spatialInfo || !spatialInfo["layerCount"]) {
                                    alert("No spatial data")
                                    return
                                } else {
                                    vm.spatialInfo = spatialInfo
                                    vm.spatialInfo.title = file.name
                                    vm.spatialInfo.upload = false
                                    $("#spatialInfoDialog").foundation('open')
                                }
                            })
                        }
                    } catch(ex) {
                        alert(ex.message || ex)
                    }
                }
                req.send(formData)
            }catch(ex) {
                alert(ex.message || ex)
            }
        }
        reader.readAsArrayBuffer(file)
      },
      importVector: function(file,callback,failedCallback) {
        // upload vector  
        var vm = this
        var fileFormat = this.getFileFormat(file.name)
        if (!fileFormat) {
            var msg = "Unsupported file format(" + file.name + ")"
            if (failedCallback) {
                failedCallback(msg)
            } else {
                alert(msg)
            }
            return
        }

        try {
            if ((fileFormat[0] === "geojson") || (fileFormat[0] === "json")) {
                var reader = new window.FileReader()
                reader.onload = function (e) {
                    try {
                        var features = new ol.format.GeoJSON().readFeatures(e.target.result,{dataProjection:"EPSG:4326"})
                        if (features && features.length) {
                           callback(features,fileFormat[0])
                        }
                    } catch(ex) {
                        if (failedCallback) failedCallback(ex.message || ex)
                    }
                }
                reader.readAsText(file)
            } else {
                var reader = new window.FileReader()
                reader.onload = function (e) {
                    try{
                        vm._importData = {formData:new window.FormData(),callback:callback,failedCallback:failedCallback}
                        vm._importData.formData.append('datasource', new window.Blob([e.target.result],{type:fileFormat[2]}), file.name)
                        var req = new window.XMLHttpRequest()
                        req.open('POST', vm.env.gokartService + '/ogrinfo')
                        req.responseType = 'blob'
                        req.withCredentials = true
                        req.onload = function (event) {
                            try{
                                if (req.status >= 400) {
                                    var reader = new FileReader()
                                    reader.readAsText(req.response)
                                    reader.addEventListener("loadend",function(e){
                                        if (failedCallback) {
                                            failedCallback(e.target.result)
                                        } else {
                                            alert(e.target.result)
                                        }
                                    })
                                    delete vm._importData
                                } else {
                                    var reader = new FileReader()
                                    reader.readAsText(req.response)
                                    reader.addEventListener("loadend",function(e){
                                        if (!e.target.result) {
                                            if (failedCallback) failedCallback("No spatial data")
                                            return
                                        }
                                        var spatialInfo = JSON.parse(e.target.result)
                                        if (!spatialInfo || !spatialInfo["layerCount"]) {
                                            callback([],"geojson")
                                            return
                                        } else if(spatialInfo["layerCount"] === 1) {
                                            vm.importLayer(spatialInfo["datasources"][0]["datasource"],spatialInfo["datasources"][0]["layers"][0],true)
                                        } else {
                                            vm.spatialInfo = spatialInfo
                                            vm.spatialInfo.title = "Please choose the layer to import"
                                            vm.spatialInfo.upload = true
                                            $("#spatialInfoDialog").foundation('open')
                                        }
                                    })
                                }
                            } catch(ex) {
                                if (failedCallback) {
                                    failedCallback(ex.message || ex)
                                } else {
                                   alert(ex.message || ex)
                                }
                            }
                        }
                        req.send(vm._importData.formData)
                    }catch(ex) {
                        if (failedCallback) failedCallback(ex.message || ex)
                    }
                }
                reader.readAsArrayBuffer(file)
            }
        } catch (ex) {
            if (failedCallback) failedCallback(ex.message || ex)
        }
      },
      importLayer:function(datasource,selectedLayer,autoChoose){
        try {
            if (!this._importData) {
                alert("Import data is missing.")
                return
            }
            fileFormat = this.getFileFormat(datasource)
            if (!fileFormat) {
                var msg = "Unsupported file format(" + datasource + ")"
                if (this._importData.failedCallback) {
                    this._importData.failedCallback(msg)
                } else {
                    alert(msg)
                }
                return
            }
            if (!selectedLayer) {
                var msg = "Please choose import layer."
                if (this._importData.failedCallback) {
                    this._importData.failedCallback(msg)
                } else {
                    alert(msg)
                }
                return
            }
            if (selectedLayer.featureCount <= 0) {
                this._importData.callback([],"geojson")
                return
            }
            var vm = this
            var importData = vm._importData
            var layers = {
                default_geometry_type:"POINT",
                layer:selectedLayer.layer,
                srs:"EPSG:4326",
                sourcelayers:{
                    parameter:"datasource",
                    datasource:datasource,
                    layer:selectedLayer.layer,
                    //default_srs:"EPSG:4326"
                }
            }
            this._importData.formData.append('layers', JSON.stringify(layers))
            var req = new window.XMLHttpRequest()
            req.open('POST', this.env.gokartService + '/download/geojson')
            req.responseType = 'text'
            req.withCredentials = true
            req.onload = function (event) {
                try{
                    if (req.status >= 400) {
                        if (importData.failedCallback) {
                            importData.failedCallback(req.response)
                        } else {
                            alert(req.response)
                        }
                    } else {
                        var features = new ol.format.GeoJSON().readFeatures(req.response,{dataProjection:"EPSG:4326"})
                        if (features && features.length) {
                            importData.callback(features,fileFormat[0])
                        }
                    }
                } catch(ex) {
                    if (importData.failedCallback) {
                        importData.failedCallback(ex.message || ex)
                    } else {
                        alert(ex.message || ex)
                    }
                }
            }
            req.send(this._importData.formData)
        } catch(ex) {
            if (importData.failedCallback) {
                importData.failedCallback(ex.message || ex)
            } else {
                alert(ex.message || ex)
            }
        } finally {
            if (this._importData) {delete this._importData}
            if (!autoChoose) {
                $("#spatialInfoDialog").foundation('close')
            }
        }
      },
      // resize map to page dimensions (in mm) for printing, save layout
      prepareMapForPrinting: function () {
        var vm = this
        $('body').css('cursor', 'progress')
        if (this.printStatus.jobs <= 0) {
            //save overviewMap status and enable overviewMap if not enabled
            this.printStatus.overviewMap.enabled = this.map.isControlEnabled("overviewMap")
            this.printStatus.overviewMap.collapsed = this.map.getControl("overviewMap").getCollapsed()
            if (this.printStatus.overviewMap.collapsed) {
                this.map.getControl("overviewMap").setCollapsed(false)
            }
            if (!this.printStatus.overviewMap.enabled) {
                this.map.enableControl("overviewMap",true)
            }
        
            //no print job is processing, get the map size and scale for recovering.
            this.printStatus.oldLayout.size = this.olmap.getSize()
            this.printStatus.oldLayout.scale = this.$root.map.getScale()
            this.printStatus.oldLayout.extent = this.olmap.getView().calculateExtent(this.olmap.getSize())

            this.printStatus.dpmm = this.minDPI / this.mmPerInch

            //disable the interactions to prevent the user from operating the map
            this.printStatus.interactions = this.olmap.getInteractions().getArray().slice(0)
            $.each(this.printStatus.interactions,function(index,interact) {
                vm.olmap.removeInteraction(interact)
            })

            //disable the controls to prevent the user from operating the map
            this.printStatus.controls = []
            $.each(this.map.mapControls,function(key,control) {
                if (key === "overviewMap") {
                    //overviewMap has been processed, ignore here
                    return
                }
                if (control.enabled) {
                    vm.printStatus.controls.push(key)
                    vm.map.enableControl(key,false)
                }
            })


            this.printStatus.startTime = new Date()
        }

        this.printStatus.layout.width = this.paperSizes[this.paperSize][0]
        this.printStatus.layout.height = this.paperSizes[this.paperSize][1]
        //adjust the map for printing.
        if (this.settings.print.retainBoundingbox) {
            this.printStatus.layout.size = [this.printStatus.dpmm * this.printStatus.layout.width, this.printStatus.dpmm * this.printStatus.layout.height]
            this.olmap.setSize(this.printStatus.layout.size)
            this.olmap.getView().fit(this.printStatus.oldLayout.extent, this.olmap.getSize())
            this.printStatus.layout.scale = (this.settings.print.snapToFixedScale)?this.$root.map.getFixedScale():this.$root.map.getScale()
            if (this.settings.print.snapToFixedScale) {
                this.$root.map.setScale(this.printStatus.layout.scale)
            }
        } else {
            this.printStatus.layout.scale = (this.settings.print.snapToFixedScale)?this.$root.map.getFixedScale(this.printStatus.oldLayout.scale):this.printStatus.oldLayout.scale
            this.printStatus.layout.size = [this.printStatus.dpmm * this.printStatus.layout.width, this.printStatus.dpmm * this.printStatus.layout.height]
            this.olmap.setSize(this.printStatus.layout.size)
            if (this.settings.print.snapToFixedScale) {
                this.$root.map.setScale(this.printStatus.layout.scale)
            }
        }
        //extent is changed because the scale is adjusted to the closest fixed scale, recalculated the extent again
        this.printStatus.layout.extent = this.olmap.getView().calculateExtent(this.olmap.getSize())

        /*
        var  msg = (this.settings.print.retainBoundingbox)?"Retain boundingbox":"Retain scale"
        msg += (this.settings.print.snapToFixedScale)?" and snap to fixed scale":""
        msg += " : old extent = " + this.printStatus.oldLayout.extent + "\t new extent = " + this.printStatus.layout.extent + "\told scale = " + this.printStatus.oldLayout.scale + "\texpected scale = " + this.printStatus.layout.scale + "\t new scale=" + this.$root.map.getScale()  + "\t old size =" + this.printStatus.oldLayout.size + "\texpected size = " + this.printStatus.layout.size + "\t new size = " + this.olmap.getSize()
        console.log(msg)
        */

        this.printStatus.jobs = (this.printStatus.jobs >= 0)?(this.printStatus.jobs + 1):1
      },
      // restore map to viewport dimensions
      restoreMapFromPrinting: function () {
        var vm = this
        this.printStatus.jobs -= 1
        if (this.printStatus.jobs <= 0) {
            //all print jobs are done
            //restore overview map
            if (this.printStatus.overviewMap.collapsed) {
                this.map.getControl("overviewMap").setCollapsed(true)
            }
            if (!this.printStatus.overviewMap.enabled) {
                this.map.enableControl("overviewMap",false)
            }
            //restore the map size and map scale
            this.olmap.setSize(this.printStatus.oldLayout.size)
            this.$root.map.setScale(this.printStatus.oldLayout.scale)
            //restore the interactions
            $.each(this.printStatus.interactions,function(index,interact) {
                vm.olmap.addInteraction(interact)
            })
            //restore controls
            $.each(this.printStatus.controls,function(index,controlKey) {
                vm.map.enableControl(controlKey,true)
            })
            this.printStatus.endTime = new Date()
            $('body').css('cursor', 'default')
        }
      },
      // generate legend block, scale ruler is 40mm wide
      renderLegend: function (bucketKey) {
        var qrcanvas = bucketKey?kjua({text: this.env.s3Service + bucketKey, render: 'canvas', size: 100}):null
        return ['data:image/svg+xml;utf8,' + encodeURIComponent(this.$els.legendsvg.innerHTML), qrcanvas]
      },
      // POST a generated JPG to the gokart server backend to convert to GeoPDF
      blobGDAL: function (blob, name, format,bucketKey) {
        var vm = this
        var _func = function(legendData) {
            var formData = new window.FormData()
            formData.append('extent', vm.printStatus.layout.extent.join(' '))
            formData.append('jpg', blob, name + '.jpg')
            if (format === "pdf" && legendData)  {
                formData.append('legends', legendData, name + '.legend.pdf')
            }
            formData.append('dpi', Math.round(vm.printStatus.layout.canvasPxPerMM * 25.4))
            formData.append('title', vm.finalTitle)
            formData.append('author', vm.legendInfo().author)
            if (bucketKey) {
                formData.append('bucket_key',bucketKey)
            }
            var req = new window.XMLHttpRequest()
            req.open('POST', vm.env.gokartService + '/gdal/' + format)
            req.withCredentials = true
            req.responseType = 'blob'
            req.onload = function (event) {
              saveAs(req.response, name + '.' + format)
            }
            req.send(formData)
        }
        if (format === "pdf") {
            vm.layerlegends.getLegendBlob(true,true,function(legendData){
                _func(legendData)
            })
        } else {
            _func()
        }
      },
      // make a printable raster from the map
      print: function (format) {
        // rig the viewport to have printing dimensions
        this.prepareMapForPrinting()
        var timer
        var vm = this
        // wait until map is rendered before continuing
        var whiteout = vm.olmap.on('precompose', function (event) {
          var canvas = event.context.canvas
          var ctx = canvas.getContext('2d')
          ctx.beginPath()
          ctx.rect(0, 0, canvas.width, canvas.height)
          ctx.fillStyle = "white"
          ctx.fill()
        })
        var mainmap_composing = null
        var overviewmap_composing = null
        var canvas = null
        var overviewmap_canvas = null
        var postcomposeFunc = function() {
          timer && clearTimeout(timer)
          timer = setTimeout(function () {
            // remove composing watcher
            vm.olmap.unByKey(whiteout)
            vm.olmap.unByKey(mainmap_composing)
            vm.map.getControl("overviewMap").getOverviewMap().unByKey(overviewmap_composing)
            var ctx = canvas.getContext('2d')

            var img = new window.Image()
            var bucketKey = (format !== 'jpg')?vm.bucketKey:null
            var legend = vm.renderLegend((format === 'pdf')?bucketKey:null)
            var url = legend[0]
            var qrcanvas = legend[1]
            // wait until legend is rendered
            img.onerror = function (err) {
              window.alert(JSON.stringify(err))
              vm.restoreMapFromPrinting()
            }
            img.onload = function () {
              //draw overview map
              ctx.drawImage(overviewmap_canvas,canvas.width - overviewmap_canvas.width - 2,2,overviewmap_canvas.width ,overviewmap_canvas.height)
              //draw overview map rectangle
              var box = $(".ol-custom-overviewmap").find(".ol-overviewmap-box")
              if (box.length) {
                var width = box.width() * vm.displayResolution[0]
                var height = box.height() * vm.displayResolution[1]
                var x = box.parent().position().left * vm.displayResolution[0]
                var y = box.parent().position().top * vm.displayResolution[1]
                ctx.beginPath()
                ctx.rect(canvas.width - overviewmap_canvas.width - 2 + x,2 + y, width, height)
                ctx.strokeStyle = "red"
                ctx.lineWidth = 2
                ctx.stroke()
              }
              //draw overview map border
              ctx.beginPath()
              ctx.rect(canvas.width - overviewmap_canvas.width - 4, 0, overviewmap_canvas.width + 4, overviewmap_canvas.height + 4)
              ctx.strokeStyle = "black"
              ctx.lineWidth = 2
              ctx.stroke()
              // legend is 12cm wide
              vm.printStatus.layout.canvasPxPerMM = canvas.width / vm.printStatus.layout.width
              var height = 120 * vm.printStatus.layout.canvasPxPerMM * img.height / img.width
              ctx.drawImage(img, 0, 0, 120 * vm.printStatus.layout.canvasPxPerMM, height)

              var disclaimerImg = $("#map-disclaimer").get(0)
              height = disclaimerImg.height
              ctx.drawImage(disclaimerImg, 
                canvas.width - disclaimerImg.width, 
                canvas.height - height, 
                disclaimerImg.width, 
                height)
              //draw qr code
              if (qrcanvas) {
                  ctx.drawImage(qrcanvas, 2, canvas.height - qrcanvas.height - 2)
              }
              window.URL.revokeObjectURL(url)
              // generate a jpg copy of the canvas contents
              var filename = vm.finalTitle.replace(/ +/g, '_')
              canvas.toBlob(function (blob) {
                vm.restoreMapFromPrinting()
                if (format === 'jpg') {
                  saveAs(blob, filename + '.jpg')
                } else {
                  vm.blobGDAL(blob, filename, format,bucketKey)
                }
              }, 'image/jpeg', 0.9)
            }
            img.src = url
          // only output after 5 seconds of no tiles
          }, 5000)
        }
        mainmap_composing = vm.olmap.on('postcompose', function (event) {
            canvas = event.context.canvas
            if (!overviewmap_composing) {
                overviewmap_composing = vm.map.getControl("overviewMap").getOverviewMap().on('postcompose', function (event) {
                    overviewmap_canvas = event.context.canvas
                    postcomposeFunc()
                })
                vm.map.getControl("overviewMap").getOverviewMap().renderSync()
            }
        })
        vm.olmap.renderSync()
      },
      download: function (key) {
        if (key) {
          // download JSON blob from the state store
          localforage.getItem('sssStateStore').then(function (store) {
            if (key in store) {
              var blob = new window.Blob([JSON.stringify(store[key], null, 2)], {type: 'application/json;charset=utf-8'})
              saveAs(blob, key+'.sss')
            }
          })
        } else {
          // download JSON blob of the current state
          localforage.getItem('sssOfflineStore').then(function (store) {
            var blob = new window.Blob([JSON.stringify(store, null, 2)], {type: 'application/json;charset=utf-8'})
            saveAs(blob, 'sss_view_' +moment().format('YYYY-MM-DD-HHmm')+'.sss')
          })
        }
      },
      open: function (key) {
        // load the JSON blob from the state store into the offline store
        localforage.getItem('sssStateStore').then(function (store) {
          if (key in store) {
            localforage.setItem('sssOfflineStore', store[key]).then(function (v) {
              document.location.reload()
            })
          }
        })
      },
      remove: function (key) {
        // if there's a key matching in the state store, remove it
        var vm = this
        localforage.getItem('sssStateStore').then(function (store) {
          if (key in store) {
            delete store[key]
            vm.states = Object.keys(store)
            localforage.setItem('sssStateStore', store)
          }
        })
      },
      load: function () {
        // upload JSON into a state slot 
        var vm = this
        var reader = new window.FileReader()
        if (this.$els.statefile.files.length > 0) {
          var key = this.$els.statefile.files[0].name.split('.', 1)[0]
          reader.onload = function (e) {
            localforage.getItem('sssStateStore', function (err, value) {
              var store = {}
              if (value) {
                store = value
              }
              store[key] = JSON.parse(e.target.result)
              localforage.setItem('sssStateStore', store).then(function (v) {
                vm.states = Object.keys(store)
              })
            })
          }
          reader.readAsText(this.$els.statefile.files[0])
        }
      },
      saveStateButton: function () {
        var key = this.$els.savestatename.value
        if (!key) {
          key = moment().format('DD/MM/YYYY HH:mm')
        }
        this.saveState(key)
      },
      saveState: function (key) {
        var vm = this
        var store = this.$root.store
        // don't save if user is in tour
        if (vm.$root.touring) { return }

        // store attributes
        store.view.center = vm.olmap.getView().getCenter()
        store.view.scale = Math.round(vm.$root.map.getScale() * 1000)
        var activeLayers = vm.$root.active.activeLayers()
        if (activeLayers === false) {
          return
        }
        store.activeLayers = activeLayers || []
        store.annotations = JSON.parse(vm.$root.geojson.writeFeatures(vm.$root.annotations.features.getArray()))

        // save in the offline store
        localforage.setItem('sssOfflineStore', vm.$root.persistentData).then(function (value) {
          vm.$root.saved = moment().toLocaleString()
        })

        // if key is defined, store in state store
        if (key) {
          localforage.getItem('sssStateStore', function (err, value) {
            var states = {}
            if (value) {
              states = value
            }
            states[key] = vm.$root.persistentData
            localforage.setItem('sssStateStore', states).then(function (value) {
              vm.states = Object.keys(states)
            })
            
          })
        }
      }
    },
    ready: function () {
      var vm = this
      var exportStatus = vm.loading.register("export","Export Component")

      exportStatus.phaseBegin("initialize",10,"Initialize")
      this._filename_re = new RegExp("filename=[\'\"](.+)[\'\"]")
      this._fileformats = [
        ["geojson",".geojson","application/vnd.geo+json"],
        ["shp",".shp","application/shp"],
        ["json",".geojson","application/json"],
        ["gpx",".gpx","application/gpx+xml"],
        ["gpkg",".gpkg","application/x-sqlite3"],
        ["7zip",".7z","application/x-7z-compressed"],
        ["zip",".zip","application/zip"],
        ["tar",".tar","application/x-tar"],
        ["tar.gz",".tar.gz","application/x-gtar-compressed"],
        ["tar.bz",".tar.bz","application/gzip"],
        ["tar.xz",".tar.xz","application/gzip"],
      ]


      $("#spatialInfoDialog").on("closed.zf.reveal",function(){
          if (vm._importData) {
            if (vm._importData.failedCallback) vm._importData.failedCallback("Cancelled")
            delete vm._importData
          }
      })
      exportStatus.phaseEnd("initialize")
      exportStatus.phaseBegin("gk-init",80,"Listen 'gk-init' event",true,true)
      this.$on('gk-init', function () {
        exportStatus.phaseEnd("gk-init")
        exportStatus.phaseBegin("load_states",10,"Load states from file system",true,false)
        // save state every render
        vm.olmap.on('postrender', global.debounce(function (ev) {vm.saveState()}, 1000, true))
        var stateStore = localforage.getItem('sssStateStore', function (err, value) {
          if (value) {
            vm.states = Object.keys(value)
          }
        })
        exportStatus.phaseEnd("load_states")
      })
    }
  }
</script>
