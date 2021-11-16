<template>
  <div class="tabs-panel is-active" id="menu-tab-layers">
    <div class="row collapse">
      <div class="columns">
        <ul class="tabs" data-tabs id="layers-tabs">
          <li class="tabs-title is-active" menu="active"><a href="#layers-active" aria-selected="true">Active</a></li>
          <li class="tabs-title" menu="catalogue"><a href="#layers-catalogue">Browse Layers</a></li>
          <li class="tabs-title" menu="export"><a href="#layers-export">Save & Print</a></li>
        </ul>
      </div>
    </div>
    <div class="row collapse" id="layers-tab-panels">
      <div class="columns">
        <div class="tabs-content vertical" data-tabs-content="layers-tabs">
          <gk-active v-ref:active></gk-active>
          <gk-catalogue v-ref:catalogue></gk-catalogue>
          <gk-export v-ref:export></gk-export>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import gkActive from './layers/active.vue'
  import gkCatalogue from './layers/catalogue.vue'
  import gkExport from './layers/export.vue'

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
    components: { gkActive, gkCatalogue, gkExport },
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
            menu = menu || "active"
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
      $("#layers-tabs").on("change.zf.tabs",function(target,selectedTab){
          var menu = selectedTab.attr('menu')
          vm.info.hoverable.splice(0,vm.info.hoverable.length)
          vm.switchMenu(menu)
          vm.$root.menuChanged()
      })
    }
  }
</script>
