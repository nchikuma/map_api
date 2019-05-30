import geocoder
import requests
import json
import xml.etree.ElementTree as et
#import time
from geopy.geocoders import Nominatim
from geopy.point import Point
import numpy as np
import pandas as pd

locationData = "./sample.csv" 

restriction = [
         Point(35.265491,139.152611), #"小田原市"
         Point(36.366314,140.478731)  #"水戸市"
        ]

index_time    = "タイムスタンプ"
index_usr     = "ユーザー名"
index_line    = "最寄り駅の沿線名"
index_station = "最寄り駅の駅名"
index_dist    = "家から最寄り駅までかかる時間"
eki           = "駅"
sen           = "線"
ten           = "、"



def get_station_info(para_list):
    url = "http://express.heartrails.com/api/json?method=getStations"
    latlog=[]
    for para in para_list:
        name = para[0]
        line = para[1].split(ten)
        line = list(map(lambda x: x.replace(sen,""),line))
        
        #print("=====")
        name = name.replace(eki,"").replace('\"','').strip()
        payload = { "name" : name }
        headers = {"content-type":"application/json"}
        ret = requests.get(url,params=payload,headers=headers)
        ret = ret.json()["response"]["station"]
        for re in ret:
            re_name = re['name']
            re_line = re['line']
            #print("re_name=",re_name, end="")
            #print("re_line=",re_line, end="")
            isTrueReturn=False
            for l in line: isTrueReturn=isTrueReturn or (l in re_line)
            isTrueReturn=isTrueReturn and (re_name==name) 
            if isTrueReturn:
                latlog.append([re['y'],re['x']])
                #print(" OK")
                break
            #else:
            #    print("")
    return latlog


def add_to_geocode(address,fullinfo=False):
    geocode = []
    print("Searching.. %d locations"%(len(address)))
    for add in address:
        print(add)
        ret = geocoder.osm(add,timeout=5.0) #OpenStreetMap
        #ret = geocoder.google(location) #Google
        geocode.append([add].append(ret.latlng))
    print("Done")
    return geocode


def add_to_geo(address,fullinfo=False):
    geocode = []
    geolocator=Nominatim(
            user_agent="my-application",
            timeout=5.0
            )
    print("Searching.. %d locations"%(len(address)))
    for add in address:
        print(add)
        ret = geolocator.geocode(add,
                viewbox=restriction,
                bounded=True,
                country_codes=['jp']
                )
        if fullinfo:
            geocode.append([add,ret])
        else:
            geocode.append([ret.latitude,ret.longitude])
    print("Done")
    return geocode


def geocode_to_add(geocode):
    address = []
    for gc in geocode:
        add = geocoder.osm(gc,method="reverse")
        address.append(add)
    return address


def geo_to_add(geocode):
    address = []
    geolocator=Nominatim(
            user_agent="my-application",
            timeout=5.0
            )
    #print("Searching.. %d locations"%(len(geocode)))
    for gc in geocode:
        #print(gc)
        add = geolocator.reverse(gc)
        address.append(add)
    #print("Done")
    return address

##############################################

loc_list=pd.read_csv(locationData)
timestamp       = np.array(loc_list[index_time]    )
#usrname         = np.array(loc_list[index_usr]     )
usrname         = loc_list[index_usr]
nearestline     = np.array(loc_list[index_line]    )
neareststation  = np.array(loc_list[index_station] )
timefromstation = np.array(loc_list[index_dist]    )
#print(timestamp      ) 
print(usrname        ) 
#print(nearestline    ) 
#print(neareststation ) 
#print(timefromstation) 

para_list=np.stack([neareststation,nearestline],1)
print(para_list)

geocode=get_station_info(para_list)

geo_list=np.array(geocode)
geo_mean=np.mean(geo_list,axis=0)

geo_list = pd.DataFrame(geo_list)
  
print("Southernmost = " , usrname[geo_list[0].idxmin()])
print("Northernmost = " , usrname[geo_list[0].idxmax()])
print("Westernmost  = " , usrname[geo_list[1].idxmin()])
print("Esternmost   = " , usrname[geo_list[1].idxmax()])


print(">>> Averaged Geo Code:",geo_mean)
geo_list = []
geo_list.append(geo_mean)
address_list=geo_to_add(geo_list)
for add in address_list:
    print("==========")
    print(add)
