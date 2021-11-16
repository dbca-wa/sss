<template>
    <a class="button drawinglog" v-bind:disabled="undoSteps == 0" @click="undo()"><i class="fa fa-undo" aria-hidden="true"></i> Undo ({{undoSteps}}/{{drawingLogs.length}})</a>
    <a class="button drawinglog" v-bind:disabled="redoSteps == 0" @click="redo()"><i class="fa fa-repeat" aria-hidden="true"></i> Redo ({{redoSteps}}/{{drawingLogs.length}})</a>
    <a class="button drawinglog" v-bind:disabled="drawingLogs.length == 0" @click="cleanLogs()"><i class="fa fa-trash" aria-hidden="true"></i> Clean ({{drawingLogs.length}})</a>
</template>
<style>
.drawinglog {
    padding-left:5px;
    padding-right:5px;
}
</style>
<script>
    import { ol,$ } from 'src/vendor.js'

    export default { 
      store: ['drawingLogs','redoPointer','settings'],
      data: function() {
        return {
            modifyingFeatures:{}
        }
      },
      computed: {
        annotations: function() {return this.$root.annotations},
        loading: function () { return this.$root.loading },
        systemsetting: function() {return this.$root.systemsetting},
        undoSteps:function() {
            return this.drawingLogs.length && this.redoPointer
        },
        redoSteps:function() {
            return this.drawingLogs.length && this.drawingLogs.length - this.redoPointer
        },
        size:{
            get:function() {
                return this.settings.undoLimit
            },
            set:function(val) {
                //Setting log size will not truncate log immediately
                //Log will be resized in the next addLog call.
                if (val < 0) {
                    //want to disable drawing logs
                    if (this.settings.undoLimit >= 0) {
                        //currently, logs is enabled, turn it off
                        this.off()
                        this.systemsetting.saveState()
                    }
                } else {
                    //want to enable drawing logs
                    if (this.settings.undoLimit < 0) {
                        //currently, logs is disabled, turn it on
                        this.on(val)
                        this.systemsetting.saveState()
                    } else if (this.settings.undoLimit !== val){
                        this.settings.undoLimit = val
                        this.systemsetting.saveState()
                    }
                }
            }
        }
      },
      methods:{
        on:function(limit) {
            limit = limit || 0
            if (limit < 0) {
                //limit is less than 0, disable the feature
                this.off()
                return
            }
            //Write logs for creating features(drawn features and imported features),removing features , moving features and modifying features.
            var vm = this

            var attachChangeEventListener = function(feature) {
                var featureId = feature.get('id')
                feature.getGeometry()._changeListenerId = feature.getGeometry()._changeListenerId || feature.getGeometry().on("change",vm._eventHandlers["geometry:change"](feature,featureId))
            
                var tool = feature.get('toolName')?vm.annotations.getTool(feature.get('toolName')):false
                if (!tool) {return}
                if (tool === vm.annotations.ui.defaultText) {
                    //for note feature, set the previous note data to current note data. 
                    //Previous note data is used to check whether note data is changed or not, if changed then record a modify log; otherwise, ignore
                    var previousNote = {}
                    var note = feature.get('note')
                    if (note) {
                        $.each(note,function(key,value){
                            previousNote[key] = value
                        })
                        feature['previousNote'] = previousNote
                    }
                    feature._propertyChangeListenerId = feature._propertyChangeListenerId || feature.on("propertychange",vm._eventHandlers["text:propertychange"](feature))
                } else if (tool === vm.annotations.ui.defaultLine || tool === vm.annotations.ui.defaultPolygon) {
                    feature._propertyChangeListenerId = feature._propertyChangeListenerId || feature.on("propertychange",vm._eventHandlers["vector:propertychange"](feature))
                } else if (tool === vm.annotations.ui.defaultPoint) {
                    feature._propertyChangeListenerId = feature._propertyChangeListenerId || feature.on("propertychange",vm._eventHandlers["pointer:propertychange"](feature))
                }
            }
            //add event handlers for existing features
            vm.annotations.features.forEach(function(feature){
                attachChangeEventListener(feature)
            })

            //add event listeners to record modifying logs
            vm._eventListenerIds["features:change"] = vm._eventListenerIds["features:change"] || vm.annotations.features.on('add',function(ev) {
                attachChangeEventListener(ev.element)
            })


            //add event listeners to record logs
            vm._eventListenerIds["features:add"] = vm._eventListenerIds["features:add"] || vm.annotations.features.on('add',function(ev) {
                if (vm._undoRedoMode) { return }
                vm.addFeatures(ev.element)
            })

            vm._eventListenerIds["features:remove"] = vm._eventListenerIds["features:remove"] || vm.annotations.features.on('remove',function(ev) {
                if (vm._undoRedoMode) { return }
                vm.removeFeatures(ev.element)
            })

            vm._eventListenerIds["translateInter:translateend"] = vm._eventListenerIds["translateInter:translateend"] || vm.annotations.ui.translateInter.on("translateend",function(ev){
                if (vm._undoRedoMode) { return }
                vm.modifyFeatures(ev.features)
            })

            vm._eventListenerIds["modifyInter:modifyend"] = vm._eventListenerIds["modifyInter:modifyend"] || vm.annotations.ui.modifyInter.on("modifyend",function(ev){
                if (vm._undoRedoMode) { return }
                vm.modifyFeatures(ev.features)
            })
            
            //add control-z and control-r  for undo and redo
            vm._keyboardInter = vm._keyboardInter || new ol.interaction.Interaction({
                handleEvent: function (mapBrowserEvent) {
                    var stopEvent = false
                    if (mapBrowserEvent.type === ol.events.EventType.KEYDOWN) {
                       var keyEvent = mapBrowserEvent.originalEvent
                       switch (keyEvent.keyCode) {
                         case 90: // z
                           if (keyEvent.ctrlKey) {
                              vm.undo()
                              stopEvent = true
                            }
                            break
                          case 89: // y
                            vm.redo()
                            stopEvent = true
                            break
                          default:
                            break
                        }
                    }
                    // if we intercept a key combo, disable any browser behaviour
                    if (stopEvent) {
                        keyEvent.preventDefault()
                    }
                    return !stopEvent
                }
            })
            vm.$root.map.olmap.addInteraction(vm._keyboardInter)

            vm.settings.undoLimit = limit
            
        },
        off:function() {
            var vm = this
            //remove event listeners from existing features
            vm.annotations.features.forEach(function(feature) {
                if (feature.getGeometry()._changeListenerId) {
                    feature.getGeometry().unByKey(feature.getGeometry()._changeListenerId)
                    delete feature.getGeometry()._changeListenerId
                }
                if (feature._propertyChangeListenerId) {
                    feature.unByKey(feature._propertyChangeListenerId)
                    delete feature._propertyChangeListenerId
                }
            })

            //remove event listeners from features collection
            if (vm._eventListenerIds["features:change"]) {
                vm.annotations.features.unByKey(vm._eventListenerIds["features:change"])
                delete vm._eventListenerIds["features:change"]
            }

            if (vm._eventListenerIds["features:add"]) {
                vm.annotations.features.unByKey(vm._eventListenerIds["features:add"])
                delete vm._eventListenerIds["features:add"]
            }

            if (vm._eventListenerIds["features:remove"]) {
                vm.annotations.features.unByKey(vm._eventListenerIds["features:remove"])
                delete vm._eventListenerIds["features:remove"]
            }

            if (vm._eventListenerIds["translateInter:translateend"]) {
                vm.annotations.ui.translateInter.unByKey(vm._eventListenerIds["translateInter:translateend"])
                delete vm._eventListenerIds["translateInter:translateend"]
            }

            if (vm._eventListenerIds["modifyInter:modifyend"]) {
                vm.annotations.ui.modifyInter.unByKey(vm._eventListenerIds["modifyInter:modifyend"])
                delete vm._eventListenerIds["modifyInter:modifyend"] 
            }

            if (vm._keyboardInter) {
                vm.$root.map.olmap.removeInteraction(vm._keyboardInter)
            }

            vm.drawingLogs.splice(0,vm.drawingLogs.length)
            vm.redoPointer = 0

            vm.settings.undoLimit = -1
        },
        addFeatures:function(features) {
            if (features instanceof ol.Collection) {
                features = features.getArray()
            } else if (!Array.isArray(features)) {
                features = [features]
            } 
            this.addLog(["C",JSON.parse(this.$root.geojson.writeFeatures(features))])
        },
        removeFeatures:function(features) {
            if (features instanceof ol.Collection) {
                features = features.getArray()
            } else if (!Array.isArray(features)) {
                features = [features]
            } 
            this.addLog(["R",JSON.parse(this.$root.geojson.writeFeatures(features))])
        },
        modifyFeatures:function(features) {
            var vm = this
            if (features instanceof ol.Collection) {
                features = features.getArray()
            } else if (!Array.isArray(features)) {
                features = [features]
            } 
            features = features.filter(function(f){ return f.get('id') in vm._modifyingFeatureIds  })
            if (features.length) {
                this.addLog(["U",JSON.parse(this.$root.geojson.writeFeatures(this._modifyingFeatures)),JSON.parse(this.$root.geojson.writeFeatures(features))])
            }
            this._modifyingFeatures = []
            this._modifyingFeatureIds = {}
            
        },
        modifyFeaturesProperty:function(features,property,oldValue,newValue) {
            var vm = this
            if (features instanceof ol.Collection) {
                features = features.getArray()
            } else if (!Array.isArray(features)) {
                features = [features]
            } 
            this.addLog(["P",features.map(function(feature){return feature.get('id')}),property,oldValue,newValue])
        },
        addLog: function(log){
            this.drawingLogs.splice(this.redoPointer,this.drawingLogs.length - this.redoPointer,log)
            if (this.size > 0 && this.drawingLogs.length > this.size) {
                //truncate the log if log is exceed the log size.
                this.drawingLogs.splice(0, this.drawingLogs.length - this.size)
            }
            this.redoPointer = this.drawingLogs.length
        },
        cleanLogs: function() {
            if (window.confirm('This will clear all change logs, and you can\'t undo/redo previous drawings anymore. Are you sure?')) {
                this.drawingLogs.splice(0,this.drawingLogs.length)
                this.redoPointer = 0
            }
        },
        undo:function() {
            var vm = this
            vm.annotations.setTool('Pan')
            try {
                vm._undoRedoMode = true
                if (vm.undoSteps <= 0) {return}
                var undoIndex = vm.redoPointer - 1
                if (vm.drawingLogs[undoIndex][0] === 'C') {
                    //create feature log; 
                    //undo action will delete the feature
                    var changedFeatures = vm.$root.geojson.readFeatures(vm.drawingLogs[undoIndex][1])
                    $.each(changedFeatures,function(i,feature) {
                        var index = vm.annotations.selectedFeatures.getArray().findIndex(function(f){return f.get('id') === feature.get('id')})
                        if (index >= 0) {
                            vm.annotations.selectedFeatures.removeAt(index)
                        }
                        index = vm.annotations.features.getArray().findIndex(function(f){return f.get('id') === feature.get('id')})
                        if (index >= 0) {
                            vm.annotations.features.removeAt(index)
                        }
                    })
                } else if (vm.drawingLogs[undoIndex][0] === 'R') {
                    //Remove feature log; 
                    //undo action will add the feature
                    var changedFeatures = vm.$root.geojson.readFeatures(vm.drawingLogs[undoIndex][1])
                    $.each(changedFeatures,function(i,feature) {
                        vm.annotations.initFeature(feature)
                        vm.annotations.features.push(feature)
                    })
                } else if (vm.drawingLogs[undoIndex][0] === 'U') {
                    //Change geature geometry log; 
                    //undo action will replace the feature's geometry
                    var changedFeatures = vm.$root.geojson.readFeatures(vm.drawingLogs[undoIndex][1])
                    $.each(changedFeatures,function(i,feature) {
                        var index = vm.annotations.features.getArray().findIndex(function(f){return f.get('id') === feature.get('id')})
                        if (index >= 0) {
                            var f = vm.annotations.features.item(index)
                            var tool = f.get('toolName')?vm.annotations.getTool(f.get('toolName')):false
                            if (tool && tool.typeIcon) {
                                delete f['typeIconStyle']
                                f.set('typeIconMetadata',undefined,true)
                            }
                            f.setGeometry(feature.getGeometry())
                            f.getGeometry().on("change",vm._eventHandlers["geometry:change"](f,feature.get('id')))
                            vm.annotations.ui.modifyInter.dispatchEvent(new ol.interaction.Modify.Event("featuresmodified",new ol.Collection([f]),null))
                        }
                    })
                } else if (vm.drawingLogs[undoIndex][0] === 'P') {
                    //Change feature property log; 
                    //undo action will replace the feature's property 
                    var changedFeatureIds = vm.drawingLogs[undoIndex][1]
                    $.each(changedFeatureIds,function(i,featureId) {
                        var index = vm.annotations.features.getArray().findIndex(function(f){return f.get('id') === featureId})
                        if (index >= 0) {
                            var f = vm.annotations.features.item(index)
                            if (typeof vm.drawingLogs[undoIndex][3] === 'object') {
                                f.set(vm.drawingLogs[undoIndex][2],$.extend(f.get(vm.drawingLogs[undoIndex][2]),vm.drawingLogs[undoIndex][3]))
                                f.changed()
                                var tool = f.get('toolName')?vm.annotations.getTool(f.get('toolName')):false
                                if (tool && tool === vm.annotations.ui.defaultText) {
                                    var note = f.get('note')
                                    f.previousNote = {}
                                    $.each(note,function(key,value){ f.previousNote[key] = value})
                                }
                            } else {
                                f.set(vm.drawingLogs[undoIndex][2],vm.drawingLogs[undoIndex][3])
                            }
                        }
                    })
                } else {
                    alert("Not support")
                    return
                }
                vm.redoPointer = undoIndex
            } finally {
                vm._undoRedoMode = false
            }
        },
        redo:function() {
            var vm = this
            vm.annotations.setTool('Pan')
            try {
                vm._undoRedoMode = true
                if (vm.redoSteps <= 0) {return}
                if (vm.drawingLogs[vm.redoPointer][0] === 'C') {
                    //create feature log; 
                    //redo action will create the feature again
                    var changedFeatures = vm.$root.geojson.readFeatures(vm.drawingLogs[vm.redoPointer][1])
                    $.each(changedFeatures,function(i,feature) {
                        vm.annotations.initFeature(feature)
                        vm.annotations.features.push(feature)
                    })
                } else if (vm.drawingLogs[vm.redoPointer][0] === 'R') {
                    //Remove feature log; 
                    //redo action will remove the feature again
                    var changedFeatures = vm.$root.geojson.readFeatures(vm.drawingLogs[vm.redoPointer][1])
                    $.each(changedFeatures,function(i,feature) {
                        var index = vm.annotations.features.getArray().findIndex(function(f){return f.get('id') === feature.get('id')})
                        if (index >= 0) {
                            vm.annotations.features.removeAt(index)
                        }
                    })
                } else if (vm.drawingLogs[vm.redoPointer][0] === 'U') {
                    //Change feature log; 
                    //redo action will replace the feature's geometry
                    var changedFeatures = vm.$root.geojson.readFeatures(vm.drawingLogs[vm.redoPointer][2])
                    $.each(changedFeatures,function(i,feature) {
                        var index = vm.annotations.features.getArray().findIndex(function(f){return f.get('id') === feature.get('id')})
                        if (index >= 0) {
                            var f = vm.annotations.features.item(index)
                            var tool = f.get('toolName')?vm.annotations.getTool(f.get('toolName')):false
                            if (tool && tool.typeIcon) {
                                delete f['typeIconStyle']
                                f.set('typeIconMetadata',undefined,true)
                            }
                            f.setGeometry(feature.getGeometry())
                            f.getGeometry().on("change",vm._eventHandlers["geometry:change"](f,feature.get('id')))
                            vm.annotations.ui.modifyInter.dispatchEvent(new ol.interaction.Modify.Event("featuresmodified",new ol.Collection([f]),null))
                        }
                    })
                } else if (vm.drawingLogs[vm.redoPointer][0] === 'P') {
                    //Change feature property log; 
                    //redo action will replace the feature's property 
                    var changedFeatureIds = vm.drawingLogs[vm.redoPointer][1]
                    $.each(changedFeatureIds,function(i,featureId) {
                        var index = vm.annotations.features.getArray().findIndex(function(f){return f.get('id') === featureId})
                        if (index >= 0) {
                            var f = vm.annotations.features.item(index)
                            if (typeof vm.drawingLogs[vm.redoPointer][4] === 'object') {
                                f.set(vm.drawingLogs[vm.redoPointer][2],$.extend(f.get(vm.drawingLogs[vm.redoPointer][2]),vm.drawingLogs[vm.redoPointer][4]))
                                f.changed()
                                var tool = f.get('toolName')?vm.annotations.getTool(f.get('toolName')):false
                                if (tool && tool === vm.annotations.ui.defaultText) {
                                    var note = f.get('note')
                                    f.previousNote = {}
                                    $.each(note,function(key,value){ f.previousNote[key] = value})
                                }
                            } else {
                                f.set(vm.drawingLogs[vm.redoPointer][2],vm.drawingLogs[vm.redoPointer][4])
                            }
                        }
                    })
                } else {
                    alert("Not support")
                    return
                }
                vm.redoPointer += 1
            } finally {
                vm._undoRedoMode = false
            }
        },
        changeUndoLimit:function() {
        }
      },
      ready:function(){
        var vm = this
        var logStatus = this.loading.register("drawinglogs","Drawing Logs Component")
        logStatus.phaseBegin("initialize",20,"Initialize")

        vm._undoRedoMode = false
        vm._modifyingFeatures = []
        vm._modifyingFeatureIds = {}
        vm._eventHandlers = {}
        vm._eventListenerIds = {}

        vm._eventHandlers["geometry:change"] = function(feature,featureId) {
            return function(ev) {
                if (vm._undoRedoMode) { return }
                if ( featureId in vm._modifyingFeatureIds) {
                    return
                }
                vm._modifyingFeatureIds[featureId] = true
                var tmpFeature = feature.clone()
                tmpFeature.setProperties({},true)
                vm._modifyingFeatures.push(tmpFeature)
            }
        }
        vm._eventHandlers["text:propertychange"] = function(feature) {
            return function(ev) {
                if (vm.annotations.tool === vm.annotations.ui.editStyle && ev.key === "noteRevision") {
                    var previousNote = feature["previousNote"]
                    var note = feature.get('note')
                    if (previousNote) {
                        var changed = false
                        $.each(['colour','text'],function(index,key){
                            if (previousNote[key] !== note[key]) {
                                changed = true
                                return false
                            }
                        })
                        if (changed) {
                            var currentNote = {}
                            $.each(note,function(key,value){
                                currentNote[key] = value
                            })
                            vm.modifyFeaturesProperty(feature,'note',previousNote,currentNote)
                            feature["previousNote"] = currentNote
                        }
                    }
                } else if ( ev.key === "note") {
                    var note = feature.get('note')
                    feature.previousNote = {}
                    $.each(note,function(key,value){ feature.previousNote[key] = value})
                }
            }
        }
        vm._eventHandlers["vector:propertychange"] = function(feature) {
            return function(ev) {
                if (vm._undoRedoMode) { return }
                if (vm.annotations.tool === vm.annotations.ui.editStyle && (ev.key === "colour" || ev.key === "size")) {
                    vm.modifyFeaturesProperty(feature,ev.key,ev.oldValue,feature.get(ev.key))
                }
            }
        }

        vm._eventHandlers["pointer:propertychange"] = function(feature) {
            return function(ev) {
                if (vm._undoRedoMode) { return }
                if (vm.annotations.tool === vm.annotations.ui.editStyle && (ev.key === "colour" || ev.key === "shape")) {
                    vm.modifyFeaturesProperty(feature,ev.key,ev.oldValue,feature.get(ev.key))
                }
            }
        }

        logStatus.phaseEnd("initialize")

        logStatus.phaseBegin("gk-postinit",60,"Listen 'gk-postinit' event",true,true)
        vm.$on('gk-postinit',function(){
            logStatus.phaseEnd("gk-postinit")

            logStatus.phaseBegin("attach_events",20,"Attach events")
            this.on(vm.settings.undoLimit)
            logStatus.phaseEnd("attach_events")
        })
      }
    }
</script>

