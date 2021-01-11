<template>
  <div class="slide">
      <HongKong v-if="locIdx==0" v-bind:path="path"></HongKong>
      <District v-else v-bind:dIndex="locIdx" v-bind:path="path" />
  </div>
</template>
<script>
import HongKong from './HongKong.vue'
import District from './District.vue'

export default {
    name: 'Slide',
    props: {
        path: String
    },
    data() {
        return{
            timer: '',
            locIdx: -1,
            locLoop: ["Hong Kong", "Central and Western", "Eastern", "Southern", "Wan Chai", 
                "Kowloon City", "Kwun Tong", "Sham Shui Po", "Wong Tai Sin",
                "Yau Tsim Mong", "Islands", "Kwai Tsing", "North",
                "Sai Kung", "Sha Tin", "Tai Po", "Tsuen Wan",
                "Tuen Mun", "Yuen Long"],
            hongKongDelay : 11000,
            districtDelay : 7000,
        }        
    },
    components:{
        HongKong,
        District,
    },
    mounted() {
        //this.timer = setInterval(this.get, 1000);
        this.path = "C:\\GitProjects\\hkcovidmap\\out\\2020-12-26";
        this.startAnim();
        
    },
    methods: {
        startAnim() {
            console.log("shit" + this.locIdx);
            this.locIdx = (this.locIdx +1)% 19;
            var delay = 0;
            if (this.locIdx == 0)
                delay = this.hongKongDelay;
            else   
                delay = this.districtDelay;
            this.timer = setTimeout(this.startAnim, delay*2);
            
        }
    },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
.slide {
    width: 100%;
    height: 100%;
}
</style>
