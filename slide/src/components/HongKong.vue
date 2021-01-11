<template>
  <div class="hk">
      <table class="display">
        <tr>
            <td class="main" colspan="2">
                <img :key="image.id" class="imageMain" :src="image.src" alt="image.alt">
                <img :key="imageNext.id" class="imageMainHidden" :src="imageNext.src" alt="image.alt">
            </td>
            <td class="ranking" rowspan="2">
                <table>
                    <tbody>
                    <tr>
                        <th>地區</th>
                        <th>今日</th>
                        <th>7日</th>
                        <th>14日</th>
                        <th>總計</th>
                    </tr>
                    <template v-for="[key, value] in rank  ">
                        <tr :key="key">
                            <td> {{ translateZh[key] }} </td>
                            <td> {{ value.today || 0 }} </td>
                            <td> {{ value.day7 || 0}} </td>
                            <td> {{ value.day14 || 0}} </td>
                            <td> {{ value.all || 0}} </td>
                        </tr>
                    </template>
                    </tbody>
                </table>
            </td>
        </tr>
        <tr>
            <td class="summary1">
                <img src= "info/hospital_case.png"/>
            </td>
            <td class="summary2">
                <table>
                    <tr>
                        <td>出院</td>
                        <td>{{hcase.discharged_count}}</td>
                    </tr>
                    <tr>
                        <td>死亡</td>
                        <td>{{hcase.deceased_count}}</td>
                    </tr>
                    <tr>
                        <td>住院</td>
                        <td>{{hcase.hospitalize_count}}</td>
                    </tr>
                </table> 
            </td>
        </tr>
        </table>
  </div>
</template>
<script>
export default {
    name: 'HongKong',
    props: {
        path: String
    },
    mounted() {
        //this.timer = setInterval(this.get, 1000);
        //this.path = "C:\\GitProjects\\hkcovidmap\\out\\2020-12-26";
        this.path = "info";
        
        this.read_rank();
        this.read_hospital_case();
        this.switchImage();
    },
    data() {
        return{
            timer: '',
            rank: '',
            hcase: '',
            index: 0,
            image: null,
            imageNext: null,
            images: [{
                    id: 1,
                    src: "info/cumulative_case.png",
                    alt: "cumulative", 
                    displayTime: 2000,
                },
                {
                    id: 2,
                    src: "info/day_case.png",
                    alt: "day case",
                    displayTime: 2000,
                },
                {
                    id: 3,
                    src: "info/age_gender.png",
                    alt: "day case",
                    displayTime: 2000,
                },
                {
                    id: 4,
                    src: "info/0-A.png",
                    alt: "danger zone",
                    displayTime: 500,
                },
                {
                    id: 5,
                    src: "info/1-A.png",
                    alt: "danger zone",
                    displayTime: 500,
                },
                {
                    id: 6,
                    src: "info/2-A.png",
                    alt: "danger zone",
                    displayTime: 500,
                },
                {
                    id: 7,
                    src: "info/3-A.png",
                    alt: "danger zone",
                    displayTime: 500,
                },
                {
                    id: 8,
                    src: "info/4-A.png",
                    alt: "danger zone",
                    displayTime: 500,
                },
                {
                    id: 9,
                    src: "info/5-A.png",
                    alt: "danger zone",
                    displayTime: 500,
                },
                {
                    id: 10,
                    src: "info/6-A.png",
                    alt: "danger zone",
                    displayTime: 2000,
                },
            ], 
            translateZh : {
                "Hong Kong": 11,
                "Central and Western": "中西區",
                "Eastern": "東區",
                "Southern": "南區",
                "Wan Chai": "灣仔區",
                "Kowloon City": "九龍城區",
                "Kwun Tong": "觀塘區",
                "Sham Shui Po": "深水埗區",
                "Wong Tai Sin": "黃大仙區",
                "Yau Tsim Mong": "油尖旺區",
                "Islands": "離島區",
                "Kwai Tsing": "葵青區",
                "North": "北區", 
                "Sai Kung": "西貢區",
                "Sha Tin": "沙田區",
                "Tai Po": "大埔區",
                "Tsuen Wan": "荃灣區",
                "Tuen Mun": "屯門區",
                "Yuen Long": "元朗區",
                "Others": "未歸類",  
            },
        }
    },
    methods: {
        read_rank(){
            var fpath = this.path + "\\rank_concat.json"
            fetch(fpath)
                .then(response => response.json())
                .then(data => {
                    delete data['Uncertain']
                    
                    // Create items array
                    var items = Object.keys(data).map(function(key) {
                    return [key, data[key]];
                    });
                    // Sort the array based on the second element
                    items.sort(function(first, second) {
                        return second[1].today - first[1].today;
                    });


                    this.rank = items;
                }
                )
        },
        read_hospital_case(){
            var fpath = this.path + "\\case_summary.json"
            fetch(fpath)
                .then(response => response.json())
                .then(data => this.hcase = data)
        },
        switchImage() {
            this.image = this.images[this.index];
            var timeout = this.images[this.index].displayTime * 2;
            this.index = (this.index + 1) % this.images.length;
            this.imageNext = this.images[this.index];
            this.timer = setTimeout(this.switchImage, timeout);
        },
        beforeDestroy(){
            clearTimeout(this.timer);
        }
    },
}
//read the statistic
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
td.main{
    height: 70%;
    width: 70%;
    background-color: white;
}
td.summary1{
    height: 30%;
    width: 35%;
    background-color: white;
}
td.summary2{
    height: 30%;
    width: 35%;
    font-size: 35px;
    background-color: white;
}
td.ranking{
    height: 100%;
    width:30%;
    font-size: 20px;
    background-color: white;
}
.hk, .display {
    width: 100%;
    height: 100%;
}
img{
    height: 250px;
}
.imageMain{
    width: 896px;
    height: 504px;
}
.imageMainHidden{
    width: 0px;
    height: 0px;
    visibility: hidden;
}
</style>
