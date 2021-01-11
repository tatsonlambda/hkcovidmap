import sys

import pandas as pd 
from datetime import datetime, timedelta
import folium
from folium.plugins import HeatMapWithTime
import numpy as np
from folium.plugins import HeatMap

import io
from PIL import Image

import urllib.request

from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt

from shapely.geometry import Polygon, Point
import json
from shapely.geometry import shape, GeometryCollection
import matplotlib.dates as dates

import os
import imageio

import logging
from logging.handlers import RotatingFileHandler
import traceback


# logging
logging.basicConfig(level=logging.INFO,
					format ="%(asctime)s %(levelname)s %(message)s",
					datefmt = "%Y-%m-%d %H:%M",
					handlers = [RotatingFileHandler("batch.log", mode='a', maxBytes=5*1024*1024, 
                                 backupCount=2, encoding=None, delay=0)])

# constant

## directory
data_dir = "./data"
out_dir = "./out"
geo_dir = "./geodata"

## data
confirm_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSr2xYotDgnAq6bqm5Nkjq9voHBKzKNWH2zvTRx5LU0jnpccWykvEF8iB_0g7Tzo2pwzkTuM3ETlr_h/pub?gid=0&range=A2:ZZ&output=csv'
highrisk_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vT6aoKk3iHmotqb5_iHggKc_3uAA901xVzwsllmNoOpGgRZ8VAA3TSxK6XreKzg_AUQXIkVX5rqb0Mo/pub?gid=0&range=A2:ZZ&output=csv'

## const data

district_list = ["Central and Western", "Eastern", "Southern", "Wan Chai", 
            "Kowloon City", "Kwun Tong", "Sham Shui Po", "Wong Tai Sin",
            "Yau Tsim Mong", "Islands", "Kwai Tsing", "North",
            "Sai Kung", "Sha Tin", "Tai Po", "Tsuen Wan",
            "Tuen Mun", "Yuen Long"]

district_zh_list = ["中西區", "東區", "南區", "灣仔區", "九龍城區", "觀塘區", 
                  "深水埗區", "黃大仙區", "油尖旺區", "離島區", "葵青區", "北區",
                  "西貢區", "沙田區", "大埔區", "荃灣區", "屯門區", "元朗區"]
				  
				  
loc_center = {
    "Hong Kong": [22.350627,114.1849161],
    "Central and Western": [22.2748365,114.14873730393252],
    "Eastern": [22.2730777,114.23359377341592],
    "Southern": [22.2192627,114.22522984854672],
    "Wan Chai": [22.27394695,114.18174874679013],
    "Kowloon City": [22.32179955,114.18859418638175],
    "Kwun Tong": [22.308648599999998,114.22766104671223],
    "Sham Shui Po": [22.33125395,114.15932119657994],
    "Wong Tai Sin": [22.34432185,114.20215028440833],
    "Yau Tsim Mong": [22.3074036,114.16552591155013],
    "Islands": [22.23007565,113.98678546827477],
    "Kwai Tsing": [22.34101175,114.10428534268473],
    "North": [22.516949349999997,114.21359265126003],
    #"Sai Kung": [22.3070096,114.37134533899689],
	"Sai Kung": [22.320539050237286, 114.28908247906098],
    "Sha Tin": [22.39157275,114.20809762908664],
    #"Tai Po": [22.480971150000002,114.30410296970287],
	"Tai Po": [22.4513638406378, 114.21404774082055],
    "Tsuen Wan": [22.364986950000002,114.07768836682578],
    "Tuen Mun": [22.3788404,113.95282979560184],
    "Yuen Long": [22.45729575,114.02131879795456],    
}


loc_zoom = {
    "Hong Kong": 11,
    "Central and Western": 14,
    "Eastern": 14,
    "Southern": 13,
    "Wan Chai": 14,
    "Kowloon City": 14,
    "Kwun Tong": 14,
    "Sham Shui Po": 14,
    "Wong Tai Sin": 14,
    "Yau Tsim Mong": 14,
    "Islands": 12,
    "Kwai Tsing": 13,
    "North": 12, 
    "Sai Kung": 13,
    "Sha Tin": 13,
    "Tai Po": 13,
    "Tsuen Wan": 14,
    "Tuen Mun": 13,
    "Yuen Long": 13,    
}

district_polys = []

# cache
cache = {}

# initialization
def init(batch_date):
	logging.info("init")
	
	str_batch = batch_date.strftime("%Y-%m-%d")
	
	# create data directory
	batch_data_dir = os.path.join(data_dir, str_batch)
	if not os.path.exists(batch_data_dir):
		os.mkdir(batch_data_dir)
	
	# create output directory
	batch_out_dir = os.path.join(out_dir, str_batch)
	if not os.path.exists(batch_out_dir):
		os.mkdir(batch_out_dir)
		
	# create all the district 
	for dis in district_list:
		output_path = os.path.join(out_dir, str_batch, dis) 
		if not os.path.exists(output_path):
			os.mkdir(output_path)
	
	# read polygon data
	global district_polys
	district_polys	= [] 
	for district in district_list:
		filename = os.path.join(geo_dir, district + ".txt")
		with open(filename) as f:
			features = json.load(f)
			district_polys.append(shape(features))
			
	return batch_data_dir, batch_out_dir

# utility function

def findDistrict(point):

    for i, poly in enumerate(district_polys):
        if poly.contains(point):
            return i
    
    return -1
	
def loc_time_range(center, df, start, end, zoom=11):
 
    is_last_14 = (df['end_date'] >= start.strftime("%Y-%m-%d")) & (df['end_date'] <= end.strftime("%Y-%m-%d")) & df['lat'].notnull()& df['lng'].notnull() 
    last_14_df = df[is_last_14]

    df1 = last_14_df[['lat', 'lng']].values.tolist()
    
    fmap = folium.Map(center, zoom_start=zoom, )
    fmap.add_child(HeatMap(data=df1, radius=10, blur=10))
    
    return fmap

def adjustedRadius(currentZoom):
    currentZoom = currentZoom -1
    if (currentZoom == 8):
        radius = 6
    elif (currentZoom == 10):
        radius = 8
    elif (currentZoom == 11):
        radius = 10
    elif (currentZoom == 12):
        radius = 12
    elif (currentZoom == 13):
        radius = 14
    elif (currentZoom == 14):
        radius = 16
    elif (currentZoom == 15):
        radius = 18
        
    return radius
	
def drawHeatMap(df, center, title, json_url, zoom=11):

    df1 = df[['lat', 'lng']].values.tolist()
    
    fmap = folium.Map(center, zoom_start=zoom, )
    
    if json_url is not None:
        fmap.add_child(folium.GeoJson(json_url, name='geojson' )) #.add_to(fmap)
    
    fmap.add_child(HeatMap(data=df1, radius=adjustedRadius(zoom), blur=6))
    
    fmap.caption = title
    
    title_html = '<h3 align="center" style="font-size:20px"><b>' + title + '</b></h3>'
    fmap.get_root().html.add_child(folium.Element(title_html))

    return fmap

def filter_distict_time_range(df, district, start, end):
 
    is_last_14 = (df['end_date'] >= start.strftime("%Y-%m-%d")) & (df['end_date'] <= end.strftime("%Y-%m-%d")) & df['lat'].notnull()& df['lng'].notnull() 
    if district is not None:
        is_last_14 = (df["real_distict"] == district) & is_last_14
    
    last_14_df = df[is_last_14]
    
    return last_14_df

def parse_zhch(s):
    return str(str(s).encode('ascii' , 'xmlcharrefreplace'))[2:-1]

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n+1)


def download_data(batch_data_dir):

	logging.info("read_data")
	
	case_fname = os.path.join(batch_data_dir, "case.csv") 
	highrisk_fname = os.path.join(batch_data_dir, "location.csv")

	f_case = open(case_fname, "w", encoding='UTF-8')
	f_highrisk = open(highrisk_fname, "w", encoding='UTF-8')

	with urllib.request.urlopen(highrisk_url) as f:
		html = f.read().decode('utf-8')
		f_highrisk.write(html)

	with urllib.request.urlopen(confirm_url) as f:
		html = f.read().decode('utf-8')
		f_case.write(html)
		
	f_case.close()
	f_highrisk.close()
	
	
def preprocess_data(batch_data_dir):
	
	case_fname = os.path.join(batch_data_dir, "case.csv") 
	highrisk_fname = os.path.join(batch_data_dir, "location.csv")

	df_case = pd.read_csv(case_fname, encoding='utf8') 
	df_loc = pd.read_csv(highrisk_fname, encoding='utf8') 
	
	# Make Central & Western back to and
	df_case['citizenship_district_en'] = df_case['citizenship_district_en'].replace("Central & Western","Central and Western")
	
	# supplement real district
	df_loc['real_distict'] = 'other'
	df_loc['real_distict_zh'] = 'other'

	for index, row in df_loc.iterrows():
		district_num = findDistrict(Point(row['lng'], row['lat']))
		if district_num != -1:
			district_en = district_list[district_num]
			district_zh = district_zh_list[district_num]
			df_loc.at[index, 'real_distict'] = district_en
			df_loc.at[index, 'real_distict_zh'] = district_zh
	
	# district group by fix
	df_case['citizenship_district_en'] = df_case['citizenship_district_en'].fillna("Others")

	return df_case, df_loc

def group_case_by_confirmation_date(df_case):

	df_by_date = df_case.loc[:, ['confirmation_date']] 
	by_date = df_by_date.groupby('confirmation_date').size()
	by_date.index = pd.to_datetime(by_date.index)
	
	return by_date

def gen_hk_daily_and_cum_case(batch_date, df_case, batch_out_dir):

	by_date = group_case_by_confirmation_date(df_case)

	logging.info("Generate hk daily case line chart")

	fig, ax = plt.subplots(figsize=(20,10))
	ax.plot_date(by_date.index.tolist(), by_date, '-')
	ax.xaxis.set_minor_locator(dates.WeekdayLocator(byweekday=(0),
													interval=1))
	ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
	#ax.xaxis.grid(True, which="minor")
	#ax.yaxis.grid()
	ax.xaxis.set_major_locator(dates.MonthLocator())
	ax.xaxis.set_major_formatter(dates.DateFormatter('\n\n\n%b\n%Y'))
	#plt.tight_layout()
	#plt.figure()
	plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
	plt.title(u'香港每日確診人數', fontsize=20)

	# save image
	fig1 = plt.gcf()
	output_path = os.path.join(batch_out_dir, "day_case.png") 
	fig1.savefig(output_path, dpi=100)

	logging.info("Generate hk cumulative case line chart")

	# Total case
	cum_date = by_date.cumsum()
	cum_date.index = pd.to_datetime(cum_date.index)

	fig, ax = plt.subplots(figsize=(20,10))
	ax.plot_date(cum_date.index.tolist(), cum_date, '-')
	ax.xaxis.set_minor_locator(dates.WeekdayLocator(byweekday=(0),
													interval=1))
	ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
	#ax.xaxis.grid(True, which="minor")
	#ax.yaxis.grid()
	ax.xaxis.set_major_locator(dates.MonthLocator())
	ax.xaxis.set_major_formatter(dates.DateFormatter('\n\n\n%b\n%Y'))
	#plt.tight_layout()
	#plt.figure()
	plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
	plt.title(u'香港累計確診人數', fontsize=20)

	# save image
	fig1 = plt.gcf()
	output_path = os.path.join(batch_out_dir, "cumulative_case.png") 
	fig1.savefig(output_path, dpi=100)

def gen_hk_admission_pie(batch_date, df_case, batch_out_dir):
	
	logging.info("Generate hk case admission pie chart")
	
	# current admission state (not discharge, death and no admission)
	is_admission = (df_case['status'] != 'discharged') & (df_case['status'] != 'deceased')  & (df_case['status'] != 'no_admission')
	data_filter = df_case[is_admission]
	df_status_group = data_filter.loc[:, ['status_zh']]
	status_case = df_status_group.groupby('status_zh').size()
	
	colorMap = {"危殆": "red", "嚴重": "dodgerblue", "穩定": "forestgreen", "待入院": "yellow"}
	colors = [colorMap[key] for key in status_case.index] 

	fig, ax = plt.subplots(figsize=(5,5))
	plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
	ax = status_case.plot.pie(legend=True,  autopct='%1.1f%%', colors=colors , title="入院嚴重程度")
	ax.get_legend().set_bbox_to_anchor((1,0.5))

	# save image
	fig1 = plt.gcf()
	output_path =  os.path.join(batch_out_dir, "hospital_case.png")
	fig1.savefig(output_path, dpi=100)

	
def gen_hk_danger_zones(batch_date, num_days, df_loc, batch_out_dir):

	logging.info("Generate hk danger zone")
	
	range_start = batch_date -  timedelta(days=7)
	range_end = batch_date

	pageIdx = 0
	for end_date in daterange(range_start, range_end):

		day14 = end_date - timedelta(days=14)
		str_endday = end_date.strftime("%Y-%m-%d")

		hk_filter = filter_distict_time_range(df_loc, None, day14, end_date)

		hk_center_pos = loc_center["Hong Kong"]
		title = parse_zhch("香港新冠肺炎危險地區 (過往14天): ") + str_endday 
		fmap = drawHeatMap(hk_filter, hk_center_pos, title, None, 11)

		# save today image
		img_data = fmap._to_png()
		img = Image.open(io.BytesIO(img_data))
		output_path =  os.path.join(batch_out_dir, str(pageIdx) + '-A.png')
		img.save(output_path)
		pageIdx = pageIdx + 1

def gen_hk_age_gender_distribution(batch_date, df_case, batch_out_dir):

	logging.info("Generating age gender distribution")

	day14 = batch_date - timedelta(days=14)
	day7 = batch_date - timedelta(days=7)

	day14_str = day14.strftime("%Y-%m-%d")
	day7_str = day7.strftime("%Y-%m-%d")
	today_str = batch_date.strftime("%Y-%m-%d")

	bins = np.arange(1, 10) * 10

	# today
	filter_criteria = (df_case['confirmation_date'] == today_str)
	data_district = df_case[filter_criteria]
	data_district['age_category'] = np.digitize(data_district.age, bins, right=True)
	counts_today = data_district.groupby(['age_category', 'gender']).age.count().unstack().fillna(0)

	for i in range(0, 10):
		if i not in counts_today.index:
			row = pd.Series({"M": 0, "F": 0}, name=i)
			counts_today = counts_today.append(row)

	filter_criteria = (df_case['confirmation_date'] > day7_str)
	data_district = df_case[filter_criteria]
	data_district['age_category'] = np.digitize(data_district.age, bins, right=True)
	counts_7 = data_district.groupby(['age_category', 'gender']).age.count().unstack()

	for i in range(0, 10):
		if i not in counts_today.index:
			row = pd.Series({"M": 0, "F": 0}, name=i)
			counts_7 = counts_7.append(row)

	filter_criteria = (df_case['confirmation_date'] > day14_str)
	data_district = df_case[filter_criteria]
	data_district['age_category'] = np.digitize(data_district.age, bins, right=True)
	counts_14 = data_district.groupby(['age_category', 'gender']).age.count().unstack()

	for i in range(0, 10):
		if i not in counts_today.index:
			row = pd.Series({"M": 0, "F": 0}, name=i)
			counts_14 = counts_14.append(row)

	index = np.arange(1, 11) * 10

	color_M = 'tab:blue'
	color_F = 'tab:orange'

	colors = {'男性': color_M, '女性': color_F}
	labels = list(colors.keys())
	handles = [plt.Rectangle([0, 0], 10, 10, color=colors[label]) for label in labels]

	plt.figure(figsize=(20,10))
	ax = plt.subplot(111)

	w=3
	w2=2.5
	ax.bar(index-w, counts_today.M, width=w2, color=color_M,align='center')
	ax.bar(index-w, counts_today.F, width=w2, color=color_F, align='center', bottom=counts_today.M)
	ax.bar(index, counts_7.M, width=w2, color=color_M, align='center')
	ax.bar(index, counts_7.F, width=w2, color=color_F, align='center', bottom=counts_7.M)
	ax.bar(index+w, counts_14.M, width=w2, color=color_M, align='center')
	ax.bar(index+w, counts_14.F, width=w2, color=color_F, align='center', bottom=counts_14.M)
	plt.legend(handles, labels)
	plt.title(u'香港確診人數性別年齡分佈 (1,7,14天)', fontsize=20)

	fig1 = plt.gcf()
	output_path=os.path.join(batch_out_dir, "age_gender.png")
	fig1.savefig(output_path, dpi=100)


def gen_district_daily_and_cum_case(batch_date, idx, df_case, batch_out_dir):
	
	logging.info("Generate daily case for district: " + district_list[idx] )
	
	cur_district = district_list[idx]
	
	# patient increase (daily and cum)
	in_district = (df_case['citizenship_district_en']  == cur_district) 
	patient_filter = df_case[in_district]
	
	df_by_date = patient_filter.loc[:, ['confirmation_date']] 
	by_date = df_by_date.groupby('confirmation_date').size()
	by_date.index = pd.to_datetime(by_date.index)

	fig, ax = plt.subplots(figsize=(20,10))
	ax.plot_date(by_date.index.tolist(), by_date, '-')
	ax.xaxis.set_minor_locator(dates.WeekdayLocator(byweekday=(0),
													interval=1))
	ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
	#ax.xaxis.grid(True, which="minor")
	#ax.yaxis.grid()
	ax.xaxis.set_major_locator(dates.MonthLocator())
	ax.xaxis.set_major_formatter(dates.DateFormatter('\n\n\n%b\n%Y'))
	#plt.tight_layout()
	#plt.figure()
	plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
	plt.title(district_zh_list[cur_district_idx] + u'每日確診人數', fontsize=20)

	# save image
	fig1 = plt.gcf()
	output_path =  os.path.join(batch_out_dir, cur_district, "day_case.png")
	fig1.savefig(output_path, dpi=100)
	
	logging.info("Generate cumulative case for district: " + district_list[idx] )
	
	# Total case
	cum_date = by_date.cumsum()
	cum_date.index = pd.to_datetime(cum_date.index)

	fig, ax = plt.subplots(figsize=(20,10))
	ax.plot_date(cum_date.index.tolist(), cum_date, '-')
	ax.xaxis.set_minor_locator(dates.WeekdayLocator(byweekday=(0),
													interval=1))
	ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
	#ax.xaxis.grid(True, which="minor")
	#ax.yaxis.grid()
	ax.xaxis.set_major_locator(dates.MonthLocator())
	ax.xaxis.set_major_formatter(dates.DateFormatter('\n\n\n%b\n%Y'))
	#plt.tight_layout()
	#plt.figure()
	plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
	plt.title(district_zh_list[cur_district_idx] + u'累計確診人數', fontsize=20)

	# save image
	fig1 = plt.gcf()
	output_path =  os.path.join(batch_out_dir, cur_district, "cumulative_case.png")
	fig1.savefig(output_path, dpi=100)
	
def gen_district_cum_case2(batch_date, cur_district_idx, df_case, batch_out_dir):

	cur_district = district_list[cur_district_idx]
	logging.info("Generate daily case for district: " + district_list[cur_district_idx] )
	cum_dates = []
	for district in district_list:
				
		in_district = (df_case['citizenship_district_en']  == district) 
		patient_filter = df_case[in_district]
		df_by_date = patient_filter.loc[:, ['confirmation_date']] 
		by_date = df_by_date.groupby('confirmation_date').size()
		by_date.index = pd.to_datetime(by_date.index)
		cum_date = by_date.cumsum()
		cum_date.index = pd.to_datetime(cum_date.index)
		
		cum_dates.append(cum_date)

	fig, ax = plt.subplots(figsize=(20,10))

	for idx, cd in enumerate(cum_dates):
		if cur_district_idx == idx:
			ax.plot_date(cd.index.tolist(), cd, '-', color='orange', linewidth=4, alpha=1)
		else:
			ax.plot_date(cd.index.tolist(), cd, '-', color='grey', linewidth=1, alpha=0.3)
		
	ax.xaxis.set_minor_locator(dates.WeekdayLocator(byweekday=(0),
													interval=1))
	ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
	#ax.xaxis.grid(True, which="minor")
	#ax.yaxis.grid()
	ax.xaxis.set_major_locator(dates.MonthLocator())
	ax.xaxis.set_major_formatter(dates.DateFormatter('\n\n\n%b\n%Y'))
	#plt.tight_layout()
	#plt.figure()

	plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
	plt.title(district_zh_list[cur_district_idx] + u'累計確診人數', fontsize=20)

	# save image
	fig1 = plt.gcf()
	output_path =  os.path.join(batch_out_dir, cur_district, "cumulative_case.png")
	fig1.savefig(output_path, dpi=100)

def gen_district_danger_zones(batch_date, idx, df_loc, batch_out_dir):

	logging.info("Generate danger zone for district: " + district_list[idx] )
	cur_district = district_list[idx]

	# find start date and end date
	loc_start_date = df_loc['start_date'].dropna().min()
	loc_end_date = df_loc['start_date'].dropna().max()

	zone_district = df_loc['real_distict'] == cur_district
	loc_filter = df_loc[zone_district]
	
	# rolling 14 day for danger zone
	df_by_date = loc_filter.loc[:, ['end_date']] 
	by_date = df_by_date.groupby('end_date').size()
	by_date.index = pd.to_datetime(by_date.index)
	#exp
	by_date_exp = pd.Series(index=pd.date_range(loc_start_date, loc_end_date), data=0)

	for i,val in by_date.iteritems():
		by_date_exp[i] = val  
		
	by_date_14 = by_date_exp.rolling(window=14).sum()
	by_date_14 = by_date_14.dropna()

	fig, ax = plt.subplots(figsize=(20,10))
	ax.plot_date(by_date_14.index.tolist(), by_date_14, '-')
	ax.xaxis.set_minor_locator(dates.WeekdayLocator(byweekday=(0),
													interval=1))
	ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
	#ax.xaxis.grid(True, which="minor")
	#ax.yaxis.grid()
	ax.xaxis.set_major_locator(dates.MonthLocator())
	ax.xaxis.set_major_formatter(dates.DateFormatter('\n\n\n%b\n%Y'))
	#plt.tight_layout()
	#plt.figure()
	plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
	plt.title(district_zh_list[idx] + u'危險地區數目', fontsize=20)

	# save image
	fig1 = plt.gcf()
	output_path =  os.path.join(batch_out_dir, cur_district, "zone14d.png")
	fig1.savefig(output_path, dpi=100)

	logging.info("Generate danger zone animation for district: " + district_list[idx] )

	range_start = batch_date - timedelta(days=7)
	range_end = batch_date

	pageIdx = 0
	for end_date in daterange(range_start, range_end):

		day14 = end_date - timedelta(days=14)
		str_endday = end_date.strftime("%Y-%m-%d")

		hk_center_pos = loc_center[cur_district]
		data_loc_cw = filter_distict_time_range(df_loc, cur_district, day14, end_date)
		title = parse_zhch(district_zh_list[idx] +  "新冠肺炎危險地區 (過往14天): ") + str_endday 
		fmap = drawHeatMap(data_loc_cw, hk_center_pos, title, "geodata/" + cur_district + ".txt", loc_zoom[cur_district])

		# save today image
		img_data = fmap._to_png()
		img = Image.open(io.BytesIO(img_data))
		output_path =  os.path.join(batch_out_dir, cur_district, str(pageIdx) + 'A.png')
		img.save(output_path)
		pageIdx = pageIdx + 1

	
def gen_district_case_num(batch_date, df_case, batch_out_dir):
	
	logging.info("Generate all district case number." )

	# get daily
	# cum sum to 7 and 14 then done
	day14 = batch_date - timedelta(days=14)
	day7 = batch_date - timedelta(days=7)

	day14_str = day14.strftime("%Y-%m-%d")
	day7_str = day7.strftime("%Y-%m-%d")
	today_str = batch_date.strftime("%Y-%m-%d")

	filter_criteria = (df_case['confirmation_date'] == today_str)
	data_district = df_case[filter_criteria]
	df_by_date = data_district.loc[:, ['citizenship_district_en']] 
	today_rank = df_by_date.groupby('citizenship_district_en').size()

	#output_path = os.path.join(batch_out_dir, 'today.csv')
	#today_rank.to_csv(output_path, index=True)

	# 7 days
	filter_criteria =  (df_case['confirmation_date'] > day7_str)
	data_district = df_case[filter_criteria]
	df_by_date = data_district.loc[:, ['citizenship_district_en']] 
	day7_rank = df_by_date.groupby('citizenship_district_en').size()

	#output_path = os.path.join(batch_out_dir, '7days.csv')
	#by_date.to_csv(output_path, index=True)

	# 14 days citizenship_district_en
	filter_criteria =  (df_case['confirmation_date'] > day14_str)
	data_district = df_case[filter_criteria]
	df_by_date = data_district.loc[:, ['citizenship_district_en']] 
	day14_rank = df_by_date.groupby('citizenship_district_en').size()

	#output_path = os.path.join(batch_out_dir, '14days.csv')
	#by_date.to_csv(output_path, index=True)
	
	df_by_date = df_case.loc[:, ['citizenship_district_en']] 
	all_rank = df_by_date.groupby('citizenship_district_en').size()
	
	today_rank.name = "today"
	day7_rank.name = "day7"
	day14_rank.name = "day14"
	all_rank.name = "all"
	rank_concat= pd.concat([today_rank, day7_rank, day14_rank, all_rank], axis=1)

	rank_concat2 = rank_concat.filter(items = district_list, axis=0)
	sum_concat = rank_concat.sum(axis = 0, skipna=True)
	sum_concat2 = rank_concat2.sum(axis=0, skipna=True)
	other_concat = sum_concat - sum_concat2
	other_concat.name="Others"
	rank_concat2 = rank_concat2.append(other_concat)
	
	rank_concat2 = rank_concat2.T
	output_path = os.path.join(batch_out_dir, 'rank_concat.json')
	rank_concat2.to_json(output_path, index=True)

	
def gen_hospitalize_case_summary(batch_date, df_case, batch_out_dir):

	logging.info("Generate hospitalize case summary." )
	
	deceased_count = 0
	discharged_count= 0
	hospitalize_count= 0
	other_count= 0
	is_deceased = df_case['status'] == 'deceased'
	data_filter = df_case[is_deceased]
	deceased_count = len(data_filter)

	is_discharged = df_case['status'] == 'discharged'
	data_filter = df_case[is_discharged]
	discharged_count = len(data_filter)

	is_hospitalize =(df_case['status'] != 'discharged') & (df_case['status'] != 'deceased')  & (df_case['status'] != 'no_admission')
	data_filter = df_case[is_hospitalize]
	hospitalize_count = len(data_filter)


	is_other = df_case['status'] == 'no_admission'
	data_filter = df_case[is_other]
	other_count = len(data_filter)
	
	result = {"deceased_count":deceased_count, "hospitalize_count":hospitalize_count, "other_count":other_count, "discharged_count":discharged_count}
	
	# write
	output_path = os.path.join(batch_out_dir, 'case_summary.json')
	f = open(output_path, "w", encoding='UTF-8')
	f.write(json.dumps(result))
	f.close()


def gen_district_data(batch_date, df_case, df_loc, batch_out_dir):

	logging.info("Generate all district data " )

	for i, district in enumerate(district_list):
		#gen_district_daily_and_cum_case(batch_date, i, df_case, batch_out_dir)
		gen_district_cum_case2(batch_date, i, df_case, batch_out_dir)
		gen_district_danger_zones(batch_date, i, df_loc, batch_out_dir)

def updateInfo(batch_out_dir):

	logging.info("Update the slide directory")

	from distutils.dir_util import copy_tree

	source_dir = batch_out_dir
	dest_dir = "./slide/public/info"

	copy_tree(source_dir, dest_dir)

def main(batch_date, batch_data_dir, batch_out_dir):

	try:
		logging.info("Batch process start")
		download_data(batch_data_dir)
		df_case, df_loc = preprocess_data(batch_data_dir)
		
		#gen_hk_daily_and_cum_case(batch_date, df_case, batch_out_dir)
		#gen_hk_admission_pie(batch_date, df_case, batch_out_dir)
		#gen_hk_danger_zones(batch_date, 7, df_loc, batch_out_dir)
		#gen_hk_age_gender_distribution(batch_date, df_case, batch_out_dir)
		#gen_district_data(batch_date, df_case, df_loc, batch_out_dir)
		
		gen_district_case_num(batch_date, df_case, batch_out_dir)
		gen_hospitalize_case_summary(batch_date, df_case, batch_out_dir)
		
		logging.info("Batch process end")

		updateInfo(batch_out_dir)
		
	except Exception as e:
		traceback.print_exception(*sys.exc_info()) 
		logging.exception("Batch process end unexpectedly with an exception.")

if __name__ == "__main__":
	
	if len(sys.argv) != 2:
		print("Usage: batch <batch_date>")
		exit(-1)
	else:
		batch_date = datetime.strptime(sys.argv[1], '%Y%m%d')
		batch_data_dir, batch_out_dir = init(batch_date)
		main(batch_date, batch_data_dir, batch_out_dir)