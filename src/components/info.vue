<template>
  <div id="info" v-bind:style="css" v-show="features" v-cloak>
    <!--div class="row collapse">
      <div class="columns title">
        <h5>{{ featuresLength }} {{ featuresLength | pluralize 'feature' }} <small>{{ coordinate }}</small></h5>
      </div>
      <button class="close-button float-right" aria-label="Dismiss info" type="button" v-on:click="features = false"><span aria-hidden="true">&times;</span></button>
    </div-->
    <div class="row">
      <div class="columns content">
        <div v-for="f in features" class="row feature-row" v-bind:class="{'feature-selected': selected(f[0]) }" v-bind:key="f[0].get('id')">
          <div class="feature-title">
            <img v-if="featureInfo(f[0],f[1]).img" class="feature-icon" v-bind:src="featureInfo(f[0],f[1]).img"/>
            <svg v-if="featureInfo(f[0],f[1]).svg" class="feature-icon"><use v-bind="{'xlink:href':featureInfo(f[0],f[1]).svg}"></use></svg>
            <i v-if="featureInfo(f[0],f[1]).icon" class="feature-icon" v-bind:class="featureInfo(f[0],f[1]).icon" aria-hidden="true"></i>
            {{featureInfo(f[0],f[1]).name}} <i v-if="featureInfo(f[0],f[1]).comments"><small>{{{featureInfo(f[0],f[1]).comments}}}</small></i>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
  .feature-icon {
    width: 24px;
    height: 24px;
  }
</style>

<script>
  import { ol } from 'src/vendor.js'
  export default {
    store: {
        hoverInfo:'settings.hoverInfo'
    },
    data: function () {
      return {
        features: false,
        hoverable: [],
        coordinate: '',
        offset: 0,
        pixel: [0, 0]
      }
    },
    // parts of the template to be computed live
    computed: {
      map: function () { return this.$root.$refs.app.$refs.map },
      catalogue: function () { return this.$root.catalogue },
      annotations: function () { return this.$root.$refs.app.$refs.annotations },
      loading: function () { return this.$root.loading },
      featuresLength: function () {
        return Object.keys(this.features).length
      },
      // info panel should be positioned near the mouse in the quadrant furthest away from the viewport edges
      css: function () {
        var map = this.$root.map
        var css = {
          'left': this.pixel[0] + this.offset + 'px',
          'top': this.pixel[1] + this.offset + 'px',
          'bottom': map.height - this.pixel[1] + this.offset + 'px',
          'right': map.width - this.pixel[0] + this.offset + 'px',
          'display': 'none'
        }
        if (this.pixel[0] < map.width / 2) {
          delete css.right
        } else {
          delete css.left
        }
        if (this.pixel[1] < map.height / 2) {
          delete css.bottom
        } else {
          delete css.top
        }
        if (this.pixel[0] > 0 && this.enabled) {
          delete css.display
        }
        return css
      },
      enabled: function() {
        return this.hoverInfo && this.$root.annotations.tool.name === "Pan"
      }
    },
    // methods callable from inside the template
    methods: {
      // update the panel content
      onPointerMove: function (event) {
        var vm = this
        if (event.dragging || !this.enabled) {
          return
        }
        if (!vm.hoverable || vm.hoverable.length === 0) {
            return
        }

        var pixel = this.$root.map.olmap.getEventPixel(event.originalEvent)
        var features = []
        this.$root.map.olmap.forEachFeatureAtPixel(pixel, function (f,layer) {
          if (vm.hoverable.indexOf(layer) >=0 ) {
              features.push([f,layer])
          }
        })
        if (features.length > 0) {
          this.features = features
          this.coordinate = ol.coordinate.toStringXY(this.$root.map.olmap.getCoordinateFromPixel(pixel), 3)
          this.pixel = pixel
        } else {
          // hide when no features
          this.pixel.$set(0, 0)
          this.features = false
        }
      },
      selected: function (f) {
        return this.$root.annotations.selectedFeatures.getArray().indexOf(f) > -1
      },
      featureInfo: function(feature,mapLayer) {
        if (this._feature === feature) {
            return this._featureInfo
        }
        var layer = mapLayer?this.catalogue.getLayer(mapLayer.get('id')):null 
        if (layer && layer.getFeatureInfo) {
            this._featureInfo = layer.getFeatureInfo(feature)   
        } else {
            this._featureInfo = {"name":feature.getId(),img:false,svg:false,icon:false,comments:false}
        }

        this._feature = feature
        return this._featureInfo
      }
    },
    ready: function () {
      var vm = this
      var infoStatus = vm.loading.register("info","Info Component")
      infoStatus.phaseBegin("gk-init",80,"Listen 'gk-init' event",true,true)
      this.$on('gk-init', function () {
        infoStatus.phaseEnd("gk-init")
        infoStatus.phaseBegin("initialize",20,"Initialize",true,false)
        // display hover popups
        this.$root.map.olmap.on('pointermove', this.onPointerMove)
        infoStatus.phaseEnd("initialize")
      })
    }
  }
</script>
