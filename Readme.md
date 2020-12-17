# Just a prototype of showing case in Hong Kong map

# 使用pip3安裝Jupyter
pip3 install --upgrade pip
pip3 install jupyter

pip3 install folium # 安裝 Folium package

selenium

download gecko driver and install firefox

set gecko driver path

# Create a program and stream it to youtube

[x] data source
[x] line-chart
[x] 18 area
[x] the central coordinate
[x] the layout

Shapely 
Fiona
 GeoPandas
 
# 18 district info
https://gis.stackexchange.com/questions/183248/getting-polygon-boundaries-of-city-in-json-from-google-maps-api

Search for the OSM id
https://nominatim.openstreetmap.org/ui/details.html?osmtype=R&osmid=2800276&class=boundary

Paste the OSM id to this website
http://polygons.openstreetmap.fr/index.py


HK
	22.350627,114.1849161
中西區	Central and Western
	22.2748365,114.14873730393252
東區	Eastern
	22.2730777,114.23359377341592
南區	Southern
	22.2192627,114.22522984854672
灣仔區	Wan Chai
	22.27394695,114.18174874679013
九龍城區	Kowloon City
	22.32179955,114.18859418638175
觀塘區	Kwun Tong
	22.308648599999998,114.22766104671223
深水埗區	Sham Shui Po
	22.33125395,114.15932119657994
黃大仙區	Wong Tai Sin
	22.34432185,114.20215028440833
油尖旺區	Yau Tsim Mong
	22.3074036,114.16552591155013
離島區	Islands
	22.23007565,113.98678546827477
葵青區	Kwai Tsing
	22.34101175,114.10428534268473
北區	North
	22.516949349999997,114.21359265126003
西貢區	Sai Kung
		22.3070096,114.37134533899689
沙田區	Sha Tin
		22.39157275,114.20809762908664
大埔區	Tai Po
	22.480971150000002,114.30410296970287
荃灣區	Tsuen Wan
		22.364986950000002,114.07768836682578
屯門區	Tuen Mun
	22.3788404,113.95282979560184
元朗區	Yuen Long
	22.45729575,114.02131879795456

# Youtube broadcast a 

* Main map
	animated for a month 
* district map
	animated for a month

* Trend
* overall	age group
* 

# A simple shit done

age group bar race date

study the format

generate the data

# Reference

https://blog.yeshuanova.com/2017/10/python-visulization-folium/

https://medium.com/coinmonks/visualizing-property-prices-in-hong-kong-with-pandas-overpy-and-folium-595240ffca90


df_city_group = data_master.loc[:, ['citizenship_en']]
city_case = df_city_group.groupby('citizenship_en').size()
ax = city_case.plot.bar()



Youtube data 


https://flourish.studio/

image: https://steachs.com/archives/36806