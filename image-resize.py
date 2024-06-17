import os
import boto3
from PIL import Image, ImageOps
from io import BytesIO
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # 클라이언트 요청에서 이미지 URL 파싱
        object_url = event['pathParameters']['objectUrl']
        bucket_name = "vplate-s3"  # 여기에 버킷 이름을 직접 설정합니다.
        object_key = object_url  # 객체 URL을 그대로 사용
        print(object_key)
        # S3에서 이미지 객체 가져오기
        image_object = s3.get_object(Bucket=bucket_name, Key=object_key)

        # 이미지 크기 조절 및 최적화
        resized_image = resize_and_optimize_image(image_object['Body'], width=200, height=200)

        # 이미지 데이터를 base64 인코딩
        encoded_image = base64.b64encode(resized_image.getvalue()).decode('utf-8')

        # 응답 구성
        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "image/jpeg"
            },
            "body": encoded_image,
            "isBase64Encoded": True
        }

    except Exception as e:
        # 오류가 발생하거나 예외 상황에서 요청받은 이미지를 응답
        print(e)
        if 'image_object' in locals():
            # image_object가 정의되어 있는 경우에만 그대로 응답
            response = {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "image/jpeg"
                },
                "body": base64.b64encode(image_object['Body'].read()).decode('utf-8'),
                "isBase64Encoded": True
            }
        else:
            # image_object가 정의되지 않은 경우 기본 오류 응답 반환
            response = {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "image/jpeg"
                },
                "body": base64.b64encode(b"An error occurred").decode('utf-8'),
                "isBase64Encoded": True
            }

    return response

def resize_and_optimize_image(image_stream, width, height):
    # 이미지 열기
    image = Image.open(image_stream)

    # 원본 이미지의 비율에 따라 새로운 가로 길이 계산
    orig_width, orig_height = image.size
    ratio = height / orig_height
    width = int(orig_width * ratio)

    # 이미지 리사이즈
    resized_image = image.resize((width, height), Image.Resampling.LANCZOS)

    # 이미지가 RGB 모드가 아니라면 RGB로 변환
    if resized_image.mode != 'RGB':
        if resized_image.mode == 'RGBA':
            background = Image.new('RGB', resized_image.size, (255, 255, 255))
            background.paste(resized_image, mask=resized_image.split()[3])
            resized_image = background
        else:
            resized_image = resized_image.convert('RGB')

    output = BytesIO()
    resized_image.save(output, format="JPEG", quality=80)
    output.seek(0)
    return output