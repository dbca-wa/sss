<template>
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
        layer:{},
        layers:[],
        showLayers:false,
        warning:false
      }

    },
    // parts of the template to be computed live
    computed: {
      loading: function () { return this.$root.loading },
      annotations: function () { return this.$root.annotations },
      catalogue:function() { return this.$root.catalogue},
      weatheroutlook:function() { return this.$root.weatheroutlook},
      active:function() { return this.$root.active},
      dialog: function () { return this.$root.dialog },
      map: function () { return this.$root.map },
      env: function () { return this.$root.env },
      enabled:function() {
        return this.layers.length > 0
      },
      isControlSelected:function() {
        if (this.annotations) {
            return !this.warning && this.annotations.tool === this._featuredetailTool
        } else {
            return false
        }
      },
      tools:function() {
        return this.layers
      }
    },
    watch:{
    },
    // methods callable from inside the template
    methods: {
      toggleTool: function (enable) {
        this.warning = false
        if (!this._featuredetailTool) {
            this.annotations.setTool(this.annotations.currentTool,true)
        } else if (enable === true && this.annotations.tool === this._featuredetailTool) {
            //already enabled
            return
        } else if (enable === false && this.annotations.tool !== this._featuredetailTool) {
            //already disabled
            return
        } else if (this.annotations.tool === this._featuredetailTool) {
            this.annotations.setTool(this.annotations.currentTool,true)
        } else  {
            this.annotations.setTool(this._featuredetailTool)
            if (this.layer !== this._featureinfo_layer) {
                // show layer if not show;enable layer, if disabled
                var mapLayer = this.map.getMapLayer(this.layer)
                if (!mapLayer) {
                this.catalogue.onLayerChange(this.layer, true)
                } else if (this.active.isHidden(mapLayer)) {
                    this.active.toggleHidden(mapLayer)
                }
            }
        }
      },
      selectTool:function(l) {
        if (this.layer === l) {
            return
        }
        /*
        if (this.layer) {
            //remove the preivouse selected layer from map
            var mapLayer = this.map.getMapLayer(this.layer)
            if (mapLayer) {
              this.catalogue.onLayerChange(this.layer, false)
            }
        }
        */
        this.layer = l
        this.warning = false
        if (this.isControlSelected) {
            // enable resource bfrs layer, if disabled
            var mapLayer = this.map.getMapLayer(this.layer)
            if (!mapLayer) {
              this.catalogue.onLayerChange(this.layer, true)
            } else if (this.active.isHidden(mapLayer)) {
                this.active.toggleHidden(mapLayer)
            }

        }
      },
      isToolActivated:function(tool) {
        return this.isControlSelected
      },
      isToolWarning:function(tool) {
        return this.warning
      },
      set_featureinfo_layer:function() {
        var vm = this
        vm._featureinfo_layer["id"] = null
        vm._featureinfo_layer["title"] = "No Active Vector Layer"
        $.each(this.active.olLayers,function(index,layer){
            layer = vm.active.getLayer(layer.get('id'))
           if (layer.service_type === 'WFS') {
                vm._featureinfo_layer["id"] = layer['id']
                vm._featureinfo_layer["title"] = layer["title"]
                return false
           }
        })
      },
    },
    ready: function () {
      var vm = this
      this._featuredetailStatus = vm.loading.register("featuredetail","Feature Detail Component")

      this._featuredetailStatus.phaseBegin("gk-init",80,"Listen 'gk-init' event",true,true)
      this.$on('gk-init', function() {
        vm._featuredetailStatus.phaseEnd("gk-init")

        vm._featuredetailStatus.phaseBegin("initialize",20,"Initialize",true,false)

        vm.catalogue.catalogue.forEach(function(layer){
            if (layer.tags && layer.tags.some(function(o) {return o.name === "detail_link" || o.name === "detail_dialog"} )) {
                layer.icon = "/dist/static/images/" + layer.id.replace(":","-").toLowerCase() + ".png"
                layer.title = layer.name || layer.id
                layer.toolid = "feauterdetail-" + layer.id.replace(":","-")
                vm.layers.splice(0,0,layer)
            }
        })
        vm._featureinfo_layer = {
            id:null,
            icon:"/dist/static/images/feature_info.svg",
            title:"Identity Tool",
            toolid:"featuredetail-vectorlayer-top"
        }
        vm.layers.push(vm._featureinfo_layer)

        vm.set_featureinfo_layer()
        vm.map.olmap.on("removeLayer",function(ev){
            vm.set_featureinfo_layer()
        })
        vm.map.olmap.on("addLayer",function(ev){
            vm.set_featureinfo_layer()
        })
        vm.map.olmap.on("changeLayerOrder",function(ev){
            vm.set_featureinfo_layer()
        })

        if (vm.layers.length) {
            vm.layer = vm.layers[0]
            
            var featuredetailInter = new ol.interaction.Interaction({
                handleEvent:function(browserEvent) {
                    if (!ol.events.condition.click(browserEvent)) {
                        return true
                    }
                    if (vm.layer.id === null) {
                        //no vector layer
                        return
                    }
                    var topLeft = vm.map.olmap.getCoordinateFromPixel(browserEvent.pixel.map(function(d){return d - 10}))
                    var bottomRight = vm.map.olmap.getCoordinateFromPixel(browserEvent.pixel.map(function(d){return d + 10}))

                    var bbox = "&bbox=" + bottomRight[1] + "," + topLeft[0] + "," + topLeft[1] + "," + bottomRight[0] + ",urn:ogc:def:crs:EPSG:4326"
                    var url = null
                    if (vm.layer !== vm._featureinfo_layer && vm.layer.tags && vm.layer.tags.some(function(o) {return o.name === "detail_link"} )) {
                        url = vm.env.kmiService + "/wfs?service=wfs&version=2.0&request=GetFeature&count=1&outputFormat=application%2Fjson&typeNames=" + getDetailLayerId(vm.layer.id) + bbox
                    } else {
                        url = vm.env.kmiService + "/wfs?service=wfs&version=2.0&request=GetFeature&outputFormat=application%2Fjson&typeNames=" + getDetailLayerId(vm.layer.id) + bbox
                    }
                    $.ajax({
                        url:url,
                        dataType:"json",
                        success: function (response, stat, xhr) {
                            if (response.totalFeatures < 1) {
                                vm.warning = true
                                return
                            }

                            vm.warning = false
                            if (vm.layer.tags && vm.layer.tags.some(function(o) {return o.name === "detail_link"} )) {
                                if (response.features[0].properties["url"]) {
                                    utils.editResource(browserEvent,null,response.features[0].properties["url"],vm.layer.id,true)
                                }
                            } else {
                                var messages = []
                                $.each(response.features[0].properties,function(key,value) {
                                    if (['ogc_fid','md5_rowhash'].indexOf(key) >= 0){
                                        return
                                    }
                                    if (vm.dialog.isLink(value)) {
                                        messages.push([[key,3,{"class":"detail_name"}],[value,9,{"type":"link","class":"detail_value","target":vm.layer.id + "." + key}]])
                                    } else {
                                        messages.push([[key,3,{"class":"detail_name"}],[value,9,{"class":"detail_value"}]])
                                    }
                                })
                                var footer = null;
                                var index = 1
                                var moveFeature = function(forward) {
                                    if (forward) {
                                        if (index < response.totalFeatures) {
                                            index += 1
                                        } else {
                                            index = 1
                                        }
                                    } else {
                                        if (index > 1) {
                                            index -= 1
                                        } else {
                                            index = response.totalFeatures
                                        }
                                    }
                                    //show current feature's property
                                    var propertyIndex = 0
                                    var vm = this
                                    $.each(response.features[index - 1].properties,function(key,value) {
                                        if (['ogc_fid','md5_rowhash'].indexOf(key) >= 0){
                                            return
                                        }
                                        vm.messages[propertyIndex][1][0]= value
                                        propertyIndex += 1
                                    })
                                    this.footer[0][2][0] = index + "/" + response.totalFeatures
                                    this.rerend()

                                }
                                if (response.totalFeatures > 1) {
                                    footer = [[
                                        ["",4],
                                        ["/dist/static/images/previous.svg",1,{
                                            type:"img",
                                            style:"text-align:center;",
                                            title:"Previous",
                                            click:function() {
                                                moveFeature.call(this,false)
                                            },
                                        }],
                                        [index + "/" + response.totalFeatures,2,{
                                            style:"text-align:center;"
                                        }],
                                        ["/dist/static/images/next.svg",1,{
                                            type:"img",
                                            style:"text-align:center;",
                                            title:"Next",
                                            click:function() {
                                                moveFeature.call(this,true)
                                            },
                                        }],
                                        ["",4],
                                    
                                    ]]
                                }
                                vm.dialog.show({
                                    title:vm.layer.title,
                                    messages:messages,
                                    footer:footer
                                })
                            }
                        },
                        error: function (xhr,status,message) {
                            vm.warning = true
                            alert(xhr.status + " : " + (xhr.responseText || message))
                        },
                        xhrFields: {
                            withCredentials: true
                        }
                    })
                    
                    return false
                }
            });

            vm._featuredetailTool = {
              name: 'FeatureDetail',
              keepSelection:true,
              interactions:[
                  featuredetailInter
              ]
            }

            vm.annotations.tools.push(vm._featuredetailTool)
        }

        vm._featuredetailStatus.phaseEnd("initialize")
      })
        
    }
  }
</script>
