<template>
  <div class="tabs-panel" id="menu-tab-tracking">
    <div class="row collapse">
      <div class="columns">
        <ul class="tabs" id="tracking-tabs">
          <li class="tabs-title is-active"><a class="label" aria-selected="true">Resource Tracking</a></li>
        </ul>
      </div>
    </div>
    <div class="row collapse" id="tracking-tab-panels">
      <div class="columns">
        <div class="tabs-content vertical" data-tabs-content="tracking-tabs">
          <div id="tracking-list-tab" class="tabs-panel is-active" v-cloak>
            <div id="tracking-list-controller-container">
            <div class="tool-slice row collapse">
              <div class="small-12">
                <div class="expanded button-group">
                  <a v-for="t in tools | filterIf 'showName' undefined" class="button button-tool" v-bind:class="{'selected': t.name == annotations.tool.name}"
                    @click="annotations.setTool(t)" v-bind:title="t.label">{{{ annotations.icon(t) }}}</a>
                </div>
                <div class="row resetmargin">
                  <div v-for="t in tools | filterIf 'showName' true" class="small-6" v-bind:class="{'rightmargin': $index % 2 === 0}" >
                    <a class="expanded secondary button" v-bind:class="{'selected': t.name == annotations.tool.name}" @click="annotations.setTool(t)"
                      v-bind:title="t.label">{{{ annotations.icon(t) }}} {{ t.label }}</a>
                  </div>
                </div>
              </div>
            </div>
            <div class="row">
              <div class="small-9 columns" >
                <div class="row">
                  <div class="switch tiny">
                    <input class="switch-input" id="resourcesInViewport" type="checkbox" v-bind:checked="viewportOnly" @change="toggleViewportOnly" />
                    <label class="switch-paddle" for="resourcesInViewport">
                      <span class="show-for-sr">Viewport resources only</span>
                    </label>
                  </div>
                  <label for="resourcesInViewport" class="side-label">Restrict to viewport ({{extentFeaturesSize}}/{{featurelistSize}})</label>
                </div>
              </div>
              <div class="small-3 columns" style="text-align:right;padding-right:0px">
                <span v-on:click="showToggles = !showToggles" style="cursor:pointer"><i class="fa {{showToggles?'fa-angle-double-up':'fa-angle-double-down'}}" aria-hidden="true"></i> Toggles</span>
              </div>
            </div>
            <div v-show="showToggles">

            <div class="row">
              <div class="switch tiny">
                <input class="switch-input" id="toggleDBCAResourceLabels" type="checkbox" v-bind:disabled="clippedOnly" v-bind:checked="showDBCAResource" @change="showDBCAResource = !showDBCAResource" />
                <label class="switch-paddle" for="toggleDBCAResourceLabels">
                  <span class="show-for-sr">Show DBCA Resources</span>
                </label>
              </div>
              <label for="toggleDBCAResourceLabels" class="side-label">Show DBCA Resources</label>
            </div>

            <div class="row">
              <div class="switch tiny">
                <input class="switch-input" id="toggleDFESResourceLabels" type="checkbox" v-bind:disabled="clippedOnly" v-bind:checked="showDFESResource" @change="showDFESResource = !showDFESResource" />
                <label class="switch-paddle" for="toggleDFESResourceLabels">
                  <span class="show-for-sr">Show DFES Resources</span>
                </label>
              </div>
              <label for="toggleDFESResourceLabels" class="side-label">Show DFES Resources</label>
            </div>

            <div class="row">
              <div class="switch tiny">
                <input class="switch-input" id="toggleOtherExternalResourceLabels" type="checkbox" v-bind:disabled="clippedOnly" v-bind:checked="showOtherExternalResource" @change="showOtherExternalResource = !showOtherExternalResource" />
                <label class="switch-paddle" for="toggleOtherExternalResourceLabels">
                  <span class="show-for-sr">Show Other Aviation Resources</span>
                </label>
              </div>
              <label for="toggleDBCAResourceLabels" class="side-label">Show Other Aviation Resources</label>
            </div>

            <div class="row">
              <div class="switch tiny">
                <input class="switch-input" id="toggleResourceLabels" type="checkbox" v-bind:checked="resourceLabels" @change="toggleResourceLabels"  v-bind:disabled="featureLabelDisabled"/>
                <label class="switch-paddle" for="toggleResourceLabels">
                  <span class="show-for-sr">Display resource labels</span>
                </label>
              </div>
              <label for="toggleResourceLabels" class="side-label">Display resource labels</label>
            </div>

            <div class="row">
              <div class="switch tiny">
                <input class="switch-input" id="toggleResourceDirections" type="checkbox" v-bind:checked="resourceDirections" @change="toggleResourceDirections" v-bind:disabled="featureDirDisabled"/>
                <label class="switch-paddle" for="toggleResourceDirections">
                  <span class="show-for-sr">Display resource directions</span>
                </label>
              </div>
              <label for="toggleResourceDirections" class="side-label">Display resource directions</label>
            </div>

            <div class="row">
              <div class="switch tiny">
                <input class="switch-input" id="toggleResourceInfo" type="checkbox" v-bind:disabled="!systemsetting.hoverInfoSwitchable" v-bind:checked="systemsetting.hoverInfo" @change="systemsetting.toggleHoverInfo" />
                <label class="switch-paddle" for="toggleResourceInfo">
                  <span class="show-for-sr">Display hovering resource info</span>
                </label>
              </div>
              <label for="toggleResourceInfo" class="side-label">Display hovering resource info</label>
            </div>

            <div class="row">
              <div class="small-12">
                <div class="columns">
                  <div class="row">
                    <div class="switch tiny">
                      <input class="switch-input" id="clippedResourceOnly" v-bind:disabled="clippedFeatures.length === 0" type="checkbox" v-model="clippedOnly"  @change="updateCQLFilter()"/>
                      <label class="switch-paddle" for="clippedResourceOnly">
                        <span class="show-for-sr">Show saved selection</span>
                     </label>
                    </div>
                    <label for="clippedResourceOnly" style="side-label" class="side-label">Show saved selection
                    </label>
                    <a class="button tiny secondary" title="Save selection" style="margin-top:0px;margin-bottom:5px;padding-top:6px;padding-left:1px;padding-right:1px;padding-bottom:0px;border:0px;height:24px;font-size:0.73rem;background-color:#2199e8" @click="clipToSelection()"  v-bind:disabled="selectedFeaturesSize === 0">
                        Save selection ({{selectedFeaturesSize}})
                    </a> 
                    ({{clippedFeatures.length}})
                  </div>
                </div>
              </div>
            </div>

            </div>
            <div class="row collapse">
              <div class="small-6 columns">
                <select name="select" v-model="groupFilter" @change="updateCQLFilter()"  v-bind:disabled="clippedOnly">
                  <option value="" selected>All resources</option> 
                  <option value="symbolid LIKE '%aircraft'">Aircraft</option>
                  <option value="symbolid LIKE '%comms_bus'">Communications Bus</option>
                  <option value="symbolid LIKE '%gang_truck'">Gang Truck</option>
                  <option value="symbolid LIKE '%heavy_duty'">Heavy Duty</option>
                  <option value="(symbolid LIKE '%heavy_duty' OR symbolid LIKE '%gang_truck')">Gang Truck and Heavy Duty</option>
                  <option value="symbolid LIKE '%light_unit'">Light Unit</option>
                  <option value="(symbolid LIKE '%dozer' OR symbolid LIKE '%grader' OR symbolid LIKE '%loader')">Machinery</option>
                  <option value="(symbolid LIKE '%2_wheel_drive' OR symbolid LIKE '%4_wheel_drive_passenger' OR symbolid LIKE '%4_wheel_drive_ute')">Other Light Fleet</option>
                </select>
              </div>
              <div class="small-6 columns">
                <input type="search" v-model="search" placeholder="Find a resource" @keyup="updateFeatureFilter(500)">
              </div>
            </div>
            <div class="row">
              <div class="small-7">
                <div class="columns">
                  <div class="row">
                    <div class="switch tiny">
                      <input class="switch-input" id="resourceHistory" type="checkbox" v-model="toggleHistory" @change="clearHistory" />
                      <label class="switch-paddle" for="resourceHistory">
						<span class="show-for-sr">Query history</span>
					  </label>
                    </div>
                    <label for="resourceHistory" class="side-label">Query history</label>
                  </div>
                </div>
              </div>
              <div class="small-5">
                <a title="Zoom to selected" class="button" @click="map.zoomToSelected()" ><i class="fa fa-search"></i></a>
                <a title="Download list as geoJSON" class="button" @click="downloadList()" ><i class="fa fa-download"></i></a>
                <a title="Download all or selected as CSV" class="button" href="{{selectRevision&&env.resourceTrackingService}}/devices.csv?{{downloadSelectedCSV()}}" target="_blank" ><i class="fa fa-table"></i></a>
              </div>
            </div>
            <div id="history-panel" v-show="toggleHistory">
              <div class="row collapse tool-slice">
                <div class="small-2">
                  <label for="historyFrom">From:</label>
                </div>
                <div class="small-5">
                  <input type="text" id="historyFromDate" class="span2" v-model="historyFromDate" placeholder="YYYY-MM-DD HH:mm" v-bind:disabled="historyRange !== '-1'" readonly></input>
                </div>
                <div class="small-5">
                  <select name="select" v-model="historyRange" >
                      <option value="21001">Last hour</option> 
                      <option value="21003">Last 3 hours</option> 
                      <option value="21024">Last 24 hours</option> 
                      <option value="31007">Last 7 days</option> 
                      <option value="31030">Last 30 days</option> 
                      <option value="-1">User Defined</option> 
                </select>
                </div>
              </div>
              <div class="row collapse tool-slice">
                <div class="small-2">
                  <label for="historyTo">To:</label>
                </div>
                <div class="small-5">
                  <input type="text" id="historyToDate" class="span2" v-model="historyToDate" placeholder="YYYY-MM-DD HH:mm"  v-bind:disabled="historyRange !== '-1'"  readonly></input>
                </div>
                <div class="small-3"></div>
                <div class="small-2">
                  <button v-bind:disabled="queryHistoryDisabled" class="button" style="float: right" @click="historyCQLFilter">Go</button>
                </div>
              </div>
            </div>
            </div>


            <div id="tracking-list" class="layers-flexibleframe scroller" style="margin-left:-15px; margin-right:-15px;">
              <template v-for="f in featurelist" track-by="get('id')">
              <div class="row feature-row" v-if="showFeature(f)" v-bind:class="{'feature-selected': isFeatureSelected(f) }" @click="toggleSelect(f)">
                <div class="columns">
                  <!--a v-if="whoami.editVehicle && ['tracplus','dfes'].indexOf(f.get('source_device_type')) < 0" @click.stop.prevent="utils.editResource($event)" title="Edit resource" href="{{env.resourceTrackingService}}/sss_admin/tracking/device/{{ f.get('id') }}/change/" target="{{env.resourceTrackingService}}" class="button tiny secondary float-right"><i class="fa fa-pencil"></i></a-->
                  <a v-if=" ['tracplus','dfes'].indexOf(f.get('source_device_type')) < 0" @click.stop.prevent="utils.editResource($event)" title="Edit resource" href="{{env.resourceTrackingService}}/sss_admin/tracking/device/{{ f.get('id') }}/change/" target="{{env.resourceTrackingService}}" class="button tiny secondary float-right"><i class="fa fa-pencil"></i></a>
                  
				  <div class="feature-title"><img class="feature-icon" id="device-icon-{{f.get('id')}}" v-bind:src="featureIconSrc(f)" /> {{ f.get('label') }} <i><small>({{ ago(f.get('seen')) }})</small></i>
                  </div>
                </div>
              </div>
              </template>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<style>
#historyFromDate, #historyToDate {
    cursor:pointer
}
</style>
<script>
  import { ol, moment, utils } from 'src/vendor.js'
  export default {
    store: {
        resourceLabels:'settings.resourceLabels',
        resourceDirections:'settings.resourceDirections',
        viewportOnly:'settings.viewportOnly',
        hintsHeight:'layout.hintsHeight',
        screenHeight:'layout.screenHeight',
        leftPanelHeadHeight:'layout.leftPanelHeadHeight',
        activeMenu:'activeMenu',
        whoami:'whoami'
    },
    data: function () {
      var fill = '#ff6600'
      var stroke = '#7c3100'
      return {
        toggleHistory: false,
        showToggles: false,
        clippedOnly: false,
        search: '',
        groupFilter: '',
        sourceflag: 3,
        tools: [],
        historyRange: '21001',
        fields: ['id', 'registration', 'rin_display', 'deviceid', 'symbol', 'district_display', 'usual_driver', 'callsign_display', 'usual_location', 'current_driver', 'contractor_details', 'source_device_type'],
        features:new ol.Collection(),
        extentFeaturesSize:0,
        featureLabelDisabled:false,
        featureDirDisabled:false,
        clippedFeatures: [],
        historyFromDate: '',
        historyToDate: '',
        tints: {
          'red': [[fill,'#ed2727'], [stroke,'#480000']],
          'orange': [[fill,'#ff6600'], [stroke,'#562200']],
          'yellow': [[fill,'#ffd700'], [stroke,'#413104']],
          'green': [[fill,'#71c837'], [stroke,'#1b310d']],
          'selected': [['#000000', '#2199e8'], [stroke,'#2199e8'], [fill, '#ffffff']],
        },
        revision:1,
        selectRevision:1,
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
      isTrackingMapLayerHidden:function() {
        return this.$root.active.isHidden(this.trackingMapLayer)
      },
      isHistoryMapLayerHidden:function() {
        return this.$root.active.isHidden(this.historyMapLayer)
      },
      selectedFeatures: function () {
        return this.annotations.getSelectedFeatures("tracking")
      },
      selectedFeaturesSize: function () {
        return this.selectRevision && this.selectedFeatures.getLength()
      },
      queryHistoryDisabled: function() {
        return !(this.selectRevision && this.selectedFeatures && this.selectedFeatures.getLength() && this.historyFromDate !== "")
      },
      showOtherExternalResource: {
        get: function() {
            return (this.sourceflag & 1) === 1
        },
        set: function(show) {
            this.setSourceFlag(1,show)
        }
      },
      showDBCAResource: {
        get: function() {
            return (this.sourceflag & 2) === 2
        },
        set: function(show) {
            this.setSourceFlag(2,show)
        }
      },
      showDFESResource: {
        get: function() {
            return (this.sourceflag & 4) === 4
        },
        set: function(show) {
            this.setSourceFlag(4,show)
        }
      },
      trackingLayer: function() {
        return this.$root.catalogue.getLayer('dpaw:resource_tracking_live')
      },
      trackingMapLayer: function() {
        return this.$root.map?this.$root.map.getMapLayer(this.trackingLayer):undefined
      },
      historyLayer: function() {
        return this.$root.catalogue.getLayer('dpaw:resource_tracking_history')
      },
      historyMapLayer: function() {
        return this.$root.map?this.$root.map.getMapLayer(this.historyLayer):undefined
      },
      featurelist:function() {
        try {
            return this.revision && this._featurelist.getArray()
        } catch (ex) {
            return [];
        }
      },
      featurelistSize:function() {
        try {
            return this.revision && this._featurelist.getLength()
        } catch (ex) {
            return 0;
        }
      },
      hasFeatureFilter: function () {
        return (this.search && this.search.trim())?true:false
      },
    },
    watch:{
      isTrackingMapLayerHidden:function(newValue,oldValue) {
        if (newValue === undefined || oldValue === undefined) {
            //layer is turned on or turned off
            return
        } else if (this.map.resolution >= 0.003) {
            //label is turned on, but resolution is not less than 0.003
            return
        } else {
            //label is enabled, hiding/showing tracking layer requires resetting the style text.
            this.trackingMapLayer.changed() 
        }
      },
      isHistoryMapLayerHidden:function(newValue,oldValue) {
        if (newValue === undefined || oldValue === undefined) {
            //layer is turned on or turned off
            return
        } else if (this.map.resolution >= 0.003) {
            //label is turned on, but resolution is not less than 0.003
            return
        } else {
            //label is enabled, hiding/showing tracking layer requires resetting the style text.
            this.historyMapLayer.changed() 
        }
      },
      resourceLabels:function(newValue,oldValue) {
        this.showResourceLabelsOrDirections()
      },
      resourceDirections:function(newValue,oldValue) {
        this.showResourceLabelsOrDirections()
      },
      toggleHistory:function() {
        this.adjustHeight()
      },
      showToggles:function(newValue,oldValue) {
        this.adjustHeight()
      },
      sourceflag:function(newValue,oldValue) {
        this.updateCQLFilter(1000)
      },
      historyRange:function(newValue,oldValue) {
        this.changeHistoryRange()
      },
      historyFromDate:function(newValue,oldValue) {
        this.changeHistoryFromDate()
      },
      historyToDate:function(newValue,oldValue) {
        this.changeHistoryToDate()
      },
    },
    methods: {
      adjustHeight:function() {
        if (this.activeMenu === "tracking") {
            $("#tracking-list").height(this.screenHeight - this.leftPanelHeadHeight - 41 - $("#tracking-list-controller-container").height() - this.hintsHeight)
        }
      },
      changeHistoryRange: function() {
        if (this.historyRange === "-1") {
            //customized
            if (!this.historyFromDate) {
                //fromDate is null, set to default value "Last hour"
                var range = utils.getDateRange(21001,"YYYY-MM-DD HH:mm")
                this.historyFromDate = range[0] || ""
                if ((range[1] || "") !== this.historyToDate) {
                    this.historyToDate = range[1] || ""
                } else {
                    this.changeHistoryToDate()
                }
            } else {
                this.changeHistoryFromDate()
                this.changeHistoryToDate()
            }
        } else { 
            var range = utils.getDateRange(this.historyRange, "YYYY-MM-DD HH:mm")
            this.historyFromDate = range[0] || ""
            this.historyToDate = range[1] || ""
        }
      },
      changeHistoryFromDate:function() {
        if (this.historyRange !== "-1") {
            //not in editing mode
            return
        }
        if (!this._historyToDatePicker) return
        try {
            if (this.historyFromDate === "") {
                this._historyToDatePicker.setStartDate(moment().subtract(10,"years").format("YYYY-MM-DD") + " 00:00")
            } else {
                this._historyToDatePicker.setStartDate(moment(this.historyFromDate,"YYYY-MM-DD HH:mm").format("YYYY-MM-DD") + " 00:00")
                //this._historyToDatePicker.setStartDate(this.historyFromDate)
            }
        } catch(ex) {
        }
      },
      changeHistoryToDate:function() {
        if (this.historyRange !== "-1") {
            //not in editing mode
            return
        }
        if (!this._historyFromDatePicker) return
        try {
            if (this.historyToDate === "") {
                this._historyFromDatePicker.setEndDate(moment().format("YYYY-MM-DD") + " 23:59")
            } else {
                this._historyFromDatePicker.setEndDate(this.historyToDate)
            }
        } catch(ex) {
        }
      },
      historyDateFilter: function() {
        if (this.historyRange !== "-1") {
            //in predefined range, reset the historyFromDate and historyToDate
            this.changeHistoryRange()
        }
        var startDate = (this.historyFromDate)?moment(this.historyFromDate,"YYYY-MM-DD HH:mm", true):null
        if (startDate && !startDate.isValid()) {
            throw "From date is under changing."
        }

        var endDate = (this.historyToDate && this.historyToDate < moment().format("YYYY-MM-DD HH:mm"))?moment(this.historyToDate,"YYYY-MM-DD HH:mm", true):null
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
            return "seen < '" + utils.nextDate(endDate,"YYYY-MM-DD HH:mm").utc().format("YYYY-MM-DDTHH:mm:ssZ") + "'"
        } else {
            throw "Please speicify history range."
        }
      },
      setSourceFlag: function(flag,show) {
        if (show === null || show === undefined) {
            //toggle 
            this.sourceflag = this.sourceflag ^ flag
        } else if (show && (this.sourceflag & flag) === 0) {
            //flag is off
            this.sourceflag += flag
        } else if (!show && (this.sourceflag & flag) === flag) {
            //flag is on
            this.sourceflag -= flag
        }
      },
      getSourceFilter:function() {
        if (this.showDBCAResource && this.showDFESResource && this.showOtherExternalResource) {
        //if (this.showDBCAResource && this.showOtherExternalResource) {
            return null
        } else if (!this.showDBCAResource && !this.showDFESResource && !this.showOtherExternalResource) {
            throw "Please choose at least one resource source."
        }
        var filter = ""
        if (this.showDBCAResource) {
            filter += "'fleetcare','iriditrak','dplus','spot','other'"
        }
        if (this.showDFESResource) {
            if (filter !== "") filter += ","
            filter += "'dfes'"
        }
        if (this.showOtherExternalResource) {
            if (filter !== "") filter += ","
            filter += "'tracplus'"
        }
        return "source_device_type in (" + filter + ")"
      },
      ago: function (time) {
        var now = moment()
        if (now.diff(moment(time), 'days') == 1) {
            return now.diff(moment(time), 'days') + ' day'
        } else if ((now.diff(moment(time), 'days') > 1)) {
            return now.diff(moment(time), 'days') + ' days'
        } else if ((now.diff(moment(time), 'hours') == 1)) {
            return now.diff(moment(time), 'hours') + ' hr'
        } else if ((now.diff(moment(time), 'hours') > 1)) {
            return now.diff(moment(time), 'hours') + ' hrs'
        } else if ((now.diff(moment(time), 'minutes') == 1)) {
            return now.diff(moment(time), 'minutes') + ' min'
        } else if ((now.diff(moment(time), 'minutes') < 1)) {
            return '<1 min'
        } else {
            return now.diff(moment(time), 'minutes') + ' mins'
        }
      },
      scrollToSelected:function() {
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
            var listElement = document.getElementById("tracking-list")
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
      toggleViewportOnly: function () {
        this.viewportOnly = !this.viewportOnly
        this.export.saveState()
      },
      toggleResourceLabels: function () {
        var vm = this
        this.resourceLabels = !this.resourceLabels
        this.export.saveState()
      },
      showResourceLabelsOrDirections:function() {
        var vm = this
        $.each([this.trackingMapLayer,this.historyMapLayer],function(index,mapLayer){
            if (mapLayer && !vm.$root.active.isHidden(mapLayer)) {
                mapLayer.changed()
            }
        })
      },
      toggleResourceDirections: function () {
        var vm = this
        this.resourceDirections = !this.resourceDirections
        this.export.saveState()
      },
      showFeature:function(feat) {
        return this.revision && (!this.viewportOnly || feat.inViewport)
      },
      featureIconSrc:function(f) {
        var vm = this
        return vm.selectRevision && this.map.getBlob(f, ['icon', 'originalTint'],this.tints,function(){
            $("#device-icon-" + f.get('id')).attr("src", vm.featureIconSrc(f))
        })
      },
      isFeatureSelected: function (f) {
        return this.selectedFeatures.getArray().findIndex(function(o){return f === o}) >= 0
      },
      downloadList: function () {
        var list = null
        if (this.viewportOnly) {
            list = this._featurelist.getArray().filter(function(f){return f.inViewport})
        } else {
            list = this._featurelist.getArray()
        }
        this.$root.export.exportVector(list, 'trackingdata')
      },
      downloadSelectedCSV: function () {
          var deviceFilter = ''
          if (this.selectedFeatures.getLength() > 0) {
              deviceFilter = 'deviceid__in=' + this.selectedFeatures.getArray().map(function(o) {return o.get("deviceid")}).join(",") + ""
          }
          return deviceFilter
      },
      clearHistory: function () {
          var historyLayer = this.historyLayer
          if (!this.toggleHistory) {
              historyLayer.cql_filter = "clearhistorylayer"
              this.$root.catalogue.onLayerChange(historyLayer, false)
          }
      },
      updateCQLFilter: function (wait) {
        var vm = this
        if (!vm._updateCQLFilter) {
            vm._updateCQLFilter = debounce(function(updateType){
                try {
                    var groupFilter = vm.groupFilter
                    var deviceFilter = ''
                    var sourceFilter = vm.getSourceFilter()
                    // filter by specific devices if "Show selected only" is enabled
                    if (vm.clippedOnly) {
                        if (vm.clippedFeatures.length > 0) {
                          deviceFilter = 'deviceid in (\'' + vm.clippedFeatures.join('\',\'') + '\')'
                        } else {
                          vm.clippedOnly = false
                        }
                    }
                    // CQL statement assembling logic
                    var cql_filter = ""
                    if (deviceFilter) {
                      cql_filter = deviceFilter
                    } else if (groupFilter && sourceFilter) {
                      cql_filter = '(' + groupFilter + ') and (' + sourceFilter + ')'
                    } else if (groupFilter) {
                      cql_filter = groupFilter
                    } else if (sourceFilter) {
                      cql_filter = sourceFilter
                    } else {
                      cql_filter = ""
                    }
                    if (cql_filter === vm.trackingLayer.cql_filter) {
                        //filter not changed
                        return
                    }
                    vm.trackingLayer.cql_filter = cql_filter
                    //clear device filter or change other filter
                    vm.trackingMapLayer.set('updated', moment().toLocaleString())
                    vm.trackingMapLayer.getSource().loadSource(deviceFilter?"querySavedSelection":"query")
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
      historyCQLFilter: function () {
        try {
            var vm = this
            var historyLayer = this.historyLayer
            var deviceFilter = 'deviceid in (\'' + this.selectedFeatures.getArray().map(function(o) {return o.get("deviceid")}).join('\',\'') + '\')'
            historyLayer.cql_filter = deviceFilter + "and " + this.historyDateFilter()
            if (this.$root.catalogue.onLayerChange(historyLayer, true)) {
                //Add history layer into the map. need to add to the hoverable
                this.info.hoverable.push(this.historyMapLayer)
            } else {
                //history layer is already turned on, manually load the history source
                var source = this.$root.map.getMapLayer(historyLayer).getSource()
                source.loadSource("query")
            }
        } catch(ex) {
            alert(ex)
        }
      },
      featureFilter: function (f) {
        var search = this.search?this.search.toLowerCase().trim():""
        var found = !search || this.fields.some(function (key) {
          return ('' + f.get(key)).toLowerCase().indexOf(search) > -1
        })
        return found
      },
      featureOrder: function (a, b) {
        var as = a.get('seen')
        var bs = b.get('seen')
        if (as < bs) {
          return 1
        } else if (as > bs) {
          return -1
        }
        return 0
      },
      //filter the loaded features
      updateFeatureFilter: function(wait) {
        var vm = this
        if (!vm._updateFeatureFilter) {
            vm._updateFeatureFilter = debounce(function(){
                var list = vm.features.getArray()
                if (vm.hasFeatureFilter) {
                    list = list.filter(vm.featureFilter)
                }
                vm._featurelist.clear()
                vm._featurelist.extend(list)
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
      setExtentFeatureSize:function() {
        var vm = this
        var size = 0
        this._featurelist.forEach(function(feat){
            if (feat.inViewport) {
                ++size
            }
        })
        this.extentFeaturesSize = size;
      },
      updateViewport: function(wait) {
        var vm = this
        if (!vm._updateViewport) {
            vm._updateViewport = debounce(function(){
                var viewportExtent = vm.map.extent
                vm.features.forEach(function(feat) {
                    feat.inViewport = feat.getGeometry() && ol.extent.containsCoordinate(viewportExtent,feat.getGeometry().getCoordinates())
                })
                vm.setExtentFeatureSize()
                if (vm.viewportOnly) {
                    vm.revision += 1;
                }
            },500)
        }
        if (wait === 0) {
            vm._updateViewport.call({wait:1})
        } else if (wait === undefined || wait === null){
            vm._updateViewport()
        } else {
            vm._updateViewport.call({wait:wait})
        }
      },
      clipToSelection:function() {
        if (this.selectedFeatures.getLength() === 0) {
            return
        }
        this.clippedFeatures.splice(0,this.clippedFeatures.length)
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
        this.annotations.restoreSelectedFeatures()

        // enable resource tracking layer, if disabled
        if (!this.trackingMapLayer) {
            this.catalogue.onLayerChange(this.trackingLayer, true)
        } else if (this.active.isHidden(this.trackingMapLayer)) {
            this.active.toggleHidden(this.trackingMapLayer)
        }

        this.annotations.selectable.push(this.trackingMapLayer)
        this.info.hoverable.push(this.trackingMapLayer)
        if (this.historyMapLayer) {
            this.info.hoverable.push(this.historyMapLayer)
        }
        this.annotations.setTool()

        this.$nextTick(this.adjustHeight)
      },
      teardown:function() {
        this.annotations.selectable.splice(0,this.annotations.selectable.length)
      }
    },
    ready: function () {
      var vm = this
      var trackingStatus = this.loading.register("tracking", "Resource Tracking Component")
      vm._featurelist = new ol.Collection()

      trackingStatus.phaseBegin("initialize", 20, "Initialize")

      //init datepicker
      $('#historyFromDate').fdatepicker({
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
          this._historyFromDatePicker = $("#historyFromDate").data().datepicker
      } catch(ex) {
          console.log(ex)
          this._historyFromDatePicker = null
      }

      $('#historyToDate').fdatepicker({
	format: 'yyyy-mm-dd hh:ii',
	disableDblClickSelection: true,
	leftArrow:'<<',
	rightArrow:'>>',
        startDate:moment().subtract(10,"years").format("YYYY-MM-DD") + " 00:00",
        endDate:moment().format("YYYY-MM-DD") + " 23:59",
        pickTime:true,
        minuteStep:1
      });

      try {
          this._historyToDatePicker = $("#historyToDate").data().datepicker
      } catch(ex) {
          this._historyToDatePicker = null
      }

      this.changeHistoryRange()

      var resourceTrackingStyleFunc = function(layerId){
        return function (res) {
            var feat = this
            // cache styles for performance
            var style = vm.map.cacheStyle(function (feat) {
              var src = vm.map.getBlob(feat, ['icon', 'tint'],vm.tints)
              if (!src) { return false }
              return new ol.style.Style({
                image: new ol.style.Icon({
                  src: src,
                  scale: 0.5,
                  snapToPixel: true
                }),
                text: new ol.style.Text({
                  offsetX: 12,
                  textAlign: 'left',
                  font: '12px Helvetica,Roboto,Arial,sans-serif',
                  stroke: new ol.style.Stroke({
                    color: '#fff',
                    width: 4
                  })
                }),
                stroke: new ol.style.Stroke({
                  color: [52, 101, 164, 0.6],
                  width: 4.0
                })
              })
            }, feat, ['icon', 'tint'])
            if (style[0].getText && style[0].getText()) {
              if (res < 0.003 && vm.resourceLabels && !vm.$root.active.isHidden(vm.map.getMapLayer(layerId))) {
                style[0].getText().setText(feat.get('label'))
              } else {
                style[0].getText().setText('')
              }
            }
            if (res < 0.003 && vm.resourceDirections) {
              var heading = feat.get('heading')
              var speed = feat.get('velocity')
              if (heading !== undefined && (heading !== 0 || speed !== 0)) {
                  //style.getImage().setRotation( (heading + 90) / 180 * Math.PI )
                  if (!vm.styleWithDirection) {
                      vm.styleWithDirection = style.concat([new ol.style.Style({
                          image: new ol.style.Icon({
                              src: "/dist/static/symbols/device/direction.svg",
                              scale:1,
                              snapToPixel:true
                          })
                      })])
                  } else {
                    vm.styleWithDirection[0] = style[0]
                  }
                  vm.styleWithDirection[1].getImage().setRotation(heading / 180 * Math.PI)
                  return vm.styleWithDirection
              }
            }
            return style
          }
      }

      var deviceLabel = function(device) {
        var name = ''
		var rin_symbols = ['heavy duty','gang truck','dozer','loader','grader','tender','float'];
        var symbol = device.get('symbol');
        var district = device.get('district_display');
        //var callsign_display = device.get('callsign_display');
		var callsign = device.get('callsign');
        var registration = device.get('registration');
        /*if (!district || district == 'Aviation' || district == 'Other'){
			if (!callsign_display || rin_symbols.indexOf(symbol) === -1){
                name = registration
            } else {
                name = callsign_display +' '+ registration
            }
        } else {
	    if (!callsign_display || rin_symbols.indexOf(symbol) === -1){
                name = district +' '+ registration
            } else {
                name = callsign_display +' '+ registration
            }
        }
        return name*/
		//name = callsign_display +' '+ registration
		name = callsign + ' ' + registration
		name = name.replace("null", "")
		return name
      }

      var addResourceFunc = function(styleFunc) {
        return function (f) {
            var now = moment()
            var timestamp = moment(f.get('seen'))
            var tint = 'red'
            if (now.diff(timestamp, 'hours') < 24) {
              tint = 'orange'
            };
            if (now.diff(timestamp, 'hours') < 3) {
              tint = 'yellow'
            };
            if (now.diff(timestamp, 'hours') < 1) {
              tint = 'green'
            };
            if (f.get("source_device_type") === "dfes") {
                f.set('icon', ['dist/static/symbols/device/external_d.svg','dist/static/symbols/device/dfes_generic.svg'], true)
            } else if (f.get("source_device_type") === "tracplus") {
                f.set('icon', ['dist/static/symbols/device/external_e.svg','dist/static/symbols/device/' + f.get('symbolid') + '.svg'], true)
            } else {
                f.set('icon', 'dist/static/symbols/device/' + f.get('symbolid') + '.svg', true)
            }
            f.set('tint', tint, true)
            f.set('originalTint', tint, true)
            f.set('label', deviceLabel(f), true)
            f.set('time', timestamp.toLocaleString(), true)
            // Set a different vue template for rendering
            f.set('partialId', 'resourceInfo', true)
            // Set id for select tools
            f.set('selectId', f.get('deviceid'), true)
            f.setStyle(styleFunc, true)
        }
      }

      var deviceExtraHoverLabel = function(device) {
	  var rin_symbols = ['heavy duty','gang truck','dozer','loader','grader','tender','float'];
          var symbol = device.get('symbol');
          var return_label = ''
          var callsign_label = ''
          var callsign_display = device.get('callsign_display');
          var c_label = ''
          var u_label = ''
          var c_driver = ' ' + (device.get("current_driver") || '');
          var u_driver = ' ' + (device.get("usual_driver") || '');
          var u_location = ' ' + (device.get("usual_location") || '');
          var contractor_label = "Contractor: " + (device.get("contractor_details") || '');

          // Set "Callsign" Label for "Light vehicles" (no RIN)
          
	  if (callsign_display && rin_symbols.indexOf(symbol) === -1) {
              callsign_label = "Callsign: " + callsign_display
          }

          // Set "Usual" Label
          if (u_driver != ' ') {
              u_label += "Usual driver:" + u_driver
              if (u_location != ' '){
                  u_label += ", Location:" + u_location
              }
          } else if (u_location != ' '){
              u_label += "Usual location:" + u_location
          }

          // Set "Current" Label
          if (c_driver != ' ') {
              c_label += "Current driver:" + c_driver
          }

          // Generate Full Label
          if (callsign_label != ''){
              return_label += callsign_label
          }
          if (callsign_label != '' & c_label != ''){
              return_label += '<br>' + c_label
          } else if (c_label != ''){
              return_label += c_label
          }
	  if ((c_label != '' || callsign_label != '') && u_label != ''){
              return_label += '<br>' + u_label
          } else if (u_label != ''){
              return_label += u_label
          }
          if ((c_label != '' || u_label != '') && contractor_label != 'Contractor: '){
              return_label += '<br>' + contractor_label
          } else if (contractor_label != 'Contractor: '){
              return_label += contractor_label
          }

          return return_label
      }

      trackingStatus.phaseBegin("load_resources", 30, "Load resources", false, true)
      var _addResourceFunc = addResourceFunc(resourceTrackingStyleFunc('dpaw:resource_tracking_live'))
      this.$root.fixedLayers.push({
        type: 'WFSLayer',
        name: 'Resource Tracking',
        id: 'dpaw:resource_tracking_live',
        features: vm._featurelist,
        cql_filter: vm.getSourceFilter(),
        getFeatureInfo: function (f) {
            var extra_device_label = deviceExtraHoverLabel(f)
            return {name: f.get("label"), img:vm.map.getBlob(f, ['icon', 'tint']),
                comments:"(" + vm.ago(f.get("seen")) + " ago, Heading:" + f.get("heading") + "&deg;)<br>" +
                    extra_device_label}
        },
        refresh: 60,
        onerror: function(status, message) {
            trackingStatus.phaseFailed("load_resources", status + " : " + message)
        },
        onload: function(loadType, vectorSource, features, defaultOnload) {
            function processResources() {
                $.each(features, function(index, f){
                    _addResourceFunc(f)
                })
                
                if (vm.selectedFeatures.getLength() > 0) {
                    var loadedFeature = null
                    for(var index = vm.selectedFeatures.getLength() - 1; index >= 0; index--) {
                        var f = vm.selectedFeatures.item(index)
                        loadedFeature = features.find(function(f1){return f1.get('deviceid') === f.get('deviceid')})
                        if (loadedFeature) {
                            vm.selectedFeatures.setAt(index, loadedFeature)
                        } else {
                            vm.selectedFeatures.removeAt(index)
                        }
                    }
                }

                vm.features.clear()
                vm.features.extend(features.sort(vm.featureOrder))
                vm.updateViewport(0)
                vm.updateFeatureFilter(0)
                //remove nonexisted deviceid from clippedFeatures
                if (loadType === "querySavedSelection") {
                    for(var index = vm.clippedFeatures.length - 1; index >= 0; index--) {
                        if (!features.find(function(f){return f.get("deviceid") === vm.clippedFeatures[index]})) {
                            vm.clippedFeatures.splice(index, 1)
                        }
                    }
                }
                trackingStatus.phaseEnd("load_resources")
            }
			//alert(vm.whoami.editVehicle)
            if ((vm.whoami.editVehicle === null || vm.whoami.editVehicle === undefined ) && features.length > 0) {
                var f = features.find(function(f) {return f.get('source_device_type') != "tracplus"})
                if (f){
                    utils.checkPermission(vm.env.resourceTrackingService + "/sss_admin/tracking/device/" + f.get('id') + "/change/","GET",function(allowed){
                        vm.whoami.editVehicle = allowed
                        processResources()
                    })
                } else {
                    processResources()
                }
            } else {
                processResources()
            }
        }
      }, {
        type: 'WFSLayer',
        name: 'Resource Tracking History',
        id: 'dpaw:resource_tracking_history',
        onadd: function(addResource) {
            return function(f){
                if (f.getGeometry() instanceof ol.geom.Point) {
                    addResource(f)
                }
            }
        }(addResourceFunc(resourceTrackingStyleFunc('dpaw:resource_tracking_history'))),
        cql_filter: false,
        getFeatureInfo: function (f) {
            if (f.getGeometry() instanceof ol.geom.Point) {
                var name = deviceLabel(f)
                var extra_device_label = deviceExtraHoverLabel(f)
                return {name:name, img:vm.map.getBlob(f, ['icon', 'tint']),
                    comments:"(" + f.get("label") + ", Heading:" + f.get("heading") + "&deg;)<br>" +
                        extra_device_label}
            } else {
                return {name:f.get("name"), img:vm.map.getBlob(f, ['icon', 'tint']), comments:"(" + f.get("startTime") + " - " + f.get("endTime") + ")"}
            }
        },
        onload: function(loadType, vectorSource, features, defaultOnload) {
            defaultOnload(loadType,vectorSource,features)
            // callback to draw the line trail after the points information is loaded
            var devices = {}
            // group by device
            features.forEach(function (feature) {
                var deviceid = feature.get("deviceid")
                if (!(deviceid in devices)) {
                  devices[deviceid] = []
                }
                devices[deviceid].push(feature)
            })
            Object.keys(devices).forEach(function (device) {
                // sort by timestamp
                devices[device].sort(vm.featureOrder)
                // pull the coordinates
                var coords = devices[device].map(function (point) {
                    point.set('label', moment(point.get('seen')).format('MMM DD HH:mm')) 
                    return point.getGeometry().getCoordinates()
                })
                // create a new linestring
                var f = devices[device][0]
                var name = deviceLabel(f)
                var feature = new ol.Feature({
                  name: name + ' path',
                  icon: f.get('icon'),
                  tint: f.get('tint'),
                  endTime: moment(f.get('seen')).format('MMM DD HH:mm'),
                  startTime: moment(devices[device][devices[device].length - 1].get('seen')).format('MMM DD HH:mm'),
                  geometry: new ol.geom.LineString(coords)
                })
                vectorSource.addFeature(feature)
            })
        }

      })

      var tools = [
        {
            name: 'Resourcetracking Select',
            label: 'Select',
            icon: 'fa-mouse-pointer',
            scope:["tracking"],
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

      trackingStatus.phaseEnd("initialize")

      trackingStatus.phaseBegin("gk-init", 30, "Listen 'gk-init' event")
      // post init event hookup
      this.$on('gk-init', function () {
        trackingStatus.phaseEnd("gk-init")

        trackingStatus.phaseBegin("attach_events", 10, "Attach events")
        vm.map.olmap.getView().on('propertychange', function() {vm.updateViewport()})

        /*var layersAdded = global.debounce(function () {
          var mapLayer = vm.trackingMapLayer
          if (!mapLayer) { return }
          if (!mapLayer.get('tracking')) {
            mapLayer.set('tracking', mapLayer.getSource().on('loadsource', viewChanged))
          }
        }, 100)
        vm.map.olmap.getLayerGroup().on('change', layersAdded)
        layersAdded()*/

        vm.selectedFeatures.on('add', function (event) {
            vm.selectRevision += 1
        })
        vm.selectedFeatures.on('remove', function (event) {
            vm.selectRevision += 1
        })


        vm.map.olmap.on("removeLayer",function(ev){
          if (ev.mapLayer.get('id') === "dpaw:resource_tracking_live") {
              vm.features.clear()
              vm._featurelist.clear()
          }
        })

        vm._resolutionChanged = debounce(function(ev){
            vm.featureLabelDisabled = (vm.map.olmap.getView().getResolution() >= 0.003)
            vm.featureDirDisabled = (vm.map.olmap.getView().getResolution() >= 0.003)
        },200)

        vm._resolutionChanged()
        vm.map.olmap.getView().on("change:resolution",function(){
            vm._resolutionChanged()
        })

        trackingStatus.phaseEnd("attach_events")

        trackingStatus.phaseBegin("init_tools", 10, "Initialize tools")
        //vm.annotations.setDefaultTool('tracking','Pan')
        
        $.each([vm.annotations.ui.defaultPan],function(index,t) {
            t.scope = t.scope || []
            t.scope.push("tracking")
        })

        vm.tools = vm.annotations.tools.filter(function (t) {
          return t.scope && t.scope.indexOf("tracking") >= 0
        })

        trackingStatus.phaseEnd("init_tools")
      })
    }
  }
</script>
