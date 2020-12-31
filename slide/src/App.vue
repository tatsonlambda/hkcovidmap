<template>
  <div id="app">
    <Slide/>
  </div>
</template>

<script>
import Slide from './components/Slide.vue'


export default {
  name: 'App',
  components: {
    Slide
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  width: 1280px;
  height: 720px;
}
</style>
