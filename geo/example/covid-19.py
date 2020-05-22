# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 11:02:42 2020
@author: Jean
"""

#导入相关库
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import geopandas as gpd
import contextily as ctx
import math

# 高德瓦片地图网址
gaodeurl="http://wprd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}"      

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


#爬取的网页地址，百度每日疫情数据
url="https://voice.baidu.com/act/newpneumonia/newpneumonia/?from=osari_pc_3"
#伪装请求头
headers ={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
#获取网页数据
r=requests.get(url,timeout=30,headers=headers)

#print(r.text)    
# with open("d:/temp/tmp.txt", "w") as fp:
#     fp.write(r.text)

# 抓取json数据
tag = "<script type=\"application/json\" id=\"captain-config\">"
nPos=r.text.find(tag)
text = r.text[nPos+52:]
tag = "</script>"
nPos=text.find(tag)
text2 = text[:nPos]
#print(text2)
data = json.loads(text2)
    
data2 = data["component"][0]["caseList"]

# with open("d:/temp/tmp.txt", "w") as fp:
#     fp.write(json.dumps(data2))
# 从 json提取数据项
provs = []  
citys = []  
for prov in data2:
    item = []
    item.append(prov["area"]); item.append(prov["confirmed"])
    item.append(prov["died"]); item.append(prov["crued"])
    item.append(prov["confirmedRelative"]); item.append(prov["diedRelative"])
    item.append(prov["curedRelative"]); item.append(prov["curConfirm"])
    item.append(prov["curConfirmRelative"]); 
    item.append(datetime.datetime.fromtimestamp(int(prov["relativeTime"])))
    provs.append(item)
    for city in prov["subList"]:
        item = []
        item.append(prov["area"]); item.append(city["city"])
        item.append(city["confirmed"]); item.append(city["died"])
        item.append(city["crued"]); item.append(city["confirmedRelative"])
        citys.append(item)
# 各省数据        
dfp = pd.DataFrame(provs)    
dfp.rename(columns={0:"area",1:"confirmed",2:"died",3:"cured",4:"confirmedRelative",\
                    5:"diedRelative",6:"curedRelative",7:"curConfirm",\
                    8:"curConfirmRelative",9:"relativeTime"}, inplace=True) 
dfp["confirmed"] = dfp["confirmed"].astype(int)
dfp = dfp.sort_values(by=["area"],axis = 0,ascending = True)
# 各市数据
dfc = pd.DataFrame(citys)    
dfc.rename(columns={0:"area",1:"city",2:"confirmed",3:"died",4:"cured",\
                    5:"confirmedRelative"},inplace=True)
# 插入1行，补上广东的云浮市    
dfc.loc[len(dfc)] = ["广东","云浮","0","0","0","0"]
# 因为有空值，令程序出错，把空值替换为0
dfc.replace("","0",inplace=True)
dfc["confirmed"] = dfc["confirmed"].astype(int)

# 合并坐标数据，来自高德地图
# 各省数据
types = {"adcode":str,"name":str,"lng":float,"lat":float}    
areas = pd.read_csv("D:/temp/geojsonutf8/行政区域代码坐标utf8.csv", dtype = types)
areasp = areas.iloc[1:35]
provs1=[]; provs2 = []; lats = []; longs=[]
for prov in dfp["area"]:
    temp = areasp.loc[areasp.name.str.contains(prov)]
    if len(temp)>0:
        provs1.append(prov); provs2.append(temp.iloc[0]["name"])
        # 转换为墨卡托投影坐标
        x,y = lonlat_to_Mercator_(temp.iloc[0]["lng"], temp.iloc[0]["lat"])
        lats.append(y); longs.append(x)
    else:
        print(prov)
dfpc = pd.DataFrame({"area":provs1,"name":provs2,"lat":lats,"lng":longs})        
dfpc = pd.merge(dfp,dfpc)
dfpc.to_csv("d:/temp/COVID-19/covid-19-provinces-CHN-Mer-Gcj.csv",index=False,encoding="utf-8")

# 各市数据
areasc = areas.loc[areas.adcode.str.contains("00")&(~areas.adcode.str.contains("0000"))]
cities1=[];cities2=[];lats = []; longs=[]; notfound = []
for city in dfc["city"]:
    temp = areasc.loc[areasc.name.str.contains(city)]
    if len(temp)>0:
        cities1.append(city); cities2.append(temp.iloc[0]["name"])
        # 转换为墨卡托投影坐标
        x,y = lonlat_to_Mercator_(temp.iloc[0]["lng"], temp.iloc[0]["lat"])        
        lats.append(y); longs.append(x)
    else:
        print(city)
        notfound.append(city)
dfcc = pd.DataFrame({"city":cities1,"name":cities2,"lat":lats,"lng":longs})        
dfcc = pd.merge(dfc,dfcc)
dfcc2 = dfcc.loc[dfcc.area.str.contains("广东")]

dfcc.to_csv("d:/temp/COVID-19/covid-19-cities-CHN-Mer-Gcj.csv",index=False,encoding="utf-8")
dfcc2.to_csv("d:/temp/COVID-19/covid-19-cities-GD-Mer-Gcj.csv",index=False,encoding="utf-8")

# 作图

# 全国疫情地图
# 地图数据，json格式
gdf = gpd.read_file("d:/temp/geojsonutf8/中华人民共和国/100000_full.json",encoding='utf-8')
# 转换为墨卡托投影坐标
gdf = gdf.to_crs(epsg=3857)
# gdf.plot()
# plt.show()
# 合并疫情数据到地图数据并作图
gdf2 = pd.merge(dfpc,gdf, left_on="name", right_on="name", how="left")
gdf = gpd.GeoDataFrame(gdf2, geometry='geometry')
#gdf.plot(column= 'confirmed', legend=True)
plt.rcParams['font.sans-serif'] = ['KaiTi'] # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
ax = gdf.plot(column= 'confirmed',cmap='Reds', legend=True,figsize=(16,16))
plt.xlabel('经度',fontsize=18)
plt.ylabel('纬度',fontsize=18)    
plt.title("全国疫情地图（确诊数）",fontsize=24)    
for idx, row in gdf.iterrows():
    ax.text(row.lng, row.lat, s=str(row.confirmed), horizontalalignment='center', fontsize=14,\
            bbox={'facecolor': "none", 'alpha':0.8, 'pad': 2, 'edgecolor':'none'}) 
plt.show()

gdf['confirmed2'] = gdf['confirmed'].apply(lambda x: str(x).zfill(5))
ax = gdf.plot(column= 'confirmed2',cmap='Reds', legend=False,figsize=(13,13))
plt.xlabel('经度',fontsize=18)
plt.ylabel('纬度',fontsize=18)    
plt.title("全国疫情地图（确诊数）",fontsize=24)    
for idx, row in gdf.iterrows():
    ax.text(row.lng, row.lat, s=str(row.confirmed), horizontalalignment='center', fontsize=14,\
            bbox={'facecolor': "none", 'alpha':0.8, 'pad': 2, 'edgecolor':'none'}) 
plt.show()

# 广东省疫情地图
gdf3 = gpd.read_file("d:/temp/geojsonutf8/中华人民共和国/广东省/440000_full.json",\
                     encoding='utf-8')
# 转换为墨卡托投影坐标
gdf3 = gdf3.to_crs(epsg=3857)    
# 合并疫情数据到地图数据
gdf4 = pd.merge(dfcc2,gdf3, left_on="name", right_on="name", how="left")
gdf3 = gpd.GeoDataFrame(gdf4, geometry='geometry')
# 计算每个多边形的地理中心备用，标注时用行政区域坐标更合适
gdf3['coords'] = gdf3['geometry'].apply(lambda x: x.representative_point().coords[:])
gdf3['coords'] = [coords[0] for coords in gdf3['coords']]
# 解决汉字显示的问题
plt.rcParams['font.sans-serif'] = ['KaiTi'] # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
# 通过对确诊病例数转化为字符串并在前面补零，减少各市之间填充颜色的差距，视觉效果更好
# 如果直接用数字，大部分地区颜色太浅，整体地图轮廓不清楚
gdf3["confirmed"] = gdf3["confirmed"].astype(int)
gdf3['confirmed2'] = gdf3['confirmed'].apply(lambda x: str(x).zfill(3))
# 画图
ax = gdf3.plot(column= 'confirmed2', legend=False, cmap='Reds', figsize=(16,16))
# 图标
plt.xlabel('经度',fontsize=18)
plt.ylabel('纬度',fontsize=18)    
plt.title("广东省疫情地图（确诊数）",fontsize=24)
# 在图上标注地区名称及确诊数字  
for idx, row in gdf3.iterrows():
    ax.text(row.lng, row.lat, s=row.city+str(row.confirmed), \
            horizontalalignment='center',fontsize=16, \
            bbox={'facecolor': "none", 'alpha':0.8, 'pad': 2, 'edgecolor':'none'}) 
plt.show()



# 输出不匹配的地市
print("\n".join(notfound))
with open("d:/temp/tmp.txt", "w") as fp:
    fp.write("\n".join(notfound)+"\n")


# 珠海市疫情地图，选出其县区数据
areaszh = areas.loc[areas.adcode.str.contains("4404")&(~areas.adcode.str.contains("00"))]
areaszh.to_csv("d:/temp/COVID-19/covid-19-areas-ZH-Gcj.csv",index=False,encoding="utf-8")
# 各区数据，随便指定个测试数据，这里等于合并了县区坐标数据与疫情数据
areaszh["confirmed"]   =[60,30,13] 
gdf5 = gpd.read_file("d:/temp/geojsonutf8/中华人民共和国/广东省/珠海市/440400_full.json",encoding='utf-8')
# 转换为墨卡托投影坐标，以便与底图合并
gdf5 = gdf5.to_crs(epsg=3857)
# 合并行政区域多边形坐标数据与驻地坐标数据及疫情数据（业务数据），注意坐标都已转换为墨卡托坐标。
gdf5 = pd.merge(areaszh,gdf5, left_on="name", right_on="name", how="left")
gdf6 = gpd.GeoDataFrame(gdf5, geometry='geometry')
# 计算行政区域地理中心坐标备用，后面还是用政府驻地的坐标来标示数据
gdf6['coords'] = gdf6['geometry'].apply(lambda x: x.representative_point().coords[:])
gdf6['coords'] = [coords[0] for coords in gdf6['coords']]
# 通过对确诊病例数转化为字符串并在前面补零，减少各市之间填充颜色的差距，视觉效果更好
# 如果直接用数字，大部分地区颜色太浅，整体地图轮廓不清楚
gdf6['confirmed2'] = gdf6['confirmed'].apply(lambda x: str(x).zfill(2))
# 解决汉字显示的问题
plt.rcParams['font.sans-serif'] = ['KaiTi'] # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
# 画多边形图,注意figsize的长宽要相等，否则后面 ctx.add_basemap(ax,source=gaodeurl) 可能取不到底图
# 另外，要与增加底图的 ctx.add_basemap(ax,source=gaodeurl) 整块代码一起执行，否则标题底图等加不上去，奇怪。
# 把 工具->偏好设置->IPython控制台->绘图->图形后端 改为“自动”，用Qt后端，则没有此问题，但会与Spyder调Orange冲突。
ax = gdf6.plot(column= 'confirmed2', cmap='Reds', legend=False, figsize=(16,16),alpha=0.5,edgecolor='k')
# 各种文字图标
plt.xlabel('经度',fontsize=18); plt.ylabel('纬度',fontsize=18)    
plt.title("珠海市疫情地图（确诊数）",fontsize=24) 
for idx, row in gdf6.iterrows():
    x,y = lonlat_to_Mercator_(row.lng,row.lat)
    ax.text(x, y, s=row["name"]+str(row.confirmed), horizontalalignment='center',fontsize=16, \
            color="red",bbox={'facecolor': "none", 'alpha':0.8, 'pad': 2, 'edgecolor':'none'}) 
# 增加底图
ctx.add_basemap(ax,source=gaodeurl)
plt.show()





# contextily包测试
# 只有1个行政区域，但有多个多边形
gdzh = gpd.read_file("d:/temp/geojsonutf8/中华人民共和国/广东省/珠海市/440400.json",encoding='utf-8')
gdzh = gdzh.to_crs(epsg=3857)
gdzh.plot(figsize=(16,16))
plt.show()
# 坐标的四个边界,都不对，为什么？只有1个行政区域，但有多个多边形，应该是随便选了第一个多边形计算
gdzh["geometry"].bounds
gdzh["geometry"].total_bounds
# 多个行政区域，多个多边形
gdzh = gpd.read_file("d:/temp/geojsonutf8/中华人民共和国/广东省/珠海市/440400_full.json",encoding='utf-8')
gdzh = gdzh.to_crs(epsg=3857)
gdzh.plot(figsize=(16,16))
plt.show()
# 多个行政区域多个多边形的情形，total_bounds对了，用total_bounds
gdzh["geometry"].bounds
gdzh["geometry"].total_bounds

we, se, ee, ne = gdzh["geometry"].total_bounds
# 计算视野需要的zoom参数 -6? 不对
zoom = ctx.tile._calculate_zoom(we, se, ee, ne)
# 计算要下载的瓦片数量，zoom=10:15，11:40, zoom = -6时只需1块 tile
_ = ctx.howmany(we, se, ee, ne, 11, ll=False)
# 下载瓦片图并画图，不接受负值的zoom，ll=True, 火星坐标等，ll=False, 墨卡托坐标,前面已转换成该坐标
# zoom=11是最合适的，就是上面ctx.add_basemap(ax,source=gaodeurl)自动选定的zoom
img, ext = ctx.bounds2img(we, se, ee, ne,11, ll=False,source=gaodeurl)
fig,ax = plt.subplots(1, figsize=(16,16))
plt.imshow(img, extent=ext)
# 另存成tif图像文件，程序挂起，？
_ = ctx.bounds2raster(we, se, ee, ne, 'zh.tif', ll=False)






# Orange Geo的离线地图，除美国外都是到省一级
gdf7 = gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin1-CHN.json",\
                     encoding='utf-8')
gdf7.plot(figsize=(16,12))
plt.show()
# 美国的地图边界到郡一级
gdf8 = gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin2-USA.json",\
                     encoding='utf-8')
gdf8.plot(figsize=(128,80))
plt.show()

# 手工建立映射表
provs3 = ["甘肃","青海","广西","贵州","重庆","北京","福建","安徽","广东","西藏","新疆","海南",\
          "宁夏","陕西","山西","湖北","湖南","四川","云南","河北","河南","辽宁","山东","天津",\
              "江西","江苏","上海","浙江","吉林","内蒙古","黑龙江","南海群岛"]
# 生成符合Orange Geo格式的数据    
gdf9 = gdf7[["admin","name"]]
gdf9["province"]=provs3
gdf10 = gdf[["area","confirmed","lat","lng"]]
gdf11 = pd.merge(gdf9,gdf10,left_on="province",right_on="area")
# 输出CSV，再从Orange读入
gdf11.to_csv("covid-19-CHN.csv",index=False,encoding="utf-8")

# 城市疫情数据转换为Orange data table，以便调试Orange Widget
dfcc3 = pd.merge(gdf9,dfcc, left_on="province",right_on="area")
dfcc3.rename(columns={"name_x":"name","name_y":"city2"},inplace=True)
dfcc3.to_csv("D:/temp/COVID-19/cities_CHN.csv",encoding="utf-8",index=False)
from Orange.data.pandas_compat import table_from_frame
otc = table_from_frame(dfcc3)
otc.save("D:/temp/COVID-19/covid-19-cities_CHN2.tab")

# 墨卡托->gcj->GPS
# 各市
from coord_convert.transform import gcj2wgs
import pandas as pd
dfcc3= pd.read_csv("D:/temp/COVID-19/cities_CHN.csv",encoding="utf-8")
lats = []; longs=[]
for idx,row in dfcc3.iterrows():   
    lng,lat = Mercator_to_lonlat(row.lng,row.lat)
    x,y = gcj2wgs(lng, lat)
    lats.append(y); longs.append(x)
dfcc3["lat"] = lats; dfcc3["lng"] = longs
dfcc3.to_csv("D:/temp/COVID-19/covid-19-cities_CHN-GPS.csv",encoding="utf-8",index=False)

# 各省
gdf11= pd.read_csv("D:/temp/COVID-19/covid-19-CHN.csv",encoding="utf-8")
lats = []; longs=[]
for idx,row in gdf11.iterrows():   
    lng,lat = Mercator_to_lonlat(row.lng,row.lat)
    x,y = gcj2wgs(lng, lat)
    lats.append(y); longs.append(x)
gdf11["lat"] = lats; gdf11["lng"] = longs
gdf11.to_csv("D:/temp/COVID-19/covid-19-CHN-GPS.csv",encoding="utf-8",index=False)

# 测试读入shp矢量坐标数据文件，由gadm.org下载，R语言RDS格式转换成shp格式
#全国
gdf = gpd.read_file("D:/temp/gadm/gadm36_CHN_0_sp.shp",encoding='utf-8')
# 转换为墨卡托投影坐标，以便与底图合并
gdf = gdf.to_crs(epsg=3857)
gdf.plot(figsize=(16,16))
gdf.to_file("D:/temp/gadm/gadm36_CHN_0_sp.json", driver='GeoJSON',encoding="utf-8")
gdf = gpd.read_file("D:/temp/gadm/gadm36_CHN_0_sp.json",encoding='utf-8')
gdf.plot(figsize=(16,16))

#各省
gdf1 = gpd.read_file("D:/temp/gadm/gadm36_CHN_1_sp.shp",encoding='utf-8')
# 转换为墨卡托投影坐标，以便与底图合并
gdf1 = gdf1.to_crs(epsg=3857)
gdf1.plot(figsize=(16,16))
gdf1.to_file("D:/temp/gadm/gadm36_CHN_1_sp.json", driver='GeoJSON',encoding="utf-8")
gdf1 = gpd.read_file("D:/temp/gadm/gadm36_CHN_1_sp.json",encoding='utf-8')
gdf1.plot(figsize=(16,16))

#各市
gdf2 = gpd.read_file("D:/temp/gadm/gadm36_CHN_2_sp.shp",encoding='utf-8')
# 转换为墨卡托投影坐标，以便与底图合并
gdf2 = gdf2.to_crs(epsg=3857)
gdf2.plot(figsize=(16,16))
gdf2.to_file("D:/temp/gadm/gadm36_CHN_2_sp.json", driver='GeoJSON',encoding="utf-8")
gdf2 = gpd.read_file("D:/temp/gadm/gadm36_CHN_2_sp.json",encoding='utf-8')
gdf2.plot(figsize=(16,16))

gdf22 = gdf2[["NAME_1","NL_NAME_1","NAME_2","NL_NAME_2"]]
name1=[]; name2=[]
for idx,row in gdf22.iterrows():
    pos = row.NL_NAME_1.find("|")
    if pos>0:
        name1.append(row.NL_NAME_1[pos+1:])
    else:
        name1.append(row.NL_NAME_1)
    pos = row.NL_NAME_2.find("|")
    if pos>0:
        name2.append(row.NL_NAME_2[pos+1:])
    else:
        name2.append(row.NL_NAME_2)
gdf22["NL_NAME_1"]=name1; gdf22["NL_NAME_2"]=name2 
gdf23 = gdf22.groupby("NAME_1").apply(lambda x: x["NAME_2"].tolist())
gdf23.to_csv("d:/temp/cities.csv",encoding="utf-8")


#县区
gdf3 = gpd.read_file("D:/temp/gadm/gadm36_CHN_3_sp.shp",encoding='utf-8')
# 转换为墨卡托投影坐标，以便与底图合并
gdf3 = gdf3.to_crs(epsg=3857)
gdf3.plot(figsize=(16,16))
gdf3.to_file("D:/temp/gadm/gadm36_CHN_3_sp.json", driver='GeoJSON',encoding="utf-8")
gdf3 = gpd.read_file("D:/temp/gadm/gadm36_CHN_3_sp.json",encoding='utf-8')
gdf3.plot(figsize=(16,16))

# 台湾
gdf4 = gpd.read_file("D:/temp/gadm/gadm36_TWN_2_sp.shp",encoding='utf-8')
# 转换为墨卡托投影坐标，以便与底图合并
gdf4 = gdf4.to_crs(epsg=3857)
gdf4.plot(figsize=(16,16))
gdf4.to_file("D:/temp/gadm/gadm36_TWN_2_sp.json", driver='GeoJSON',encoding="utf-8")
gdf4 = gpd.read_file("D:/temp/gadm/gadm36_TWN_2_sp.json",encoding='utf-8')
gdf4.plot(figsize=(16,16))
#香港
gdf5 = gpd.read_file("D:/temp/gadm/gadm36_HKG_1_sp.shp",encoding='utf-8')
# 转换为墨卡托投影坐标，以便与底图合并
gdf5 = gdf5.to_crs(epsg=3857)
gdf5.plot(figsize=(16,16))
gdf5.to_file("D:/temp/gadm/gadm36_HKG_1_sp.json", driver='GeoJSON',encoding="utf-8")
gdf5 = gpd.read_file("D:/temp/gadm/gadm36_HKG_1_sp.json",encoding='utf-8')
gdf5.plot(figsize=(16,16))
#澳门
gdf6 = gpd.read_file("D:/temp/gadm/gadm36_MAC_2_sp.shp",encoding='utf-8')
# 转换为墨卡托投影坐标，以便与底图合并
gdf6 = gdf6.to_crs(epsg=3857)
gdf6.plot(figsize=(16,16))
gdf6.to_file("D:/temp/gadm/gadm36_MAC_2_sp.json", driver='GeoJSON',encoding="utf-8")
gdf6 = gpd.read_file("D:/temp/gadm/gadm36_MAC_2_sp.json",encoding='utf-8')
gdf6.plot(figsize=(16,16))


# 中国地图到市一级，中国admin2行政区域是地级市，美国州直接到郡县，没有地级市
# 改成Orange Geo要求的格式，参考后面美国行政区域admin2 GeoJSON文件的结构设置字段名称及内容
# Orange Geo支持细节下钻到admin2
gdf3 = gpd.read_file("D:/temp/gadm/gadm36_CHN_2_sp.json",encoding='utf-8')
gdf3.plot(figsize=(16,16))
plt.show()
# hsac是国际邮政编码（管理层次缩写，例: US.NY.QU代表Queens, New York）
gdf3["hsac"]=gdf3["GID_2"].apply(lambda x: x.split("_")[0])
gdf3["NAME_0"] = "CN"
gdf3.rename(columns={"GID_0":"adm0_a3","NAME_1":"state","GID_2":"_id","ENGTYPE_2":"type",\
                     "NAME_2":"name","NAME_0":"iso_a2","GID_1":"fips"},inplace=True)
# fips是美国国内的行政区域编码，类似国内的行政区域编码，例：36081代表Queens, New York
gdf3["fips"]=  gdf3["hsac"]
gdf3.drop(["CC_2","HASC_2"],axis=1,inplace=True)
gdf3["capital"]=gdf3["name"]
# 输出admin2-CHN.json，注意文件要按Orange Geo的规范命名，并放在其指定的位置
# 一定要有 ""_id"列
gdf3.to_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin2-CHN.json",\
             driver='GeoJSON',encoding="utf-8")

# 输出不包含地图坐标的信息到excel表，以便浏览分析
gdf10 = gdf3
gdf10.drop(['geometry'],axis=1,inplace=True)
gdf10.to_csv("d:/temp/COVID-19/admin2-CHN.csv", index=False,encoding="utf-8")

# 美国的地图边界到郡县一级
gdf8 = gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin2-USA.json",\
                     encoding='utf-8')
gdf8.plot(figsize=(160,160))
plt.show()
# 输出不包含地图坐标的信息到excel表，以便浏览分析
gdf9 = gdf8
gdf9.drop(['geometry','coords'],axis=1,inplace=True)
gdf9.to_csv("d:/temp/admin2-USA.csv", index=False)

# 计算行政区域地理中心坐标备用，后面还是用政府驻地的坐标来标示数据
gdf8['coords'] = gdf8['geometry'].apply(lambda x: x.representative_point().coords[:])
gdf8['coords'] = [coords[0] for coords in gdf8['coords']]
gdf8["lng"] = [coords[0] for coords in gdf8['coords']]
gdf8["lat"] = [coords[1] for coords in gdf8['coords']]

gdf = gpd.read_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojson/admin1-CHN.json",\
                     encoding='utf-8')

dfc = pd.read_csv("D:/temp/COVID-19/covid-19-cities_CHN-GPS.csv",encoding="utf-8")
dfc = dfc[["city2","confirmed","died","cured","lat","lng"]]
dfc2 = pd.merge(gdf10,dfc,left_on="NL_NAME_2",right_on="city2")
dfc2.to_csv("d:/temp/COVID-19/covid-19-cities_CHN-GPS2.csv", index=False,encoding="utf-8")


gdf=gpd.read_file("D:/temp/广东省2014乡镇区划/广东省2014乡镇区划.shp",encoding="gbk")
gdf.plot()
gdf.to_file("D:/Anaconda3/Lib/site-packages/orangecontrib/geo/geojsonCHN/admin4-CHN.json",\
             driver='GeoJSON',encoding="utf-8")
