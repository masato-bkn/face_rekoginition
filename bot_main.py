# coding: utf-8

import json
import os
from time import sleep 
import traceback
import urllib

import aws_settings as aw
import face_reco
import file_operation as fo
from invalid_img_exception import Invalid_img_exception
import mention
import slackbot_settings as ss


def main(message,context):
    """
    slackにファイル解析結果をリプライする。

    Parameters
    ----------
    message : dict
        メッセージ
    context　: LambdaContext
        コンテキスト
    """

    # 投稿されたファイル情報を取得
    try:
        print("rekoginition_face start")
        
        # 投稿したファイルがfile.listAPIに反映されるまでの繋ぎメッセージをpost
        # (反映されるまで約30秒かかる)
        for text in ss.TEXTS:
            request = mention.make_post_wait_request(message["channel_name"],text)
            result = urllib.request.urlopen(request)
            sleep(9)
        
        # ファイルデータ取得
        url = fo.get_file_data(message["timestamp"])['url_private_download']
        
        # ファイルをダウンロード
        fo.download_img(url)
        
        # ファイルをs3にアップロード
        fo.file_upload(ss.DIR_PATH + os.path.basename(url))

        # ファイル解析
        reko = face_reco.rekoginition_face(os.path.basename(url))

        # アタッチメントの作成
        attachments = mention.make_attachments(reko[-1], os.path.basename(url))
            
        # リクエストを作成しslackに投げる
        request = mention.make_post_request(message["channel_name"], os.path.basename(url), attachments)
        result = urllib.request.urlopen(request)
        
        print("== post_result==")
        print(result)
        
        # tmp配下のファイル削除
        fo.remove_file(ss.DIR_PATH)
        
        print("rekoginition_face end")
    except Invalid_img_exception:
        # 解析失敗の場合、スタックトレースをpost
        stack_trace = traceback.format_exc()
        mention.post_failure_message(message["channel_name"], stack_trace)
        
    except Exception as e:
        print(e)
        
