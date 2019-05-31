import geocoder
import requests
import json
import xml.etree.ElementTree as et
#import time
from geopy.geocoders import Nominatim
from geopy.point import Point
import numpy as np
import pandas as pd

class myGeocoding:

    restriction = [
             Point(35.265491,139.152611), #"小田原市"
             Point(36.366314,140.478731)  #"水戸市"
            ]
 
    def get_station_info(self,para_list):
        # para_list : [ [ "Station Name", ["Line1 Name","Line2 Name"] ], ... ]
        # Return a list of [lattitude,longitude]
    
        url = "http://express.heartrails.com/api/json?method=getStations"
        latlog=[]
        for para in para_list:
            name = para[0]
            line = para[1]
            #line = para[1].split(ten)
            #line = list(map(lambda x: x.replace(sen,""),line))
            #print("=====")
            #name = name.replace(eki,"").replace('\"','').strip()
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
    
    
    def add_to_geocode(self,address,fullinfo=False):
        geocode = []
        print("Searching.. %d locations"%(len(address)))
        for add in address:
            print(add)
            ret = geocoder.osm(add,timeout=5.0) #OpenStreetMap
            #ret = geocoder.google(location) #Google
            geocode.append([add].append(ret.latlng))
        print("Done")
        return geocode
    
    
    def add_to_geo(self,address,fullinfo=False):
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
    
    
    def geocode_to_add(self,geocode):
        address = []
        for gc in geocode:
            add = geocoder.osm(gc,method="reverse")
            address.append(add)
        return address
    
    
    def geo_to_add(self,geocode):
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
