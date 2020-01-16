# coding: utf-8

import json
import urllib

import  boto3

import aws_settings as aw
import file_operation as fo
import slackbot_settings as ss

def make_attachments(reko, img):
    """
    アタッチメントを作成する。

    Parameters
    ----------
    reko : dict
        ファイル解析結果
    img : str
        ファイル名

    Returns
    -------
    attachments : dict
        アタッチメント
    """

    try:
        # ファイルをリサイズ
        resized_img = fo.resize_img(img, reko["BoundingBox"])

        # サムネイルURLに使用するファイルをS3に送信する。
        fo.file_upload(ss.DIR_PATH + resized_img)
        print("aaaa")
        
        # サムネイルURL
        thumb_url = f"{aw.S3_URL}/{aw.BUCKET_NAME}/{resized_img}"

        attachments = [
            {
                "color": ss.COLOR,
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
                    },
                    {
                        "title": "Smile",
                        "value": str(reko["Smile"]),
                        "short": "true"
                    },
                    {
                        "title": "Eyeglasses",
                        "value": str(reko["Eyeglasses"]),
                        "short": "true"
                    },
                    {
                        "title": "Sunglasses",
                        "value": str(reko["Sunglasses"]),
                        "short": "true"
                    },
                    {
                        "title": "Beard",
                        "value": str(reko["Beard"]),
                        "short": "true"
                    },
                    {
                        "title": "Mustache",
                        "value": str(reko["Mustache"]),
                        "short": "true"
                    },
                    {
                        "title": "EyesOpen",
                        "value": str(reko["EyesOpen"]),
                        "short": "true"
                    },
                    {
                        "title": "MouthOpen",
                        "value": str(reko["MouthOpen"]),
                        "short": "true"
                    }
                ]
            }
        ]
        return attachments

    except Exception:
        raise

def make_post_request(channel, img, attachments):
    """
    解析結果をpostするメッセージ作成。

    Parameters
    ----------
    channel : str
        投稿するチャンネル
    img : str
        ファイル名
    attachments : dict
        アタッチメント
    """
    try:
        print("==make_post_request start ==")
        
        url = ss.MESSAGE_POST_URL
        
        headers = {
            'Authorization': f'Bearer {ss.API_TOKEN}',
            'Content-Type': 'application/json; charset=utf-8'
        }
        
        method = 'POST'
    
        data = {
            "channel": channel,
            "icon_url": ss.ICON_URL,
            "username": ss.BOT_NAME,
            "text": img,
            "attachments": attachments
        }
        json_data = json.dumps(data).encode("utf-8")
        
        return urllib.request.Request(url=url, data=json_data, headers=headers, method=method)
        
        print("==make_post_request end ==")
    except Exception:
        raise

def make_post_wait_request(channel,text):
    """
    file.listAPIに投稿したファイルが反映されるまでの繋ぎメッセージを作成

    Parameters
    ----------
    channel : str
        チャンネル
    text : str
        テキスト
    """

    try:
        print("==make_post_wait_request start==")
        URL = ss.MESSAGE_POST_URL
        
        headers = {
            'Authorization': f'Bearer {ss.API_TOKEN}',
            'Content-Type': 'application/json; charset=utf-8'
        }
        
        method = 'POST'
    
        data = {
            "channel": channel,
            "icon_url": ss.ICON_URL,
            "username": ss.BOT_NAME,
            "text": text
        }
        json_data = json.dumps(data).encode("utf-8")
        print("==make_post_wait_request end==")
        return urllib.request.Request(url=URL, data=json_data, headers=headers, method=method)

    except Exception:
        raise

def post_failure_message(channel,stack_trace):
    try:
        print("==post_failure_message start==")
        URL = ss.MESSAGE_POST_URL
        
        headers = {
            'Authorization': f'Bearer {ss.API_TOKEN}',
            'Content-Type': 'application/json; charset=utf-8'
        }
        
        attachments = [
            {
                "color": ss.COLOR,
                "fields": [
                    {
                        "title": "Stacktrace",
                        "value": stack_trace,
                        "short": "true"
                    }
                ]
            }
        ]

        method = 'POST'
    
        data = {
            "channel": channel,
            "icon_url": ss.ICON_URL,
            "username": ss.BOT_NAME,
            "text": ss.DETECT_FACE_FAILURE_MESSAGE,
            "attachments": attachments
        }
        json_data = json.dumps(data).encode("utf-8")
        request = urllib.request.Request(url=URL, data=json_data, headers=headers, method=method)
        urllib.request.urlopen(request)

        print("==post_failure_message end==")

    except Exception:
        raise