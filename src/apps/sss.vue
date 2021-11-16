<template>
    <gk-loading v-ref:loading application="SSS"></gk-loading>
    <div class="off-canvas-wrapper">
        <div class="off-canvas-wrapper-inner" data-off-canvas-wrapper>
            <div class="off-canvas position-left" id="offCanvasLeft" data-off-canvas>
                <a id="side-pane-close" class="button alert hide-for-medium">&#x2715;</a>
                <div class="tabs-content vertical" data-tabs-content="menu-tabs">
                    <gk-settings v-ref:settings></gk-settings>
                    <gk-layers v-ref:layers></gk-layers>
                    <gk-annotations v-ref:annotations></gk-annotations>
                    <gk-tracking v-ref:tracking></gk-tracking>
					<gk-thermal v-ref:thermal></gk-thermal>
                    <gk-bfrs v-ref:bfrs></gk-bfrs>
                    <gk-dialog v-ref:dialog></gk-dialog>
                </div>
                <div class="tool-slice row collapse" style="width:100%; margin-top:-32px" v-if="$root.hasHints" >
                  <div v-if="$root.isShowHints" id="hints">
                      <hr class="small-12" style="margin-bottom:0; margin-top:0"/>
                      <template v-for="hint in hints">
                          <div class="small-12">{{hint.name}}:</div>
                          <div class="small-12">
                            <ul style="margin-bottom:0px">
                            <template v-for="description in hint.description">
                                <li>{{description}}</li>
                            </template>
                            </ul>
                          </div>
                      </template>
                  </div>
                  <div class="small-12 " style="text-align:right;">
                      <img src="dist/static/images/question-mark.png" style="height:32px;width:32px" @click="systemsetting.toggleShowHints()">
                  </div>
                </div>
            </div>
            <div class="off-canvas-content" data-off-canvas-content>
                <ul class="tabs vertical map-widget" id="menu-tabs" data-tabs>
                    <li class="tabs-title side-button is-active" menu="layers">
                        <a href="#menu-tab-layers" title="Map Layers">
                            <svg class="icon">
                                <use xlink:href="dist/static/images/iD-sprite.svg#icon-layers"></use>
                            </svg>
                        </a>
                    </li>
                    <li class="tabs-title side-button" menu="annotations">
                        <a href="#menu-tab-annotations" title="Drawing Tools">
                            <i class="fa fa-pencil" aria-hidden="true"></i>
                        </a>
                    </li>
                    <li class="tabs-title side-button"  menu="tracking">
                        <a href="#menu-tab-tracking" title="Resources Tracking">
                            <i class="fa fa-truck" aria-hidden="true"></i>
                        </a>
                    </li>
					<li class="tabs-title side-button"  menu="thermal">
                        <a href="#menu-tab-thermal" title="Thermal Imaging">
                            <i class="fa fa-plane" aria-hidden="true"></i>
                        </a>
                    </li>
                    <li class="tabs-title side-button" menu="bfrs">
                        <a href="#menu-tab-bfrs" title="Bushfire Report System">
                            <i class="fa fa-fire" aria-hidden="true"></i>
                        </a>
                    </li>
                    <li class="tabs-title side-button" menu="settings">
                        <a href="#menu-tab-settings" title="System Settings">
                            <i class="fa fa-cog" aria-hidden="true"></i>
                        </a>
                    </li>
                </ul>
                <gk-map v-ref:map></gk-map>
            </div>
        </div>
    </div>
    <div id="external-controls"></div>
</template>

<script>
    import gkMap from '../components/map.vue'
    import gkLayers from '../components/layers.vue'
    import gkAnnotations from '../components/annotations.vue'
    import gkTracking from '../components/sss/tracking.vue'
	import gkThermal from '../components/sss/thermal.vue'
    import gkLoading from '../components/loading.vue'
    import gkSettings from '../components/settings.vue'
    import gkBfrs from '../components/sss/bfrs.vue'
    import gkDialog from '../components/dialog.vue'
    import { ol } from 'src/vendor.js'


    export default { 
      store:{
        activeMenu:'activeMenu',
        activeSubmenu:'activeSubmenu',
        hints:'hints'
      },
      data: function() {
        return {
        }
      },
      computed: {
          layers: function () { return this.$root.layers },
          info: function () { return this.$root.info },
          systemsetting: function () { return this.$root.systemsetting },
          settings: function () { return this.$root.settings },
      },
      components: {gkMap, gkLayers, gkAnnotations, gkTracking, gkThermal, gkLoading, gkSettings, gkBfrs, gkDialog},
      methods:{
        switchMenu: function(menu) {
			//alert('sss.vue L110 switchMenu')
            if ((this.activeMenu === menu) || (!this.activeMenu && !menu)) {
                //new active menu is equal to current active menu, do nothing
                return
            }
            if (this.activeMenu && this.$root[this.activeMenu].teardown) {
                this.$root[this.activeMenu].teardown()
            }
            this.activeMenu = menu || null
            this.activeSubmenu = null

			if (this.activeMenu && this.$root[this.activeMenu].setup) {
                this.$root[this.activeMenu].setup()
            }
            if (["layers", "settings"].indexOf(menu) < 0) {
                this.activeSubmenu = null
            }
            this.$root.menuChanged()
        }
      },
      ready: function () {
        var vm = this
        $("#menu-tabs").on("change.zf.tabs", function(target, selectedTab){
            var menu = selectedTab.attr('menu')
            vm.info.hoverable.splice(0, vm.info.hoverable.length)
            vm.switchMenu(menu)
        })
      }
    }
</script>

