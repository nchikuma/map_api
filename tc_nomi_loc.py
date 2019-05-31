#!/bin/python

import myGeocoding

import sys
import numpy as np
import pandas as pd




def main(locationData = "./sample.csv" ):
    
    ## Data Format
    index_time    = "タイムスタンプ"
    index_usr     = "ユーザー名"
    index_line    = "最寄り駅の沿線名"
    index_station = "最寄り駅の駅名"
    index_dist    = "家から最寄り駅までかかる時間"
    eki           = "駅"
    sen           = "線"
    ten           = "、"
    
    # Read data
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
    

    # Pre-processing
    tmp = []
    for para in para_list:
        name = para[0]
        line = para[1].split(ten)
        line = list(map(lambda x: x.replace(sen,""),line))
        name = name.replace(eki,"").replace('\"','').strip()
        tmp.append([name,line])
    para_list = tmp
    del tmp

    print(para_list)

    ## Call myGeocoding Class 
    mygeo = myGeocoding.myGeocoding()

    geocode=mygeo.get_station_info(para_list)
    
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
    address_list=mygeo.geo_to_add(geo_list)
    for add in address_list:
        print("==========")
        print(add)

if __name__ == '__main__':

    if len(sys.argv)!=0:
        main(sys.argv[1])
    else:
        main()
