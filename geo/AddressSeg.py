# -*- coding: utf-8 -*-
"""
Created on Sat May  9 11:44:44 2020

@author: Jean
"""
#导入相关库
import jieba
import json
import requests
import urllib.request as ur
from urllib.request import urlopen, quote
import webbrowser
import gzip

import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx
import math


# 高德瓦片地图网址
gaodeurl="http://wprd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}"      
application_key = "your token key"

# 1.天地图
def TDGeoCode(address):    
     url = 'http://api.tianditu.gov.cn/geocoder?ds={"keyWord":"'+address+'"}&tk='+application_key
     #print(url)
     try:
         # 模拟浏览器，否则会被禁止访问
         headers={
             'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0'
             }
         response = requests.get(url,headers=headers)
         response.encoding = 'utf-8'
         temp = response.json()
         if temp['status'] == '0':
            lng = float(temp['location']['lon'])  # 纬度
            lat = float(temp['location']['lat'])  # 经度
            print(lat, lng)
            return(lng,lat)
         else:
            print(address+" 没找到")
            return(None,None)         
     except Exception as ex:
         print(ex)
         return(None,None) 

# 2.腾讯地图
def TxGeoCode(address):
    url = 'https://apis.map.qq.com/ws/geocoder/v1/'
    output = 'json'
    ak = 'OB4BZ-D4W3U-B7VVO-4PJWW-6TKDJ-WPB77'
    #由于本文地址变量为中文，为防止乱码，先用quote进行编码    
    add = quote(address)
    uri = url + '?' + 'address=' + add  + '&output=' + output + '&key=' + ak
    uri = uri+"&region="+quote("珠海市")
    # 伪装浏览器请求头，通过其检查
    request = ur.Request(
        url=uri,
        headers={
            "Accept":"*/*",
            "Accept-Encoding":"gzip, deflate, br",
            "Accept-Language":"zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection":"keep-alive",            
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
            "Origin":"https://lbs.qq.com",
            "Referer":"https://lbs.qq.com/service/webService/webServiceGuide/webServiceGeocoder",
            'Host':"apis.map.qq.com"})
    req = urlopen(request)
    # 服务器返回压缩后的数据，要先解压
    res =gzip.decompress(req.read()).decode()  
    temp = json.loads(res)

    if temp['status'] == 0 :
        lng = float(temp['result']['location']['lng'])  # 纬度
        lat = float(temp['result']['location']['lat'])  # 经度
        print(lat, lng)
        return(lng,lat)
    else:
        print(address+" 没找到")
        return(None,None)
    

# 3.高德地图 带国家名字和省市区。首选
# 高德地图 请求成功 状态码count 失败0 成功1    和百度相反
def geocode(address):
    parameters = {'address': address, 'key': '9fdf0730355e6f834499edf349161769'}
    url = 'https://restapi.amap.com/v3/geocode/geo?parameters'
    response = requests.get(url, parameters)
    # answer = response.geocodes['location']
    # print(answer)
    answer = response.json()
    if answer['count'] == str(1):
        # print(address + "的经纬度：", answer['geocodes'][0]['location'])
        location = answer['geocodes'][0]['location'].split(',')
        country = answer['geocodes'][0]['country']
        province = answer['geocodes'][0]['province']
        city = answer['geocodes'][0]['city']

        lat = float(location[1])       #纬度
        lng = float(location[0])      #经度
        print(lat,lng)
        return(lng,lat)        
    else:
        print(address+" 没找到")
        return(None,None)


# 4.百度地图api，不带国家具体信息
# 百度地图：请求状态吗  status 成功0 失败 1   和高德相反
# http://www.voidcn.com/article/p-apeiortj-bpp.html
def getlnglat(address):
    url = 'http://api.map.baidu.com/geocoding/v3/'
    output = 'json'
    ak = 'D3AqomSjXDyHmyQ64HzvChncTtr4UYVZ'
    #由于本文地址变量为中文，为防止乱码，先用quote进行编码    
    add = quote(address)
    uri = url + '?' + 'address=' + add  + '&output=' + output + '&ak=' + ak
    uri = uri+"&city="+quote("珠海市")
    req = urlopen(uri)
    res = req.read().decode()
    temp = json.loads(res)

    if temp['status'] == 0 :
        lng = float(temp['result']['location']['lng'])  # 纬度
        lat = float(temp['result']['location']['lat'])  # 经度
        print(lat, lng)
        return(lng,lat)
    else:
        print(address+" 没找到")
        return(None,None)

# to Mercator
def lonlat_to_Mercator_(lon,lat):
    x=lon*20037508.34/180
    y=math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    y=y*20037508.34/180    
    return x,y

# from Mercator
def Mercator_to_lonlat(x,y):
    lon=x/20037508.34*180
    lat=y/20037508.34*180
    lat= 180/math.pi*(2*math.atan(math.exp(lat*math.pi/180))-math.pi/2)
    return lon,lat


#地址分词测试
address = "广东省珠海市香洲区九洲大道东1273号"
address = "广东省广州市天河区花城大道19号"
seg_list = jieba.cut(address, cut_all=True)
print("Full Mode: " + "/ ".join(seg_list))  # 全模式

seg_list = jieba.cut(address, cut_all=False)
print("Default Mode: " + "/ ".join(seg_list))  # 精确模式

seg_list = jieba.cut(address)  # 默认是精确模式
print(", ".join(seg_list))

seg_list = jieba.cut_for_search(address)  # 搜索引擎模式
print(", ".join(seg_list))

# 读入税务登记地址数据
types={"NSRSBH":str,"DJXH":str,"SHXYDM":str,"SSDABH":str,"ZZJG_DM":str,"NSRMC":str,\
       "KZZTDJLX_DM":str,"DJZCLX_DM":str,"HY_DM":str,"ZGSWSKFJ_DM":str,"NSRZT_DM":str,\
           "SCJYDZXZQHSZ_DM":str,"SCJYDZ":str,"ZCDZXZQHSZ_DM":str,"ZCDZ":str,"JDXZ_DM":str}
swdj = pd.read_csv("D:/temp/税务登记地址/swdj.csv",encoding="utf-8",dtype=types)

types={"JDXZ_DM":str,"JDXZMC":str}
jdxz = pd.read_csv("D:/temp/税务登记地址/jdxz.csv",encoding="utf-8",dtype=types)

types = {"KZZTDJLX_DM":str,"KZZTDJLXMC":str}
kzztdjlx = pd.read_csv("D:/temp/税务登记地址/kzztdjlx.csv",encoding="utf-8",dtype=types)

types = {"DJZCLX_DM":str,"DJZCLXMC":str}
djzclx = pd.read_csv("D:/temp/税务登记地址/djzclx.csv",encoding="utf-8",dtype=types)

types = {"NSRZT_DM":str,"NSRZTMC":str}
nsrzt = pd.read_csv("D:/temp/税务登记地址/nsrzt.csv",encoding="utf-8",dtype=types)

zcdz = swdj[["DJXH","NSRMC","ZCDZ","JDXZ_DM"]][(swdj.NSRZT_DM<='03')& (swdj.KZZTDJLX_DM<'1300')]

#测试地址地理编码服务及地图标记服务
address = "广东省珠海市香洲区人民东路2号市府大院1号楼3楼"
nsrmc = "珠海市人民政府办公室"
# 4.百度地图
x, y = getlnglat(address)
def BaiDuURL_mask(location: str,address:str, name: str):
    url_a = 'http://api.map.baidu.com/marker'
    url_b = "?location=" + location+"&title="+name+"&content="+address
    url_c = '&output=html&src=webapp.baidu.openAPIdemo&zoom=20'
    URL = url_a + url_b + url_c
    webbrowser.open(URL)
# 在浏览器上标示出该地址的位置
BaiDuURL_mask(str(y)+","+str(x), address, nsrmc)
    
# 3.高德地图 
x, y = geocode(address)
def GaoDeURL_mask(location: str,address:str, name:str):
    url_a = 'https://uri.amap.com/marker'
    url_b = "?markers=" + location+","+name
    url_c = '&src=mypage&callnative=0'
    URL = url_a + url_b + url_c
    webbrowser.open(URL)
# 在浏览器上标示出该地址的位置
GaoDeURL_mask(str(x)+","+str(y), address, nsrmc)

# 2.腾讯地图 
x, y = TxGeoCode(address)
def TxURL_mask(location: str,address:str, name:str):
    url_a = 'https://apis.map.qq.com/uri/v1/marker'
    url_b = "?marker=coord:" + location+";title:"+name+";addr:"+address
    url_c = '&referer=myapp'
    URL = url_a + url_b + url_c
    webbrowser.open(URL)
# 在浏览器上标示出该地址的位置
TxURL_mask(str(y)+","+str(x), address, nsrmc)

# 1.天地图 提供的是静态地图及标注夫妇，不是其它地图的地图调起API
x, y = TDGeoCode(address)
# width,height: 1~1024, zoom:3~18
def TDURL_mask(location: str,address:str, name:str,application_key:str):
    url_a = 'http://api.tianditu.gov.cn/staticimage? width=1024&height=1024&zoom=18&layers=vec_c,cva_c'
    url_b = "&center=" + location+"&markers="+location+"&markerStyles=-1,,"+quote(nsrmc)
    url_c = '&tk='+application_key
    URL = url_a + url_b + url_c
    webbrowser.open(URL)
# 在浏览器上标示出该地址的位置
TDURL_mask(str(x)+","+str(y), address, nsrmc,application_key)


lng, lat = lonlat_to_Mercator_(x, y)

from shapely.geometry import  Polygon;
from geopandas import GeoSeries,GeoDataFrame
# 创造Polygon
rd = 0.01
plyg = Polygon([(lng-rd, lat-rd), (lng-rd, lat+rd), (lng+rd, lat+rd), (lng+rd, lat-rd)])
# 构造空间属性，即GeoSeries
gs = GeoSeries([plyg])
# 添加属性
gdf = GeoDataFrame({'address' : [address]}, geometry=gs)

#gdf = gpd.read_file("d:/temp/geojsonutf8/中华人民共和国/广东省/珠海市/440400_full.json",encoding='utf-8')
# 转换为墨卡托投影坐标，以便与底图合并
#gdf = gdf.to_crs(epsg=3857)
# 解决汉字显示的问题
plt.rcParams['font.sans-serif'] = ['KaiTi'] # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
ax = gdf.plot(legend=False, figsize=(16,16),alpha=0.5,edgecolor='k')
#x, y = lonlat_to_Mercator_(lng,lat)
ax.text(lng, lat, s=address, horizontalalignment='center',fontsize=16, \
        color="red",bbox={'facecolor': "none", 'alpha':0.8, 'pad': 2, 'edgecolor':'none'}) 
# 增加底图
ctx.add_basemap(ax,source=gaodeurl)
plt.show()



