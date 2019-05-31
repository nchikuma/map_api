#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import makeMap
import matplotlib.pyplot as plt

def main():

    # Output figure name
    figname = "outfigname.png"
    

    # 東京駅
    center_Lat = 35.681111
    center_Lon = 139.766667

    gap = 0.002 * 100
    minLat = center_Lat - gap
    minLon = center_Lon - gap * 1.2
    maxLat = center_Lat + gap
    maxLon = center_Lon + gap * 1.2

    print("北緯%f 東経%f - 北緯%f 東経%f" % (minLat, minLon, maxLat, maxLon))

    image=makeMap.makeMap(minLat, minLon, maxLat, maxLon)    
    

    plt.imshow(image, vmin = 0, vmax = 255)
    plt.savefig(figname, dpi=72)
    plt.show()
   

if __name__ == '__main__':
    main()
