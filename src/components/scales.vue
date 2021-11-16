<template>
    <div style="display:none">
    <select class="map-control" v-el:scale-select @change="$root.map.setScale($event.target.value)" id="menu-scale" v-cloak>
        <option value="{{ $root.map.scale }}" selected>{{ scaleString }}</option>
        <option v-for="s in fixedScales" value="{{ s }}">{{ $root.map.getScaleString(s) }}</option>
    </select>
    </div>
</template>

<style>

</style>

<script>
  import { $, ol } from 'src/vendor.js'
  export default {
    store: ['fixedScales'],
    data: function () {
      return {}
    },
    computed: {
      // scale string for the current map zoom level
      scaleString: function () {
        return this.$root.map.getScaleString(this.$root.map.scale)
      }
    },
    methods: {
      reset: function () {
        this.$els.scaleSelect.selectedIndex = 0
      }
    },
    ready: function () {
      var vm = this;
      this.$on('gk-init', function () {
        this.$root.map.olmap.on('postrender', function () {
          vm.reset()
        })
      })
    }
  }
</script>
