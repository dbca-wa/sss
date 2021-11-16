<template>
  <div class="tabs-panel" id="menu-tab-settings">
    <div class="row collapse">
      <div class="columns">
        <ul class="tabs" data-tabs id="settings-tabs">
          <li class="tabs-title is-active" menu="systemsetting"><a href="#systemsetting" aria-selected="true">System</a></li>
          <li class="tabs-title" menu="weatheroutlook"><a href="#weatheroutlook" aria-selected="true">Weather Outlook</a></li>
        </ul>
      </div>
    </div>
    <div class="row collapse" id="settings-tab-panels">
      <div class="columns">
        <div class="tabs-content vertical" data-tabs-content="settings-tabs">
          <gk-systemsetting v-ref:systemsetting></gk-systemsetting>
          <gk-weatheroutlook v-ref:weatheroutlook></gk-weatheroutlook>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import gkSystemsetting from './systemsetting.vue'
  import gkWeatheroutlook from './weatheroutlook.vue'

  export default { 
    store: {
        activeMenu:'activeMenu',
        activeSubmenu:'activeSubmenu'
    },
    data: function () {
      return {
        menu:null
      }
    },
    components: { gkSystemsetting,gkWeatheroutlook },
    computed: {
        info: function () { return this.$root.info },
    },
    methods:{
        setup: function() {
            this.$root.annotations.setTool()
            this.switchMenu(this.menu)
        },
        teardown:function() {
            if (this.activeSubmenu && this.$root[this.activeSubmenu].teardown) {
                this.$root[activeSubmenu].teardown()
            }
        },
        switchMenu:function(menu) {
            menu = menu || "systemsetting"
            if ((this.activeSubmenu === menu) || (!this.activeSubmenu && !menu)) {
                //new active submenu is equal to current active submenu, do nothing
                return
            }
            if (this.activeSubmenu && this.$root[this.activeSubmenu].teardown) {
                this.$root[this.activeSubmenu].teardown()
            }
            this.activeSubmenu = menu
            if (this.activeSubmenu && this.$root[this.activeSubmenu].setup) {
                this.$root[this.activeSubmenu].setup()
            }
            this.menu = menu
        }
    }, 
    ready: function () {
      var vm = this
      $("#settings-tabs").on("change.zf.tabs", function(target, selectedTab){
          var menu = selectedTab.attr('menu')
          vm.info.hoverable.splice(0, vm.info.hoverable.length)
          vm.switchMenu(menu)
          vm.$root.menuChanged()
      })
	}
  }
</script>
