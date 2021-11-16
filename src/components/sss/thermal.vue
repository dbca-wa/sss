<template>
  <div class="tabs-panel" id="menu-tab-thermal">
    <div class="row collapse">
      <div class="columns">
        <ul class="tabs" id="thermal-tabs">
          <li class="tabs-title is-active"><a class="label" aria-selected="true">Thermal Imaging</a></li>
        </ul>
      </div>
    </div>
    <div class="row collapse" id="thermal-tab-panels">
      <div class="columns">
        <div class="tabs-content vertical" data-tabs-content="thermal-tabs">
          <div id="thermal-list-tab" class="tabs-panel is-active" v-cloak>
            <div id="thermal-list-controller-container">
            <div class="tool-slice row collapse">
              <div class="small-12">
				<div class="expanded button-group">
				  <a v-for="t in tools" class="button button-tool" v-bind:class="{'selected': t.name == annotations.tool.name}"
					@click="annotations.setTool(t)" v-bind:title="t.label" style="font-size: 0.9rem;">{{{ annotations.icon(t) }}} {{t.showName?t.label:""}}</a>
				</div>	
              </div>
            </div>
            <div class="row">
              <div class="small-9 columns" >
                <div class="row">
                  <div class="switch tiny">
                    <input class="switch-input" id="thermalInViewport" type="checkbox" v-bind:checked="viewportOnly" @change="toggleViewportOnly" />
                    <label class="switch-paddle" for="thermalInViewport">
                      <span class="show-for-sr">Viewport thermal imagery only</span>
                    </label>
                  </div>
                  <label for="thermalInViewport" class="side-label">Restrict to viewport ({{extentFeaturesSize}}/{{featurelistSize}})</label>
                </div>
              </div>
		    </div>
			<div class="row">
              <div class="small-9 columns" >
                <div class="row">
                  <div class="switch tiny">
                    <input class="switch-input" id="showFlightFootprint" type="checkbox" v-bind:checked="showFlightFootprint" @change="toggleFlightFootprint" />
                    <label class="switch-paddle" for="showFlightFootprint">
                      <span class="show-for-sr">Show Flight Footprint</span>
                    </label>
                  </div>
                  <label for="showFlightFootprint" class="side-label">Show flight footprint</label>
                </div>
              </div>
		    </div>
			<div class="row">
              <div class="small-9 columns" >
                <div class="row">
                  <div class="switch tiny">
                    <input class="switch-input" id="mosaicRawImage" type="checkbox" v-bind:checked="showRawImageMosaic" @change="toggleRawImageMosaic" />
                    <label class="switch-paddle" for="mosaicRawImage">
                      <span class="show-for-sr">Mosaic raw image</span>
                    </label>
                  </div>
                  <label for="mosaicRawImage" class="side-label">Show mosaic image</label>
                </div>
              </div>
		    </div>
			<div class="row">
              <div class="small-9 columns" >
                <div class="row">
                  <div class="switch tiny">
                    <input class="switch-input" id="dateRange" type="checkbox" v-model="showDateRange" @change="toggleDateRange" />
                    <label class="switch-paddle" for="dateRange">
                      <span class="show-for-sr">Date range</span>
                    </label>
                  </div>
                  <label v-if="showDateRange" for="dateRange" class="side-label">Date range (on)</label>
				  <label v-else for="dateRange" class="side-label">Date range (off)</label>
                </div>
              </div>
		    </div>
			<div v-if="!showDateRange" class="row">
              <div class="small-9 columns" >
                <div class="row">
                    <label>Date:
						<input type="date" class="date" id="singleDate" v-model="thermalSingleDate">
					</label>
                </div>
              </div>
		    </div>
            <div id="date-range-panel" v-show="showDateRange">
              <div class="row collapse tool-slice">
                <div class="small-2">
                  <label for="dateRangeFrom">From:</label>
                </div>
                <div class="small-5">
                  <input type="text" id="thermalFromDate" class="span2" @click="changeThermalFromDate" v-model="thermalFromDate" placeholder="YYYY-MM-DD HH:mm"  v-bind:disabled="thermalDateRange !== '-1'"  readonly></input>
				  <!--input type="text" id="thermalFromDate" class="span2" v-model="thermalFromDate" placeholder="YYYY-MM-DD HH:mm"  v-bind:disabled="thermalDateRange !== '-1'"  readonly></input-->
                </div>
                <div class="small-5">
                  <select name="select" v-model="thermalDateRange" >
                      <!--option value="21001">Last hour</option--> 
					  <option value="21004">Last 4 hours</option> 
					   <option value="21008">Last 8 hours</option> 
					  <option value="21024">Last 24 hours</option> 
					  <option value="31002">Last 48 hours</option> 
                      <option value="31003">Last 3 days</option> 
                      <option value="31005">Last 5 days</option> 
                      <option value="31007">Last 7 days</option> 
                      <option value="31030">Last 30 days</option> 
                      <option value="-1">User Defined</option> 
                </select>
                </div>
              </div>
              <div class="row collapse tool-slice">
                <div class="small-2">
                  <label for="dateRangeTo">To:</label>
                </div>
                <div class="small-5">
                  <input type="text" id="thermalToDate" class="span2" v-model="thermalToDate" placeholder="YYYY-MM-DD HH:mm"  v-bind:disabled="thermalDateRange !== '-1'"  readonly></input>
                </div>
              </div>
            </div>
			<div class="row">
              <div class="small-9 columns" >
                <div class="row">
				</div>
			  </div>
			</div>
			<div class="row">
			</div>
			<div class="row">
              <div class="small-9 columns" >
                <div class="row">
                    <a class="button" @click="loadHotspotLayers" title="Show Hotspots">Show Hotspots </a>
                </div>
              </div>
		    </div>
			<!--div class="row">
              <div class="small-9 columns" >
                <div class="row">
                    <a class="button" @click="showEmailComposerPanel" title="Show Email Composer"><i class="fa fa-envelope" aria-hidden="true" v-model="mdlShowEmailComposer"></i> Email </a>
                </div>
              </div>
		    </div>
			<div v-show="showEmailComposer" id="emailPanel" >
				<form id="emailForm">
				<p>Email to
				<select id="emailRecipient">
				</select>
				
   				</p>
				<div>
				<textarea id="emailText" placeholder="Type message here" style="width:360px; height:190px; color:#000; opacity:1"></textarea>
				<p></p>
				</div>
				<div v-show="showEmailComposer">
				<input v-on:click="sendEmail" type="button" id="sendEmail" style="background-color:#39e" value="Send">
				<input v-on:click="showEmailComposer = !showEmailComposer" type="reset" id="cancelEmail" style="background-color:#39e" value="Cancel">
				</div>
				</form>
			</div-->
        </div>
		
		<div id="hotspot-list" class="layers-flexibleframe scroller" style="margin-left:-15px; margin-right:-15px;">
              <!--template v-for="f in featurelist" track-by="get('hotspot_no')"-->
			  <template v-for="f in featurelist" >
			    <div v-if="showFeature(f)" class="row feature-row" v-bind:class="{\'feature-selected\': isFeatureSelected(f) }" @click="toggleSelect(f)"> 
			    <button class="collapsible" v-on:click="toggleImageList">{{f.get('flight_datetime')}} {{f.get('hotspot_no')}}</button>
				<!--button class="collapsible" @click="toggleImageList(event, f.get('flight_datetime'), f.get('hotspot_no'))">{{f.get('flight_datetime')}} {{f.get('hotspot_no')}}</button-->
			    <div class="showImages">
				  <template v-for="imageFile in f.shortImages" >
				  <!--a class="button" @click="showImage(imageFile)" id={{imageFile}}><i class="fa fa-camera"></i>View image {{imageFile}}</a-->
				  <!--button v-bind:id="'img_' + imageFile" class="button"  v-on:click="showImage(imageFile)" ><i class="fa fa-camera"></i>View image {{imageFile}}</button-->
				  <button v-bind:id="'img_' + imageFile" v-bind:class=["button"] v-on:click="changeButtons" @click="showImage(f.get('flight_datetime'), f.get('hotspot_no'), imageFile, $index, $parent.$index)">
					<i class="fa fa-camera"></i>        image {{imageFile}}</button>
				  <!--button v-bind:id="'img_' + imageFile" v-bind:class=["button"] @click="showImage(f.get('flight_datetime'), imageFile)" ><i class="fa fa-camera"></i>View image {{imageFile}}</button-->
				  <!--template>
					  <div class="images" v-for="imageFile in f.shortImages" :key="imageFile">
						<button class="favorite" v-on:click="imageFile.favorited = !imageFile.favorited">
							<i v-bind:class="[{ 'red' : imageFile.favorited }, 'fa fa-camera']">View image {{imageFile}}</i>
						</button>           
					  </div-->
				  </template>
				</div>
				</div>
			  </template>
		</div>
      </div>
    </div>
  </div>
</template>

<style>
#thermalFromDate, #thermalToDate, #singleDate {
    cursor:pointer}
	
/* Style the button that is used to open and close the collapsible content */
.collapsible {
  background-color: #eee;
  color: #444;
  cursor: pointer;
  padding: 10px;
  width: 100%;
  border: 1px solid #009;
  text-align: left;
  outline: none;
  font-size: 15px;
}

/* Add a background color to the button if it is clicked on (add the .active class with JS), and when you move the mouse over it (hover) */
.active, .collapsible:hover {
  background-color: #ccc;
}

/* Style the collapsible content. Note: hidden by default */
.showImages {
  padding: 0 1px;
  display: none;
  overflow: hidden;
  background-color: #f1f1f1;
}

/*Button colours*/
.red {
       background-color: red;
   }
.blue {
       background-color: blue;
   }
</style>


<script>
  import { ol, moment, Msal, nodemailer, postmark, kjua, qs, axios, utils } from 'src/vendor.js'		//kjua is here for QR codes
  export default {
    store: {
        //showFootprint:'settings.showFlightFootprint',
        //showMosaic:'settings.showRawImageMosaic',
		//showDateRange:'settings.showDateRange',
		hotspotLabels: true,	//boolean defining whether to show labels (can be later changed to use settings.
        viewportOnly: 'settings.viewportOnly',
        hintsHeight: 'layout.hintsHeight',
        screenHeight: 'layout.screenHeight',
        leftPanelHeadHeight: 'layout.leftPanelHeadHeight',
        activeMenu: 'activeMenu',
        whoami: 'whoami'
    },
    data: function () {
      return {
	    clicked: false,
        showFlightFootprint: false,
		showRawImageMosaic: false,
		showDateRange: false,
		showEmailComposer: false,
		flights: [],
        //clippedOnly: false,
        search: '',
        groupFilter: '',
        tools: [],
        thermalDateRange: '21024',
        features: new ol.Collection(),
        extentFeaturesSize: 0,
		footprints: new ol.Collection(),
		imagesShow: {},
		emailList: [],
        featureLabelDisabled: false,
        clippedFeatures: [],
        thermalFromDate: '',
        thermalToDate: '',
		//dateRange: '',
        revision: 1,
        selectRevision: 1,
		extent: null
      }
    },
    computed: {
      map: function () { return this.$root.map },
      env: function () { return this.$root.env },
      active: function () { return this.$root.active },
      annotations: function () { return this.$root.$refs.app.$refs.annotations },
      info: function () { return this.$root.info },
      systemsetting: function () { return this.$root.systemsetting },
      catalogue: function () { return this.$root.catalogue },
      export: function () { return this.$root.export },
      loading: function () { return this.$root.loading },
      utils: function () { return this.$root.utils },
      selectedFeatures: function () {
        return this.annotations.getSelectedFeatures("thermal")
      },
      selectedFeaturesSize: function () {
        return this.selectRevision && this.selectedFeatures.getLength()
      },
      /*queryThermalDateRangeDisabled: function() {
        return !(this.selectRevision && this.selectedFeatures && this.selectedFeatures.getLength() && this.thermalFromDate !== "")
      },*/
	  hotspotLayer: function() {
        return this.$root.catalogue.getLayer("hotspots:hotspot_centroids")
      },
      hotspotMapLayer: function() {
        return this.$root.map?this.$root.map.getMapLayer(this.hotspotLayer):undefined
      },
	  //based on the much more complex bfrsStyleFunc, may be overcomplex
	  hotspotStyleFunc: function() {
		if (!this._hotspotStyleFunc) {
            this._hotspotStyleFunc = function () {
                //var vm = this
				var labelStyleFunc = function(){
					return new ol.style.Style({
						text: new ol.style.Text({
						  //text: f.get('hotspot_no'),
						  text: 'o',
						  font: '24px Calibri,sans-serif',
						  fill: new ol.style.Fill({ color: '#fff' }),
						  stroke: new ol.style.Stroke({color: '#fff', width: 2})
						}),
						image : new ol.style.Circle({
							fill: new ol.style.Fill({color: [0, 0, 255]}),
							radius: 12
						})
					})
				}
				return function(res) {
					var feat = this
					var labelStyle = labelStyleFunc.call(feat, res)
					return labelStyle
				}
			}.call(this)
        }
        return this._hotspotStyleFunc
      },
	  flightFootprintLayer: function() {
        return this.$root.catalogue.getLayer("hotspots:hotspot_flight_footprints")
      },
	  
      flightFootprintMapLayer: function() {
        return this.$root.map?this.$root.map.getMapLayer(this.flightFootprintLayer):undefined
      },
	  
	  footprintStyle: function() {
		return newfootprintStyle = new ol.style.Style({
			stroke: new ol.style.Stroke({
				width: 5,
				color: [0, 0, 255]
			})
		})
	  },
	  
	  postmark_client: function(){
		  var postmark = require('postmark')
		
		  var client = new postmark.Client("c5abeaf7-cf27-4539-8f8a-790786320f30")
		  //var client = new postmark.ServerClient("c5abeaf7-cf27-4539-8f8a-790786320f30")
		  return client
	  },

      featurelist: function() {
        try {
            //return this.revision && this._featurelist.getArray().sort(function(a, b){return a.get('hotspot_no') - b.get('hotspot_no')})
			return this.revision && this._featurelist.getArray().reverse()
        } catch (ex) {
            return [];
        }
      },
	  
      featurelistSize: function() {
        try {
            return this.revision && this._featurelist.getLength()
        } catch (ex) {
            return 0;
        }
      },
	  
      hasFeatureFilter: function () {		//prob replace with a hasDateFilter function based on whether a date or date range is specified
        return (this.search && this.search.trim())?true:false
      },

    },
    watch:{
      thermalDateRange: function(newValue, oldValue) {
        this.changeThermalDateRange()
      },
      thermalFromDate: function(newValue, oldValue) {
        this.changeThermalFromDate()
      },
      thermalToDate: function(newValue, oldValue) {
        this.changeThermalToDate()
      }
    },
    
	methods: {
      adjustHeight_OLD: function() {
        if (this.activeMenu === "thermal") {
            $("#hotspot-list").height(this.screenHeight - this.leftPanelHeadHeight - 41 - $("#hotspot-list-controller-container").height() - this.hintsHeight)
        }
      },
	  
	  adjustHeight: function() {
		"thermal"===this.activeMenu&&$("#hotspot-list").height(this.screenHeight-this.leftPanelHeadHeight-$("#hotspot-list-controller-container").height()-50)
	  },
	  
      changeThermalDateRange: function() {
        if (this.thermalDateRange === "-1") {
            //customized
           if (!this.thermalFromDate) {
                //fromDate is null, set to default value "Last 24 hours"
                var range = utils.getDateRange(21024, "YYYY-MM-DD HH:mm")
                this.thermalFromDate = range[0] || ""
                if ((range[1] || "") !== this.thermalToDate) {
                    this.thermalToDate = range[1] || ""
                } else {
                    this.changeThermalToDate()
                }
            } else {
                this.changeThermalFromDate()
                this.changeThermalToDate()
            }
        } else { 
            var range = utils.getDateRange(this.thermalDateRange ,"YYYY-MM-DD HH:mm")
            this.thermalFromDate = range[0] || ""
            this.thermalToDate = range[1] || ""
        }
      },
	  
      changeThermalFromDate: function() {
        if (this.thermalDateRange !== "-1") {
            return
        }
        if (!this._thermalToDatePicker) return
		try {
            if (this.thermalFromDate === "") {
                this._thermalToDatePicker.setStartDate(moment().subtract(10, "years").format("YYYY-MM-DD") + " 00:00")
            } else {
                this._thermalToDatePicker.setStartDate(moment(this.thermalFromDate,"YYYY-MM-DD HH:mm").format("YYYY-MM-DD") + " 00:00")
            }
        } catch(ex) {
        }
      },

      changeThermalToDate: function() {
        if (this.thermalDateRange !== "-1") {
            //not in editing mode
            return
        }
        if (!this._thermalFromDatePicker) return	
			
        try {
            if (this.thermalToDate === "") {
                this._thermalFromDatePicker.setEndDate(moment().format("YYYY-MM-DD") + " 23:59")
            } else {
                this._thermalFromDatePicker.setEndDate(this.thermalToDate)
            }
        } catch(ex) {
        }
      },
	  
	  thermalSingleDateFilter: function() {
		if (this.showFlightFootprint){
			alert("showFlightFootprint")
		}
		else {
			alert("DON'T showFlightFootprint")
		}
		if (this.showMosaicRawImage){
			alert("showMosaicRawImage")
		}
		else {
			alert("DON'T showMosaicRawImage")
		}
	  },
	  
      /*thermalDateRangeFilter: function() {
        if (this.thermalDateRange !== "-1") {
            //in predefined range, reset the thermalFromDate and thermalToDate
            this.changeThermalDateRange()
        }
        var startDate = (this.thermalFromDate)?moment(this.thermalFromDate,"YYYY-MM-DD HH:mm", true):null
        if (startDate && !startDate.isValid()) {
            throw "From date is under changing."
        }

        var endDate = (this.thermalToDate && this.thermalToDate < moment().format("YYYY-MM-DD HH:mm"))?moment(this.thermalToDate,"YYYY-MM-DD HH:mm", true):null
        if (endDate && !endDate.isValid()) {
            throw "To date is under changing."
        }

        if (startDate) {
            if (endDate) {
                if (startDate >= endDate) {
                    throw "Start date must be earlier than end date."
                }
                return "seen BETWEEN '" + startDate.utc().format("YYYY-MM-DDTHH:mm:ssZ") + "' AND '" + utils.nextDate(endDate,"YYYY-MM-DD HH:mm").utc().format("YYYY-MM-DDTHH:mm:ssZ") + "'"
            } else {
                return "seen >= '" + startDate.utc().format("YYYY-MM-DDTHH:mm:ssZ") + "'"
            }
        } else if (endDate) {
            return "seen < '" + utils.nextDate(endDate, "YYYY-MM-DD HH:mm").utc().format("YYYY-MM-DDTHH:mm:ssZ") + "'"
        } else {
            throw "Please specify date range."
        }
      },*/
	  
	  hasDateFilter: function() {
	    var dateFilterSpecified = false
		if (this.showDateRange || this.thermalSingleDate != undefined) {dateFilterSpecified = true}
		return dateFilterSpecified
	  },

	  showFeature:function(feat){return this.revision&&(!this.viewportOnly||feat.inViewport)},

      scrollToSelected: function() {
        if (this.selectedFeatures.getLength() === 0) return
        var index = -1

        for (var i = 0;i < this._featurelist.getLength() ;i++) {
            if (this.showFeature(this._featurelist.item(i))) {
                index += 1
                if (this._featurelist.item(i) === this.selectedFeatures.item(0)) {
                    break
                }
            }
        }
        if (index >= 0) {
            var listElement = document.getElementById("hotspot-list")
            if (index < listElement.children.length) {
                listElement.scrollTop += listElement.children[index].getBoundingClientRect().top - listElement.getBoundingClientRect().top
            }
        }
      },
	  
      toggleSelect: function (f) {
        if (this.isFeatureSelected(f)) {
          this.selectedFeatures.remove(f)
        } else {
          this.selectedFeatures.push(f)
        }
      },
	  
      toggleViewportOnly: function() {
        this.viewportOnly = !this.viewportOnly
        this.export.saveState()
      },
	  
      toggleFlightFootprint: function() {
		this.showFlightFootprint = !this.showFlightFootprint
        this.export.saveState()
		var vm = this
		var map = this.$root.map			
		// Check if footprints layer already loaded
		var footprintsLoaded = false
		var hotspotsLoaded = false
		map.olmap.getLayers().forEach(function (layer) {
			if (layer.get('name') === 'Flight footprints') {
					footprintsLoaded = true
			}
			if (layer.get('name') === 'Hotspots') {
					hotspotsLoaded = true
			}
		})
		if (hotspotsLoaded && this.showFlightFootprint) {
			this.flightFootprintLayer.style = this.footprintStyle
			var footprintOLLayer = map['createWFSLayer'](this.flightFootprintLayer)
			map.olmap.addLayer(footprintOLLayer)
			footprintOLLayer.refresh()
		}
		else if (hotspotsLoaded && !this.showFlightFootprint) {
			map.olmap.getLayers().forEach(function (layer) {
				if (layer.get('name') === 'Flight footprints') {
						map.olmap.removeLayer(layer)
				}
			})
		}
      },
	  
	  toggleRawImageMosaic: function() {
		this.showRawImageMosaic = !this.showRawImageMosaic
        this.export.saveState()
		var vm = this
		var map = this.$root.map			
		// Check if mosaic layer already loaded
		var mosaicLoaded = false
		var hotspotsLoaded = false
		map.olmap.getLayers().forEach(function (layer) {
			if (layer.get('name') === 'Flight mosaics') {
					mosaicLoaded = true
			}
			if (layer.get('name') === 'Hotspots') {
					mosaicPosition = map.olmap.getLayers().getArray().findIndex(function(l){return l === layer})
					hotspotsLoaded = true
			}
		})
		if (hotspotsLoaded && this.showRawImageMosaic) {
			/*var mosaicLayers = []
			if (!this.hasDateFilter()) {mosaicLayers.push('vrt-test')}
			map['createWMSLayer'](mosaicLayers, position)*/
			var dateInfo = this.getDateInfoForMosaics(vm)
			map['createWMSLayer'](mosaicPosition, dateInfo)
		}
		else if (hotspotsLoaded && !this.showRawImageMosaic) {
			map.olmap.getLayers().forEach(function (layer) {
				if (layer.get('name') === 'Flight mosaics') {
						map.olmap.removeLayer(layer)
				}
			})
		}
      },
	  
	  toggleDateRange: function(){
		this.thermalSingleDate = undefined
		if (!this.showDateRange) {
		    this.thermalFromDate = undefined, this.thermalToDate = undefined
		}	
	  },
	  
      isFeatureSelected: function(f) {
        return this.selectedFeatures.getArray().findIndex(function(o){return f === o}) >= 0
      },
	  
      updateCQLFilter: function (wait) {
	  //alert('625: updateCQLFilter')
        var vm = this
        if (!vm._updateCQLFilter) {
            vm._updateCQLFilter = debounce(function(updateType){
                try {
                    var cql_filter = ""
                    if (cql_filter === vm.hotspotLayer.cql_filter) {
                        //filter not changed
                        return
                    }
                    vm.hotspotLayer.cql_filter = cql_filter
                    //clear device filter or change other filter
                    vm.hotspotMapLayer.set('updated', moment().toLocaleString())
					vm.hotspotMapLayer.getSource().loadSource('query')
                } catch(ex) {
                    alert(ex)
                }
            }, 500)
        }
        if (wait === 0) {
            vm._updateCQLFilter.call({wait:1})
        } else if (wait === undefined || wait === null) {
            vm._updateCQLFilter()
        } else {
            vm._updateCQLFilter.call({wait:wait})
        }
      },

	  getDateInfoForMosaics: function(vm) {
		var dateInfo = []
		if (vm.showDateRange) {
			var start = vm.thermalFromDate.replace(/-/g, "").replace(' ', '_').replace(':', '')
			var end = vm.thermalToDate.replace(/-/g, "").replace(' ', '_').replace(':', '')
			dateInfo.push(start)
			if (end==="") {dateInfo.push("now")}
			else {dateInfo.push(end)}
		}
		else if (vm.thermalSingleDate != undefined) {
			var singleDate = vm.thermalSingleDate.replace(/-/g, "")
			dateInfo.push(singleDate)
		}
		return dateInfo
	  },
	  
      removeImages_OLD: function(){
		var hotspotButtons = document.getElementById("hotspot-list").querySelectorAll(".collapsible")
		hotspotButtons.forEach(function(button){
			var imageListContent = button.nextElementSibling
			if (imageListContent.style.display === "block") {
				imageListContent.style.display = "none"
			}
		})
				
				var map = this.$root.map
				// Close any single images for this hotspot
				map.olmap.getLayers().forEach(function (layer) {
					if (layer.get('name').startsWith('Hotspot image ')) {
						map.olmap.removeLayer(layer)
					}
				})
		
		return
	  },
	   
	  removeImages:function(){
		var hotspotButtons=(this.$root.map,document.getElementById("hotspot-list").querySelectorAll(".collapsible"))
		var i = 0
		return hotspotButtons.forEach(function(button){
			"block"===button.nextElementSibling.style.display&&(setTimeout(function(){button.click()},10),i+=1)})
			, i},
	  
	  loadHotspotLayers_OLD: function() {
		var vm = this
	    var map = vm.$root.map
		this.imagesShow = {}
		var layersToRemove = []
		
		map.olmap.getLayers().forEach(function (layer) {
			/*if (layer.get('name') === 'Hotspots') {
				map.olmap.removeLayer(layer)
			}
			if (layer.get('name') === 'Flight footprints') {
				map.olmap.removeLayer(layer)
			}*/
			//alert("698: " + layer.get('name'))
			if (layer.get('name') === 'Flight mosaics') {
				map.olmap.removeLayer(layer)
				//layersToRemove.push(layer)
			}
			if (layer.get('name').startsWith('Hotspot image')) {
				//map.olmap.removeLayer(layer)
				layersToRemove.push(layer)
			}
		})

		if (layersToRemove.length > 0) {
			alert('You need to remove the images before you can look at a new set of hotspots.  Close images by clicking on the names of any hotspots in the list with an image ON')
			return
		}

		var mosaicPosition = map.olmap.getLayers().getArray().length - 1
	
		if (vm.showFlightFootprint){
			vm.flightFootprintLayer.style = vm.footprintStyle
			var footprintOLLayer = map['createWFSLayer'](vm.flightFootprintLayer)
			map.olmap.addLayer(footprintOLLayer)
			footprintOLLayer.refresh()
		}
		
	    // enable hotspot layer, if disabled
        if (!vm.hotspotMapLayer) {
            vm.catalogue.onLayerChange(vm.hotspotLayer, true)
        } else if (vm.active.isHidden(vm.hotspotMapLayer)) {
            vm.active.toggleHidden(vm.hotspotMapLayer)
        }
		else {
			//switch off then on, should apply new filter if any
			vm.hotspotMapLayer.getSource().loadSource('query')
			vm.catalogue.onLayerChange(vm.hotspotLayer, false)
			vm.catalogue.onLayerChange(vm.hotspotLayer, true)
			//vm.hotspotMapLayer.refresh()
			//vm.hotspotMapLayer.getSource().changed()
			//vm.catalogue.onLayerChange(vm.hotspotLayer, true)
			//vm.hotspotMapLayer.getSource().loadSource('query')
			//this.catalogue.onLayerChange(this.flightFootprintLayer, false)
			//this.catalogue.onLayerChange(this.flightFootprintLayer, true)
		}
		
		if (vm.showRawImageMosaic){
			var dateInfo = this.getDateInfoForMosaics(vm)
			map['createWMSLayer'](mosaicPosition, dateInfo)
		}
	  },

	  loadHotspotLayers:function(){
		var _this = this
		var vm = this
		var map = vm.$root.map
		var imagesRemoved = vm.removeImages();
		
		timeout = 10 * imagesRemoved
		setTimeout(function(){
			map.olmap.getLayers().getArray().slice().forEach(function(layer){
				"Flight footprints"===layer.get("name")&&map.olmap.removeLayer(layer),"Flight mosaics"===layer.get("name")&&map.olmap.removeLayer(layer)
		})
		var mosaicPosition=map.olmap.getLayers().getArray().length-1
		if (vm.showFlightFootprint){
			vm.flightFootprintLayer.style = vm.footprintStyle
			var footprintOLLayer = map.createWFSLayer(vm.flightFootprintLayer)
			map.olmap.addLayer(footprintOLLayer)
			footprintOLLayer.refresh()}
		if(vm.hotspotMapLayer?vm.active.isHidden(vm.hotspotMapLayer)?vm.active.toggleHidden(vm.hotspotMapLayer):(vm.catalogue.onLayerChange(vm.hotspotLayer,!1),vm.catalogue.onLayerChange(vm.hotspotLayer,!0)):vm.catalogue.onLayerChange(vm.hotspotLayer,!0),vm.showRawImageMosaic){
			var dateInfo=_this.getDateInfoForMosaics(vm)
			map.createWMSLayer(mosaicPosition,dateInfo)}},timeout)},
		
      featureFilter: function (f) {
        var search = this.search?this.search.toLowerCase().trim():""
        var found = !search || this.fields.some(function (key) {
          return ('' + f.get(key)).toLowerCase().indexOf(search) > -1
        })
        return found
      },

	  featureOrderOLD: function (a, b) {
        var as = a.get('hotspot_no')
        var bs = b.get('hotspot_no')
        if (as < bs) {
          return 1
        } else if (as > bs) {
          return -1
        }
        return 0
      },
	  
	  featureOrder: function (a, b) {
        var as = [a.get('flight_datetime'), a.get('hotspot_no')]
        var bs = [b.get('flight_datetime'), b.get('hotspot_no')]
        if (as[0] < bs[0]) {
          return 1
        } else if (as[0] > bs[0]) {
          return -1
        }
        else  if (as[1] < bs[1]) {
          return 1
		} else if (as[1] > bs[1]) {
          return -1
        }
		return 0
      },
	  
      //filter the loaded hotspot features
      updateFeatureFilter: function(wait) {
        var vm = this
		vm.flights = []
        if (!vm._updateFeatureFilter) {
            vm._updateFeatureFilter = debounce(function(){
                var list = vm.features.getArray()
				//var list = vm.features.getArray().sort(vm.featureOrder)
                if (vm.hasFeatureFilter) {
                    list = list.filter(vm.featureFilter)
                }
				if (vm.hasDateFilter()) {
					if (vm.thermalSingleDate != undefined) {
						var singleDate = vm.thermalSingleDate.replace(/-/g, "")
						list = list.filter(
							function(feature) {
								return feature.get('flight_datetime').startsWith(singleDate)
							}
						)
					}
					else if (vm.showDateRange) {
						var start = vm.thermalFromDate.replace(/-/g, "").replace(' ', '_').replace(':', '')
						var end = vm.thermalToDate.replace(/-/g, "").replace(' ', '_').replace(':', '')
						if (end==="") {
							list = list.filter(
								function(feature) {
									return feature.get('flight_datetime') > start
								}
							)
						}
						else {list = list.filter(
								function(feature) {
									return feature.get('flight_datetime') > start && feature.get('flight_datetime') < end
								}
							)
						}
					}
					if (list.length == 0) {
						alert('No hotspots recorded in that period')
						return
					}

					list.forEach(function(feature){
						var flight = feature.get('flight_datetime')
						if (! vm.flights.includes(flight)) {
							vm.flights.push(flight)
						}
					})
				}

                vm._featurelist.clear()
                vm._featurelist.extend(list)
				
				//get extent of filtered features and set extent of map to this
				if (!this.showFlightFootprint) {
					var extent = list[0].getGeometry().getExtent()	//.slice(0)
					list.forEach(function(feature){ ol.extent.extend(extent,feature.getGeometry().getExtent())})
					vm.$root.map.olmap.getView().fit(extent, vm.$root.map.olmap.getSize())
				}
				
                vm.setExtentFeatureSize()
                if (vm.selectedFeatures.getLength() > 0) {
                    if (list.length === 0) {
                        vm.selectedFeatures.clear()
                        vm.clippedFeatures.splice(0, vm.clippedFeatures.length)
                    } else {
                        for(var index = vm.selectedFeatures.getLength() - 1; index >= 0; index--) {
                            if (!list.find(function(f){return f === vm.selectedFeatures.item(index)})) {
                                vm.selectedFeatures.removeAt(index)
                            }
                        }
                    }
                }
                vm.revision += 1;
            }, 500)
        }
        if (wait === 0) {
            vm._updateFeatureFilter.call({wait:1})
        } else if (wait === undefined || wait === null){
            vm._updateFeatureFilter()
        } else {
            vm._updateFeatureFilter.call({wait:wait})
        }
      },
	  
	//filter the loaded footprints
      updateFootprintFilter: function(wait) {
        var vm = this
        if (!vm._updateFootprintFilter) {
            vm._updateFootprintFilter = debounce(function(){
                var list = vm.footprints.getArray()
                if (vm.hasFeatureFilter) {
                    list = list.filter(vm.featureFilter)
                }
				if (vm.hasDateFilter()) {
					if (vm.thermalSingleDate != undefined) {
						var singleDate = vm.thermalSingleDate.replace(/-/g, "")
						list = list.filter(
							function(feature) {
								return feature.get('flight_datetime').startsWith(singleDate)
							}
						)
					}
					else if (vm.showDateRange) {
						var start = vm.thermalFromDate.replace(/-/g, "").replace(' ', '_').replace(':', '')
						var end = vm.thermalToDate.replace(/-/g, "").replace(' ', '_').replace(':', '')
						if (end==="") {
							list = list.filter(
								function(feature) {
									return feature.get('flight_datetime') > start
								}
							)
						}
						else {list = list.filter(
								function(feature) {
									return feature.get('flight_datetime') > start && feature.get('flight_datetime') < end
								}
							)
						}
					}
				}
                vm._footprintlist.clear()
                vm._footprintlist.extend(list)
				
				//get extent of filtered features and set extent of map to this
				var extent = list[0].getGeometry().getExtent()	//.slice(0)
				list.forEach(function(feature) { ol.extent.extend(extent,feature.getGeometry().getExtent()) })
				vm.$root.map.olmap.getView().fit(extent, vm.$root.map.olmap.getSize())
            }, 500)
        }
        if (wait === 0) {
            vm._updateFootprintFilter.call({wait:1})
        } else if (wait === undefined || wait === null){
            vm._updateFootprintFilter()
        } else {
            vm._updateFootprintFilter.call({wait:wait})
        }
      },
	  
	  toggleImageList: function(event) {
			//event.target is the button wh was clicked; its nextElementSibling is the associated content (list of images for that hotspot)
			var hotspotID = event.target.innerHTML
			var imageListContent = event.target.nextElementSibling
			if (imageListContent.style.display === "block") {
			  var children = imageListContent.children		//HTML Collection object
			  for (let item of children) {
				item.innerHTML = item.innerHTML.replace("<b>", "").replace(" ON</b>", "")
			  }
			  imageListContent.style.display = "none"
			  var map = this.$root.map
				// Close any single images for this hotspot
				map.olmap.getLayers().forEach(function (layer) {
					if (layer.get('name') === 'Hotspot image ' + hotspotID) {
						map.olmap.removeLayer(layer)
					}
				})
			} else {
			  imageListContent.style.display = "block"
			}
	  },
	  
	  listImageFiles: function(f) {		//Not used at present
		var imagesString = f.get('images')
		var imagesArrayPrelim = imagesString.split(',')
		var imagesArray = []
		imagesArrayPrelim.forEach(function(item) {
			var pos1 = item.indexOf("/PNGs/") + 6
			var pos2 = item.indexOf(".png")
			var imageName = item.slice(pos1, pos2)
			imagesArray.push(imageName)
		})
		return imagesArray
	  },
	  
	  showImage: function(flight_datetime, hotspot_no, file, index, parentIndex) {
		file = file.replace(" ", "")		// Get rid of whitespace
	    var map = this.$root.map
		var hotspots_position = 0
		var other_hotspot_images = 0	// counts number of other hotpsots with an image displayed
		// Close any other single images for the same hotspot
		map.olmap.getLayers().forEach(function (layer) {
			if (layer.get('name') === 'Hotspot image ' + flight_datetime + ' ' + hotspot_no) {
				map.olmap.removeLayer(layer)
			}
		})
		// Add new single image
		var position = map.olmap.getLayers().getArray().length - 1
		map.olmap.getLayers().forEach(function (layer) {
			if (layer.get('name') === 'Flight mosaics') {
					mosaicLoaded = true
			}
			if (layer.get('name') === 'Hotspots') {
					hotspots_position = map.olmap.getLayers().getArray().findIndex(function(l){return l === layer})
					hotspotsLoaded = true
			}
			//if (layer.get('name').startsWith('Hotspot image')) {
			//	other_hotspot_images += 1
			//	alert(other_hotspot_images.toString() + " other_hotspot_images")
			//}
		})
		//position = hotspots_position + other_hotspot_images + 1
		position = hotspots_position
		map.createWMSLayerSingleImage(position, flight_datetime, hotspot_no, file)
		//this.imagesShow[parentIndex] = index
	  },
	  
	  changeButtons: function(event) {
	    var siblingButtons = this.getSiblingButtons(event.target)
		if (!event.target.innerHTML.endsWith(" ON") && !event.target.innerHTML.endsWith(" ON</b>")) {	
			event.target.innerHTML = event.target.innerHTML.replace("image ", "<b>image ") + " ON</b>"
			//event.target.outerHTML = event.target.outerHTML.replace("<button ", '<button style="background-color:blue" ')	//altering outerHTML cuts link to on-click function
		}
		siblingButtons.forEach(function (item, index) {
			item.innerHTML = item.innerHTML.replace("<b>", "").replace(" ON</b>", "")
			//item.outerHTML = item.outerHTML.replace('style="background-color:blue" ', '')
		})
	  },
	  
	  getSiblingButtons: function (buttonElement) {
		var siblings = [];
		var sibling = buttonElement.parentNode.firstChild;
		while (sibling) {
			if (sibling.nodeType === 1 && sibling !== buttonElement) {
				siblings.push(sibling);
			}
			sibling = sibling.nextSibling
		}
		return siblings;
	  },

	  removeHotspotLayers: function() {	//not used at present (the removal is done in map.vue L1811)
        try {
            var vm = this
			var map = this.$root.map			
			// Remove layers if exist
			map.olmap.getLayers().forEach(function (layer) {
				if (layer.get('name') === 'Hotspots') {
					map.olmap.removeLayer(layer)
				}
				if (layer.get('name') === 'Flight footprints') {
					map.olmap.removeLayer(layer)
				}
				if (layer.get('name') === 'Flight mosaics') {
					map.olmap.removeLayer(layer)
				}
			})
		}
        catch(ex) {
            alert(ex)
		}
    },

	  showEmailComposerPanel_OLD: function() {
		this.showEmailComposer = !this.showEmailComposer
		var vm = this
		if (vm.emailList.length == 0){
			if (this.env.gokartService = "") { 
				this.env.gokartServicewindow.location.href.slice(0, -4)
			}
			$.get(this.env.gokartService + '/hotspot_email_list').then(function(response) {
				var jsonObject = JSON.parse(response)
				vm.emailList = jsonObject['objects']
				select = document.getElementById( 'emailRecipient')
				for( email in vm.emailList ) {
					select.add( new Option( vm.emailList[email] ) )
				}
			})
		}
	  },
	  
	  showEmailComposerPanel: function() {
		if (this.flights.length == 0 && this.showEmailComposer == 0)
		return void alert("The email function is designed to work only if one or more hotspot flights are loaded in the map.");
		this.showEmailComposer = !this.showEmailComposer
		var vm = this
		if (vm.emailList.length == 0){
		    if (this.env.gokartService = "") { 
				this.env.gokartServicewindow.location.href.slice(0, -4)
			}
			$.get(this.env.gokartService+"/hotspot_email_list").then(function(response){
			vm.emailList = JSON.parse(response)
			select=document.getElementById("emailRecipient")
			for( item in vm.emailList) {
					select.add( new Option(vm.emailList[item]['email']))
				}
			})}},
	 
	  sendEmail_OLD: function() {
		var  recipient = document.getElementById("emailRecipient").value
		var messageText = document.getElementById("emailText").value
		var vm = this
		var cqlFilter = ""
		if (vm.hasDateFilter()) {
			if (vm.thermalSingleDate != undefined) {
					var singleDate = vm.thermalSingleDate.replace(/-/g, "")
					cqlFilter = "strStartsWith(flight_datetime, '" + singleDate + "') = true"
				}
		}
		
		var dateInfo = this.getDateInfoForMosaics(vm)
		if (messageText.length == 0) {
			alert ("You need to type in a message.")
			return
		}
		//alert('1040 flights: ' + this.env.gokartService + '/send_hotspot_email/' + recipient + '/' + messageText + '/' + vm.flights + '/' + cqlFilter)
		$.get(this.env.gokartService + '/send_hotspot_email/' + recipient + '/' + messageText + '/' + vm.flights + '/' + cqlFilter).then(function(response) {
			alert(response)
		})
	  },

	  sendEmail: function(){var recipient=document.getElementById("emailRecipient").value,messageText=document.getElementById("emailText").value,vm=this,cqlFilter="";if(vm.hasDateFilter()&&void 0!=vm.thermalSingleDate){cqlFilter="strStartsWith(flight_datetime, '"+vm.thermalSingleDate.replace(/-/g,"")+"') = true"}this.getDateInfoForMosaics(vm);if(0==messageText.length)return void alert("You need to type in a message.");try{$.get(this.env.gokartService+"/send_hotspot_email/"+recipient+"/"+messageText+"/"+vm.flights+"/"+cqlFilter).then(function(response){alert(response)})}catch(err){alert(err.name+": "+err.message)}},

      setExtentFeatureSize_OLD: function() {
        var vm = this
        var size = 0
        this._featurelist.forEach(function(feat){
            if (feat.inViewport) {
                ++size
            }
        })
        this.extentFeaturesSize = size;
      },
	  
	  setExtentFeatureSize: function(){
		var vm = this
		var size=0
		this._featurelist.forEach(function(feat){feat.inViewport&&++size}),this.extentFeaturesSize=size
		//alert(this.extentFeaturesSize)
		},

      updateViewport: function(wait) {
        var vm = this
        if (!vm._updateViewport) {
            vm._updateViewport = debounce(function(){
                var viewportExtent = vm.map.extent
                vm.features.forEach(function(feat) {
                    feat.inViewport = feat.getGeometry() && ol.extent.containsCoordinate(viewportExtent, feat.getGeometry().getCoordinates())
                })
                vm.setExtentFeatureSize()
                if (vm.viewportOnly) {
                    vm.revision += 1;
                }
            }, 500)
        }
        if (wait === 0) {
            vm._updateViewport.call({wait:1})
        } else if (wait === undefined || wait === null){
            //vm._updateViewport()
			vm._updateViewport.call({wait:1})
        } else {
            vm._updateViewport.call({wait:wait})
        }
      },
	  
      updateViewport_NEW: function(wait){
		var vm = this
		vm._updateViewport||(vm._updateViewport=debounce(function(){
			var viewportExtent=vm.map.extent
			vm.features.forEach(function(feat){
				feat.inViewport = feat.getGeometry() && ol.extent.containsCoordinate(viewportExtent, feat.getGeometry().getCoordinates())
			})
			vm.setExtentFeatureSize()
			vm.viewportOnly&&(vm.revision+=1)},500)),0===wait?vm._updateViewport.call({wait:1}):void 0===wait||null===wait?vm._updateViewport():vm._updateViewport.call({wait:wait})},
	  
	  clipToSelection:function() {
        if (this.selectedFeatures.getLength() === 0) {
            return
        }
        this.clippedFeatures.splice(0, this.clippedFeatures.length)
        for (var index = 0;index < this.selectedFeatures.getLength();index++) {
            this.clippedFeatures.push(this.selectedFeatures.item(index).get("deviceid"))
        }
        if (this.clippedOnly) {
            this.updateCQLFilter()
        }
      },

      //filter the loaded features based on report name and fire number
      setup: function() {

        //restore the selected features
        //this.annotations.restoreSelectedFeatures()
		
        /*this.annotations.selectable.push(this.trackingMapLayer)
        this.info.hoverable.push(this.trackingMapLayer)
        if (this.historyMapLayer) {
            this.info.hoverable.push(this.historyMapLayer)
        }
        this.annotations.setTool()*/
        this.$nextTick(this.adjustHeight)
      },
      
	  teardown:function() {
        this.annotations.selectable.splice(0, this.annotations.selectable.length)
      }
    },

    ready: function () {
      var vm = this
      var thermalStatus = this.loading.register("thermal", "Thermal Imaging Component")
      vm._featurelist = new ol.Collection()
	  vm._footprintlist = new ol.Collection()

      thermalStatus.phaseBegin("initialize", 20, "Initialize")

      //init datepicker
      $('#thermalFromDate').fdatepicker({
		format: 'yyyy-mm-dd hh:ii',
		disableDblClickSelection: true,
		leftArrow:'<<',
		rightArrow:'>>',
        startDate:moment().subtract(10, "years").format("YYYY-MM-DD") + " 00:00",
        endDate:moment().format("YYYY-MM-DD") + " 23:59",
        pickTime:true,
        minuteStep:1
      });
	  
      try {
          this._thermalFromDatePicker = $("#thermalFromDate").data().datepicker
      } catch(ex) {
          console.log(ex)
		  alert('thermal 952: ' + ex)
          this._thermalFromDatePicker = null
      }

      $('#thermalToDate').fdatepicker({
		format: 'yyyy-mm-dd hh:ii',
		disableDblClickSelection: true,
		leftArrow:'<<',
		rightArrow:'>>',
        startDate:moment().subtract(10, "years").format("YYYY-MM-DD") + " 00:00",
        endDate:moment().format("YYYY-MM-DD")  + " 23:59",
        pickTime:true,
        minuteStep:1
      });
	  
      try {
          this._thermalToDatePicker = $("#thermalToDate").data().datepicker
      } catch(ex) {
          this._thermalToDatePicker = null
      }

	  this.changeThermalDateRange()

	  thermalStatus.phaseBegin("load_hotspots", 30, "Load hotspots", false, true)
	  this.$root.fixedLayers.push({
        type: 'WFSLayer',
        name: 'Hotspots',
        id: 'hotspots:hotspot_centroids',
        features: vm._featurelist,
        getFeatureInfo: function (f) {
			return {flight_datetime: f.get("flight_datetime"), hotspot_no: f.get('hotspot_no'), images: f.get('images')}
        },
        onerror: function (status, message) {
            thermalStatus.phaseFailed("load_hotspots", status + " : " + message)
        },
		onload: function (loadType, vectorSource, features, defaultOnload) {
			var s = function(hotspot_no) {
				return new ol.style.Style({
						text: new ol.style.Text({
						  text: hotspot_no,
						  font: '16px Calibri,sans-serif',
						  fill: new ol.style.Fill({ color: '#fff' }),
						  stroke: new ol.style.Stroke({color: '#fff', width: 0.8})
						}),
						image : new ol.style.Circle({
							fill: new ol.style.Fill({color: [0, 0, 255]}),
							radius: 15
						})
					})
			}
			$.each(features, function (index, feature){
				var hotspot_no = feature.get('hotspot_no').toString()
				feature.setStyle(s(hotspot_no))
				
				var imagesString = feature.get('images')
				var imagesArray = imagesString.split(',')
				feature.shortImages = imagesArray
			})
			vm.features.clear()
			vm.features.extend(features.sort(vm.featureOrder))
			vm.updateFeatureFilter(0)		
		}
      })
	  
	 this.$root.fixedLayers.push({
        type: 'WFSLayer',
        name: 'Flight footprints',
        id: 'hotspots:hotspot_flight_footprints',
        features: vm._footprintlist,
        getFeatureInfo: function (f) {
			return {flight_datetime: f.get("flight_datetime")}
        },
        onerror: function (status, message) {
            thermalStatus.phaseFailed("load_hotspots", status + " : " + message)
        },
		onload:  function (loadType, vectorSource, features, defaultOnload) {
			vm.footprints.clear()
			vm.footprints.extend(features)
			vm.updateFootprintFilter(0)
		}
      })
	  
	  /*this.$root.fixedLayers.push({
        type: 'WMSLayer',
        name: 'Flight mosaics',
        id: 'hotspots:vrt-test',		//will need changing once testing done
        onerror: function (status, message) {
            thermalStatus.phaseFailed("load_hotspots", status + " : " + message)
        },
		onload:  function (loadType, vectorSource, features, defaultOnload) {	//needs changing
			vm.footprints.clear()
			vm.footprints.extend(features)
			vm.updateFootprintFilter(0)
		}
      })*/
	  
	  thermalStatus.phaseEnd('load_hotspots')

      var tools = [
        {
            name: 'Thermal Imaging Select',
            label: 'Select',
            icon: 'fa-mouse-pointer',
            scope:["thermal"],
            selectedFeatures:vm.selectedFeatures,
            keepSelection:true,
            interactions: [
              vm.annotations.dragSelectInterFactory({
                listeners: {
                    selected:function(selectedFeatures) {   
                        vm.scrollToSelected()
                    }
                }
              }),
              vm.annotations.polygonSelectInterFactory({
                listeners: {
                    selected:function(selectedFeatures) {   
                        vm.scrollToSelected()
                    }
                }
              }),
              vm.annotations.selectInterFactory({
                listeners: {
                    selected:function(selectedFeatures) {   
                        vm.scrollToSelected()
                    }
                }
              })
            ],
            onSet: function() {
                vm.annotations.ui.dragSelectInter.setMulti(true)
                vm.annotations.ui.selectInter.setMulti(true)
            },
            comments:[
              {
                  name:"Tips",
                  description:[
                      "Select all features using shortcut key 'Ctrl + A'",
                      "Select features using mouse.",
                      "Hold 'Ctrl' to enable polygon selection",
                      "Delete selected features using key 'Del'"
                  ]
              }
            ]
          }
      ]

      tools.forEach(function (tool) {
        vm.annotations.tools.push(tool)
      })

      thermalStatus.phaseEnd('initialize')

      thermalStatus.phaseBegin('gk-init', 30, "Listen 'gk-init' event")
      // post init event hookup
      this.$on('gk-init', function () {
        thermalStatus.phaseEnd('gk-init')

        thermalStatus.phaseBegin('attach_events', 10, 'Attach events')
        vm.map.olmap.getView().on('propertychange', function() {vm.updateViewport()})

        vm.selectedFeatures.on('add', function (event) {
            vm.selectRevision += 1
        })
        vm.selectedFeatures.on('remove', function (event) {
            vm.selectRevision += 1
        })

        vm.map.olmap.on('removeLayer', function(ev){
          if (ev.mapLayer.get('id') === "hotspots:hotspot_centroids") {
              vm.features.clear()
              vm._featurelist.clear()
          }
		  else if (ev.mapLayer.get('id') === "hotspots:hotspot_flight_footprints") {
              vm.footprints.clear()
              vm._footprintlist.clear()
          }
        })

        vm._resolutionChanged = debounce(function(ev){
            vm.featureLabelDisabled = (vm.map.olmap.getView().getResolution() >= 0.003)
            vm.featureDirDisabled = (vm.map.olmap.getView().getResolution() >= 0.003)
        }, 200)

        vm._resolutionChanged()
        vm.map.olmap.getView().on('change:resolution', function(){
            vm._resolutionChanged()
        })

        thermalStatus.phaseEnd('attach_events')

        thermalStatus.phaseBegin('init_tools', 10, 'Initialize tools')
        
        $.each([vm.annotations.ui.defaultPan], function (index, t) {
            t.scope = t.scope || []
            t.scope.push('thermal')
        })

        vm.tools = vm.annotations.tools.filter(function (t) {
          return t.scope && t.scope.indexOf('thermal') >= 0
        })

        thermalStatus.phaseEnd('init_tools')
      })
	}
  }
</script>
