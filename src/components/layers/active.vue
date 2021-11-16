<template>
  <div class="tabs-panel is-active" id="layers-active" v-cloak>

    <div class="layers-flexibleframe scroller row" id="layers-active-list-container">
      <div class="columns">

        <div id="layers-active-list">
          <div v-for="l in olLayers" track-by="values_.id" class="row feature-row status-row" 
            v-bind:class="layerRefreshProgress(l)" data-id="{{ l.get('id') }}" @click="layer = getLayer(l.get('id'))">
            <div class="small-9">
              <div class="layer-title">{{ l.get("name") || l.get("id") }} - {{ Math.round(l.getOpacity() * 100) }}%</div>
              <small v-if="layerRefreshStatus(l)" style="white-space:pre-wrap">Updated: {{ layerRefreshStatus(l) }}</small>
            </div>
            <div class="small-3">
              <div class="text-right">
                <a @click.stop="toggleHidden(l)" class="button small icon2x" v-bind:class="{success:!isHidden(l),warning:isHidden(l)}" v-bind:title="isHidden(l)?'Show in map':'Hide in map'">
                    <i class="fa fa-eye-slash fa-2x" v-if="isHidden(l)" > </i>
                    <i class="fa fa-eye fa-2x" v-if="!isHidden(l)"> </i>
                </a>
                <a @click="removeLayer(l)" class="button small icon2x alert remove-layer" title="Remove from map">
                    <i class="fa fa-close fa-2x" > </i>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="row collapse scroller" id="layer-config-container">
      <hr class="small-12"/>
      <div id="layer-config" class="columns">
        <h4 v-if="layer && mapLayer()">{{ layer.name }}</h4>
        <div class="tool-slice row" v-if="layerRefreshConfigable()">
          <div class="columns small-3"><label class="tool-label">Refresh:<br/>{{ formattedLayerRefreshInterval }}</label></div>
          <div class="columns small-8">
            <input class="layer-opacity" v-if="layerRefreshIntervalConfigable()" type="range" v-bind:min="layer.min_interval" v-bind:max="layer.max_interval" v-bind:step="layer.interval_step || 1" v-model="layerRefreshInterval">
          </div>
          <div class="columns small-1">
            <a title="Stop auto refresh" v-if="!layerRefreshStopped" class="button tiny secondary float-right" @click="stopLayerRefresh()" ><i class="fa fa-stop"></i></a>
            <a title="Start auto refresh" v-if="layerRefreshStopped"class="button tiny secondary float-right" @click="startLayerRefresh()" ><i class="fa fa-play"></i></a>
          </div>
        </div>
        <div class="tool-slice row" v-if="layer && mapLayer()">
          <div class="columns small-3"><label class="tool-label">Transparency:<br/>{{ layerOpacity }}%</label></div>
          <div class="columns small-9"><input class="layer-opacity" type="range" min="0" max="100" step="1" v-model="layerOpacity"></div>
        </div>
        <div class="tool-slice row" v-if="layer.timeline && mapLayer()">
          <div class="columns small-3"><label class="tool-label">Timeline:</label></div>
          <div class="columns small-9"><input type="range" v-bind:disabled="sliderMax < 0" v-bind:max="sliderMax" min="0" step="1" v-model="sliderTimeline" title="{{layer.timeline.length}} layers"></div>
          <div class="columns small-12"><label class="tool-label">{{ timelineTS }}</label></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { Vue, dragula,moment } from 'src/vendor.js'
  export default {
    store:{
        screenHeight:'layout.screenHeight',
        leftPanelHeadHeight:'layout.leftPanelHeadHeight',
        activeMenu:'activeMenu',
        activeSubmenu:'activeSubmenu'
    },
    // variables
    data: function () {
      return {
        sliderOpacity: 0,
        layer: {},
        layerRefreshStopped:false,
        refreshRevision:1,
        allMapLayers: [],
        timeIndex:0
      }
    },
    // parts of the template to be computed live
    computed: {
      map: function () { return this.$root.map },
      sliderTimeline: {
        get: function () {
          var mapLayer = this.mapLayer()
          this.timeIndex = mapLayer?(mapLayer.get('timeIndex') || 0):0
          return this.timeIndex
        },
        set: function (val) {
          this.mapLayer().set('timeIndex', val)
          this.refreshRevision += 1
          this.timeIndex = val
        }
      },
      olLayers:function() {
        var layers = []
        for (var index = this.allMapLayers.length - 1;index >= 0;index--) {
            if (this.allMapLayers[index].dependentLayer === true) continue
            layers.push(this.allMapLayers[index])
        }
        return layers
      },
      timelineTS: function () {
        var mapLayer = this.mapLayer()
        try{
            return this.refreshRevision && this.layer.timeline[mapLayer?(mapLayer.get('timeIndex') || 0):0][0]
        } catch(ex) {
            return this.refreshRevision && ""
        }
      },
      sliderMax: function () {
        return this.layer.timeline.length - 1
      },
      layerOpacity: {
        get: function () {
          return Math.round(this.mapLayer().getOpacity() * 100)
        },
        set: function (val) {
          this.mapLayer().setOpacity(val / 100)
        }
      },
      layerRefreshInterval: {
        get: function () {
          return this.refreshRevision && this.layer.refresh
        },
        set: function (val) {
          var vm = this
          this.refreshRevision += 1
          vm.map.setRefreshInterval(vm.layer,val)
          if (vm.layerRefreshStopped) {
            return
          }
          vm.layer.changeRefreshInterval = vm.layer.changeRefreshInterval || global.debounce(function () {
            vm.mapLayer().stopAutoRefresh()
            vm.mapLayer().startAutoRefresh()
          }, 5000)

          vm.layer.changeRefreshInterval()
                  
        }
      },
      formattedLayerRefreshInterval: function() {
        if (this.layerRefreshStopped) {
          return this.refreshRevision && "Stopped"
        } else {
          var format = "H\\hm\\ms\\s"
          if (this.layer.refresh < 60) {
            format = "s\\s"
          } else if (this.layer.refresh < 3600) {
            format = "m\\ms\\s"
          }
          return this.refreshRevision && moment(new Date(this.layer.refresh * 1000)).utc().format(format) 
        }
      },
    },
    watch: {
      "layer": function() {
        this.layerRefreshStopped = this.layer.refresh?(this.layer.autoRefreshStopped || false):true
      },
    },
    // methods callable from inside the template
    methods: {
      adjustHeight:function() {
        if (this.activeMenu === "layers" && this.activeSubmenu === "active") {
            var height = this.screenHeight - this.leftPanelHeadHeight - 180
            if (height > 65) {
                $("#layers-active-list-container").height(height)
                if ($("#layer-config-container").height() < 180) {
                    $("#layer-config-container").height(180)
                }
            } else if (height <= -30) {
                $("#layers-active-list-container").height(this.screenHeight - this.leftPanelHeadHeight)
                $("#layer-config-container").height(0)
            } else {
                $("#layers-active-list-container").height(65)
                $("#layer-config-container").height(this.screenHeight - this.leftPanelHeadHeight - 65)
            }
        }
      },
      setup:function() {
        this.adjustHeight()
      },
      isHidden:function(layer) {
        return layer?(layer.getOpacity() === 0):undefined
      },
      toggleHidden:function(layer) {
        if (this.isHidden(layer)) {
            layer.setOpacity(1)
        } else {
            layer.setOpacity(0)
        }
      },
      stopLayerRefresh:function() {
        this.mapLayer().stopAutoRefresh()
        this.layer.autoRefreshStopped = true
        this.layerRefreshStopped = true
      },
      startLayerRefresh:function() {
        this.mapLayer().startAutoRefresh()
        this.layer.autoRefreshStopped = false
        this.layerRefreshStopped = false
      },
      layerRefreshConfigable:function(id) {
        var layer = id?this.getLayer(id):this.layer
        return (layer && this.mapLayer(layer) && (layer.type === "WFSLayer" || layer.type === "TileLayer") && layer.refresh)?true:false
      },
      layerRefreshIntervalConfigable:function(id) {
        var layer = id?this.getLayer(id):this.layer
        return ((layer.type === "WFSLayer" || layer.type === "TileLayer") && layer.refresh && layer.min_interval && layer.max_interval)?true:false
      },
      layerRefreshProgress: function(l) {
        return this.refreshRevision && (l.progress || "")
      },
      layerRefreshStatus: function(l) {
        return this.refreshRevision && l && l.get("updated") || ""
      },
      activeLayers: function () {
        var catalogue = this.$root.catalogue
        var results = []
        var success = this.olLayers.every(function (layer) {
          // catlayer doesn't exist at startup, need to
          // persist relevant catalogue entries perhaps?
          var catLayer = catalogue.getLayer(layer)
          if (!catLayer) {
            return false
          }
          var options = {
            id: layer.get('id'),
            //name: layer.get('name'),
            //type: catLayer.type,
            opacity: layer.getOpacity()
          }
          results.push([layer.get('id'), options])
          return true
        })
        if (!success) {
          return false
        }
        return results
      },
      mapLayer: function (id) { 
        if (!this.$root.map) {
          return null
        }
        return this.$root.map.getMapLayer(id || this.layer) 
      },
      getLayer: function (id) {
        return this.$root.catalogue.getLayer(id)
      },
      removeLayer: function (olLayer) {
        var layer = olLayer.layer
        if (this.layer === layer) {
            this.layer = {}
        }

        this.map.olmap.removeLayer(olLayer)
        this.map.olmap.dispatchEvent(this.map.createEvent(this.map,"removeLayer",{mapLayer:olLayer,layer:layer}))
      },
      // change order of OL layers based on "Map Layers" list order
      updateOrder: function (el) {
        var map = this.$root.map
        Array.prototype.slice.call(el.parentNode.children).reverse().forEach(function (row) {
          var mapLayer = map.getMapLayer(row.dataset.id)
          map.olmap.removeLayer(mapLayer)
          map.olmap.addLayer(mapLayer)

          map.olmap.dispatchEvent(map.createEvent(map,"changeLayerOrder",{mapLayer:mapLayer}))
        })
      }
    },
    ready: function () {
      dragula([document.querySelector('#layers-active-list')]).on('drop', this.updateOrder)
      this.$on('gk-init', function () {
        this.allMapLayers = this.$root.map.olmap.getLayers().getArray()
      })
    }
  }
</script>
