<template src="./legend.svg"></template>
<script>
  export default {
    computed: {
      legendInfo: {
        cache: false,
        get: function () {
          return this.$root.export.legendInfo()
        }
      },
      title: function () {
        return this.$root.export.title
      }
    }
  }
</script>
