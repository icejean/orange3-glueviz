# -*- coding: utf-8 -*-
"""
Created on Sat May 23 20:10:15 2020

@author: Jean
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point,Polygon, MultiPolygon
import requests
import webbrowser
from coord_convert.transform import wgs2gcj
import math

application_key = "your key of www.tianditu.gov.cn"
# 天地图
def TDGeoCode(address):    
     url = 'http://api.tianditu.gov.cn/geocoder?ds={"keyWord":"'+address+'"}&tk='+application_key
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
     
        
# 高德地图，解释各区分局地址为坐标，并在地图上标示
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
        lat = float(location[1])       #纬度
        lng = float(location[0])      #经度
        print(lat,lng)
        return(lng,lat)        
    else:
        print(address+" 没找到")
        return(None,None)

def GaoDeURL_mask(location: str,name:str):
    url_a = 'https://uri.amap.com/marker'
    url_b = "?markers=" + location+","+name
    url_c = '&src=mypage&callnative=0'
    URL = url_a + url_b + url_c
    webbrowser.open(URL)

# polygon转换wgs坐标为gcj坐标
def poly2gcj(ploy):
    x, y = ploy.exterior.coords.xy
    ps = []
    for i in range(len(x)):
        x2,y2 = wgs2gcj(x[i],y[i])
        ps.append(Point(x2,y2))
    poly2 = Polygon(ps)
    return poly2
    
# gdf转换gcj坐标为wgs坐标    
def gdf2gcj(gdf):
    gdf2 = gdf.copy()    
    geos = gdf2["geometry"].to_list()
    for i in range(len(geos)):
        if isinstance(geos[i],Polygon):
            geos[i] = poly2gcj(geos[i])
        elif isinstance(geos[i],MultiPolygon):
            polys = [p for p in geos[i]]
            for j in range(len(polys)):
                polys[j] = poly2gcj( polys[j])
            geos[i] = MultiPolygon(polys)
    gdf2["geometry"] = geos
    return gdf2  
  
# 珠海市各乡镇街道
gdf=gpd.read_file("D:/temp/广东省2014乡镇区划/广东省2014乡镇区划.shp",encoding="gbk")
gdf.rename(columns={"OBJECTID":"_id","乡镇名称":"name","乡镇代码":"xzdm","区县名称":"county",\
                    "区县代码":"adcode","地市名称":"city","地市代码":"citycode"},inplace=True)
gdf = gdf[gdf.city=="珠海市"]
# 从WGS84坐标转换为GCJ坐标
gdf = gdf2gcj(gdf)    
# 再转换为墨卡托投影坐标，以便与地图底图合并
gdf = gdf.to_crs(epsg=3857)
gdf.plot(column= 'name')
# 计算各乡镇街道的几何中心    
gdf['coords'] = gdf["geometry"].centroid
gdf["lng"] = gdf['coords'].apply(lambda x: x.coords[0][0])
gdf["lat"] = gdf['coords'].apply(lambda x: x.coords[0][1])
# 拆分成各区分局的辖区
# 横琴新区局辖区
gdfHQ = gdf[gdf.name.isin(["横琴镇"])]
gdfHQ.plot()
# 香洲区局辖区
gdfXZ = gdf[gdf.name.isin(["翠香街道办","梅华街道办","前山街道办","前山商贸物流中心","吉大街道办",\
                           "香湾街道办","狮山街道办","拱北街道办"])]
gdfXZ.plot()
# 高新区局辖区
gdfGX = gdf[gdf.name.isin(["唐家湾镇","金鼎工业园","大学园区"])]
gdfGX.plot()
# 保税区局辖区
gdfBS = gdf[gdf.name.isin(["南屏镇","湾仔街道办","保税区","洪湾商贸物流中心","南屏科技园"])]
gdfBS.plot()
# 万山区局辖区
gdfWS = gdf[gdf.name.isin(["桂山镇","万山镇","担杆镇"])]
gdfWS.plot()
# 斗门区局辖区
gdfDM = gdf[gdf.name.isin(["井岸镇","白藤街道办事处","斗门镇","乾务镇","白蕉镇","莲洲镇"])]
gdfDM.plot()
# 金湾区局辖区
gdfJW = gdf[gdf.name.isin(["三灶镇","红旗镇","联港工业区","航空产业园"])]
gdfJW.plot()
# 开发区局辖区
gdfKF = gdf[gdf.name.isin(["南水镇","平沙镇"])]
gdfKF.plot()

# 合并分局下辖各乡镇街道的多边形
def merge_ploygon(gdf):
    geos = gdf["geometry"].to_list()
    for i in range(len(geos)-1):
        geo2 = geos[i+1]
        geos[0] =geos[0].union(geo2)
    s = gpd.GeoSeries(geos[0])
    s.plot()
    return geos[0]
        
geoFJ = []
# 按顺序：横琴、香洲、高新、保税、万山、斗门、金湾、开发
geoFJ.append(merge_ploygon(gdfHQ)); geoFJ.append(merge_ploygon(gdfXZ))
geoFJ.append(merge_ploygon(gdfGX)); geoFJ.append(merge_ploygon(gdfBS))
geoFJ.append(merge_ploygon(gdfWS)); geoFJ.append(merge_ploygon(gdfDM))
geoFJ.append(merge_ploygon(gdfJW)); geoFJ.append(merge_ploygon(gdfKF))
# 各区分局辖区地图
name=["横琴","香洲","高新","保税","万山","斗门","金湾","开发"]
fjdm=["1440494","1440402","1440491","1440452","1440493","1440421","1440404","1440492"]
gdf2 = pd.DataFrame({"fjdm":fjdm,"branch":name,"geometry":geoFJ})
gdf2 = gpd.GeoDataFrame(gdf2, geometry='geometry')
# 画各分局的辖区边界地图
gdf2.plot(column= 'branch')
gdfYFJ = gdf2[gdf2.branch.isin(["香洲","高新","保税","万山"])]
geoFJ.append(merge_ploygon(gdfYFJ))
# 插入1行，大企业局    
gdf2.loc[len(gdf2)] = ["1440490","一分局",geoFJ[-1]]
# 画出来看看
gdf2.plot(column= 'branch')
# 各区分局辖区中心的坐标
gdf2['coords'] = gdf2["geometry"].centroid
gdf2["lng"] = gdf2['coords'].apply(lambda x: x.coords[0][0])
gdf2["lat"] = gdf2['coords'].apply(lambda x: x.coords[0][1])
gdf2.drop(["coords"],axis=1,inplace=True)
# 解释各区分局地址为坐标，斗门局的地址，天地图是1169号，高德是1173号，广东税务网站是1173号，天地图未更新
# 国家税务总局珠海市斗门区税务局 珠海市斗门区珠峰大道1173号 珠峰大道1169号东南方向101米
swjgdz = ["珠海市横琴新区金融产业发展基地4号楼","珠海市香洲区兴业路393号","珠海市南方软件园A2栋3楼",\
        "珠海市香洲区南湾南路5002号鸿景花园8栋首层","珠海市香洲区紫荆路357号30栋",\
        "珠峰大道1169号东南方向101米","珠海市金湾区西湖城区金帆路1008号",\
            "珠海市高栏港经济区南水镇南港路39号","珠海市香洲区九洲大道东1273号"]
# to Mercator
def lonlat_to_Mercator_(lon,lat):
    x=lon*20037508.34/180
    y=math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    y=y*20037508.34/180    
    return x,y
    
swjgx=[]; swjgy=[]
for i in range(len(swjgdz)):
    #x, y = geocode(swjgdz[i])
    x, y = TDGeoCode(swjgdz[i])    
    # 转换为墨卡托投影坐标
    x2, y2 = lonlat_to_Mercator_(x,y)
    swjgx.append(x2); swjgy.append(y2)
    # 在浏览器上标示出该地址的位置
    # GaoDeURL_mask(str(x)+","+str(y), swjg)
# 合并税务机关地址及坐标到地图数据库
gdf2["dz"] = swjgdz; gdf2["lng_dz"] =  swjgx; gdf2["lat_dz"] =  swjgy   
# 各区分局辖区地图输出存盘
gdf2.to_file("D:/temp/geojsonutf8/ZhuHaiShuiWu.json",driver='GeoJSON',encoding="utf-8")

# 读入珠海市税务登记地址数据
types={"NSRSBH":str,"DJXH":str,"SHXYDM":str,"SSDABH":str,"ZZJG_DM":str,"NSRMC":str,\
       "KZZTDJLX_DM":str,"DJZCLX_DM":str,"HY_DM":str,"ZGSWSKFJ_DM":str,"NSRZT_DM":str,\
           "SCJYDZXZQHSZ_DM":str,"SCJYDZ":str,"ZCDZXZQHSZ_DM":str,"ZCDZ":str,"JDXZ_DM":str}
swdj = pd.read_csv("D:/temp/税务登记地址/swdj.csv",encoding="utf-8",dtype=types)
swdj2 = swdj[["DJXH","NSRMC","JDXZ_DM","KZZTDJLX_DM","ZGSWSKFJ_DM","NSRZT_DM"]]\
    [(swdj.NSRZT_DM<='03')&((swdj.KZZTDJLX_DM=='1110')|(swdj.KZZTDJLX_DM=='1120'))]
# 增加分局代码列
swdj2["FJ_DM"] = swdj2['ZGSWSKFJ_DM'].apply(lambda x: str(x)[:7])
# 统计登记状态正常的单位纳税人及个体户户数
# 单位纳税人
swdjtj1 = swdj2[["DJXH","FJ_DM"]][swdj2.KZZTDJLX_DM=='1110'].groupby("FJ_DM").count()
swdjtj1 = swdjtj1.reset_index()
swdjtj1.rename(columns={"DJXH":"DW"},inplace=True)
# 个体户
swdjtj2 = swdj2[["DJXH","FJ_DM"]][swdj2.KZZTDJLX_DM=='1120'].groupby("FJ_DM").count()
swdjtj2 = swdjtj2.reset_index()
swdjtj2.rename(columns={"DJXH":"GT"},inplace=True)
# 合并统计数据
swdjtj3 = pd.merge(swdjtj1,swdjtj2, left_on="FJ_DM",right_on="FJ_DM", how="outer")
swdjtj3 = swdjtj3[swdjtj3.FJ_DM.str.contains("14404")]
swdjtj3["DW"] = swdjtj3["DW"].astype(int); swdjtj3["GT"] = swdjtj3["GT"].astype(int)
# 合并数据到地图
gdf3 = pd.merge(gdf2,swdjtj3, left_on="fjdm",right_on="FJ_DM", how="left")
gdf3 = gpd.GeoDataFrame(gdf3, geometry='geometry')
gdf3['fjNum']=(gdf3.index+1).astype(str)
# 不含一分局地图
gdf4 = gdf3[gdf3.branch=="一分局"]
# 一分局地图
gdf5 = gdf3[gdf3.branch!="一分局"]

# 高德瓦片地图网址，用作底图
#url="http://wprd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}" 
# 天地图瓦片地图网址
url="https://t6.tianditu.gov.cn/vec_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&"+\
        "STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILECOL={x}&TILEROW={y}&TILEMATRIX={z}&tk="+\
        application_key
plt.rcParams['font.sans-serif'] = ['KaiTi'] # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
# 在地图上显示单位纳税人统计数据并标注
ax = gdf5.plot(column= 'DW',cmap='Reds', legend=True,figsize=(16,16),alpha=0.8)
plt.xlabel('经度',fontsize=18)
plt.ylabel('纬度',fontsize=18)    
plt.title("珠海市各区分局税务登记统计（单位纳税人）",fontsize=24)
# 叠加画上一分局的图层，透明度设大一点，以显示所覆盖的香洲、高新、保税、万山分局原来的颜色
gdf4.plot(ax=ax,color="blue",alpha=0.3)
# 标注数据
for idx, row in gdf3.iterrows():
    # 标注区分局名称及数量
    ax.text(row.lng, row.lat, s=str(row.fjNum+row.branch)+"\n"+str(row.DW), horizontalalignment='center', \
      color="blue",fontsize=14,bbox={'facecolor': "none", 'alpha':0.5, 'pad': 2, 'edgecolor':'none'})
    # 标注区分局机关坐标
    ax.scatter(row.lng_dz,row.lat_dz,marker="o",s=15,c="green")
    # 在区分局机关坐标旁标注编号，以便与上面的名称及数量对应
    ax.text(row.lng_dz, row.lat_dz, s=str(row.fjNum), color="green",fontsize=10)   
# 增加底图
ctx.add_basemap(ax,source=url)
plt.show()