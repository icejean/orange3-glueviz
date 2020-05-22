# -*- coding: utf-8 -*-
"""
Created on Sat May 16 10:45:15 2020

@author: Jean
"""
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point,Polygon, MultiPolygon, shape as Shape
from coord_convert.transform import gcj2wgs
# 修正地图程序，把台湾、香港、澳门、藏南地区加入admin0及admin1中国地图，其中藏南地区并入admin1西藏地图
# 从印度admin0及admin1地图中减去藏南地区部分, 藏南边界由高德地图西藏部分与印度阿鲁纳恰尔邦地图的交集得到。
# 高德地图是GCJ火星坐标系，要先转换为WGS84坐标系。
# 海岛部分后面慢慢检查修改。
# 地图改好后, 用新的admin0.json，admin1-CHN.json，admin1-IND.json替换geojson下原文件
# 并删除原admin1-HKG.json，admin1-MAC.json及admin1-TWN.json文件。
# 读入admin0世界地图
gdf =  gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin0.json",\
                     encoding="utf-8")
gdf.plot()
# 提取其中的中国大陆、台、港、澳地图 
gdfCN = gdf[gdf.adm0_a3=="CHN"]; gdfHK = gdf[gdf.adm0_a3=="HKG"]
gdfMO = gdf[gdf.adm0_a3=="MAC"]; gdfTW = gdf[gdf.adm0_a3=="TWN"]
# 合并两个地图成一个整体地图的函数   
def merge(gdf1,gdf2):
    geo = gdf1["geometry"].to_list()[0]
    p1 = [ p for p in geo]
    geo = gdf2["geometry"].to_list()[0]
    p2 = [ p for p in geo]
    geo = MultiPolygon(p1+p2)
    gdf3 = gdf1.copy()
    gdf3["geometry"] = [geo]
    return gdf3
# 合并台湾、香港、澳门地图到admin0的中国地图
gdfCN2 = merge(gdfCN, gdfTW)
gdfCN2 = merge(gdfCN2, gdfHK)
gdfCN2 = merge(gdfCN2, gdfMO)
gdfCN2.plot()


# 周边有关国家的地图
# 日本：钓鱼岛
gdfJP = gdf[gdf.adm0_a3=="JPN"]
gdfJP.plot()
# 印度：藏南
gdfIN= gdf[gdf.adm0_a3=="IND"]
gdfIN.plot()
# 印尼：南沙群岛
gdfID= gdf[gdf.adm0_a3=="IDN"]
gdfID.plot()
# 马来西亚：南沙群岛
gdfMY= gdf[gdf.adm0_a3=="MYS"]
gdfMY.plot()
# 菲律宾: 东沙群岛
gdfPH= gdf[gdf.adm0_a3=="PHL"]
gdfPH.plot()
# 越南：西沙群岛
gdfVM= gdf[gdf.adm0_a3=="VNM"]
gdfVM.plot()


# 处理藏南地区，即与印度有争议的阿鲁纳恰尔邦
# 从高德地图读入西藏地图
gdf1 =  gpd.read_file("D:/temp/geojsonutf8/中华人民共和国/西藏自治区/540000.json",encoding="utf-8")
gdf1.plot()
# 转换为wgs坐标
geo = gdf1["geometry"].to_list()[0]
x, y = geo.exterior.coords.xy
ps = []
for i in range(len(x)):
    x2,y2 = gcj2wgs(x[i],y[i])
    ps.append(Point(x2,y2))
geo2 = Polygon(ps)
# 画出来看看
s = gpd.GeoSeries(geo2)
s.plot()
# 从 admin1-IND.json取出该地区边界地图
gdf2 =  gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin1-IND.json",\
                     encoding="utf-8")
gdf2.plot()
# 与传统控制线比较，该邦既有传统中国的藏南部分，如达旺等，也有印度传统控制的部分。
gdfAR = gdf2[gdf2.name=="Arunachal Pradesh"]
gdfAR.plot()
gdfIN= gdf[gdf.adm0_a3=="IND"]
gdfIN.plot()
geo1 = gdfAR["geometry"].to_list()[0]
# 与高德地图的交集得到中国主张的边界
geo3 = geo2.intersection(geo1)
# 剩下的是印度的
geo4 = geo1.difference(geo3)
# 画出来看看
s = gpd.GeoSeries(geo3)
s.plot()
s1 = gpd.GeoSeries(geo4)
s1.plot()

# 印度admin0地图减去中国主张的地区
gdfCNZN = gdfAR.copy()
gdfCNZN["geometry"] = [geo3]
gdfCNZN.plot()
gdfIN2 = gpd.overlay(gdfIN, gdfCNZN, how='difference', make_valid=True, keep_geom_type=True)
gdfIN2.plot()
# 印度admin1地图减去中国主张的地区
gdfAR2 = gpd.overlay(gdfAR, gdfCNZN, how='difference', make_valid=True, keep_geom_type=True)
gdfAR2.plot()
gdf2.drop(gdf2[gdf2.name=="Arunachal Pradesh"].index, inplace=True)
gdf22 = pd.concat([gdf2,gdfAR2],axis=0)
gdf22.plot()
# 更新印度admin1输出存盘
gdf22.to_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojsonCHN/admin1-IND.json",\
             driver='GeoJSON',encoding="utf-8")
# 更新admin0中中国与印度的地图
geo = gdfCN2["geometry"].to_list()[0]
p1 = [ p for p in geo]
# 找出中国国地图主体的多边形
for i in range(len(p1)):
    s = s = gpd.GeoSeries(p1[i])
    s.plot()
# 是第61个多边形，合并藏南地区多边形与大陆多边形，画该多边形确认
s = gpd.GeoSeries(p1[60])
s.plot()
# 合并多边形
geo = gdfCNZN["geometry"].to_list()[0]
p2 = p1[60].union(geo)
# 替换成合并后的多边形
p1[60] = p2
geo = MultiPolygon(p1)
gdfCN3 = gdfCN2.copy()
gdfCN3["geometry"] = [geo]
gdfCN3.plot()
gdfNEW = gdf.copy()
geos = gdfNEW["geometry"].to_list()
geo = gdfCN3["geometry"].to_list()[0]
# 替换admin0中国地图
geos[42] = geo
# 替换admin0印度地图
geo = gdfIN2["geometry"].to_list()[0]
geos[104] = geo
# 画修改好的地图并输出存盘
gdfNEW["geometry"] = geos
gdfNEW.plot()
# admin0.json输出存盘
gdfNEW.to_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojsonCHN/admin0.json",\
             driver='GeoJSON',encoding="utf-8")
# 重画两国地图确认
gdfIN= gdfNEW[gdf.adm0_a3=="IND"]
gdfIN.plot()
gdfCHN= gdfNEW[gdf.adm0_a3=="CHN"]
gdfCHN.plot()


# 处理中国admin1地图
gdf3 =  gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin1-CHN.json",\
                     encoding="utf-8")
gdf3.plot()
# 藏南地区加入西藏
gdfXZ=gdf3[gdf3.name=="Xizang"]
gdfXZ.plot()
# 合并西藏与藏南地区地图多边形
p1 = gdfXZ["geometry"].to_list()[0]
p2 = gdfCNZN["geometry"].to_list()[0]
geo = p1.union(p2)
# 画合并后的地图
s = gpd.GeoSeries(geo)
s.plot()
gdfXZ2 = gdfXZ.copy()
gdfXZ2["geometry"] = [geo]
gdfXZ2.plot()
# 更新西藏的版图，西藏是第10个省
geos = gdf3["geometry"].to_list()
geos[9] = geo
gdf3["geometry"] = geos
gdf3.plot()

# 处理台湾地区
# 读入原台湾地区admin1地图，获得台北的坐标"longitude":[121.559],"latitude":[25.0904]
gdf4 =  gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin1-TWN.json",\
                     encoding="utf-8")
geo = gdfTW["geometry"].to_list()[0]
gdfCN3 = gdf3.copy()
# 按中国admin1格式新建一个DataFrame
gdfTW2 = pd.DataFrame({"name":["Taiwan"],"type":["Province"],"adm0_a3":["CHN"],"hasc":["CH.TW"],\
                       "_id":["CHN-3401"],"iso_a2":["CN"],"fips":["CH34"],"admin":["China"],\
                           "longitude":[121.559],"latitude":[25.0904],"geometry":[geo]})
gdfCN3 = pd.DataFrame(gdfCN3)
gdfCN3 = pd.concat([gdfCN3,gdfTW2],axis=0)
gdfCN3 = gpd.GeoDataFrame(gdfCN3, geometry='geometry')    
gdfCN3.plot()

# 处理香港特别行政区
# 读入原香港特别行政区admin1地图，获得香港的坐标	longitude	latitude 114.19	22.3268
gdf5 =  gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin1-HKG.json",\
                     encoding="utf-8")
gdf5.plot()
geo = gdfHK["geometry"].to_list()[0]
# 按中国admin1格式新建一个DataFrame
gdfHK2 = pd.DataFrame({"name":["Hong Kong"],"type":["Special Administrative Region"],"adm0_a3":["CHN"],"hasc":["CH.HK"],\
                       "_id":["CHN-3501"],"iso_a2":["CN"],"fips":["CH35"],"admin":["China"],\
                           "longitude":[114.19],"latitude":[22.3268],"geometry":[geo]})
gdfCN3 = pd.DataFrame(gdfCN3)
gdfCN3 = pd.concat([gdfCN3,gdfHK2],axis=0)
gdfCN3 = gpd.GeoDataFrame(gdfCN3, geometry='geometry')    
gdfCN3.plot()

# 处理澳门特别行政区 	
# 读入原澳门特别行政区admin1地图，获得澳门的坐标	longitude	latitude 113.56	22.1349
gdf6 =  gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin1-MAC.json",\
                     encoding="utf-8")
gdf6.plot()
geo = gdfMO["geometry"].to_list()[0]
# 按中国admin1格式新建一个DataFrame
gdfMO2 = pd.DataFrame({"name":["Macao"],"type":["Special Administrative Region"],"adm0_a3":["CHN"],"hasc":["CH.MC"],\
                       "_id":["CHN-3601"],"iso_a2":["CN"],"fips":["CH36"],"admin":["China"],\
                           "longitude":[113.56],"latitude":[22.1349],"geometry":[geo]})
gdfCN3 = pd.DataFrame(gdfCN3)
gdfCN3 = pd.concat([gdfCN3,gdfMO2],axis=0)
gdfCN3 = gpd.GeoDataFrame(gdfCN3, geometry='geometry')    
gdfCN3.plot()

# 中国admin1地图输出存盘
gdfCN3.to_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojsonCHN/admin1-CHN.json",\
             driver='GeoJSON',encoding="utf-8")

# 藏南达旺坐标，转换为gcj，在高德地图上显示
from coord_convert.transform import wgs2gcj
lon, lat = 91.773756958000263, 27.763810323000065
gcj_lon, gcj_lat = wgs2gcj(lon, lat)
print(gcj_lon, gcj_lat)



# 读入admin0世界地图，检查admin0、admin1海岛地图，另外找数据补全
gdf =  gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin0.json",\
                     encoding="utf-8")
gdf.plot()
# 周边海岛有关国家的admin0/admin1地图
# 日本：钓鱼岛
gdfJP = gdf[gdf.adm0_a3=="JPN"]
gdfJP.plot()
gdfJP2 =  gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin1-JPN.json",\
                     encoding="utf-8")
gdfJP2.plot()
# 印尼：南沙群岛
gdfID= gdf[gdf.adm0_a3=="IDN"]
gdfID.plot()
gdfID2 =  gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin1-IDN.json",\
                     encoding="utf-8")
gdfID2.plot()
# 马来西亚：南沙群岛
gdfMY= gdf[gdf.adm0_a3=="MYS"]
gdfMY.plot()
gdfMY2 =  gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin1-MYS.json",\
                     encoding="utf-8")
gdfMY2.plot()
# 菲律宾: 东沙群岛，中沙群岛
gdfPH= gdf[gdf.adm0_a3=="PHL"]
gdfPH.plot()
gdfPH2 =  gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin1-PHL.json",\
                     encoding="utf-8")
gdfPH2.plot()
# 越南：西沙群岛
gdfVM= gdf[gdf.adm0_a3=="VNM"]
gdfVM.plot()
gdfVM2 =  gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin1-VNM.json",\
                     encoding="utf-8")
gdfVM2.plot()

# 原中国admin1台湾及南海部分岛屿
gdfCN = gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojsonCHN/admin1-CHN.json",\
             encoding="utf-8")
# 台湾地图不包括太平岛等    
gdfTW = gdfCN[gdfCN.name=="Taiwan"]
gdfTW.plot()
# admin0-1中国部分岛屿图
gdfIslands = gdfCN[gdfCN.name=="Paracel Islands"]
gdfIslands.plot()

# polygon转换gcj坐标为wgs坐标
def poly2wgs(ploy):
    x, y = ploy.exterior.coords.xy
    ps = []
    for i in range(len(x)):
        x2,y2 = gcj2wgs(x[i],y[i])
        ps.append(Point(x2,y2))
    poly2 = Polygon(ps)
    return poly2
    
# gdf转换gcj坐标为wgs坐标    
def gdf2wgs(gdf):
    gdf2 = gdf.copy()    
    geos = gdf2["geometry"].to_list()
    for i in range(len(geos)):
        if isinstance(geos[i],Polygon):
            geos[i] = poly2wgs(geos[i])
        elif isinstance(geos[i],MultiPolygon):
            polys = [p for p in geos[i]]
            for j in range(len(polys)):
                polys[j] = poly2wgs( polys[j])
            geos[i] = MultiPolygon(polys)
    gdf2["geometry"] = geos
    return gdf2


# 用高德地图全国简图来检查admin0/admin1世界地图中海岛部分有没有问题
# 高德地图全国简图，Polygon数据格式不规范，改成MultiPolygon
import simplejson as json
file = "D:/temp/geojsonutf8/中华人民共和国/100000.json"
with open(file, encoding='utf-8') as f:
    collection = json.load(f, encoding='utf-8')
ps = collection['features'][0]["geometry"]["coordinates"]
geos = []
for i in range(len(ps)):
    geos.append(Polygon(ps[i]))
geos = MultiPolygon(geos)
gdfCN3 = gpd.read_file(file,encoding="utf-8")
gdfCN3["geometry"] = [geos]
gdfCN3.plot()
# 转换为wgs坐标
gdfCN4 = gdf2wgs(gdfCN3)
gdfCN4.plot()
# 用台湾地图匹配来检测地图的精度， 只有台湾岛，精度不够
gdfTW2 = gpd.overlay(gdfCN4, gdfTW, how='intersection')
gdfTW2.plot()


# 高德地图全国简图全图full, 已是MultiPolygon格式
gdfCN2 = gpd.read_file("D:/temp/geojsonutf8/中华人民共和国/100000_full.json",\
             encoding="utf-8")
gdfCN2.plot()
# 台湾地图不包括金门、太平岛等    
gdfTW2 = gdfCN2[gdfCN2.adcode==710000]
gdfTW2.plot()
# 转换成WGS坐标    
gdfCN5 = gdf2wgs(gdfCN2)    
gdfCN5.plot()
gdfTW2 = gdfCN5[gdfCN5.adcode==710000]
gdfTW2.plot()

# 用台湾地图匹配来检测地图的精度，有台湾岛、金门、澎湖、兰屿，精度还是不够
gdfTW2 = gpd.overlay(gdfCN5, gdfTW, how='intersection')
gdfTW2.plot()
# 与日本admin0/admin1地图没有交集
gdfJP3 = gpd.overlay(gdfCN5, gdfJP, how='intersection')
gdfJP3.plot()
gdfJP3 = gpd.overlay(gdfCN5, gdfJP2, how='intersection')
gdfJP3.plot()
# 与印尼admin0/admin1地图没有交集
gdfID3 = gpd.overlay(gdfCN5, gdfID, how='intersection')
gdfID3.plot()
gdfID3 = gpd.overlay(gdfCN5, gdfID2, how='intersection')
gdfID3.plot()
# 与马来西亚地图admin0/admin1没有交集
gdfMY3 = gpd.overlay(gdfCN5, gdfMY, how='intersection')
gdfMY3.plot()
gdfMY3 = gpd.overlay(gdfCN5, gdfMY2, how='intersection')
gdfMY3.plot()
# 与菲律宾admin0/admin1地图没有交集
gdfPH3 = gpd.overlay(gdfCN5, gdfPH, how='intersection')
gdfPH3.plot()
gdfPH3 = gpd.overlay(gdfCN5, gdfPH2, how='intersection')
gdfPH3.plot()
# 与越南admin0/admin1地图有交集，北纬22度，广西、云南，应该是陆上边界的坐标不准确
gdfVM3 = gpd.overlay(gdfCN5, gdfVM, how='intersection')
gdfVM3.plot()
gdfVM3 = gpd.overlay(gdfCN5, gdfVM2, how='intersection')
gdfVM3.plot()

# 高德地图三沙市的岛屿
file = "D:/temp/geojsonutf8/中华人民共和国/海南省/三沙市/460300.json"
gdfSS = gpd.read_file(file,encoding="utf-8")
gdfSS.plot()
# 用于协助选出岛屿，153个
import simplejson as json
with open(file, encoding='utf-8') as f:
    collection = json.load(f, encoding='utf-8')
# 转换为规范的MultiPolygon    
ps = collection['features'][0]["geometry"]["coordinates"]
geos = []
for i in range(len(ps)):
    geos.append(Polygon(ps[i]))
geos = MultiPolygon(geos)
gdfSS2 = gpd.read_file(file,encoding="utf-8")
gdfSS2["geometry"] = [geos]
gdfSS2.plot()
# 转换为wgs84坐标
gdfSS3 = gdf2wgs(gdfSS2)
gdfSS3.plot()
# 替换原admin1中的岛屿数据
gdfIslands2 = gdfIslands.copy()
geos = gdfSS3["geometry"].to_list()[0]
gdfIslands2["geometry"]=[geos]
gdfIslands2.plot()
gdfCN1 = gdfCN.copy()
gdfCN1.drop(gdfCN1[gdfCN1.name=="Paracel Islands"].index, inplace=True)
gdfCN1 = pd.concat([gdfCN1,gdfIslands2],axis=0)
gdfCN1.plot()
# 中国admin1地图输出存盘，命名为admin1-2-CHN.json备用
# 海岛地图补充了几十个南海小岛，但在admin1层面的地图上，看不出来，都太小了。
gdfCN1.to_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojsonCHN/admin1-2-CHN.json",\
             driver='GeoJSON',encoding="utf-8")


#海岛地图数据来自 https://github.com/xiaohk/ggplot2-china-map，不确定是wgs84还是gcj坐标系
gdfCNHN2 = gpd.read_file("D:/temp/中国地图shp南海诸岛等/bou2_4p.shp",encoding="gbk")
gdfCNHN3 = gdfCNHN2[gdfCNHN2.NAME=="海南省"]
gdfCNHN3.plot()
#gdfCNHN3.crs = {'init' :'epsg:4326'}
# 一般中国地图南中国海的坐标都是gcj，转换为wgs84
gdfCNHN4 = gdf2wgs(gdfCNHN3)
geos = gdfCNHN4["geometry"].to_list()
# 去掉海南岛本岛，有78个岛屿
geos = geos[1:]
geos2 = MultiPolygon(geos)
# 画出来看看，太小了，都看不到
s = s = gpd.GeoSeries([geos2])
s.plot()
# 替换原admin1中的岛屿数据
gdfIslands2 = gdfIslands.copy()
gdfIslands2["geometry"]=[geos2]
gdfIslands2.plot()
gdfCN1 = gdfCN.copy()
gdfCN1.drop(gdfCN1[gdfCN1.name=="Paracel Islands"].index, inplace=True)
gdfCN1 = pd.concat([gdfCN1,gdfIslands2],axis=0)
gdfCN1.plot()
# 中国admin1地图输出存盘,命名为admin1-1-CHN.json备用
# 海岛地图补充了几十个南海小岛，但在admin1层面的地图上，看不出来，都太小了。
gdfCN1.to_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojsonCHN/admin1-1-CHN.json",\
             driver='GeoJSON',encoding="utf-8")

    