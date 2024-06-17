import boto3
import os
from rembg import remove
from PIL import Image
from urllib.parse import urlparse
import time

print('Loading function')

def lambda_handler(event, context):
    try:
        image_path = event['image_path']
        print("image_path = " + image_path)
        # "image_path": "https://vplate-s3.s3.ap-northeast-2.amazonaws.com/1553520742423Scene1.jpg"

        s3_path = event['s3_path']
        print("s3_path = " + s3_path)
        # "s3_path": "/userSource/1553520742423Scene1.png"
        
        file_name = os.path.basename(image_path)
        print("file_name = " + file_name)
        basename, ext = os.path.splitext(file_name)
        print("basename = " + basename)

        # URL을 파싱하여 도메인과 경로를 추출
        parsed_url = urlparse(image_path)
        # 경로에서 필요한 부분만 추출
        dirname = os.path.dirname(parsed_url.path)
        print("dirname = " + dirname)

        bucket = 'vplate-s3'
        lambda_tmp_path = '/tmp/'

        s3 = boto3.client('s3')
        print(f"s3 = {s3}")
        
        input_image_path = os.path.join(lambda_tmp_path, file_name)
        print(f"input_image_path = {input_image_path}")

        if dirname.startswith('/'):
            dirname = dirname[1:]
        print(f"dirname = {dirname}")
        
        if dirname != '':
            down_path = dirname + '/' + file_name
        else:
            down_path = file_name
            
        print(f"down_path = {down_path}")

        time.sleep(1)
        s3.download_file(bucket, down_path, input_image_path)
        print("s3.download_file 완료!")
        
        output_path = os.path.join(lambda_tmp_path, basename +  '_re.png')
        print(f"output_path = {output_path}")

        # image = Image.open(output_path)
        # 이미지 타입 확인
        # image_type = image.format
        # print(f"image_type = {image_type}")

        # with open(input_image_path, 'rb') as i:
        #     with open(output_path, 'wb') as o:
        #         input = i.read()
        #         output = remove(input)
        #         o.write(output)
        input = Image.open(input_image_path)
        output = remove(input)
        output.save(output_path)
        
        if s3_path.startswith('/'):
            s3_path = s3_path[1:]
        print(f"s3_path startswith = {s3_path}")
                
        s3.upload_file(output_path, bucket, s3_path)
        print("s3.upload_file 완료!")
        
        s3_url = f"https://{bucket}.s3.amazonaws.com/{s3_path}"

        # 이미지 파일 열기
        img = Image.open(input_image_path)
        img = img.convert('RGB')
        
        # 이미지 정보 추출
        width, height = img.size  # 가로 길이와 세로 길이
        file_size_bytes = os.path.getsize(input_image_path)  # 파일 크기 (바이트)
        file_size_mb = max(round(file_size_bytes / (1024 * 1024), 2), 0.01)

        response = {
            'statusCode': 200,
            'isSuccess': True,
            'url': s3_url,
            'width': width,
            'height': height,
            'file_size': file_size_mb,
            'file_extension': ext.lower()[1:]
        }
    except Exception as e:    
        print(f'Error: {str(e)}')
        response = {
            'isSuccess': False,
        }
    finally:
        print('rembg Lambda function execution completed.')

    return response

def split_path(path):
  domain = os.path.splitext(path)[0].split('/')[-2]
  path = path.replace(domain, '')
  path = path.replace('/', '')
  print(f"domain = {domain}")
  print(f"path = {path}")

  return path