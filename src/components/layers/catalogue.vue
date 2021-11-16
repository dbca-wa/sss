<template>
  <div class="tabs-panel" id="layers-catalogue" v-cloak>
    <div class="row" id="catalogue-filter-container">
      <div class="columns">
        <div class="row collapse">
          <div class="small-6 columns">
            <select name="select" v-model="search">
              <option value="" selected>All layers</option> 
              <option v-for="filter in catalogueFilters" v-bind:value="filter[0]">{{ filter[1] }}</option>
              <option v-bind:value="search">Custom search</option>
            </select>
          </div>
          <div class="small-6 columns">
            <input id="find-layer" type="search" v-model="search" placeholder="Find a layer">
          </div>
        </div>
        <div v-show="search.length > 0 && search !== 'basemap'" class="row">
          <div class="columns text-right">
            <label for="switchBaseLayers" class="side-label">Toggle all</label>
          </div>
          <div class="small-2 text-right">
            <div class="switch tiny" title="Toggle all filtered layers">
              <input class="switch-input" title="Toggle all filtered layers" id="ctlgswall" @change="toggleAll($event.target.checked, $event)" type="checkbox" />
              <label class="switch-paddle" for="ctlgswall">
                <span class="show-for-sr">Toggle all</span>
              </label>
            </div>
          </div>
        </div>
        <div class="row" v-show="search === 'basemap'" >
          <div class="switch tiny">
            <input class="switch-input" id="switchBaseLayers" type="checkbox" v-model="swapBaseLayers" />
            <label class="switch-paddle" for="switchBaseLayers">
              <span class="show-for-sr">Switch out base layers</span>
            </label>
          </div>
          <label for="switchBaseLayers" class="side-label">Switch out base layers automatically</label>
        </div>
      </div>
    </div>
    <div class="layers-flexibleframe scroller row collapse" id="catalogue-list-container">
      <div class="columns">
        <div id="layers-catalogue-list">
          <div v-for="l in catalogue.getArray() | filterBy search in searchAttrs | orderBy 'name'" class="row layer-row" @mouseover="preview(l)" track-by="mapLayerId" @mouseleave="preview(false)" style="margin-left:0px;margin-right:0px">
            <div class="small-10">
              <a v-if="editable(l)" @click.stop.prevent="utils.editResource($event)" title="Edit catalogue entry" href="{{env.catalogueAdminService}}/admin/catalogue/record/{{l.systemid}}/change/" target="{{env.catalogueAdminService}}" class="button tiny secondary float-right short"><i class="fa fa-pencil"></i></a>
              <div class="layer-title">{{ l.name || l.id }}</div>
            </div>
            <div class="small-2">
              <div class="text-right">
                <div class="switch tiny" @click.stop v-bind:title="getMapLayer(l) === undefined?'Add to map':'Remove from map'">
                  <input class="switch-input ctlgsw" id="ctlgsw{{ $index }}" @change="onLayerChange(l, $event.target.checked)" v-bind:checked="getMapLayer(l) !== undefined"
                    type="checkbox" />
                  <label class="switch-paddle" for="ctlgsw{{ $index }}">
                    <span class="show-for-sr">Toggle layer</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-el:layerdetails class="hide">
          <div class="layerdetails row">
            <div class="columns small-12">
              <h5>{{ layer.name }}</h5>
              <img v-if="layer.legend" v-bind:src="layer.legend" class="cat-legend"/>
              <p>{{ layer.abstract }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.short.button {
    margin: 0px;
}

/* hide preview on tablets and mobile */
@media screen and (max-width: 60em) {
    .ol-previewmap {
        display: none;
    }
}

.ol-previewmap {
    width: 424px;
    height: 100vh;
    z-index: 1;
}

.ol-previewmap .ol-overviewmap-map {
    width: 100%;
    height: 100%;
    border: 0px;
    margin: 0px;
}

div.ol-previewmap.ol-uncollapsible {
  background-color: rgba(51, 61, 70, 0.9);
}

.ol-previewmap .ol-overviewmap-map .ol-overviewmap-box {
    display: none;
}

.cat-legend {
    max-height: 50vh;
}

#cat-loading {
    padding: 0.5em;
    font-style: italic;
    text-align: center;
}

.layerdetails {
    position: absolute;
    background-color: rgba(39,48,55,0.7);
    width: 100%;
    padding-bottom: 0.5em;
}

.layerdetails p {
    white-space: pre-wrap;
    font-size: 12px;
}

</style>

<script>
  import { $, ol, Vue, utils } from 'src/vendor.js'
  Vue.filter('lessThan', function(value, length) {
    return value.length < length
  })
  export default {
    store: {
        catalogueFilters:'catalogueFilters', 
        screenHeight:'layout.screenHeight',
        leftPanelHeadHeight:'layout.leftPanelHeadHeight',
        activeMenu:'activeMenu',
        activeSubmenu:'activeSubmenu',
        whoami:'whoami'
    },
    data: function () {
      return {
        layer: {},
        catalogue: new ol.Collection(),
        swapBaseLayers: true,
        search: '',
        searchAttrs: ['name', 'id', 'tags'],
        overview: false,
        layerDetails: false
      }
    },
    computed: {
      map: function () { return this.$root.$refs.app.$refs.map },
      app: function () { return this.$root.app },
      env: function () { return this.$root.env },
      utils: function () { return this.$root.utils},
      loading: function () { return this.$root.loading },
    },
    watch:{
      "search":function(newValue,oldvalue) {
        this.adjustHeight()
      }
    },
    methods: {
      editable:function(layer) {
        return layer.systemid && this.whoami.editLayer
      },  
      adjustHeight:function() {
        if (this.activeMenu === "layers" && this.activeSubmenu === "catalogue") {
            $("#catalogue-list-container").height(this.screenHeight - this.leftPanelHeadHeight - $("#catalogue-filter-container").height())
        }
      },
      setup:function() {
        this.adjustHeight()
      },
      preview: function (l) {
        if (this.layer === l) {
          return
        }
        if (this.layer.preview) {
          this.layer.preview.setMap(null)
        }
        if (!l) {
          this.layer = {}
          return
        }
        if (!l.preview) {
          l.preview = new ol.control.OverviewMap({
            className: 'ol-overviewmap ol-previewmap',
            layers: [this.$root.map['create' + l.type]($.extend({}, l, {refresh:0,previewLayer:true}))],
            collapsed: false,
            collapsible: false,
            min_ratio:1,
            max_ratio:1,
            view: new ol.View({
              projection: 'EPSG:4326'
            })
          })
        }
        l.preview.setMap(this.$root.map.olmap)
        var previewEl = $(l.preview.getOverviewMap().getViewport())
        this.layer = l
        if (!previewEl.find('.layerdetails').length > 0) {
          this.$nextTick(function() {
            previewEl.prepend(this.$els.layerdetails.innerHTML)
          })
        }
      },
      toggleAll: function (checked, event) {
        var switches = $(this.$el).find('input.ctlgsw')
        switches.attr('checked', !checked).trigger('click')
      },
	  
      // helper function to simulate a <label> style click on a row
      onToggle: function (index) {
        $(this.$el).find('#ctlgsw' + index).trigger('click')
      },
	  
      // toggle a layer in the Layer Catalogue
      //return true if layer's state is changed; otherwise return false
      onLayerChange: function (layer, checked) {
		//alert('catalogue 228 onLayerChange: ' + layer.id)
        var vm = this
        var active = this.$root.active
        var map = this.$root.map
        // if layer matches state, return
        if (checked === (map.getMapLayer(layer) !== undefined)) {
          return false
        }
        // make the layer match the state
        if (checked) {
		  var olLayer = map['create' + layer.type](layer)
          olLayer.setOpacity(layer.opacity || 1)
          if (layer.base) {
            // "Switch out base layers automatically" is enabled, remove
            // all other layers with the "base" option set.
            if (this.swapBaseLayers) {
              active.olLayers.forEach(function (mapLayer) {
                if (mapLayer.get('dependentLayer')) return
                if (vm.getLayer(mapLayer).base) {
                  active.removeLayer(mapLayer)
                }
              })
            }
            // add new base layer to bottom
            map.olmap.getLayers().insertAt(0, olLayer)
          } else {
            map.olmap.addLayer(olLayer)
          }
          this.map.olmap.dispatchEvent(this.map.createEvent(this.map, "addLayer", {mapLayer:olLayer}))
        } else {
          active.removeLayer(map.getMapLayer(layer))
        }
        return true
      },

      // helper to populate the catalogue from a remote service
      loadRemoteCatalogue: function (callback, failedCallback) {
        var vm = this
        var req = new window.XMLHttpRequest()
        req.withCredentials = true
        req.onload = function () {
          var checkingLayer = null
          var layers = []
          JSON.parse(this.responseText).forEach(function (l) {
            // overwrite layers in the catalogue with the same identifier
            i = 0
			if (vm.getLayer(l.identifier)) {
                vm.catalogue.remove(vm.getLayer(l.identifier))
				i += 1
            }
            l.systemid = l.id;
            l.id = getIndependentLayerId(l.identifier);
            // add the base flag for layers tagged 'basemap'
            l.base = l.tags.some(function (t) {return t.name === 'basemap'})
            // set the opacity to 50% for layers tagged 'overlaymap'
            if (l.tags.some(function (t) { return t.name === 'overlaymap' })) {
                l.opacity = 0.5
            }
            // set the live map refresh interval
            if (l.tags.some(function (t) { return t.name === 'livemap_10min' })) {
                l.refresh = 600
            }
            if (l.tags.some(function (t) { return t.name === 'livemap_2min' })) {
                l.refresh = 120
            }
            if (!checkingLayer) {
                checkingLayer = l
            }
            layers.push(l)
          })
          if (checkingLayer) { 
			 utils.checkPermission(vm.env.catalogueAdminService + "/admin/catalogue/record/" + checkingLayer.systemid + "/change/", "GET", function(allowed){
                vm.whoami.editLayer = allowed
				vm.catalogue.extend(layers)
				/*var my_array = vm.catalogue.getArray()
				var arrayLength = my_array.length;
				for (var i = 0; i < arrayLength; i++) {
				alert(my_array[i]['name'] + ", "  + my_array[i]['id']  + ", "  +  my_array[i]['title'] )}*/
                callback()
              })
          } else {
              vm.whoami.editLayer = false
              vm.catalogue.extend(layers)
              callback()
          }
        }

        req.onerror = function (ev) {
          var msg ='Couldn\'t load layer catalogue!' +  (req.statusText? (" (" + req.statusText + ")") : '')
          if (failedCallback) {
            failedCallback(msg)
          } else {
            console.error(msg)
          }
        }
		req.open('GET', vm.env.cswService + "?format=json&application__name=" + getAppId(this.app.toLowerCase()))
        req.send()
      },
      getLayer: function (id) {
        // handle openlayers layers as well as raw ids
        if (id && id.get) { id = id.get('id') }
        return this.catalogue.getArray().find(function (layer) {
          return layer.mapLayerId === id
        })
      },
      getMapLayer: function (id) {
        return this.$root.map.getMapLayer(id)
      }
    },
    ready: function () {
	  var vm = this
      var catalogueStatus = vm.loading.register("catalogue", "Catalogue Component")
      this.catalogue.on('add', function (event) {
        var l = event.element
        l.id = l.id || l.identifier
        l.name = l.name || l.title
        l.type = l.type || 'TileLayer'
		
        if (l.type === 'TileLayer') {
          if (l.legend) {
            if (!(l.legend.toLowerCase().startsWith("http"))) {
                l.legend = vm.env.catalogueAdminService + l.legend
            }
          } else {
            l.legend = (l.service_type === "WFS")?(vm.env.legendSrc + getLayerId(l.id)):null
          }
        }
        l.mapLayerId = l.mapLayerId || l.id
        if (l.dependentLayers) {
            $.each(l.dependentLayers,function(index,layer){
                layer.mapLayerId = layer.mapLayerId || layer.id
            })
        }

        if (l.refresh) {
            vm.map.setRefreshInterval(l,l.refresh)
        }
      })
      catalogueStatus.phaseBegin("gk-init", 80, "Listen 'gk-init' event", true, true)
      this.$on('gk-init', function() {
        catalogueStatus.phaseEnd("gk-init")

        catalogueStatus.phaseBegin("initialize", 20, "Initialize", true, false)
        $(this.$root.map.olmap.getTargetElement()).on('mouseleave', '.ol-previewmap', function() {
            vm.preview(false)
        })
        catalogueStatus.phaseEnd("initialize")
      })
    }
  }
</script>
