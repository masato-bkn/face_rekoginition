# coding: utf-8

import boto3

import aws_settings as aws
from invalid_img_exception import Invalid_img_exception

def rekoginition_face(img):
    """
    画像をrecoginotionに投げ、分析結果(感情、年齢、性別)を返す。

    Parameters
    ----------
    img : str
        画像名

    Returns
    -------
    analysis_result : dict
        分析結果
    """
    try:
        print("==  rekoginition_face start==")
        BUCKET= aws.BUCKET_NAME
        client = boto3.client('rekognition')
        response = client.detect_faces(Image={'S3Object': {'Bucket': BUCKET, 'Name': img}}, Attributes=['ALL'])
        
        details = response["FaceDetails"]

        # 分析に失敗した場合。
        if len(details) == 0:
            raise Invalid_img_exception
        
        # 分析結果
        analysis_result = []
        for detail in details:
            emotions = [emotion for emotion in detail["Emotions"]]
            emotion_dict = make_emotion_list(emotions)
            
            # emotion
            emotion = emotion_dict[sorted(emotion_dict.keys())[-1]]
            # age_range
            age_range = f'{detail["AgeRange"]["Low"]} - {detail["AgeRange"]["High"]}'
            # gender
            gender = detail["Gender"]["Value"]
            # BoundingBox
            bouding_box = detail["BoundingBox"]
            # Smile
            smile = detail["Smile"]["Value"]
            # Eyeglasses
            eyeglasses = detail["Eyeglasses"]["Value"]
            # Sunglasses
            sunglasses = detail["Sunglasses"]["Value"]
            # Beard
            beard = detail["Beard"]["Value"]
            # Mustache
            mustache = detail["Mustache"]["Value"]
            # EyesOpen
            eyesopen = detail["EyesOpen"]["Value"]
            # MouthOpen
            mouthopen = detail["MouthOpen"]["Value"]
            
            analysis_result.append({
                ""
                "Emotion": emotion,
                "AgeRange": age_range,
                "Gender": gender,
                "BoundingBox" : bouding_box,
                "Smile": smile,
                "Eyeglasses": eyeglasses,
                "Sunglasses": sunglasses,
                "Beard": beard,
                "Mustache": mustache,
                "EyesOpen": eyesopen,
                "MouthOpen": mouthopen
            })
            
            print("==  rekoginition_face end==")
            return analysis_result
    except Exception:
        raise

def make_emotion_list(emotions):
    """
    emotionリストを作って返す
    """
    try:
        print("==  make_emotion_list start==")
        emotion_dict = {}
        for emotion in emotions:
            emotion_dict[emotion["Confidence"]] = emotion["Type"]
            
        print("==  make_emotion_list end==")

        return emotion_dict  # key -> Confidence
                             # value -> Type
    except Exception:
        raise
