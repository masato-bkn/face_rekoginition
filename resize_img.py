# coding: utf-8

import math

import cv2
from PIL import Image

def resize_img(name, img_box):
    try:
        # 画像を読み込む
        # # cv2が日本語対応していないので、ファイル名は英数字
        img = cv2.imread(name)
        
        # 画像の縦横値を取得
        h, w = img.shape[0:2]
        
        print("w" + str(w))
        print("h" + str(h))
        
        """
        ['Width']:0.19862690567970276
        ['Height']:0.38048163056373596
        ['Left']:0.5620142817497253
        ['Top']:-0.04076896980404854
        """
        
        # リサイズ値算出
        # img_boxには顔の位置が%で入っている。
        wr = math.ceil(w * img_box["Width"])
        wl = math.ceil(w * img_box["Height"])
        hb = math.ceil(h * img_box["Left"])
        ht = math.ceil(h * img_box["Top"])
        
        print("wr" + str(wr))
        print("wl" + str(wl))
        print("hb" + str(hb))
        print("ht" + str(ht))
        
        # cv2.imwriteにマイナス値を設定できないので、
        # topがマイナスの場合は0に設定。
        if ht < 0:
            ht = 0
        
        # 顔を正方形にリサイズ
        if hb > wl:
            wl = hb
        else:
            hb = wl

        # リサイズ
        cut_img = img[ht:ht + hb, wr:wr + wl]
        
        #書き出し
        cv2.imwrite(name, cut_img)

        img = Image.open(name)
        img.thumbnail((75, 75), Image.ANTIALIAS)
        img.save(name)
        
        return name
    except Exception as e:
        print(e)