# -*- coding: utf-8 -*-
"""
Created on Wed May 13 11:42:41 2020

@author: Jean
"""

import pandas as pd

types = {"county":str,"income":str}
income = pd.read_csv("D:/temp/中国2017年财政收入10亿以上县市.csv",encoding="gbk",dtype=types)

types ={"adcode":str,"name":str,"lng":float,"lat":float}
adcode = pd.read_csv("D:/temp/geojson/行政区域代码坐标.csv",encoding="gbk",dtype=types)

income2 = pd.merge(adcode,income,left_on="name",right_on="county", how="right")
income2.drop_duplicates(subset = ['county'],keep='first',inplace=True)
income3 = income2[["county","income"]].loc[income2.name.isna()]
income2 = income2.loc[~income2.name.isna()]
income3["county2"] = income3["county"].apply(lambda x: x[:-1])
adcode["name2"] = adcode["name"].apply(lambda x: x[:-1])
income4 = pd.merge(adcode,income3,left_on="name2",right_on="county2", how="right")
income4.drop_duplicates(subset = ['county2'],keep='first',inplace=True)
income4.drop(['name2', 'county2'], axis=1, inplace=True)
income2 = pd.concat([income2,income4])
income2.to_csv("D:/temp/中国2017年财政收入10亿以上县市2.csv",index=False,encoding="utf-8")

import geopandas as gpd
import matplotlib.pyplot as plt

gdf3 = gpd.read_file("D:/temp/gadm/gadm36_CHN_3_sp.json",encoding='utf-8')
gdf3.plot(figsize=(16,16))
plt.show()
# hsac是国际邮政编码（管理层次缩写，例: US.NY.QU代表Queens, New York）
gdf3["hsac"]=gdf3["GID_3"].apply(lambda x: x.split("_")[0])
gdf3["NAME_0"] = "CN"
gdf3.rename(columns={"GID_0":"adm0_a3","NAME_1":"province","GID_3":"_id","ENGTYPE_3":"type",\
                     "NAME_3":"name","NAME_0":"iso_a2","GID_2":"fips"},inplace=True)
# fips是美国国内的行政区域编码，类似国内的行政区域编码，例：36081代表Queens, New York
gdf3["fips"]=  gdf3["hsac"]
gdf3.drop(["CC_3","HASC_3"],axis=1,inplace=True)
gdf3["capital"]=gdf3["name"]
# 输出admin2-CHN.json，注意文件要按Orange Geo的规范命名，并放在其指定的位置
# 一定要有 ""_id"列
gdf3.to_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin3-CHN.json",\
             driver='GeoJSON',encoding="utf-8")


gdf3 = gpd.read_file("D:/temp/gadm/gadm36_CHN_1_sp.json",encoding='utf-8')
gdf3.plot(figsize=(16,16))
plt.show()
# hsac是国际邮政编码（管理层次缩写，例: US.NY.QU代表Queens, New York）
gdf3["hsac"]=gdf3["GID_1"].apply(lambda x: x.split("_")[0])
gdf3["NAME_0"] = "CN"
gdf3.rename(columns={"GID_0":"adm0_a3","GID_1":"_id","ENGTYPE_1":"type",\
                     "NAME_1":"name","NAME_0":"iso_a2"},inplace=True)
# fips是美国国内的行政区域编码，类似国内的行政区域编码，例：36081代表Queens, New York
gdf3["fips"]=  gdf3["hsac"]
gdf3.drop(["CC_1","HASC_1"],axis=1,inplace=True)
gdf3["adm0_a3"]=gdf3["name"]
# 输出admin2-CHN.json，注意文件要按Orange Geo的规范命名，并放在其指定的位置
# 一定要有 ""_id"列
gdf3.to_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin0-CHN.json",\
             driver='GeoJSON',encoding="utf-8")

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# 广东乡镇行政区域矢量地图，购自地理国情监测云平台    
gdf=gpd.read_file("D:/temp/广东省2014乡镇区划/广东省2014乡镇区划.shp",encoding="gbk")
gdf.rename(columns={"OBJECTID":"_id","乡镇名称":"name","乡镇代码":"xzdm","区县名称":"county",\
                    "区县代码":"adcode","地市名称":"city","地市代码":"citycode"},inplace=True)
gdf["_id"] = gdf["xzdm"]       
# 地图转换成GeoJSON格式，给Orange Geo Choropleth Widget使用
# 注意输出的.json数据文件中，坐标是(lng,lat,z)三元组，用UltraEdit直接删去z轴数据
# Orange Geo Choropleth Widget要求二维坐标
gdf.to_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojsonCHN/admin4-CHN.json",\
             driver='GeoJSON',encoding="utf-8")
gdf.plot()
# 计算行政区域地理中心坐标，后面与乡镇数据合并后用来标示数据坐标
gdf['coords'] = gdf["geometry"].centroid
gdf["lng"] = gdf['coords'].apply(lambda x: x.coords[0][0])
gdf["lat"] = gdf['coords'].apply(lambda x: x.coords[0][1])

# 合并时舍弃边界坐标数据
gdf2 = gdf
gdf2.drop(["geometry"],axis=1,inplace=True)
# 这是乡镇统计数据乡镇街道名字数据的格式
gdf2["xzjd"] = gdf2["county"]+gdf2["name"]
# 乡镇几何中心的坐标
gdf3 = gdf2[["xzjd","coords","lng","lat"]]
# 乡镇统计数据，来自中国国统计年鉴乡镇卷
xztj = pd.read_csv("D:/temp/广东省2107年乡镇统计数据.csv",encoding="gbk")
# 与坐标数据合并
xzsj = pd.merge(xztj,gdf3,left_on="name",right_on="xzjd", how="left")
xzsj2 = xzsj.loc[xzsj.xzjd.isna()]
xzsj = xzsj.loc[~xzsj.xzjd.isna()]
# 输出数据去作图
xzsj.to_csv("D:/temp/广东省2107年乡镇统计数据2.csv",index=False,encoding="utf-8")

