<template>
    <form id="get_weatherforecast" name="weatherforecast" action="{{env.gokartService + '/weatherforecast'}}" method="post" target="weatherforecast">
        <input type="hidden" name="data" id="weatherforecast_data">
    </form>
</template>

<style>
</style>

<script>
  import { ol,$,utils} from 'src/vendor.js'
  export default {
    store: {
    },
    data: function () {
      return {
        forecastTool:{},
        forecastTools:[
            {toolid:"incident-weather-forecast",title:"Incident Weather Forecast",icon:"/dist/static/images/weather-forecast.svg"}
        ],
      }

    },
    // parts of the template to be computed live
    computed: {
      loading: function () { return this.$root.loading },
      map: function () { return this.$root.map },
      annotations: function () { return this.$root.annotations },
      env: function () { return this.$root.env },
      isControlSelected:function() {
        if (this.annotations) {
            return this.annotations.tool === this._weatherforecastTool
        } else {
            return false
        }
      },
      tools:function() {
        return this.forecastTools
      }
    },
    watch:{
      isControlSelected:function(newValue,oldValue) {
        if (newValue) {
            this._overlay.setMap(this.map.olmap)
        } else {
            this._overlay.setMap(null)
        }
      },
    },
    // methods callable from inside the template
    methods: {
      toggleTool: function (enable) {
        this.warning = false
        if (!this._weatherforecastTool) {
            this.annotations.setTool(this.annotations.currentTool,true)
        } else if (enable === true && this.annotations.tool === this._weatherforecastTool) {
            //already enabled
            return
        } else if (enable === false && this.annotations.tool !== this._weatherforecastTool) {
            //already disabled
            return
        } else if (this.annotations.tool === this._weatherforecastTool) {
            this.annotations.setTool(this.annotations.currentTool,true)
        } else  {
            this.annotations.setTool(this._weatherforecastTool)
        }
      },
      selectTool:function(tool) {
        if (this.forecastTool === tool) {
            return
        }
        this.forecastTool = tool
      },
      isToolActivated:function(tool) {
        return this.isControlSelected
      },
      setPosition:function(coordinate) {
        this._features.clear()
        this._features.push(new ol.Feature({geometry:new ol.geom.Point(coordinate)}))
      },
      getWeatherForecast:function(coordinate) {
        var vm = this
        vm._getWeatherForecast = vm._getWeatherForecast || function(coordinate,position) {
            var requestData = {
                point:coordinate,
                position:position,
                forecast_url:vm.env.weatherForecastUrl
            }
            $("#weatherforecast_data").val(JSON.stringify(requestData))
            utils.submitForm("get_weatherforecast",{width: (screen.width > 1890)?1890:screen.width, height:(screen.height > 1060)?1060:screen.height},true)
        }

        this.map.getPosition(coordinate,function(position){
            vm._getWeatherForecast.call(this,coordinate,position)
        })
        
      },
    },
    ready: function () {
      var vm = this
      this._weatherforecastStatus = vm.loading.register("weatherforecast","Weather Forecast Component")

      this._weatherforecastStatus.phaseBegin("gk-init",80,"Listen 'gk-init' event",true,true)
      var map = this.$root.map

      this.$on('gk-init', function() {
        vm._weatherforecastStatus.phaseEnd("gk-init")

        vm._weatherforecastStatus.phaseBegin("initialize",20,"Initialize",true,false)

        vm._features = new ol.Collection()
        vm._features.on("add",function(event){
          vm.getWeatherForecast(event.element.getGeometry().getCoordinates())
        })
        vm._style =  new ol.style.Style({
            image: new ol.style.Icon({
              src: "dist/static/images/pin.svg",
              anchorOrigin:"bottom-left",
              anchorXUnits:"pixels",
              anchorYUnits:"pixels",
              anchor:[8,0]
            })
        })
        vm._source = new ol.source.Vector({
            features:vm._features
        })
        vm._overlay = new ol.layer.Vector({
            source: vm._source,
            style: vm._style
        })
  
        //initialize the overlay and interactions
        var weatherforecastInter = new ol.interaction.Draw({
            source: vm._source,
            type: 'Point',
            style: vm._style
        });
  
        weatherforecastInter.on('drawend',function(){
          vm._features.clear()
        }, vm)
  
        vm._weatherforecastTool = {
          name: 'WeatherForecast',
          keepSelection:true,
          interactions:[
              weatherforecastInter
          ]
        }
  
        vm.annotations.tools.push(this._weatherforecastTool)

        vm._weatherforecastStatus.phaseEnd("initialize")
      })
        
    }
  }
</script>
