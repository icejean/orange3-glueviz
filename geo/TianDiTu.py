# -*- coding: utf-8 -*-
"""
Created on Thu May 28 08:51:31 2020

@author: Jean
"""

import pandas as pd
import requests
from shapely.geometry import  Point,Polygon;
import webbrowser


# 天地图 地理编码
def TDGeoCode(address, key):    
     url = 'http://api.tianditu.gov.cn/geocoder?ds={"keyWord":"'+address+'"}&tk='+key
     #print(url)
     try:
         # 模拟浏览器，否则会被禁止访问
         headers={
             'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
             # Modified by Jean @ 2022/01/06
             'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
             'Accept-Encoding': 'gzip, deflate, br',
             'Accept-Language': 'zh-CN,zh;q=0.9',
             'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
             'sec-ch-ua-mobile': '?0',
             'Upgrade-Insecure-Requests': '1'
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
     
# 天地图 地理编码，批量处理
def dfTDGeoCode(df,key):      
    lng=[]; lat=[]
    for i in range(len(df["address"])):
        address = df["address"].iloc[i]
        x, y = TDGeoCode(address,key)
        lng.append(x); lat.append(y)
    res = df.copy()
    res["lng"]=lng; res["lat"]=lat
    return(res)
        

# 天地图 地图标记, JavaScript API
def TDshowMarker(df,zoom,GEN_HTML,key,showName = True):
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
    
