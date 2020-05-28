# -*- coding: utf-8 -*-
"""
Created on Tue May 26 11:45:46 2020

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
import time

application_key = "Your key of tianditu.gov.cn"

# 1.天地图 地理编码，批量处理
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
            # print(lat, lng)
            return(lng,lat)
         else:
            # print(address+" 没找到")
            return(None,None)         
     except Exception as ex:
         # print(ex)
         return(None,None) 
     

# 1.天地图 提供的是静态地图及标注，不是其它地图的动态地图调起API
# width,height: 1~1024, zoom:3~18
def TDURL_mask(location: str,address:str, name:str,application_key:str):
    url_a = 'http://api.tianditu.gov.cn/staticimage? width=800&height=600&zoom=18&layers=vec_c,cva_c'
    url_b = "&center=" + location+"&markers="+location+"&markerStyles=-1,,"+quote(address)
    url_c = '&tk='+application_key
    URL = url_a + url_b + url_c
    webbrowser.open(URL)

#测试地址地理编码服务及地图标记服务
address = "广东省珠海市香洲区人民东路2号市府大院1号楼3楼"
nsrmc = "珠海市人民政府办公室"
address = "珠海市井岸镇中兴南路404号406号"
nsrmc = "珠海市斗门尖峰房产开发公司"
x, y = TDGeoCode(address)
    
# 在浏览器上标示出该地址的位置
TDURL_mask(str(x)+","+str(y), address, nsrmc,application_key)

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
zcdz["ZCDZ"] = zcdz["ZCDZ"].str.strip()
# 丢掉地址为空的
zcdz = zcdz[~zcdz.ZCDZ.isna()]
# 是否包含市字
zcdz1 = zcdz[~zcdz.ZCDZ.str.contains("市")]       
zcdz2 = zcdz[zcdz.ZCDZ.str.contains("市")] 
# 包含“市场”但不包含“珠海市”   
zcdz3 = zcdz2[(zcdz2.ZCDZ.str.contains("市场"))&(~zcdz2.ZCDZ.str.contains("珠海市"))]
# 包含“珠海市”或不包含“市场”
zcdz2 = zcdz2[(~zcdz2.ZCDZ.str.contains("市场"))|(zcdz2.ZCDZ.str.contains("珠海市"))]
# 不包含城市前缀的
zcdz1 = pd.concat([zcdz1,zcdz3])
zcdz1 = zcdz1.sort_values(by=["ZCDZ"],axis = 0,ascending = True)
# 排序后丢掉为字母数字的无效地址, pandas dataframe字符串字段没有比较函数，但python有字符串比较，绕个弯实现
zcdz1["ZCDZ"] = zcdz1["ZCDZ"].apply(lambda x: x if x>"万山" else None)
zcdz1 = zcdz1[~zcdz1.ZCDZ.isna()]
zcdz3 = zcdz1[zcdz1.ZCDZ.str.contains(r"中国|上海|香港|深圳|中山|区|县",regex=True)]
zcdz4 = zcdz1[~zcdz1.ZCDZ.str.contains(r"中国|上海|香港|深圳|中山|区|县",regex=True)]
zcdz5 = zcdz3[zcdz3.ZCDZ.str.contains(r"香洲区|斗门区|金湾区",regex=True)]
zcdz3 = zcdz3[~zcdz3.ZCDZ.str.contains(r"香洲区|斗门区|金湾区",regex=True)]
zcdz4 = pd.concat([zcdz4,zcdz5]); del zcdz5
# 补上城市前缀
zcdz4["ZCDZ"] = zcdz4["ZCDZ"].apply(lambda x: "珠海市"+x)
# 不规范的地址，不多，不处理。
zcdz5 = zcdz4[zcdz4.ZCDZ.str.contains(r"：|:",regex=True)]
zcdz6 = zcdz2[zcdz2.ZCDZ.str.contains(r"：|:",regex=True)]
# 取头1000条解释地址
# zcdz7 = zcdz4.head(1000)
# 全量解释地址
zcdz7 = zcdz4.copy()

# 调用地理编码服务，批量解释地址
# 先用不带城市定义的地址测试一下
lng=[]; lat=[]
t1 = time.time()    
for i in range(len(zcdz7["ZCDZ"])):
    address = zcdz7["ZCDZ"].iloc[i]
    x, y = TDGeoCode(address)
    lng.append(x); lat.append(y)
    t2 = time.time()        
    print(i,address,x,y,round(t2-t1,2))

# 合并坐标数据    
zcdz7["lng"]=lng; zcdz7["lat"]=lat
# 先把坐标数据存盘，以便下次装入使用及从crash中恢复
zcdz7.to_csv("D:/temp/税务登记地址/税务登记地址坐标.csv",index=False,encoding="utf-8")
# 重新读入数据
types={"DJXH":str,"NSRMC":str,"ZCDZ":str,"JDXZ_DM":str,"lng":float,"lat":float}
zcdz7 = pd.read_csv("D:/temp/税务登记地址/税务登记地址坐标.csv",encoding="utf-8",dtype=types)
# 随机抽样10个地址，看看地址解释的效果
zcdz8 = zcdz7.sample(n=10, axis=0)




# 天地图的地图标记是静态的，改用高德地图来显示地址解释的效果，都是GCJ坐标，不用转换
def GaoDeURL_mask(df):
    df["lng"] = df["lng"].astype(str)
    df["lat"] = df["lat"].astype(str)
    dz = df["ZCDZ"].to_list(); name = df["NSRMC"].to_list()
    lng = df["lng"].to_list(); lat = df["lat"].to_list()
    markers = lng[0]+","+lat[0]+","+name[0]+"@"+dz[0]
    for i in range(len(dz)-1):
        marker = "|"+lng[i+1]+","+lat[i+1]+","+name[i+1]+"@"+dz[i+1]
        markers = markers + marker
    url_a = 'https://uri.amap.com/marker'
    url_b = "?markers=" + markers
    url_c = '&src=mypage&callnative=0'
    URL = url_a + url_b + url_c
    print(URL)
    webbrowser.open(URL)

# 在浏览器上标示出抽样地址的位置
# 天地图的坐标在高德中显示会有几百米的偏差，虽然都是GCJ坐标，看起来不能互用
GaoDeURL_mask(zcdz8)

# 在浏览器上标示出抽样地址的位置
# 天地图自己标注，坐标就是准确的
def dfTDURL_mask(df):
    df["lng"] = df["lng"].astype(str)
    df["lat"] = df["lat"].astype(str)
    dz = df["ZCDZ"].to_list(); name = df["NSRMC"].to_list()
    lng = df["lng"].to_list(); lat = df["lat"].to_list()
    for i in range(len(dz)):
        TDURL_mask(str(lng[i])+","+str(lat[i]), dz[i], name[i],application_key)

dfTDURL_mask(zcdz8)


import pandas as pd
from shapely.geometry import  Point,Polygon;
from geopandas import GeoSeries,GeoDataFrame

types={"DJXH":str,"NSRMC":str,"ZCDZ":str,"JDXZ_DM":str,"lng":float,"lat":float}
zcdz7 = pd.read_csv("D:/temp/税务登记地址/税务登记地址坐标.csv",encoding="utf-8",dtype=types)

# 随机抽样10个地址，看看地址解释的效果
zcdz8 = zcdz7.sample(n=10, axis=0)
zcdz8.rename(columns={"NSRMC":"name","ZCDZ":"address"},inplace=True)

key = "Your key of tianditu.gov.cn"
zoom = 11
#命名生成的html
htmlfile = "D:/JetBrains/IdeaProjects/MyPyhton38/scripts/test.html" 

TDshowMarker(zcdz8,zoom,htmlfile,key)

TDshowMarker(zcdz8,zoom,htmlfile,key,False)


def TDshowMarker(df,zoom,GEN_HTML,key,showName = True):
    import webbrowser
    lngs = df["lng"].to_list(); lats = df["lat"].to_list()
    names = df["name"].to_list(); addresses = df["address"].to_list()
    ps = []
    # 计算几何中心
    for i in range(len(df)):
        ps.append((lngs[i],lats[i]))
    poly = Polygon(ps)
    central = poly.centroid
    #打开文件，准备写入
    f = open(GEN_HTML,'w',encoding="utf-8")
    #写入文件
    message = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
        <title>天地图－地图API地址解析标注</title>
        <script type="text/javascript" src="http://api.tianditu.gov.cn/api?v=4.0&tk="""+key+""""></script>
        <style type="text/css">
            body, html {
                width: 100%;
                height: 100%;
                margin: 0;
                font-family: "微软雅黑";
            }
            #mapDiv {
                height: 100%;
                width: 100%;
            }
            input, p {
                margin-top: 10px;
                margin-left: 5px;
                font-size: 14px;
            }
        </style>
        <script>
            var map
            var zoom = """+str(zoom)+";"
    f.write(message) 
    message = """
            function onLoad() {
                //初始化地图对象
                map = new T.Map("mapDiv");
                //设置显示地图的中心点和级别
                map.centerAndZoom(new T.LngLat(%s, %s), zoom);
    """%(str(central.x),str(central.y))
    f.write(message) 
    message = """
                // 向地图添加标注
                var bounds = map.getBounds();
                var sw = bounds.getSouthWest();
                var ne = bounds.getNorthEast();
                var lngSpan = Math.abs(sw.lng - ne.lng);
                var latSpan = Math.abs(ne.lat - sw.lat);
                var point;
                var marker;
                var label;
    """
    f.write(message) 
    
    for i in range(len(lngs)):
        message = """
         point = new T.LngLat(%s,%s);
         marker = new T.Marker(point);// 创建标注
         map.addOverLay(marker);
         label = new T.Label({
                text: "%s",
                position: point,
                offset: new T.Point(-9, 0)
            });
         //创建地图文本对象
         map.addOverLay(label);
        """%(str(lngs[i]),str(lats[i]),names[i] if showName else addresses[i])
        f.write(message) 
    
    message = """
            }
        </script>
    </head>
    <body onLoad="onLoad()">
    <div id="mapDiv"></div>
    <p>本例演示添加多个点的标注</p>
    </body>
    </html>
    """
    f.write(message) 
    
    #关闭文件
    f.close()
    #运行完自动在网页中显示
    webbrowser.open(GEN_HTML,new = 1) 
    

# 测试工具函数
# 随机抽样10个地址，看看地址解释的效果
zcdz8 = zcdz7.sample(n=10, axis=0)
zcdz8.rename(columns={"NSRMC":"name","ZCDZ":"address"},inplace=True)
zcdz8.drop(['lng', 'lat'], axis=1, inplace=True)
application_key = "Your key of tianditu.gov.cn"

from orangecontrib.geo.TianDiTu import dfTDGeoCode,TDshowMarker
zcdz9 = dfTDGeoCode(zcdz8,application_key)
zoom = 11
#命名生成的html
htmlfile = "D:/JetBrains/IdeaProjects/MyPyhton38/scripts/test.html" 
TDshowMarker(zcdz9,zoom,htmlfile,application_key,False)

