# coding: utf-8

import boto3

import aws_settings as aws

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
        分析結果。要素には感情、年齢、性別が入っている。
    """
    try:
        bucket= aws.BUCKET_NAME
        client = boto3.client('rekognition')
        
        response = client.detect_faces(Image={'S3Object': {'Bucket': bucket, 'Name': img}}, Attributes=['ALL'])

        details = response["FaceDetails"]
        # 分析結果
        analysis_result = []
        for detail in details:
            emotions = [emotion for emotion in detail["Emotions"]]
            emotion_dict = make_emotion_list(emotions)
            
            # 感情
            emotion = emotion_dict[sorted(emotion_dict.keys())[-1]]
            # 年齢
            age_range = f'{detail["AgeRange"]["Low"]} - {detail["AgeRange"]["High"]}'
            # 性別
            gender = f'{detail["Gender"]["Value"]}'
            # 年齢幅
            bouding_box = detail["BoundingBox"]

            analysis_result.append({
                ""
                "Emotion": emotion,
                "AgeRange": age_range,
                "Gender": gender,
                "BoundingBox" : bouding_box
            })

            return analysis_result

    except Exception as e:
        print(e)

def make_emotion_list(emotions):
    '''
    emotionリストを作って返す
    '''
    emotion_dict = {}
    for emotion in emotions:
        emotion_dict[emotion["Confidence"]] = emotion["Type"]
    return emotion_dict  # array[0] -> Confidence
                         # array[1] -> Type
