<template>
  <div id="map-measure-tooltips"></div>
</template>

<style>
#map-measure button {
    width: 48px;
    height: 48px;
    margin: 0;
}

#map-measure button {
    margin-bottom: 1px;
}

  .feature-icon {
    width: 24px;
    height: 24px;
  }
  #map-measure {
    position: absolute;
    left: auto;
    right: 16px;
    bottom: auto;
    padding: 0;
  }
  #map-measure .selected{
    background-color: #2199E8;
  }
</style>

<script>
  import { ol,$} from 'src/vendor.js'
  export default {
    store: ['settings'],
    data: function () {
      return {
      }

    },
    // parts of the template to be computed live
    computed: {
      loading: function () { return this.$root.loading },
      map: function () { return this.$root.map },
      active: function () { return this.$root.active },
      featuredetail: function () { return this.$root.featuredetail },
      catalogue: function () { return this.$root.catalogue },
      annotations: function () { 
        return this.$root.$refs.app.$refs.annotations 
      },
      measureType: function() {
        if (["MeasureLength","MeasureArea","MeasureBearing"].indexOf(this.annotations.tool.name) >= 0) {
            return this.annotations.tool.name
        } else {
            return ""
        }
      },
      showClear: function () {
        return this.measureType != "" && this.features.getLength()
      },
      isMeasureLength: function () {
        return this.measureType === "MeasureLength"
      },
      isMeasureArea:function() {
        return this.measureType === "MeasureArea"
      },
      isMeasureBearing:function() {
        return this.measureType === "MeasureBearing"
      },
      lengthUnit: function() {
        return this.settings.lengthUnit
      },
      areaUnit: function() {
        return this.settings.areaUnit
      },
      measureFeature:function() {
        return this.settings.measureFeature
      },
      tools:function() {
        return [
            {
                toolid:"MeasureLength",
                title:"Measure Length",
                icon:"/dist/static/images/measure-length.svg",
                assistantButtons:[
                    {name:"Clear", title:"Clear Measurements",icon:"/dist/static/images/clear.svg"}
                ]
            },{
                toolid:"MeasureArea",
                title:"Measure Area",
                icon:"/dist/static/images/measure-area.svg",
                assistantButtons:[
                    {name:"Clear", title:"Clear Measurements",icon:"/dist/static/images/clear.svg"}
                ]
            },{
                toolid:"MeasureBearing",
                title:"Measure Bearing",
                icon:"/dist/static/images/measure-bearing.svg",
                assistantButtons:[
                    {name:"Clear", title:"Clear Measurements",icon:"/dist/static/images/clear.svg"}
                ]
            },
        ]
      },
    },
    watch:{
        lengthUnit:function(newValue,oldValue) {
            var vm = this
            var geom = null
            this.features.forEach(function(feature) {
                vm.measuring(feature,null,true,false,false,"changeUnit",true) 
            })

            $.each(vm._measureLayers,function(index,layer){
                layer[1].forEach(function(feature) {
                    var tool = vm.annotations.getTool(feature.get('toolName'))
                    if (tool.measureLength) {
                        vm.measuring(feature,tool?tool.getMeasureGeometry:null,true,false,false,"changeUnit") 
                    }
                })
            })
        },
        areaUnit:function(newValue,oldValue) {
            var vm = this
            this.features.forEach(function(feature) {
                vm.measuring(feature,null,false,true,false,"changeUnit",true) 
            })

            $.each(vm._measureLayers,function(index,layer){
                layer[1].forEach(function(feature){
                    var tool = vm.annotations.getTool(feature.get('toolName'))
                    if (tool.measureArea) {
                        vm.measuring(feature,tool?tool.getMeasureGeometry:null,false,true,false,"changeUnit") 
                    }
                })
            })
        },
        measureFeature:function(newValue,oldValue) {
            var vm = this
            $.each(this._measureLayers,function(index,layer) {
                var mapLayer = vm.map.getMapLayer(layer[0])
                if (mapLayer && !vm.active.isHidden(mapLayer)) {
                    vm.enableLayerMeasurement(layer,newValue)
                }
            })
        },
        measureType:function(newVal,oldVal){
            if (newVal === "") {
                //switchoff
                if (this.overlay) {
                    this.overlay.setMap(null)
                }
                if (this.drawingFeature) {
                    this.removeTooltip(this.drawingFeature)
                    this.drawingFeature = null
                }
                //hidden measuretips
                this.showTooltip(this.features,false)
            } else if (oldVal === ""){
                //switchon
                this.overlay.setMap(this.map.olmap)
                this.showTooltip(this.features,true)
            } else {
                //switch measure type
                if (this.drawingFeature) {
                    this.removeTooltip(this.drawingFeature)
                    this.drawingFeature = null
                }
            }
        },
    },
    // methods callable from inside the template
    methods: {
      //layer can be layer id, layer object
      register:function(layer,features,filter) {
        this._measureLayers = this._measureLayers || []
        this._measureLayers.push([layer["id"] || layer,features || null, filter||null,{}])
      },
      selectTool:function(tool) {
      },
      toggleTool: function (enable,tool) {
          this.toggleMeasure(tool.toolid,enable)

      },
      isToolActivated:function(tool) {
        return this.measureType !== ""
      },
      showAssistantButton:function(button) {
        return this.showClear
      },
      clickAssistantButton:function(button) {
        this.clearMeasure()
      },
      //layer can be layerid, layer object, and memeber of this._measureLayers
      enableLayerMeasurement:function(layer,enable) {
        var vm = this
        var layer = (Array.isArray(layer))?layer:this._measureLayers.find(function(l) {return l[0] === (layer["id"] || layer)})
        if (!layer) return
        if(enable) {
            //enable
            //register the add /remove listener for features
            layer[3]["features_remove"] = layer[3]["features_remove"] || layer[1].on("remove",function(ev){
                var feature = ev.element
                if (feature.tooltip) {
                    vm.removeTooltip(feature)
                }
            })

            layer[3]["features_add"] = layer[3]["features_add"] || layer[1].on("add",function(ev){
                if (vm.map.getMapLayer(layer[0])) {
                    var feature = ev.element
                    if (!layer[2] || layer[2](feature)) {
                        var tool = vm.annotations.getTool(feature.get('toolName'))
                        if (!tool) {return}
                        if (tool.measureLength || tool.measureArea) {
                            if (vm.measureFeature) {
                                vm.createTooltip(feature,tool.getMeasureGeometry,tool.measureLength,tool.measureArea)
                                vm.measuring(feature,tool.getMeasureGeometry,tool.measureLength,tool.measureArea,false,"show")
                            }
                        }
                    }
                }
            })


            var mapLayer = vm.map.getMapLayer(layer[0])
            if (mapLayer && !mapLayer._change_opacity) {
                mapLayer._change_opacity = mapLayer._change_opacity || mapLayer.on("change:opacity",vm._changeOpacityHandler)
            }


            $.each(layer[1].getArray(),function(index,feature){
                var tool = vm.annotations.getTool(feature.get('toolName'))
                if (!tool) {return}
                if (!tool.measureLength && !tool.measureArea) {return}
                if (feature.tooltip) {
                    vm.showTooltip(feature,true)
                    if (!feature.get("measurement")) {
                        vm.measuring(feature,tool.getMeasureGeometry,tool.measureLength,tool.measureArea,false,"show")
                    }
                } else {
                    vm.createTooltip(feature,tool.getMeasureGeometry,tool.measureLength,tool.measureArea)
                    vm.measuring(feature,tool.getMeasureGeometry,tool.measureLength,tool.measureArea,false,"show")
                }
            })
        } else {
            if (layer[3]["features_remove"]) {
                layer[1].unByKey(layer[3]["features_remove"])
                delete layer[3]["features_remove"] 
            }

            if (layer[3]["features_add"]) {
                layer[1].unByKey(layer[3]["features_add"])
                delete layer[3]["features_add"] 
            }

            //disable
            this.showTooltip(layer[1],false)
        }
      },
      clearFeatureMeasurement:function(feature) {
        var vm = this
        vm._clearFeatureMeasurement = vm._clearFeatureMeasurement || function(feat) {
            if (!feat) return
            this.removeTooltip(feat,true) 
            feat.unset("measurement",true)
        }
        if (feature instanceof ol.Collection) {
            feature.forEach(function(feat) {
                vm._clearFeatureMeasurement(feat)
            })
        } else if (Array.isArray(feature)) {
            $.each(feature,function(index,feat) {
                vm._clearFeatureMeasurement(feat)
            })
        } else {
            vm._clearFeatureMeasurement(feature)
        }
      },
      remeasureFeature:function(feature) {
        var vm = this
        vm._remeasureFeature = vm._remeasureFeature || function(feat) {
            if (!feat) return
            var tool = vm.annotations.getTool(feat.get('toolName'))
            if (!tool) {return}
            if (!(tool.measureLength || tool.measureArea || tool.measureBearing)) {return}

            this.removeTooltip(feat,true) 
            feat.unset("measurement",true)

            vm.createTooltip(feat,tool.getMeasureGeometry,tool.measureLength,tool.measureArea)
            vm.measuring(feat,tool.getMeasureGeometry,tool.measureLength,tool.measureArea,false,"show")
        }
        if (feature instanceof ol.Collection) {
            feature.forEach(function(feat) {
                vm._remeasureFeature(feat)
            })
        } else if (Array.isArray(feature)) {
            $.each(feature,function(index,feat) {
                vm._remeasureFeature(feat)
            })
        } else {
            vm._remeasureFeature(feature)
        }
      },
      toggleMeasure: function (type,enable) {
        if (enable === true && this.measureType === type) {
            //already enabled
            return 
        } else if (enable === false && this.measureType !== type) {
            //already disabled
            return
        } else if (this.measureType === type) {
            this.annotations.setTool(this.annotations.currentTool,true)
        } else  {
            this.annotations.setTool(type)
        }
      },
      clearMeasure:function() {
        var vm = this
        if (this.features) {
            this.features.clear()
        }
        if (this.drawingFeature) {
            this.removeTooltip(this.drawingFeature)
            this.drawingFeature = null
        }
        if (this.measureType) {
            //readd the interact to remove the drawing features.
            $.each(this.annotations.tool.interactions,function(index,interact){
                vm.map.olmap.removeInteraction(interact)       
            })
            $.each(this.annotations.tool.interactions,function(index,interact){
                vm.map.olmap.addInteraction(interact)       
            })
        }
      },
      startMeasureFunc:function(measureLength,measureArea,measureBearing){
        var vm = this
        return function(evt) {
            //console.log("Start measure")
            // set feature
            vm.drawingFeature = evt.feature

            vm.createTooltip(vm.drawingFeature,null,measureLength,measureArea,measureBearing,true)

            vm.geometryChangeHandler = vm.drawingFeature.getGeometry().on('change', function(feature,measureLength,measureArea,measureBearing){
                return function(evg) {
                    vm.measuring(feature,null,measureLength,measureArea,measureBearing,"drawing",true)
                }
            }(vm.drawingFeature,measureLength,measureArea,measureBearing))
        }
      },
      measuring: function(feature,getMeasureGeometry,measureLength,measureArea,measureBearing,mode,measureFeature,indexes) {
        var vm = this
        this._measure = this._measure || function(feature,geom,tooltipElement,tooltip,measurement,measureLength,measureArea,measureBearing,mode) {
            if (!tooltipElement) {
                return measurement
            } else if (geom instanceof ol.geom.LineString || geom instanceof ol.geom.Polygon) {
                if (
                    (geom instanceof ol.geom.LineString && (measureLength || measureBearing)) || 
                    (geom instanceof ol.geom.Polygon && measureLength)
                ) {
                    measurement = measurement || {}
                    var length = null
                    if (!measurement["length"] || mode === "drawing") {
                        if (geom instanceof ol.geom.LineString) {
                            length = vm.getLength(geom.getCoordinates())
                        } else if(geom instanceof ol.geom.Polygon) {
                            length = vm.getLength(geom.getLinearRing(0).getCoordinates())
                        }
                        measurement["length"] = length
                    } else {
                        length = measurement["length"]
                    }
                    if (measureLength) {
                        tooltipElement.find(".length").html(vm.formatLength(length))
                    }
                }
                if (measureArea && geom instanceof ol.geom.Polygon) {
                    measurement = measurement || {}
                    var area = null
                    if (!measurement["area"] || mode === "drawing") {
                        /*
                        var sourceProj = vm.$root.map.olmap.getView().getProjection()
                        var geom = (polygon.clone().transform(
                            sourceProj, 'EPSG:4326'))
                        */
                        area = vm.getArea(geom)
                        measurement["area"] = area
                    } else {
                        area = measurement["area"]
                    }
                    tooltipElement.find(".area").html(vm.formatArea(area))
                }
                if (measureBearing && geom instanceof ol.geom.LineString) {
                    measurement = measurement || {}
                    var bearing = null
                    if (!measurement["bearing"] || mode === "drawing") {
                        var coordinates = geom.getCoordinates()
                        bearing = Math.round(vm.getBearing(coordinates[0],coordinates[coordinates.length - 1]) * 100) / 100 + "&deg;"
    
                        bearing = "<span style='color:red;font-weight:bold'>" + bearing + "\n" + vm.formatLength(measurement["length"],"nm") + "</span>\n" + vm.formatLength(measurement["length"],"km")
                        measurement["bearing"] = bearing
                    } else {
                        bearing = measurement["bearing"]
                    }
                    tooltipElement.find(".bearing").html(bearing)
                }
                if (mode === "drawing" || mode === "show" || mode === "measure") {
                    var tooltipCoord = null
                    if (geom instanceof ol.geom.Polygon) {
                        tooltipCoord = geom.getInteriorPoint().getCoordinates()
                    } else if (geom instanceof ol.geom.LineString) {
                        if (measureBearing) {
                            tooltipCoord = geom.getCoordinateAt(0.5)
                        } else {
                            tooltipCoord = geom.getLastCoordinate()
                        }
                    }
                    tooltip.setPosition(tooltipCoord)
                }
                if (mode === "show") {
                    tooltipElement.get(0).className = 'tooltip-measure tooltip-measured'
                    tooltip.setOffset([0, -7])
                } else if(mode === "measure") {
                    tooltipElement.get(0).className = 'tooltip-measure tooltip-measured'
                    if (tooltip.getMap()) {
                        vm.map.olmap.removeOverlay(tooltip)
                    }
                }
                return measurement
            } else if (geom instanceof ol.geom.MultiPolygon && (measureLength || measureArea)) {
                measurement = measurement || []
                $.each(geom.getPolygons(),function(index,p){
                    if (index >= measurement.length) {
                        measurement.push(vm._measure(feature,p,tooltipElement[index],tooltip[index],null,measureLength,measureArea,measureBearing,mode))
                    } else {
                        measurement[index] = vm._measure(feature,p,tooltipElement[index],tooltip[index],measurement[index],measureLength,measureArea,measureBearing,mode)
                    }
                })
                return measurement
            } else if (geom instanceof ol.geom.MultiLineString && (measureLength || measureBearing)) {
                measurement = measurement || []
                $.each(geom.getLineStrings(),function(index,p){
                    if (index >= measurement.length) {
                        measurement.push(vm._measure(feature,p,tooltipElement[index],tooltip[index],null,measureLength,measureArea,measureBearing,mode))
                    } else {
                        measurement[index] = vm._measure(feature,p,tooltipElement[index],tooltip[index],measurement[index],measureLength,measureArea,measureBearing,mode)
                    }
                })
                return measurement
            } else if (geom instanceof ol.geom.GeometryCollection && (measureLength || measureBearing || measureArea)) {
                measurement = measurement || []
                $.each(geom.getGeometriesArray(),function(index,p){
                    if (index >= measurement.length) {
                        measurement.push(vm._measure(feature,p,tooltipElement[index],tooltip[index],null,measureLength,measureArea,measureBearing,mode))
                    } else {
                        measurement[index] = vm._measure(feature,p,tooltipElement[index],tooltip[index],measurement[index],measureLength,measureArea,measureBearing,mode)
                    }
                })
                return measurement
            } else {
                return measurement
            }
        }

        measureFeature = (((measureFeature === undefined || measureFeature === null))?vm.measureFeature:measureFeature) && (measureLength || measureArea || measureBearing)
        if(indexes && feature.get('measurement') !== undefined && feature.get('measurement') !== null) {
            var geom = this.annotations.getSelectedGeometry(feature,indexes)
            var measurement = this.getMeasurementObject(feature.get('measurement'),indexes,true,indexes.length - 2)
            measurement.splice(indexes[indexes.length - 1],0,(geom instanceof ol.geom.GeometryCollection || geom instanceof ol.geom.MultiPoint || geom instanceof ol.geom.MultiLineString || geom instanceof ol.geom.MultiPolygon)?[]:(geom instanceof ol.geom.Point?null:{}))
            measurement = measurement[indexes[indexes.length - 1]]
            this._measure(feature,geom,this.getMeasurementObject(feature.tooltipElement,indexes),this.getMeasurementObject(feature.tooltip,indexes),measurement,measureLength,measureArea,measureBearing,mode)
        } else if (measureFeature || (feature.get('measurement') !== undefined && feature.get('measurement') !== null)) {
            var measurement = this._measure(
                feature,
                getMeasureGeometry?getMeasureGeometry.call(feature):feature.getGeometry(),
                feature.tooltipElement,
                feature.tooltip,
                feature.get('measurement'),
                measureLength,
                measureArea,
                measureBearing,mode
            )
            if (measurement && measurement !== feature.get('measurement')) {
                feature.set('measurement',measurement,true)
            }
        }
      },
      endMeasure: function(feature) {
        //console.log("End measure")
        var vm = this
        this._endMeasure = this._endMeasure|| function(tooltipElement,tooltip) {
            if (!tooltipElement) {
                return
            } else if (Array.isArray(tooltipElement)){
                $.each(tooltipElement,function(index,t){
                    vm._endMeasure(t,tooltip[index])
                })
            } else {
                tooltipElement.get(0).className = 'tooltip-measure tooltip-measured'
                tooltip.setOffset([0, -7])
            }
        }
        this._endMeasure(feature.tooltipElement,feature.tooltip)
      },
      showTooltip:function(feature,show) {
        var vm = this
        //return true, if show/unshow the tootip; return false, if already showed/unshowed before.
        vm._showTooltip = vm._showTooltip || function(tooltip,show) {
            if (!tooltip) {
                return true
            } else if (Array.isArray(tooltip)) {
                var process= true
                $.each(tooltip,function(index,t){
                    process = vm._showTooltip(t,show)
                    if (process === false) {return false}
                })
                return process
            } else {
                if (show) {
                    if (tooltip.getMap()) {
                        //already show,return
                        return false
                    } else {
                        vm.map.olmap.addOverlay(tooltip)
                        tooltip.setOffset([0, -7])
                        return true
                    }
                } else {
                    if (tooltip.getMap()) {
                        vm.map.olmap.removeOverlay(tooltip)
                        return true
                    } else {
                        //already removed, return
                        return false
                    }
                }
            }
        }
        if (feature instanceof ol.Collection) {
            $.each(feature.getArray(),function(index,f){
                if (vm._showTooltip(f.tooltip,show) === false) {return false}
            })
        } else if (Array.isArray(feature)) {
            $.each(feature,function(index,f){
                if (vm._showTooltip(f.tooltip,show) === false) {return false}
            })
        } else {
            vm._showTooltip(feature.tooltip,show)
        }
      },
      getMeasurementObject:function(obj,indexes,createIfEmpty,end) {
        if (obj === undefined || obj === null) {
            return null
        }
        end = (end === null || end === undefined)?(indexes.length - 1):end
        if (end < 0) {return obj}
        for (i = 0; i <= end;i++){
            if (!obj[indexes[i]] && createIfEmpty) {
                obj[indexes[i]] = []
            }
            obj = obj[indexes[i]]
        }
        return obj
      },
      removeMeasurementObject:function(feature,property,indexes,removeFunc,isProperty){
        var measurementObj = this.getMeasurementObject(isProperty?feature.get(property):feature[property],indexes,false,indexes.length - 2)
        if (measurementObj) {
            if (measurementObj[indexes[indexes.length - 1]] && removeFunc) {
                removeFunc(measurementObj[indexes[indexes.length - 1]])
            }
            //try to remove the empty array if the remove object is the only member 
            measurementObj.splice(indexes[indexes.length - 1],1)
            for(i = indexes.length - 3;i >= -1 && measurementObj.length === 0; i--) {
                measurementObj = this.getMeasurementObject(isProperty?feature.get(property):feature[property],indexes,false,i)
                measurementObj.splice(indexes[i + 1],1)
            }
            if (isProperty) {
                if (feature.get(property) && feature.get(property).length === 0) {
                    feature.unset(property,true)
                 }
            } else {
                if (feature[property] && feature[property].length === 0) {
                    delete feature[property]
                 }
            }
        }
      },
      createTooltip: function (feature,getMeasureGeometry,measureLength,measureArea,measureBearing,measureFeature,indexes) {
        var vm = this

        this._createTooltipElement = this._createTooltipElement || function(geom,measureLength,measureArea,measureBearing) {
            if (geom instanceof ol.geom.Point) {
                return null
            } else if (
                (geom instanceof ol.geom.LineString && (measureLength || measureBearing)) || 
                (geom instanceof ol.geom.Polygon && (measureLength || measureArea))
            ) {
                var measureTooltipElement = $("<div></div>")
                if (measureLength) {
                    measureTooltipElement.append("<div class='length'></div>")
                }
                if (measureArea && geom instanceof ol.geom.Polygon) {
                    measureTooltipElement.append("<div class='area'></div>")
                }
                if (measureBearing && geom instanceof ol.geom.LineString) {
                    measureTooltipElement.append("<div class='bearing' style='white-space:pre;'></div>")
                }
                measureTooltipElement.addClass('tooltip-measure tooltip-measuring')

                $("#map-measure-tooltips").append(measureTooltipElement)

                return measureTooltipElement
            } else if(geom instanceof ol.geom.MultiLineString && (measureLength || measureBearing)) {
                var elements = []
                $.each(geom.getLineStrings(),function(index,g) {
                    elements.push(vm._createTooltipElement(g,measureLength,measureArea,measureBearing))
                })
                return elements
            } else if(geom instanceof ol.geom.MultiPolygon && (measureLength || measureArea)) {
                var elements = []
                $.each(geom.getPolygons(),function(index,g) {
                    elements.push(vm._createTooltipElement(g,measureLength,measureArea,measureBearing))
                })
                return elements
            } else if(geom instanceof ol.geom.GeometryCollection && (measureLength || measureArea || measureBearing)) {
                var elements = []
                $.each(geom.getGeometriesArray(),function(index,g) {
                    elements.push(vm._createTooltipElement(g,measureLength,measureArea,measureBearing))
                })
                return elements
            } else {
                return null
            }
        }

        this._createTooltip = this._createTooltip || function(tooltipElement) {
            if (!tooltipElement) {
                return null
            } else if(Array.isArray(tooltipElement)) {
                var tooltips = []
                $.each(tooltipElement,function(index,t){
                    tooltips.push(vm._createTooltip(t))
                })
                return tooltips
            } else {
                var measureTooltip = new ol.Overlay({
                  element: tooltipElement.get(0),
                  offset: [0, -15],
                  stopEvent:false,
                  positioning: 'bottom-center'
                })
                vm.map.olmap.addOverlay(measureTooltip)
                return measureTooltip
            }
        }
    
        measureFeature = (((measureFeature === undefined || measureFeature === null))?vm.measureFeature:measureFeature) && (measureLength || measureArea || measureBearing)
        var tooltipElement = null
        if (feature.tooltipElement === undefined || feature.tooltipElement === null) {
            //console.log("Create measure tooltip element")
            if (measureFeature) {
                tooltipElement = this._createTooltipElement(getMeasureGeometry?getMeasureGeometry.call(feature):feature.getGeometry(),measureLength,measureArea,measureBearing)
                if (tooltipElement && (!Array.isArray(tooltipElement) || tooltipElement.length > 0)) {
                    feature['tooltipElement'] = tooltipElement
                }
            }
        } else if (Array.isArray(indexes)) {
            tooltipElement = this.getMeasurementObject(feature.tooltipElement,indexes,true,indexes.length - 2)
            var geom = this.annotations.getSelectedGeometry(feature,indexes)
            tooltipElement.splice(indexes[indexes.length - 1],0,this._createTooltipElement(geom,measureLength,measureArea,measureBearing))
            tooltipElement = tooltipElement[indexes[indexes.length - 1]] 
        } else {
            return
        }

        if (feature.tooltip === undefined || feature.tooltip === null) { 
            //console.log("Create measure tooltip overlay")
            if (measureFeature && feature['tooltipElement']) {
                feature['tooltip'] = this._createTooltip(feature['tooltipElement'])
            }
        } else if(Array.isArray(indexes)){
            var tooltip = this.getMeasurementObject(feature.tooltip,indexes,true,indexes.length - 2)
            tooltip.splice(indexes[indexes.length - 1],0,this._createTooltip(tooltipElement))
        }

      },
      removeTooltip: function (feature,removeTooltipElement,indexes) {
        var vm = this
        this._removeTooltip = this._removeTooltip || function(tooltip) {
            if (!tooltip) {
                return
            } else if(Array.isArray(tooltip)) {
                $.each(tooltip,function(index,t){
                    vm._removeTooltip(t)
                })
            } else {
                if (tooltip.getMap()) {
                    vm.map.olmap.removeOverlay(tooltip)
                }
            }
        }

        this._removeTooltipElement = this._removeTooltipElement || function(tooltipElement) {
            if (!tooltipElement) {
                return
            } else if(Array.isArray(tooltipElement)) {
                $.each(tooltipElement,function(index,t){
                    vm._removeTooltipElement(t)
                })
            } else {
                tooltipElement.remove()
            }
        }

        removeTooltipElement = removeTooltipElement === undefined?true:removeTooltipElement
        if (feature.tooltip) {
            if(indexes) {
                this.removeMeasurementObject(feature,"tooltip",indexes,this._removeTooltip)
            } else {
                this._removeTooltip(feature.tooltip)
                delete feature.tooltip
            }
        }
        if (removeTooltipElement && feature.tooltipElement) {
            if (indexes) {
                this.removeMeasurementObject(feature,"tooltipElement",indexes,this._removeTooltipElement)
            } else {
                this._removeTooltipElement(feature.tooltipElement)
                delete feature.tooltipElement
            }
        }
      },
      getArea:function(polygon) {
        var area = 0
        var vm = this
        if (Array.isArray(polygon)) {
            //coodinates array
            $.each(polygon,function(index,linearRing){
                if (index === 0) {
                    area = Math.abs(vm.wgs84Sphere.geodesicArea(linearRing))
                } else {
                    area -= Math.abs(vm.wgs84Sphere.geodesicArea(linearRing))
                }
            })
        } else {
            $.each(polygon.getLinearRings(),function(index,linearRing){
                if (index === 0) {
                    area = Math.abs(vm.wgs84Sphere.geodesicArea(linearRing.getCoordinates()))
                } else {
                    area -= Math.abs(vm.wgs84Sphere.geodesicArea(linearRing.getCoordinates()))
                }
            })
        }
        return area
      },
      getTotalArea:function(geom) {
        var area = 0
        var vm = this
        if (geom instanceof ol.geom.Polygon) {
            area = this.getArea(geom)
        } else if (geom instanceof ol.geom.MultiPolygon){
            $.each(geom.getPolygons(),function(index,p){
                area += vm.getArea(p)
            })
        } else if (geom instanceof ol.geom.GeometryCollection) {
            $.each(geom.getGeometriesArray(),function(index,g){
                area += vm.getTotalArea(g)
            })
        }
        return area
      },
      convertArea:function(area,unit) {
        unit = unit || "km2"
        if (unit === "ha") {
            return area / 10000
        } else if(unit === "km2") {
            return area / 1000000
        } else {
            return area
        }
      },
      getLength: function(coordinates) {
        var length = 0
        var sourceProj = this.$root.map.olmap.getView().getProjection()
        for (var i = 0, ii = coordinates.length - 1; i < ii; ++i) {
          var c1 = ol.proj.transform(coordinates[i], sourceProj, 'EPSG:4326')
          var c2 = ol.proj.transform(coordinates[i + 1], sourceProj, 'EPSG:4326')
          length += this.wgs84Sphere.haversineDistance(c1, c2)
        }
        return length
      },
      getTotalLength: function(geom) {
        var length = 0
        if (geom instanceof ol.geom.Polygon) {
            length = this.getLength(geom.getCoordinates())
        } else if (geom instanceof ol.geom.LineString) {
            length = this.getLength(geom.getCoordinates())
        } else if (geom instanceof ol.geom.MultiPolygon){
            $.each(geom.getPolygons(),function(index,p){
                length += this.getLength(p.getCoordinates())
            })
        } else if (geom instanceof ol.geom.MultiLineString){
            $.each(geom.getLineStrings(),function(index,l){
                length += this.getLength(l.getCoordinates())
            })
        } else if (geom instanceof ol.geom.GeometryCollection) {
            $.each(geom.getGeometriesArray(),function(index,g){
                length += this.getTotalLength(g)
            })
        }
        return length
      },
      convertLength:function(length,unit) {
        unit = unit || "m"
        if (unit === "nm") {
            return (length * 250) / (463 * 1000)
        } else if (unit === "mile") {
            return (length * 15625) / (25146 * 1000)
        } else if (unit === "km"){
            return length / 1000
        } else {
            return length
        }
      },
      getBearing: function (coordinates1, coordinates2) {
        var lon1 = this._degrees2radians * coordinates1[0];
        var lon2 = this._degrees2radians * coordinates2[0];
        var lat1 = this._degrees2radians * coordinates1[1];
        var lat2 = this._degrees2radians * coordinates2[1];
        var a = Math.sin(lon2 - lon1) * Math.cos(lat2);
        var b = Math.cos(lat1) * Math.sin(lat2) -
            Math.sin(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1);

        var bearing = this._radians2degrees * Math.atan2(a, b); 
        return (bearing >= 0)?bearing:bearing + 360
      },
      getDirection:function(bearing,mode){
        if (!this._direction) {
            this._direction = {
                '4':[360/4,Math.floor(360 / 8 * 100) / 100,["N","E","S","W"]],
                '8':[360/8,Math.floor(360 / 16 * 100) / 100,["N","NE","E","SE","S","SW","W","NW"]],
                '16':[360/16,Math.floor(360 / 32 * 100) / 100,["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]],
                '32':[360/32,Math.floor(360 / 64 * 100) / 100,["N","NbE","NNE","NEbN","NE","NEbE","ENE","EbN","E","EbS","ESE","SEbE","SE","SEbS","SSE","SbE","S","SbW","SSW","SWbS","SW","SWbW","WSW","WbS","W","WbN","WNW","NWbW","NW","NWbN","NNW","NbW"]],
            }
        }

        mode = mode || 16
        var key = mode.toString()
        if (!this._direction[key]) {
            mode = 16
            key = "16"
        }

        var directionIndex = (Math.floor(bearing / this._direction[key][0])  + ((Math.round(bearing % this._direction[key][0] * 100) / 100 <= this._direction[key][1])?0:1)) % mode
        return this._direction[key][2][directionIndex]
      },
      formatLength : function(length,unit) {
        var output = null
        unit = unit || this.lengthUnit
        if (unit === "nm") {
              output = "nm"
        } else if (unit === "mile") {
              output = ' mile'
        } else {
            if (length > 100) {
                unit = "km"
                output = "km"
            } else {
                unit = "m"
                output = "m"
            }
        }
        length = this.convertLength(length,unit)
        if (length < 10) {
            length = Math.round(length * 100) / 100
        } else {
            length = Math.round(length)
        }
        output = length + output
        return output
      },
      formatArea : function(area) {
        var output = null
        var unit = null
        if (this.areaUnit === "ha") {
            unit = "ha"
            output = "ha"
        } else {
            if (area > 10000) {
              unit = "km2"
              output = 'km<sup>2</sup>'
            } else {
              unit = "m2"
              output = 'm<sup>2</sup>'
            }
        }
        area = this.convertArea(area,unit)
        if (area < 10) {
            area = Math.round(area * 100) / 100
        } else {
            area = Math.round(area)
        }
        output = area + output
        return output
      },
      featureChanged:function(feature) {
        var vm = this
        if (feature instanceof ol.Collection) {
            feature.forEach(function(feat) {
                vm._featureChanged(feat)
            })
        } else if (Array.isArray(feature)) {
            $.each(feature,function(index,feat) {
                vm._featureChanged(feat)
            })
        } else {
            vm._featureChanged(feature)
        }
      }
    },
    ready: function () {
      var vm = this
      this._degrees2radians = Math.PI / 180
      this._radians2degrees = 180 / Math.PI
      var measureStatus = vm.loading.register("measure","Measurement Component")

      measureStatus.phaseBegin("initialize",30,"Initialize")

      //initialize the overlay and interactions
      this.features = new ol.Collection()
      this.features.on("remove",function(event){
          if (event.element['tooltipElement']) {
              //console.log("Remove measured tooltip")
              vm.removeTooltip(event.element)
          }
      })
      this.style =  new ol.style.Style({
          fill: new ol.style.Fill({
            color: 'rgba(0,0,0, 0.25)'
          }),
          stroke: new ol.style.Stroke({
            color: 'rgba(0, 0, 0, 0.5)',
            lineDash: [10, 10],
            width: 2,
          }),
          image: new ol.style.Circle({
            radius: 5,
            fill: new ol.style.Fill({
              color: 'rgb(0, 153, 255)'
            })
          })
      })
      this.source = new ol.source.Vector({
          features:this.features
      })
      this.overlay = new ol.layer.Vector({
          source: this.source,
          style: this.style
      })

      var measureSnap = new ol.interaction.Snap({
          features: vm.annotations.features
      });

      var measureLengthInter = new ol.interaction.Draw({
          source: this.source,
          type: 'LineString',
          style: this.style
      });

      var drawendHandler = function(ev) {
        vm.endMeasure(ev.feature)
        vm.drawingFeature = null
      }
      measureLengthInter.on('drawstart',this.startMeasureFunc(true,false,false),this)
      measureLengthInter.on('drawend',drawendHandler, this)

      var measureLength = {
        name: 'MeasureLength',
        keepSelection:true,
        interactions:[
            //vm.map.dragPanInter,
            //vm.map.doubleClickZoomInter,
            //vm.map.keyboardPanInter,
            //vm.map.keyboardZoomInter,
            measureLengthInter,
            measureSnap
        ]
      }
      this.annotations.tools.push(measureLength)

      var measureBearingInter = new ol.interaction.Draw({
              source: this.source,
              type: 'LineString',
              style: this.style,
              freehand:false,
              maxPoints:2,
              minPoints:2,
      });

      measureBearingInter.on('drawstart',this.startMeasureFunc(false,false,true),this)
      measureBearingInter.on('drawend',drawendHandler, this)

      var measureBearing = {
        name: 'MeasureBearing',
        keepSelection:true,
        interactions:[
            //vm.map.dragPanInter,
            //vm.map.doubleClickZoomInter,
            //vm.map.keyboardPanInter,
            //vm.map.keyboardZoomInter,
            measureBearingInter,
            measureSnap
        ]
      }
      this.annotations.tools.push(measureBearing)

      var measureAreaInter = new ol.interaction.Draw({
              source: this.source,
              type: 'Polygon',
              style: this.style
            });
      measureAreaInter.on('drawstart',this.startMeasureFunc(true,true,false),this)
      measureAreaInter.on('drawend',drawendHandler, this)

      var measureArea = {
        name: 'MeasureArea',
        keepSelection:true,
        interactions:[
            //vm.map.dragPanInter,
            //vm.map.doubleClickZoomInter,
            //vm.map.keyboardPanInter,
            //vm.map.keyboardZoomInter,
            measureAreaInter,
            measureSnap
        ]
      }

      //add measure tooltips when adding annotation layer and measureFeature is true
      vm._changeOpacityHandler = function(ev) {
        if (!vm.measureFeature) { return }
        if (ev.target.get(ev.key) === 0) {
            vm.enableLayerMeasurement(ev.target.get('id'),false)
        } else if(ev.oldValue === 0) {
            vm.enableLayerMeasurement(ev.target.get('id'),true)
        }
      }
      vm._featureChanged = function(feature){
        var tool = vm.annotations.getTool(feature.get('toolName'))
        if (!tool) {return}
        if (!(tool.measureLength || tool.measureArea || tool.measureBearing)) {return}
        feature.unset('measurement',true)
        if (feature.tooltip) {
            if (vm.measureFeature) {
                vm.measuring(feature,tool.getMeasureGeometry,tool.measureLength,tool.measureArea,false,"show")
                //console.log("Recalculated")
            } else {
                feature.unset("measurement",true)
                //console.log("Remove tooltip because feature is changed")
            }
        }
      }

      this.annotations.tools.push(measureArea)
      var featuresChangedListener = function(ev){
        ev.features.forEach(function(feature) {
            vm._featureChanged(feature)
        })
      }
      var featureChangedListener = function(ev){
        vm._featureChanged(ev.feature)
      }
      var addFeatureGeometryListener = function(ev) {
        var tool = ev.feature.get('toolName')
        tool = tool?vm.annotations.getTool(tool):null
        if (!tool) {return}
        if (!(tool.measureLength || tool.measureArea || tool.measureBearing)) {return}
        
        vm.createTooltip(ev.feature,tool.getMeasureGeometry,tool.measureLength,tool.measureArea,false,vm.measureFeature,ev.indexes)
        vm.measuring(ev.feature,tool.getMeasureGeometry,tool.measureLength,tool.measureArea,false,vm.measureFeature?"show":"measure",vm.measureFeature,ev.indexes) 
      }
      var deleteFeatureGeometryListener = function(ev) {
        var tool = ev.feature.get('toolName')
        tool = tool?vm.annotations.getTool(tool):null
        if (!tool) {return}
        if (!(tool.measureLength || tool.measureArea || tool.measureBearing)) {return}
        
        vm.removeTooltip(ev.feature,true,ev.indexes) 
        vm.removeMeasurementObject(ev.feature,"measurement",ev.indexes,null,true)

      }
      var deleteFeatureAllGeometriesListener = function(ev) {
        var tool = ev.feature.get('toolName')
        tool = tool?vm.annotations.getTool(tool):null
        if (!tool) {return}
        if (!(tool.measureLength || tool.measureArea || tool.measureBearing)) {return}
        
        vm.removeTooltip(ev.feature,true) 
        ev.feature.unset("measurement",true)
      }

      this.annotations.tools.push(measureArea)

      this.wgs84Sphere = new ol.Sphere(6378137);
      measureStatus.phaseEnd("initialize")

      measureStatus.phaseBegin("gk-init",30,"Listen 'gk-init' event",true,true)
      this.$on("gk-init",function() {
          measureStatus.phaseEnd("gk-init")
        
          measureStatus.phaseBegin("attach_event_to_olmap",10,"Attach event to olmap")
          //add measure tooltips when adding annotation layer and measureFeature is true
          vm.map.olmap.on("addLayer",function(ev){
              var layer = vm._measureLayers.find(function(l){return l[0] === ev.mapLayer.get('id')})
              if (layer) {
                  if (vm.measureFeature) {
                      vm.enableLayerMeasurement(layer,true)
                  }
                  ev.mapLayer._change_opacity = ev.mapLayer._change_opacity || ev.mapLayer.on("change:opacity",vm._changeOpacityHandler)
              }
          })

          //remove measure tooltips when removing annotation layer
          vm.map.olmap.on("removeLayer",function(ev){
              var layer = vm._measureLayers.find(function(l){return l[0] === ev.mapLayer.get('id')})
              if (layer) {
                  if (ev.mapLayer._change_opacity) {
                    ev.mapLayer.unByKey(ev.mapLayer._change_opacity)
                    delete ev.mapLayer._change_opacity
                  }
                  if (vm.measureFeature) {
                      vm.enableLayerMeasurement(layer,false)
                  }
              }
          })
          measureStatus.phaseEnd("attach_event_to_olmap")

          measureStatus.phaseBegin("gk-postinit",20,"Listen 'gk-postinit' event",true,true)
          this.$on("gk-postinit",function() {
              measureStatus.phaseEnd("gk-postinit")

              measureStatus.phaseBegin("attach_event_to_tool",5,"Attach event to tool")
              var processedInteractions = []
              $.each(vm.annotations.tools,function(index1,tool){
                $.each(tool.interactions,function(index2,interaction){
                    if (!processedInteractions.find(function(o){return o === interaction})) {
                        if (interaction instanceof ol.interaction.Modify) {
                            //console.log('===================')
                            interaction.on("featuresmodified",featuresChangedListener)
                        } else if (interaction instanceof ol.interaction.Translate) {
                            interaction.on("translateend",featuresChangedListener)
                        } else if (interaction instanceof ol.interaction.Draw && interaction.events && interaction.events["addfeaturegeometry"]) {
                            interaction.on("addfeaturegeometry",addFeatureGeometryListener)
                        }
                        if (interaction.events && interaction.events["deletefeaturegeometry"]) {
                            interaction.on("deletefeaturegeometry",deleteFeatureGeometryListener)
                        }
                        if (interaction.events && interaction.events["deleteallgeometries"]) {
                            interaction.on("deleteallgeometries",deleteFeatureAllGeometriesListener)
                        }
                        processedInteractions.push(interaction)
                    }
                })
              })

              measureStatus.phaseEnd("attach_event_to_tool")

              measureStatus.phaseBegin("init_measurable_layers",5,"Initialize measurable layers")
              //initialize measure layers
              if (vm.measureFeature) {
                  $.each(vm._measureLayers,function(index,layer){
                    if (vm.active.isHidden(vm.map.getMapLayer(layer[0])) === false) {
                        vm.enableLayerMeasurement(layer,true)
                    }
                  })
              }

              measureStatus.phaseEnd("init_measurable_layers")
          })
      })

    }
  }
</script>
