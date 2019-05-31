#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import requests
from io import StringIO
import string
import pandas as pd
import numpy as np

import matplotlib.colors as colors
from matplotlib import cm

from scipy import misc
import tempfile

from math import pi
from math import tanh
from math import sin
from math import asin
from math import exp
from numpy import arctanh


# ピクセル座標を経緯度に変換する
def fromPointToLatLng(pixelLat,pixelLon, z):
    L = 85.05112878
    lon = 180 * ((pixelLon / 2.0**(z+7) ) - 1)
    lat = 180/pi * (asin(tanh(-pi/2**(z+7)*pixelLat + arctanh(sin(pi/180*L)))))
    return lat, lon


# 経緯度をピクセル座標に変換する
def fromLatLngToPoint(lat,lon, z):
    L = 85.05112878
    pointX = int( (2**(z+7)) * ((lon/180) + 1) )
    pointY = int( (2**(z+7)/pi) * (-1 * arctanh(sin(lat * pi/180)) + arctanh(sin(L * pi/180))) )
    return pointX, pointY    


# 経緯度をタイル座標に変換する(pix: 1タイルのピクセル数)
def fromLatLngToTile(lat,lon, z,pix=256):
    pointX, pointY = fromLatLngToPoint(lat,lon, z)
    return pointX/pix, pointY/pix    


# 指定経緯度範囲が異なるタイルにまたがる最小のズームレベルとそのタイル座標を返す
def getTile(Tiles, minLat, minLon, maxLat, maxLon):
    
    for z in range(0,20):
        tileX1, tileY1 = fromLatLngToTile(minLat, minLon, z)
        tileX2, tileY2 = fromLatLngToTile(maxLat, maxLon, z)
        
        if tileX2 - tileX1 >= Tiles - 1  and tileY1 - tileY2 >= Tiles - 1: break

    return z, tileX1, tileY1, tileX2, tileY2 

# 画像補正用シグノイド関数
def sigmoid(x):
    a = 5.0
    b = 0.4
    return 1.0 / (1.0 + exp(a * (b - x)))



# 地図画像データを読み込み各ピクセルをRGB値に変換した配列を返す
def load_imgColors(urlFormat, z, x1, y1, x2, y2):

    im=None
    for x in range(int(x1), int(x2)+1):
        im_v=None
        for y in range(int(y2), int(y1)+1):

            #地図画像データを読み込む
            url = urlFormat.format(z=z,x=x,y=y)
            print(url)
            response = requests.get(url)
            if response.status_code == 404:
                 #地図画像データが無い区画は白塗りにする
                 colors=np.ones((256, 256, 3), dtype=object)
            else:
                 #画像READ
                 with tempfile.NamedTemporaryFile(dir="./") as f:
                     f.write(response.content)
                     f.file.seek(0)
                     img = misc.imread(f.name)
                 
            #　画像タイルを縦に連結
            if y == int(y2):
                 im_v = img
            else:
                 im_v = np.concatenate([im_v, img], axis = 0) #縦
                
        # 画像タイルを横に連結
        if x == int(x1):
            im = im_v
        else:
            im = np.concatenate([im,im_v], axis = 1) #横
        
    print(im.shape)
    return im



def makeMap(minLat, minLon, maxLat, maxLon,Tiles=3):
    # Tiles: 描画に使用する縦横の最小タイル数

    # 指定経緯度範囲の最適ズームとタイル座標範囲を求める
    z, x1, y1, x2, y2  = getTile(Tiles, minLat, minLon, maxLat, maxLon)


    # OpenStreetMapのタイル画像のURLフォーマット
    urlFormat = 'https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png'

    # OpenStreetMapのタイル画像を読み込み連結して１枚の画像として返す
    imgColors = load_imgColors(urlFormat, z, x1, y1, x2, y2) 

    # 地図画像RGBデータは256で割って0..1に正規化しておく
    imgColors = imgColors/256.

    # 合成画像の輝度値の標準偏差を32,平均を80になんとなく変更
    imgColors = (imgColors-np.mean(imgColors))/np.std(imgColors)*32+80
    imgColors = (imgColors-imgColors.min())/(imgColors.max()-imgColors.min())
    
    # コントラスト補正をかける
    lut = np.empty(256)
    sigmoid0 = sigmoid(0.0)
    sigmoid1 = sigmoid(1.0)
    for i in range(256):
        x = i / 255.0
        x = (sigmoid(x) - sigmoid0) / (sigmoid1 - sigmoid0)  # コントラスト補正をかける
        lut[i] = 255.0 * x

    imgColors = np.uint8(imgColors*255)
    imgColors = lut[imgColors]
    imgColors /= 255.

    return imgColors
