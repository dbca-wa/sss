<template >
  <div class="reveal" id="active-layer-legends" data-reveal data-v-offset="0px" data-overlay="false" data-close-on-esc="false" data-close-on-click="false" >
    <h4 id="legend-title" @mouseenter="enableMove(true)" @mouseout="enableMove(false)">Legends ({{displayLegendLayers.length}}/{{legendLayers.length}})</h4>
    <div id="active-layer-legend-list">
        <template v-for="l in displayLegendLayers" track-by="id">
            <div class="layer-row layer-legend-row row" >
                <div class="small-11">
                    <h6 class="layer-title" >{{ l.name || l.id }} </h6>
                </div>
                <div class="small-1">
                    <a class="button tiny secondary" @click="hideLegend(l)" title="Hide"><i class="fa fa-eye-slash"></i></a>
                </div>
                <div class="small-12">
                    <img v-bind:src="l.legend" class="cat-legend" @error="loadLegendFailed($index,l)" crossOrigin="use-credentials"/>
                </div>
            </div>
        </template>
    </div>
    <button v-bind:class={disabled:disableShowall} v-bind:disabled="disableShowall" type="button" class="showall-button" @click="showAll()" title="Show All">
      <i class="fa fa-eye"></i>
    </button>
    <button v-bind:class="{disabled:disablePrint}" v-bind:disabled="disablePrint" type="button" class="print-button" @click="printLegends()" title="Print">
      <i class="fa fa-print"></i>
    </button>
    <button class="close-button" data-close aria-label="Close modal" type="button" title="Close">
      <span aria-hidden="true">&times;</span>
    </button>
  </div>
</template>
<style>
#active-layer-legends {
    height:99%;
}
#legend-title {
    cursor:move;
}
#active-layer-legends-list {
    height:99%;
}
#active-layer-legends .disabled{
    color: #8a8a8a;
}
#active-layer-legends button{
    color: #2199e8;
}
#active-layer-legends .showall-button{
    right: 4.5rem;
    font-size: 1.3em;
    position: absolute;
    top: 1rem;
}
#active-layer-legends .print-button{
    right: 2.5rem;
    font-size: 1.3em;
    position: absolute;
    top: 1rem;
}
.layer-legend-row{
    padding-bottom:50px
}
</style>
<script>
  import { saveAs, $, jsPDF,interact } from 'src/vendor.js'
  export default {
    store: [ 'dpmm'],
    data: function() {
      return {
          legendLayers:[],
          filteredLegendLayers:[],
          hiddenLayers:{},
          position:"right-top"
      }
    },
    computed: {
      displayLegendLayers:function() {
        return this.filteredLegendLayers || this.legendLayers
      },
      disableShowall:function() {
        return this.filteredLegendLayers?false:true
      },
      disablePrint:function() {
        return this.displayLegendLayers.length == 0
      },
      legendsPanel:function() {
        this._legendsPanel = this._legendsPanel || new Foundation.Reveal($("#active-layer-legends"))
        return this._legendsPanel
      },
      loadFinished: {
        cache: false,
        get: function() {
            var finished = true
            $("#active-layer-legend-list").find("img").each(function(index,img){
                if (img.naturalWidth === 0 || img.naturalWidth === undefined || img.naturalHeight === 0 || img.naturalHeight === undefined) {
                    finished = false
                    return false
                }
            })
            return finished
        }
      }
    },
    methods:{
      enableMove:function(enable) {
        this._interact.draggable(enable)
      },
      showAll:function() {
        this.hiddenLayers = {}
        this.filteredLegendLayers = null
        
      },
      hideLegend:function(l) {
        if (this.hiddenLayers[l.id]) return
        this.hiddenLayers[l.id] = true
        if (this.filteredLegendLayers == null) {
            var vm = this
            this.filteredLegendLayers = this.legendLayers.filter(function(layer){
                return !vm.hiddenLayers[layer.id]
            })
        } else {
            this.filteredLegendLayers.splice(this.filteredLegendLayers.indexOf(l),1)
        }
      },
      //return true if changed, otherwise return false
      syncLegendLayers: function(){
        var vm = this
        var catalogue = vm.$root.catalogue
        var results = []
        var legendLen = 0
        vm.$root.active.olLayers.every(function (layer) {
          var catLayer = catalogue.getLayer(layer)
          if (catLayer) {
            if (catLayer.legend && (catLayer.loadLegendFailed == undefined || !catLayer.loadLegendFailed)) {
                results.push(catLayer)
                legendLen += catLayer.hidden?0:1
            }
            return true
          } else {
            return false
          }
        })
        if (results.length == vm.legendLayers) {
            results = results.reverse()
            var changed = false
            for(var i = 0;i < results.length; i++) {
                if (results[i].id != vm.legendLayers.id) {
                    changed = true
                    break
                }
            }
            if (!changed) {
                return false
            }
        } else {
            results = results.reverse()
        }
        vm.legendLayers = results 
        if (vm.legendLayers.find(function(layer){return vm.hiddenLayers[layer.id]})) {
            vm.filteredLegendLayers = vm.legendLayers.filter(function(layer){
                return !vm.hiddenLayers[layer.id]
            })
        } else {
            vm.filteredLegendLayers = null
        }
        return true
      },
      toggleLegends: function() {
        var vm = this
        if (vm.legendsPanel.isActive) {
            vm.legendsPanel.close()
            vm.unwatchActiveLayers()
            vm.unwatchActiveLayers = false
            return
        }
        if (!vm.unwatchActiveLayers) {
            this.syncLegendLayers()
            vm.unwatchActiveLayers = this.$root.active.$watch("olLayers",function(newVal,oldVal){
                vm.syncLegendLayers()
            })
        }
        vm.legendsPanel.open()
      },
      loadLegendFailed:function(index,l) {
        this.legendLayers.splice(index,1)
        l.loadLegendFailed = true
        if(this.filteredLegendLayers ) {
            var index = this.filteredLegendLayers.indexOf(l)
            if (index >= 0) {
                this.filteredLegendLayers.splice(index,1)
            }
        }
        
      },
      getImageDataURL: function(img,format) {
        format = format || "image/jpeg"
        var canvas = document.createElement("canvas");
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        $(document.body).append($(canvas))
        var ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0,img.naturalWidth,img.naturalHeight,0,0,canvas.width,canvas.height);
        return canvas.toDataURL(format,1);
      },
      printLegends:function() {
        var vm = this
        this.getLegendBlob(false,false,function(blobData){
            var filename = vm.$root.export.finalTitle.replace(' ', '_') + ".legend.pdf"
            saveAs(blobData,filename)
        })
      },
      getLegendBlob:function(printAll,sync,callback) {
        var vm = this
        printAll = printAll || false
        sync = sync || false
        var hiddenLayers = null
        var filteredLegendLayers = null
        var nextTick = false
        if (!vm.legendsPanel.isActive) {
            //legend panel is not active, data is outdated.
            nextTick = vm.syncLegendLayers()
            //$("#active-layer-legends").css("zIndex",-999)
            //vm.legendsPanel.open()
        }
        if (printAll && vm.filteredLegendLayers != null) {
            //show all legends for printing
            hiddenLayers = vm.hiddenLayers
            filteredLegendLayers = vm.filteredLegendLayers
            vm.showAll()
            nextTick = true
        }
        var printFunc = function() {
            try {
                if ($("#active-layer-legend-list .layer-legend-row").length === 0) {
                    //no legend;
                    callback(null)
                    return
                }
                var paperSize = vm.$root.export.paperSizes["A4"]
                var style = { 
                  top: 20, 
                  bottom: 20, 
                  left: 20,
                  right:20,
                  width: paperSize[1],
                  height:paperSize[0],
                  fontHeight:10,
                  padding:5,
                  font:"helvetica",
                  fontType:"bold",
                  fontSize:10,
                  textColor:[0,0,0],
                  lineWidth: 1,
                  lineColor:[77,77,77]
                }
                var getImageSize = function(img,textHeight) {
                  var width = 0
                  var height = 0
                  var maxImageSize = [style.width - style.left - style.right,style.height - style.top - style.bottom - textHeight]
                  var imgSize = [Math.floor(img.naturalWidth / vm.dpmm), Math.floor(img.naturalHeight / vm.dpmm)]
                
                  if (imgSize[0] / imgSize[1] > maxImageSize[0] /maxImageSize[1]) {
                    if (imgSize[0] <= maxImageSize[0]) {
                        width = imgSize[0]
                        height = imgSize[1]
                    } else {
                        width = maxImageSize[0]
                        height = (imgSize[1] * width) / imgSize[0]
                    }
                  } else {
                    if (imgSize[1] <= maxImageSize[1]) {
                        height = imgSize[1]
                        width = imgSize[0]
                    } else {
                        height = maxImageSize[1]
                        width = (imgSize[0] * height) / imgSize[1]
                    }
                  }
                  return [width,height]
                }
                var doc = new jsPDF();
                doc.setFontSize(style.fontSize)
                doc.setFont(style.font)
                doc.setFontType(style.fontType)
                doc.setTextColor(style.textColor[0],style.textColor[1],style.textColor[2])
                doc.setLineWidth(style.lineWidth)
                doc.setDrawColor(style.lineColor[0],style.lineColor[1],style.lineColor[2])
                var top = style.top
                $("#active-layer-legend-list .layer-legend-row").each(function(index,element){
                    var imgElement = $(element).find("img").get(0)
                    var imageSize = getImageSize(imgElement,style.fontHeight)
                    if (top != style.top && top + style.fontHeight + imageSize[1] + style.bottom + 2 * style.padding + style.lineWidth > style.height) {
                        doc.addPage()
                        top = style.top
                    } else if (top !=style.top) {
                        top += style.padding
                        doc.setLineWidth(style.lineWidth)
                        doc.line(style.left,top,style.width - style.right,top)
                        top += style.lineWidth
                        top += style.padding
                    }
                    doc.text(style.left,top,$(element).find(".layer-title").text())
                    top += style.fontHeight
                    doc.addImage(vm.getImageDataURL(imgElement,"image/jpeg"),"JPEG",style.left,top,imageSize[0],imageSize[1])
                    top += imageSize[1]
                })
                callback(doc.output("blob"))
            } finally {
                if (hiddenLayers) {
                    //restore the legend panel
                    vm.hiddenLayers = hiddenLayers
                    vm.filteredLegendLayers = filteredLegendLayers
                }
            }
        }
        var syncedFunc = null
        syncedFunc = function() {
            if (!sync) {
                printFunc()
            } else if (vm.loadFinished) {
                //wait 2 seconds to let browser draw the image.
                setTimeout(printFunc,2000)
            } else {
                setTimeout(syncedFunc,500)
            }
        }

        if (nextTick) {
            vm.$nextTick(syncedFunc)
        } else {
            syncedFunc()
        }
      },
      setPosition:function(left,right,top,bottom) {
        if (left == null) {
            this._position[0] = right - parseInt($("#active-layer-legends").css('width'))
        } else {
            this._position[0] = left
        } 
        if (right == null) {
            this._position[1] = left + parseInt($("#active-layer-legends").css('width'))
        } else {
            this._position[1] = right
        }
        if (top == null) {
            this._position[2] = bottom - parseInt($("#active-layer-legends").css('height'))
        } else {
            this._position[2] = top
        }
        if (bottom == null) {
            this._position[3] = top + parseInt($("#active-layer-legends").css('height'))
        } else {
            this._position[3] = bottom
        }
        $("#active-layer-legends").get(0).style.left = this._position[0] + "px"
        $("#active-layer-legends").get(0).style.right = this._position[1] + "px"
        $("#active-layer-legends").get(0).style.top = this._position[2] + "px"
        $("#active-layer-legends").get(0).style.bottom = this._position[3] + "px"
      },
    },
    ready: function () {
      var vm = this
      vm._position = null
      $("#active-layer-legends").on("open.zf.reveal",function(){
        if (vm._position == null) {
            vm._position = [null,null,null,null]
            vm.setPosition(null,parseInt($(document.body).css('width')),0,null)
        } else {
            vm.setPosition(vm._position[0],vm._position[1],vm._position[2],vm._position[3])
        }

      })

      vm._interact = interact($("#active-layer-legends").get(0),{
        })
        .resizable({
            edges:{
                top:true,
                left:true,
                bottom:true,
                right:false
            },
            preserveAspectRatio:false,
            onmove:function(event){
                var target = event.target

                // update the element's style
                target.style.width  = event.rect.width + 'px';
                target.style.height = event.rect.height + 'px';
                vm.setPosition(event.rect.left,event.rect.right,event.rect.top,event.rect.bottom)
            }
        })
        .draggable({
            intertia:true,
            restrict:{
                restriction:document.body,
                endOnly:true,
                elementRect:{top:0,left:0,bottom:1,right:1}
            },
            autoScroll:true,
            onmove: function(event){
                var target = event.target
                // keep the dragged position in the data-x/data-y attributes
                //console.log("x0 = " + event.x0 +",y0= " + event.y0 + ",clientX0=" + event.clientX0 + ",clientY0=" + event.clientY0 + ",dx=" + event.dx + ",dy=" + event.dy)
                vm._position[0] = vm._position[0] + event.dx
                vm._position[1] = vm._position[1] + event.dx
                vm._position[2] = vm._position[2] + event.dy
                vm._position[3] = vm._position[3] + event.dy
                //vm.setPosition(vm._position[0] + event.dx,vm._position[1] + event.dx ,vm._position[2] + event.dy,vm._position[3] + event.dy)
                vm.setPosition(vm._position[0],vm._position[1] ,vm._position[2],vm._position[3])

            },
            onend:function(event) {
                //vm._interact.draggable(false)
            }
        })
      vm._interact.draggable(false)
    }
  }
</script>
