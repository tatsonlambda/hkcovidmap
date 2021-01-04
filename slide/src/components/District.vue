<template>
    <div class="district">
        <h1 class="title">{{locLoopZh[dIndex]}}</h1>
        <img :key="image.id" class="imageMain" :src="image.src" alt="image.alt">
        <img :key="imageNext.id" class="imageMainHidden" :src="imageNext.src" alt="imageNext.alt">
        <!--<table class="display">
        <tr>
            <td class="main" rowspan="2" >
                
            </td>
            <td class="case" >
                <img :key="99" class="imageCase" :src="imageCase" alt="daily case in district">
            </td>
        </tr>
        <tr>
            <td class="danger">
                <img :key="100" class="imageDanger" :src="imageDanger" alt="danger place in district">
            </td>
        </tr>
        </table>-->
    </div>
</template>
<script>
export default {
  name: 'District',
  props: {
    dIndex: Number,
    path: String,
  },
  data() {
        return{
            index: 0,
            timer: '',
            locLoop: ["Hong Kong", "Central and Western", "Eastern", "Southern", "Wan Chai", 
                "Kowloon City", "Kwun Tong", "Sham Shui Po", "Wong Tai Sin",
                "Yau Tsim Mong", "Islands", "Kwai Tsing", "North",
                "Sai Kung", "Sha Tin", "Tai Po", "Tsuen Wan",
                "Tuen Mun", "Yuen Long"],
            locLoopZh: ["香港", "中西區", "東區", "南區", "灣仔區", "九龍城區", "觀塘區", 
                  "深水埗區", "黃大仙區", "油尖旺區", "離島區", "葵青區", "北區",
                  "西貢區", "沙田區", "大埔區", "荃灣區", "屯門區", "元朗區"
            ],
            image: null,
            imageNext: null,
            images: [{
                    id: 1,
                    src: "info/%s/cumulative_case.png",
                    srcT: "info/%s/cumulative_case.png",
                    alt: "cumulative", 
                    displayTime: 2000,
                },
                {
                    id: 2,
                    src: "info/%s/0A.png",
                    srcT: "info/%s/0A.png",
                    alt: "danger zone",
                    displayTime: 500,
                },
                {
                    id: 3,
                    src: "info/%s/1A.png",
                    srcT: "info/%s/1A.png",
                    alt: "danger zone",
                    displayTime: 500,
                },
                {
                    id: 4,
                    src: "info/%s/2A.png",
                    srcT: "info/%s/2A.png",
                    alt: "danger zone",
                    displayTime: 500,
                },
                {
                    id: 5,
                    src: "info/%s/3A.png",
                    srcT: "info/%s/3A.png",
                    alt: "danger zone",
                    displayTime: 500,
                },
                {
                    id: 6,
                    src: "info/%s/4A.png",
                    srcT: "info/%s/4A.png",
                    alt: "danger zone",
                    displayTime: 500,
                },
                {
                    id: 7,
                    src: "info/%s/5A.png",
                    srcT: "info/%s/5A.png",
                    alt: "danger zone",
                    displayTime: 500,
                },
                {
                    id: 8,
                    src: "info/%s/6A.png",
                    srcT: "info/%s/6A.png",
                    alt: "danger zone",
                    displayTime: 2000,
                },
            ],
            imageCase: 'info/%s/day_case.png',
            imageDanger: 'info/%s/zone14d.png',
            imageCaseT: 'info/%s/day_case.png',
            imageDangerT: 'info/%s/zone14d.png',
        }        
    },
    watch: { 
        dIndex: function(newVal, oldVal) { // watch it
            if(newVal == oldVal) return;
            //eslint-disable-next-line no-console 
            //debugger
            console.log("watcher...");
            this.resetComponent(newVal);
        }
    },
    created() {
        this.resetComponent(this.dIndex);
    },
    methods: {
        resetComponent(newVal){
            if(this.timer != '')
                clearTimeout(this.timer);
            this.index = 0;
            
            //update all the image shit
            console.log("shit" + newVal)
            var districtName = this.locLoop[newVal]; 
            console.log("shit" + newVal + " " + districtName);
            
            this.imageCase = this.imageCaseT.replace("%s", districtName);
            this.imageDanger = this.imageDangerT.replace("%s", districtName);

            for(var i=0; i<this.images.length; ++i){
                let ii = this.images[i];
                ii.src = ii.srcT.replace("%s", districtName);
            }

            this.switchImage();
        },
        switchImage() {
            this.image = this.images[this.index];
            var timeout = this.images[this.index].displayTime *2;
            this.index = (this.index + 1) % this.images.length;
            this.imageNext = this.images[this.index];
            this.timer = setTimeout(this.switchImage, timeout);
        },
        beforeDestroy(){
            clearTimeout(this.timer);
        }
    }
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
.district{
    width: 100%;
    height: 100%;
}
.title{
    height: 40px;
}
.display{
    width: 100%;
    height: 90%;
}
td.main{
    height: 100%;
    width: 60%;
    background-color: blue;
}
td.case{
    height: 50%;
    width: 40%;
    background-color: yellow;
}
td.danger{
    height: 50%;
    width: 40%;
    background-color: green;
}
.imageMain{
    width: 1280px;
    height: 650px;
}
.imageMainHidden{
    width: 0px;
    height: 0px;
    visibility: hidden;
}
.imageCase{
    width: 512px;
}
.imageDanger{
    width: 512px;
}
</style>
0