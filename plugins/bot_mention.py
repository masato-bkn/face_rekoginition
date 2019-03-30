# coding: utf-8

import os
import base64
import requests
import shutil
import codecs
import json
import urllib

from slackbot.bot import respond_to     # @botname: で反応するデコーダ
from slackclient import SlackClient
import boto3

import aws_settings as aw
import slackbot_settings as ss
import face_reco
from resize_img import resize_img

@respond_to("(.*)")
def rekoginition_face(message,params):
    """
    slackに画像解析結果をリプライする。

    Parameters
    ----------
    message : ?
        メッセージ
    params　: ?
        ?
    """

    # 投稿された画像情報を取得
    try:
        # 多重起動防止

        url = ""
        if 'files' in message.body:
            url = message.body['files'][-1]['url_private_download']
            
            # 画像をダウンロード
            download_img(url)

            file_upload(os.path.basename(url))
            
            # 画像解析
            reko = face_reco.rekoginition_face(os.path.basename(url))
            
            # アタッチメントの作成
            attachments = make_attachments(reko[-1], os.path.basename(url))
            
            # リクエストを作成しslackに投げる
            request = make_post_request(message.body["channel"], attachments)
            result = urllib.request.urlopen(request)
            print(result)
    except Exception as e:
        print(e)
        
        # os.remove(os.path.basename(url))

def make_attachments(reko, img):
    """
    アタッチメントを作成する。

    Parameters
    ----------
    reko : dict
        画像解析結果
    img　: str
        画像名

    Returns
    -------
    attachments : dict
        アタッチメント
    """

    try:
        # 画像をリサイズ
        resized_img = resize_img(img, reko["BoundingBox"])
        
        # サムネイルURLに使用する画像をS3に送信する。
        file_upload(resized_img)
        
        # サムネイルURL
        thumb_url = f"{aw.S3_URL}/{aw.BUCKET_NAME}/{resized_img}"

        attachments = [
            {
                "color": "#36a64f",
                "title": "aws-rekoginition",
                "thumb_url": thumb_url,
                "fields": [
                    {
                        "title": "Emotion",
                        "value": reko["Emotion"],
                        "short": "true"
                    },
                    {
                        "title": "AgeRange",
                        "value": reko["AgeRange"],
                        "short": "true"
                    },
                    {
                        "title": "Gender",
                        "value": reko["Gender"],
                        "short": "true"
                    }
                ]
            }
        ]
        return attachments

    except Exception as e:
        print(e)
    
def download_img(url):
    """
    画像をダウンロードする。

    Parameters
    ----------
    url : str
        画像URL
    """

    try:
        rst = requests.get(url, allow_redirects=True, headers={'Authorization': 'Bearer %s' % ss.API_TOKEN}, stream=True).content
        
        ss.API_TOKEN
        target_file = codecs.open(os.path.basename(url), 'wb')
        target_file.write(rst)
        target_file.close()
    except Exception as e:
        print(e)

def make_post_request(channel, attachments):
    """
    ポストリクエストを作成する。

    Parameters
    ----------
    channel : str
        投稿するチャンネル
    attachments : dict
        アタッチメント
    """
    try:
        url = 'https://slack.com/api/chat.postMessage'
        
        headers = {
            'Authorization': f'Bearer {ss.API_TOKEN}',
            'Content-Type': 'application/json; charset=utf-8'
        }
        
        method = 'POST'
        
        data = {
            "channel": channel,
            "username": ss.BOT_NAME,
            "attachments": attachments
        }
        json_data = json.dumps(data).encode("utf-8")
        
        return urllib.request.Request(url=url, data=json_data, headers=headers, method=method)
    except Exception as e:
        print(e)

def file_upload(img):
    """
    画像をS3にアップロードする。

    Parameters
    ----------
    img : str
        画像名
    """
    try:
        boto3.resource('s3').Bucket(aw.BUCKET_NAME).upload_file(img,img)
    except Exception as e:
        print(e)
    