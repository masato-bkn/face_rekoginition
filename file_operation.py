# coding: utf-8

import os
import glob
import math
import codecs

import  requests
import cv2
from PIL import Image
import boto3

import aws_settings as aw
import  slackbot_settings as ss


def remove_file(dir_path):
    """
    lambda上の画像保存領域配下のファイルを削除する

    Parameters
    ----------
    dir_path : str
      削除対象のディレクトリパス

    Returns
    -------
    なし
    
    """

    print("== remove_file start==")
    # tmp配下のファイルを取得
    file_list = glob.glob(dir_path + "*")
    
    # 取得ファイル数
    print(f"取得ファイル数:{len(file_list)}")
    
    # サイズ
    print(f"サイズ:{get_dir_size(dir_path)}")
    
    #ファイル削除
    for file in file_list:
        print(f"ファイル名:{os.path.basename(file)}")
        os.remove(file)

    print("== remove_file end==")
    
def get_dir_size(dir_path):
    """
    ディレクトリサイズを算出

    Parameters
    ----------
    なし
    
    Returns
    -------
    total : ディレク配下に存在するファイルサイズの合計
    
    """

    print("== get_dir_size start==")
    total = 0
    with os.scandir(dir_path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    
    print("== get_dir_size end==")
    
    return total

def resize_img(name, img_box):
    try:
        print("==resize start==")
        
        # 画像を読み込む
        # cv2が日本語対応していないので、ファイル名は英数字
        file_path = ss.DIR_PATH + name
        img = cv2.imread(file_path)
        
        # 画像の縦横値を取得
        h, w = img.shape[0:2]
        
        # リサイズ値算出
        # img_boxには顔の位置が%で入っている。
        wl = math.ceil(w * img_box["Width"])
        hb = math.ceil(h * img_box["Height"])
        wr = math.ceil(w * img_box["Left"])
        ht = math.ceil(h * img_box["Top"])
        
        print("==bounding_box==")
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
        cv2.imwrite(file_path, cut_img)
        
        # 保存
        img = Image.open(file_path)
        img.thumbnail((75, 75), Image.ANTIALIAS)
        img.save(file_path)

        print("==resize end==")
        
        return name
    except Exception as e:
        print(e)

def file_upload(img):
    """
    ファイルをS3にアップロードする。

    Parameters
    ----------
    img : str
        ファイル名
    """
    try:
        print("== file_upload start==")
        
        s3fp = os.path.basename(img)
        boto3.resource('s3').Bucket(aw.BUCKET_NAME).upload_file(img,s3fp)
        
        # s3upload コマンド
        print(f"boto3.resource('s3').Bucket({aw.BUCKET_NAME}).upload_file({img},{s3fp})")
        
        print("== file_upload end==")
    except Exception:
        raise

def download_img(url):
    """
    ファイルをダウンロードする。

    Parameters
    ----------
    url : str
        ファイルURL
    """

    try:
        print("== download_img start==")
        result = requests.get(url, allow_redirects=True, headers={'Authorization': 'Bearer %s' % ss.API_TOKEN}, stream=True).content
        
        target_file = codecs.open(ss.DIR_PATH + os.path.basename(url), 'wb')

        target_file.write(result)
        target_file.close()
        print("== download_img end==")

    except Exception:
        raise

def get_file_data(timestamp):
    """
    timestampの一番新しいファイルを取得する。

    Parameters
    ----------
    timestamp : str
        ファイルが投稿されたtimestamp
    """
    
    try:
        print("== get_file_data start ==")
        
        LEGACY_TOKEN = ss.LEGACY_TOKEN 
        url = f"{ss.FILE_LIST_URL}?token={LEGACY_TOKEN}&count=5&pretty=1&page={1}"
        
        response = requests.get(url)
        data = response.json()
        
        # timestampの一番新しいファイル
        latest_file = sort_data(data)
        
        print(f"取得ファイルデータ:{latest_file}")
        print("== get_file_data end ==")

        return latest_file
    except Exception:
        raise
    
def sort_data(file_data):
    """
    timestampが一番新しいファイルを返す。

    Parameters
    ----------
    file_data : str
        ファイルデータ
    """
    try:
        print("sort_data start")
        files = file_data["files"]
        
        timestamp = ""
        # timestampが一番新しいファイル
        latest_file = ""
        
        for i,file in enumerate(files):
            if i == 0:
                timestamp = files[i]["timestamp"]
                latest_file = files[i]
            else:
                if int(files[i]["timestamp"]) > int(timestamp):
                    latest_file = files[i]
                    timestamp = files[i]["timestamp"]
        print("sort_data end")
        return latest_file
    except Exception:
        raise

